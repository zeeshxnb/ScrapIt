"""
Gmail Integration Module - Consolidated
Handles Gmail API integration and email synchronization
"""
import os
import time
import email.utils
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
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
        """Authenticate with Gmail"""
        try:
            credentials = Credentials(
                token=self.user.get_access_token(),
                refresh_token=self.user.get_refresh_token(),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
            )
            
            self.service = build('gmail', 'v1', credentials=credentials)
            return True
        except Exception:
            return False
    
    def list_messages(self, query: str = None, max_results: int = 50):
        """List Gmail messages with rate limiting"""
        if not self.service:
            self.authenticate()
            
        try:
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            # Small delay to respect rate limits
            time.sleep(0.1)
            
            return result.get('messages', [])
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit exceeded
                print("Rate limit exceeded, waiting...")
                time.sleep(2)
                return []
            return []
        except Exception:
            return []
    
    def get_message(self, message_id: str):
        """Get single Gmail message with rate limiting"""
        if not self.service:
            self.authenticate()
            
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            # Small delay to respect rate limits
            time.sleep(0.05)
            
            # Extract headers
            headers = {}
            if 'payload' in message and 'headers' in message['payload']:
                for header in message['payload']['headers']:
                    headers[header['name'].lower()] = header['value']
            
            return {
                'id': message.get('id'),
                'subject': headers.get('subject', ''),
                'from': headers.get('from', ''),
                'to': headers.get('to', ''),
                'date': headers.get('date', ''),
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            }
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit exceeded
                print(f"Rate limit exceeded for message {message_id}, skipping...")
                time.sleep(1)
            return None
        except Exception:
            return None
    
    def sync_emails(self, db: Session, max_results: int = 100, incremental: bool = True) -> dict:
        """Enhanced email sync with incremental support and deduplication"""
        if not self.authenticate():
            return {"success": False, "error": "Authentication failed"}
        
        try:
            # For incremental sync, get emails newer than the latest we have
            query = None
            if incremental:
                latest_email = db.query(Email).filter(
                    Email.user_id == str(self.user.id)
                ).order_by(Email.received_date.desc()).first()
                
                if latest_email and latest_email.received_date:
                    # Get emails after the latest one we have
                    after_date = latest_email.received_date.strftime("%Y/%m/%d")
                    query = f"after:{after_date}"
            
            # Get messages from Gmail
            messages = self.list_messages(query=query, max_results=max_results)
            
            new_count = 0
            updated_count = 0
            error_count = 0
            processed_ids = set()
            
            for msg in messages:
                try:
                    # Skip if we've already processed this ID (deduplication)
                    if msg['id'] in processed_ids:
                        continue
                    processed_ids.add(msg['id'])
                    
                    # Check if email already exists
                    existing = db.query(Email).filter(
                        Email.gmail_id == msg['id'],
                        Email.user_id == str(self.user.id)
                    ).first()
                    
                    # Get full message details
                    email_data = self.get_message(msg['id'])
                    if not email_data:
                        error_count += 1
                        continue
                    
                    # Parse received date
                    received_date = datetime.now()
                    if email_data['date']:
                        try:
                            received_date = email.utils.parsedate_to_datetime(email_data['date'])
                        except:
                            # Fallback to current time if date parsing fails
                            pass
                    
                    if existing:
                        # Update existing email if needed
                        updated = False
                        if existing.subject != email_data['subject']:
                            existing.subject = email_data['subject']
                            updated = True
                        if existing.labels != email_data['labels']:
                            existing.labels = email_data['labels']
                            updated = True
                        
                        if updated:
                            updated_count += 1
                    else:
                        # Create new email record
                        email_record = Email(
                            user_id=str(self.user.id),
                            gmail_id=email_data['id'],
                            subject=email_data['subject'] or '(No Subject)',
                            sender=self.extract_email_address(email_data['from']),
                            recipient=self.extract_email_address(email_data['to']),
                            snippet=email_data['snippet'] or '',
                            labels=email_data['labels'] or [],
                            received_date=received_date,
                            is_processed=False
                        )
                        
                        db.add(email_record)
                        new_count += 1
                
                except Exception as e:
                    error_count += 1
                    print(f"Error processing message {msg.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Commit all changes
            db.commit()
            
            return {
                "success": True,
                "new_emails": new_count,
                "updated_emails": updated_count,
                "error_count": error_count,
                "total_processed": len(processed_ids),
                "sync_type": "incremental" if incremental else "full"
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def extract_email_address(self, email_string: str) -> str:
        """Extract clean email address from 'Name <email@domain.com>' format"""
        if not email_string:
            return ""
        
        try:
            # Use email.utils to parse the address
            name, address = email.utils.parseaddr(email_string)
            return address or email_string
        except:
            # Fallback: simple regex-like extraction
            if '<' in email_string and '>' in email_string:
                start = email_string.find('<') + 1
                end = email_string.find('>')
                return email_string[start:end]
            return email_string
    
    def get_email_count(self) -> int:
        """Get total email count from Gmail"""
        if not self.authenticate():
            return 0
        
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('messagesTotal', 0)
        except:
            return 0

# Routes
@router.post("/sync")
async def sync_emails(
    max_results: int = 100,
    incremental: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced email sync from Gmail"""
    
    # Validate parameters
    if max_results > 500:
        raise HTTPException(status_code=400, detail="max_results cannot exceed 500")
    
    gmail_service = GmailService(current_user)
    result = gmail_service.sync_emails(db, max_results, incremental)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": f"Sync completed: {result['new_emails']} new, {result['updated_emails']} updated",
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
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }
    }

@router.get("/stats")
async def get_gmail_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Gmail sync statistics"""
    
    gmail_service = GmailService(current_user)
    
    # Local email counts
    total_local = db.query(Email).filter(Email.user_id == current_user.id).count()
    spam_local = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.is_spam == True
    ).count()
    unprocessed_local = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.is_processed == False
    ).count()
    
    # Latest sync info
    latest_email = db.query(Email).filter(
        Email.user_id == current_user.id
    ).order_by(Email.received_date.desc()).first()
    
    # Gmail total (if available)
    gmail_total = gmail_service.get_email_count()
    
    return {
        "local_stats": {
            "total_emails": total_local,
            "spam_emails": spam_local,
            "unprocessed_emails": unprocessed_local,
            "latest_email_date": latest_email.received_date.isoformat() if latest_email and latest_email.received_date else None
        },
        "gmail_stats": {
            "total_emails": gmail_total,
            "sync_coverage": round((total_local / gmail_total * 100), 2) if gmail_total > 0 else 0
        },
        "sync_status": {
            "is_connected": gmail_service.authenticate(),
            "needs_sync": gmail_total > total_local if gmail_total > 0 else False
        }
    }

@router.post("/full-sync")
async def full_sync(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform a full email sync (non-incremental)"""
    
    gmail_service = GmailService(current_user)
    result = gmail_service.sync_emails(db, max_results=500, incremental=False)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": f"Full sync completed: {result['new_emails']} new emails",
        **result
    }

# Export router
gmail_router = router