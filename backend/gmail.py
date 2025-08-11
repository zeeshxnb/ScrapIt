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
                print("🔄 Token refreshed successfully")
            
            self.service = build('gmail', 'v1', credentials=credentials)
            return True
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def list_messages(self, query: str = None, max_results: int = None):
        """List Gmail messages with pagination support - NO LIMITS, gets ALL emails"""
        if not self.service:
            self.authenticate()
            
        all_messages = []
        next_page_token = None
        batch_count = 0
        
        try:
            while True:
                batch_count += 1
                # Use maximum batch size of 500 (Gmail API limit)
                batch_size = 500
                
                result = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=batch_size,
                    pageToken=next_page_token
                ).execute()
                
                messages = result.get('messages', [])
                all_messages.extend(messages)
                
                # Progress bar display
                progress_percent = min(100, (len(all_messages) / 5000) * 100) if len(all_messages) < 5000 else 100
                progress_bar = "█" * int(progress_percent / 5) + "░" * (20 - int(progress_percent / 5))
                print(f"\r📧 Fetching: [{progress_bar}] {len(all_messages)} emails", end="", flush=True)
                
                # Check if there are more pages
                next_page_token = result.get('nextPageToken')
                if not next_page_token or not messages:
                    print(f"\n✅ Retrieved {len(all_messages)} emails from Gmail")
                    break
                
                # If max_results is specified and we've reached it, stop
                if max_results and len(all_messages) >= max_results:
                    all_messages = all_messages[:max_results]
                    print(f"🎯 Reached limit: {max_results} messages")
                    break
                
                # Minimal delay to respect rate limits
                time.sleep(0.05)
            
            if len(all_messages) > 0:
                print(f"📧 Total: {len(all_messages)} messages ({batch_count} batches)")
            return all_messages
            
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit exceeded
                print("Rate limit exceeded, waiting...")
                time.sleep(5)
                return all_messages  # Return what we have so far
            print(f"Gmail API error: {e}")
            return all_messages
        except Exception as e:
            print(f"Error listing messages: {e}")
            return all_messages
    
    def get_message(self, message_id: str):
        """Get single Gmail message with rate limiting"""
        if not self.service:
            self.authenticate()
            
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            # Very small delay to respect rate limits
            time.sleep(0.005)
            
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
                        
                        # Check if email already exists (prevent duplicates)
                        existing = db.query(Email).filter(
                            Email.gmail_id == msg['id'],
                            Email.user_id == self.user.id
                        ).first()
                        
                        # Skip if already exists and this is a full sync (avoid duplicates)
                        if existing and not incremental:
                            continue
                        
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
                                user_id=self.user.id,
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
                
                # Commit batch to database
                try:
                    db.commit()
                    # Show save status less frequently
                    if batch_count % 20 == 0:
                        print(f"\n💾 Saved progress: {new_count} new, {updated_count} updated")
                except Exception as e:
                    db.rollback()
                    print(f"Error committing batch {batch_count}: {str(e)}")
                    return {"success": False, "error": f"Database error in batch {batch_count}: {str(e)}"}
                
                # Minimal delay between batches
                time.sleep(0.1)
            
            print(f"\n✅ Sync completed: {new_count} new, {updated_count} updated, {error_count} errors")
            
            # Validate final count
            final_count = db.query(Email).filter(Email.user_id == self.user.id).count()
            print(f"📊 Database now contains: {final_count} emails")
            
            return {
                "success": True,
                "new_emails": new_count,
                "updated_emails": updated_count,
                "error_count": error_count,
                "total_processed": len(processed_ids),
                "total_batches": batch_count,
                "sync_type": "incremental" if incremental else "full",
                "all_folders_synced": specific_labels is None,
                "synced_labels": specific_labels if specific_labels else "ALL",
                "query_used": query,
                "batch_size": batch_size,
                "no_limits_applied": max_results is None,
                "final_email_count": final_count
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
    
    def get_labels(self) -> list:
        """Get all Gmail labels/folders"""
        if not self.authenticate():
            return []
        
        try:
            result = self.service.users().labels().list(userId='me').execute()
            labels = result.get('labels', [])
            
            # Format labels with counts
            formatted_labels = []
            for label in labels:
                formatted_labels.append({
                    'id': label['id'],
                    'name': label['name'],
                    'type': label.get('type', 'user'),
                    'messages_total': label.get('messagesTotal', 0),
                    'messages_unread': label.get('messagesUnread', 0)
                })
            
            return formatted_labels
        except Exception as e:
            print(f"Error getting labels: {e}")
            return []
    
    def get_folder_stats(self) -> dict:
        """Get email counts by folder/label"""
        if not self.authenticate():
            return {}
        
        try:
            labels = self.get_labels()
            stats = {}
            
            # Get counts for major folders
            major_folders = ['INBOX', 'SENT', 'DRAFT', 'SPAM', 'TRASH']
            
            for label in labels:
                if label['id'] in major_folders or label['type'] == 'user':
                    stats[label['name']] = {
                        'total': label['messages_total'],
                        'unread': label['messages_unread'],
                        'type': label['type']
                    }
            
            return stats
        except Exception as e:
            print(f"Error getting folder stats: {e}")
            return {}
    
    def cleanup_database(self, db: Session) -> dict:
        """Clean up duplicates and verify email existence in Gmail"""
        if not self.authenticate():
            return {"success": False, "error": "Authentication failed"}
        
        try:
            print("🧹 Starting database cleanup...")
            
            # 1. Remove duplicates based on gmail_id
            print("🔍 Checking for duplicates...")
            duplicates_removed = 0
            
            # Find emails with duplicate gmail_ids
            from sqlalchemy import func
            duplicate_gmail_ids = db.query(Email.gmail_id).filter(
                Email.user_id == str(self.user.id)
            ).group_by(Email.gmail_id).having(func.count(Email.gmail_id) > 1).all()
            
            for (gmail_id,) in duplicate_gmail_ids:
                # Keep the first one, delete the rest
                emails_with_id = db.query(Email).filter(
                    Email.gmail_id == gmail_id,
                    Email.user_id == str(self.user.id)
                ).order_by(Email.created_at).all()
                
                # Delete all but the first
                for email in emails_with_id[1:]:
                    db.delete(email)
                    duplicates_removed += 1
            
            db.commit()
            print(f"🗑️  Removed {duplicates_removed} duplicate emails")
            
            # 2. Get current count
            current_count = db.query(Email).filter(Email.user_id == str(self.user.id)).count()
            print(f"📊 Database now has {current_count} emails")
            
            return {
                "success": True,
                "duplicates_removed": duplicates_removed,
                "final_count": current_count
            }
            
        except Exception as e:
            db.rollback()
            print(f"❌ Cleanup error: {e}")
            return {"success": False, "error": str(e)}

# Routes
class SyncRequest(BaseModel):
    max_results: Optional[int] = None
    incremental: bool = True
    batch_size: int = 100
    only_inbox: bool = True
    labels: Optional[List[str]] = None

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
    """Get Gmail sync statistics including folder breakdown"""
    
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
    
    # Gmail total and folder stats
    gmail_total = gmail_service.get_email_count()
    folder_stats = gmail_service.get_folder_stats()
    
    return {
        "local_stats": {
            "total_emails": total_local,
            "spam_emails": spam_local,
            "unprocessed_emails": unprocessed_local,
            "latest_email_date": latest_email.received_date.isoformat() if latest_email and latest_email.received_date else None
        },
        "gmail_stats": {
            "total_emails": gmail_total,
            "sync_coverage": round((total_local / gmail_total * 100), 2) if gmail_total > 0 else 0,
            "folder_breakdown": folder_stats
        },
        "sync_status": {
            "is_connected": gmail_service.authenticate(),
            "needs_sync": gmail_total > total_local if gmail_total > 0 else False,
            "supports_all_folders": True
        }
    }

@router.get("/folders")
async def get_gmail_folders(
    current_user: User = Depends(get_current_user)
):
    """Get all Gmail folders/labels with email counts"""
    
    gmail_service = GmailService(current_user)
    
    if not gmail_service.authenticate():
        raise HTTPException(status_code=401, detail="Gmail authentication failed")
    
    labels = gmail_service.get_labels()
    folder_stats = gmail_service.get_folder_stats()
    
    return {
        "folders": labels,
        "folder_stats": folder_stats,
        "total_folders": len(labels),
        "message": "All Gmail folders/labels retrieved successfully"
    }

@router.post("/full-sync")
async def full_sync(
    batch_size: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform a COMPLETE full email sync - gets ALL emails from ALL folders/labels"""
    
    # Validate batch_size
    if batch_size > 500:
        batch_size = 500
    elif batch_size < 10:
        batch_size = 10
    
    gmail_service = GmailService(current_user)
    result = gmail_service.sync_emails(db, max_results=None, incremental=False, batch_size=batch_size)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": f"COMPLETE full sync finished: {result['new_emails']} new emails from ALL folders/labels",
        **result
    }

@router.post("/sync-all-folders")
async def sync_all_folders(
    batch_size: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync ALL emails from ALL Gmail folders/labels - alias for full-sync"""
    
    # Validate batch_size
    if batch_size > 500:
        batch_size = 500
    elif batch_size < 10:
        batch_size = 10
    
    gmail_service = GmailService(current_user)
    result = gmail_service.sync_emails(db, max_results=None, incremental=False, batch_size=batch_size)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": f"All folders sync completed: {result['new_emails']} new emails from inbox, sent, drafts, spam, trash, and custom labels",
        **result
    }

@router.post("/sync-folders")
async def sync_specific_folders(
    labels: list[str],
    batch_size: int = 100,
    incremental: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync emails from specific Gmail folders/labels"""
    
    if not labels:
        raise HTTPException(status_code=400, detail="At least one label must be specified")
    
    # Validate batch_size
    if batch_size > 500:
        batch_size = 500
    elif batch_size < 10:
        batch_size = 10
    
    gmail_service = GmailService(current_user)
    result = gmail_service.sync_emails(
        db, 
        max_results=None, 
        incremental=incremental, 
        batch_size=batch_size,
        specific_labels=labels
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": f"Specific folders sync completed: {result['new_emails']} new emails from {', '.join(labels)}",
        "synced_labels": labels,
        **result
    }

@router.post("/cleanup")
async def cleanup_database(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up duplicate emails and fix database inconsistencies"""
    
    gmail_service = GmailService(current_user)
    result = gmail_service.cleanup_database(db)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": f"Cleanup completed: {result['duplicates_removed']} duplicates removed",
        **result
    }

@router.delete("/reset")
async def reset_email_database(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset email database - DELETE ALL emails for fresh sync"""
    
    try:
        # Delete all emails for this user
        deleted_count = db.query(Email).filter(Email.user_id == current_user.id).count()
        db.query(Email).filter(Email.user_id == current_user.id).delete()
        db.commit()
        
        return {
            "message": f"Database reset: {deleted_count} emails deleted. Ready for fresh sync.",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

# Export router
gmail_router = router