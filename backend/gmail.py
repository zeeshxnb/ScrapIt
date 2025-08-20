"""
Gmail Integration Module - Consolidated
Handles Gmail API integration and email synchronization
"""
import os
import time
import email.utils
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

from database import get_db
from models import User, Email
from auth import get_current_user

router = APIRouter()

class GmailService:
    """Gmail API service"""
    
    def __init__(self, user: User):
        self.user = user
        self.service = None
        
    def authenticate(self) -> bool:
        """Authenticate with Gmail and refresh token if needed"""
        try:
            credentials = Credentials(
                token=self.user.get_access_token(),
                refresh_token=self.user.get_refresh_token(),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
            )
            
            # Refresh token if expired
            if credentials.expired and credentials.refresh_token:
                from google.auth.transport.requests import Request
                credentials.refresh(Request())
                
                # Update stored tokens
                from database import get_db
                db = next(get_db())
                self.user.set_access_token(credentials.token)
                if credentials.refresh_token:
                    self.user.set_refresh_token(credentials.refresh_token)
                db.commit()
            
            self.service = build('gmail', 'v1', credentials=credentials)
            return True
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False
    
    def list_messages(self, query: str = "", max_results: int = None) -> List[dict]:
        """List messages matching the query"""
        if not self.authenticate():
            return []
        
        try:
            # Get messages matching query
            result = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = result.get('messages', [])
            
            # Get additional pages if available
            while 'nextPageToken' in result and (max_results is None or len(messages) < max_results):
                page_token = result['nextPageToken']
                result = self.service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
                messages.extend(result.get('messages', []))
                
                if max_results and len(messages) >= max_results:
                    messages = messages[:max_results]
                    break
            
            return messages
        except Exception as e:
            print(f"Error listing messages: {str(e)}")
            return []
    
    def search_messages(self, query: str, max_results: int = 100) -> List[dict]:
        """Search for messages matching the query"""
        return self.list_messages(query, max_results)
    
    def get_message(self, message_id: str) -> dict:
        """Get a specific message"""
        if not self.authenticate():
            return None
        
        try:
            return self.service.users().messages().get(userId='me', id=message_id).execute()
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit exceeded
                print(f"Rate limit exceeded for message {message_id}, skipping...")
                time.sleep(1)
            return None
        except Exception:
            return None
            
    def batch_modify_messages(self, message_ids: List[str], add_label_ids: Optional[List[str]] = None, remove_label_ids: Optional[List[str]] = None) -> bool:
        """Apply label modifications to many messages at once.
        
        For system labels (e.g., 'INBOX', 'TRASH', 'SPAM'), pass the label name directly in add/remove lists.
        """
        if not message_ids:
            return True
        if not self.service and not self.authenticate():
            return False
        try:
            body = {
                'ids': message_ids,
                'addLabelIds': add_label_ids or [],
                'removeLabelIds': remove_label_ids or [],
            }
            self.service.users().messages().batchModify(userId='me', body=body).execute()
            return True
        except Exception as e:
            print(f"Gmail batchModify failed: {str(e)}")
            return False
            
    def batch_delete_messages(self, message_ids: List[str]) -> bool:
        """Permanently delete many messages at once."""
        if not message_ids:
            return True
        if not self.service and not self.authenticate():
            return False
        try:
            self.service.users().messages().batchDelete(userId='me', body={'ids': message_ids}).execute()
            return True
        except Exception as e:
            print(f"Gmail batchDelete failed: {str(e)}")
            return False
            
    def archive_message(self, message_id: str) -> bool:
        """Archive a message (remove from inbox)."""
        return self.batch_modify_messages([message_id], remove_label_ids=["INBOX"])
        
    def trash_message(self, message_id: str) -> bool:
        """Move a message to trash."""
        return self.batch_modify_messages([message_id], add_label_ids=["TRASH"], remove_label_ids=["INBOX"])
    
    def sync_emails(self, db: Session, max_results: int = None, incremental: bool = False, batch_size: int = 100, specific_labels: list = None, only_inbox: bool = True) -> dict:
        """Enhanced email sync with full Gmail access - gets ALL emails from ALL folders/labels"""
        if not self.authenticate():
            return {"success": False, "error": "Authentication failed"}
        
        try:
            # Build query based on parameters
            if specific_labels:
                # Sync specific folders/labels
                label_queries = [f"label:{label}" for label in specific_labels]
                query = " OR ".join(label_queries)
                print(f"Syncing specific labels: {specific_labels}")
            else:
                # Default: only sync INBOX for speed and expected counts
                query = "in:inbox" if only_inbox else "in:anywhere"
                print("Sync scope:", "INBOX only" if only_inbox else "ALL folders/labels")
            
            # For incremental sync, add date filter
            if incremental:
                latest_email = db.query(Email).filter(
                    Email.user_id == self.user.id
                ).order_by(Email.received_date.desc()).first()
                
                if latest_email and latest_email.received_date:
                    # Get emails after the latest one we have
                    after_date = latest_email.received_date.strftime("%Y/%m/%d")
                    query = f"{query} after:{after_date}"
            
            print(f"🔍 Query: '{query}'")
            print(f"📊 Max results: {max_results if max_results else 'UNLIMITED'}")
            print(f"📦 Batch size: {batch_size}")
            print(f"🔄 Sync type: {'INCREMENTAL' if incremental else 'FULL'}")
            
            # Get messages from Gmail - NO LIMITS unless specified
            messages = self.list_messages(query=query, max_results=max_results)
            
            new_count = 0
            updated_count = 0
            error_count = 0
            processed_ids = set()
            batch_count = 0
            
            # Process emails in batches for better performance and memory management
            for i in range(0, len(messages), batch_size):
                batch_count += 1
                batch_messages = messages[i:i + batch_size]
                # Progress bar for processing
                processed = i + len(batch_messages)
                progress_percent = (processed / len(messages)) * 100
                progress_bar = "█" * int(progress_percent / 5) + "░" * (20 - int(progress_percent / 5))
                print(f"\r💾 Processing: [{progress_bar}] {processed}/{len(messages)} emails ({progress_percent:.1f}%)", end="", flush=True)
                
                for msg in batch_messages:
                    try:
                        # Skip if we've already processed this ID (deduplication)
                        if msg['id'] in processed_ids:
                            continue
                        processed_ids.add(msg['id'])
                        
                        # Check if email already exists in database
                        existing_email = db.query(Email).filter(
                            Email.gmail_id == msg['id'],
                            Email.user_id == self.user.id
                        ).first()
                        
                        # Get full message details from Gmail
                        full_message = self.get_message(msg['id'])
                        if not full_message:
                            error_count += 1
                            continue
                        
                        # Extract email data
                        headers = {header['name']: header['value'] for header in full_message.get('payload', {}).get('headers', [])}
                        subject = headers.get('Subject', '')
                        sender = headers.get('From', '')
                        recipient = headers.get('To', '')
                        snippet = full_message.get('snippet', '')
                        
                        # Parse date
                        date_str = headers.get('Date')
                        received_date = None
                        if date_str:
                            try:
                                # Parse email date format
                                timetuple = email.utils.parsedate_tz(date_str)
                                if timetuple:
                                    timestamp = email.utils.mktime_tz(timetuple)
                                    received_date = datetime.fromtimestamp(timestamp)
                            except:
                                pass
                        
                        # Get labels
                        labels = full_message.get('labelIds', [])
                        
                        if existing_email:
                            # Update existing email
                            existing_email.subject = subject
                            existing_email.sender = sender
                            existing_email.recipient = recipient
                            existing_email.snippet = snippet
                            existing_email.received_date = received_date
                            existing_email.labels = labels
                            updated_count += 1
                        else:
                            # Create new email
                            new_email = Email(
                                gmail_id=msg['id'],
                                user_id=self.user.id,
                                subject=subject,
                                sender=sender,
                                recipient=recipient,
                                snippet=snippet,
                                received_date=received_date,
                                labels=labels,
                                is_processed=False
                            )
                            db.add(new_email)
                            new_count += 1
                    except Exception as e:
                        print(f"\nError processing message {msg['id']}: {str(e)}")
                        error_count += 1
                
                # Commit batch
                db.commit()
            
            print(f"\n✅ Sync completed: {new_count} new, {updated_count} updated, {error_count} errors")
            
            return {
                "success": True,
                "new_emails": new_count,
                "updated_emails": updated_count,
                "error_count": error_count,
                "total_batches": batch_count
            }
        except Exception as e:
            print(f"Sync error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_labels(self) -> List[dict]:
        """Get all labels for the user"""
        if not self.authenticate():
            return []
        
        try:
            results = self.service.users().labels().list(userId='me').execute()
            return results.get('labels', [])
        except Exception as e:
            print(f"Error getting labels: {str(e)}")
            return []
    
    def ensure_label(self, label_name: str) -> str:
        """Ensure a label exists, creating it if necessary, and return its ID"""
        if not self.authenticate():
            return None
        
        try:
            # Check if label already exists
            labels = self.get_labels()
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']
            
            # Create new label
            label = self.service.users().labels().create(
                userId='me',
                body={'name': label_name}
            ).execute()
            
            return label['id']
        except Exception as e:
            print(f"Error ensuring label: {str(e)}")
            return None

# Request Models
class SyncRequest(BaseModel):
    max_results: Optional[int] = None
    incremental: bool = True
    batch_size: int = 100
    only_inbox: bool = True
    labels: Optional[List[str]] = None

# Routes
@router.post("/sync")
async def sync_emails(
    body: SyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fast, sensible sync defaults: incremental INBOX by default."""

    batch_size = max(10, min(500, body.batch_size))

    gmail_service = GmailService(current_user)
    result = gmail_service.sync_emails(
        db,
        max_results=body.max_results,
        incremental=body.incremental,
        batch_size=batch_size,
        specific_labels=body.labels,
        only_inbox=body.only_inbox if not body.labels else False,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    sync_message = f"Sync completed: {result['new_emails']} new, {result['updated_emails']} updated"
    if result.get('total_batches'):
        sync_message += f" (processed in {result['total_batches']} batches)"

    return {
        "message": sync_message,
        **result
    }

@router.get("/emails")
async def get_emails(
    limit: int = 50,
    offset: int = 0,
    category: str = None,
    is_spam: bool = None,
    is_processed: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's emails with filtering"""
    
    # Build query
    query = db.query(Email).filter(Email.user_id == current_user.id)
    
    # Apply filters
    if category:
        query = query.filter(Email.category == category)
    if is_spam is not None:
        query = query.filter(Email.is_spam == is_spam)
    if is_processed is not None:
        query = query.filter(Email.is_processed == is_processed)
    
    # Get total count for pagination
    total_count = query.count()
    
    # Apply pagination and ordering
    emails = query.order_by(Email.received_date.desc()).offset(offset).limit(limit).all()
    
    return {
        "emails": [
            {
                "id": str(email.id),
                "gmail_id": email.gmail_id,
                "subject": email.subject,
                "sender": email.sender,
                "snippet": email.snippet,
                "category": email.category,
                "confidence_score": email.confidence_score,
                "is_spam": email.is_spam,
                "is_processed": email.is_processed,
                "spam_reason": email.spam_reason,
                "sender_risk": email.sender_risk,
                "received_date": email.received_date.isoformat() if email.received_date else None,
                "labels": email.labels
            }
            for email in emails
        ],
        "total": total_count,
        "limit": limit,
        "offset": offset
    }

@router.get("/emails/{email_id}")
async def get_email(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific email"""
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return {
        "id": str(email.id),
        "gmail_id": email.gmail_id,
        "subject": email.subject,
        "sender": email.sender,
        "snippet": email.snippet,
        "category": email.category,
        "confidence_score": email.confidence_score,
        "is_spam": email.is_spam,
        "is_processed": email.is_processed,
        "spam_reason": email.spam_reason,
        "sender_risk": email.sender_risk,
        "received_date": email.received_date.isoformat() if email.received_date else None,
        "labels": email.labels
    }

@router.get("/labels")
async def get_labels(
    current_user: User = Depends(get_current_user)
):
    """Get all labels for the user"""
    gmail_service = GmailService(current_user)
    labels = gmail_service.get_labels()
    
    return {
        "labels": labels
    }

@router.post("/full-sync")
async def full_sync(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Full sync of ALL emails (non-incremental)"""
    gmail_service = GmailService(current_user)
    result = gmail_service.sync_emails(
        db,
        incremental=False,
        only_inbox=False  # Get ALL emails
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/sync-all-folders")
async def sync_all_folders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync emails from all folders"""
    gmail_service = GmailService(current_user)
    result = gmail_service.sync_emails(
        db,
        only_inbox=False  # Get ALL emails
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

# Export router
gmail_router = router