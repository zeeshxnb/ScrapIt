"""
Gmail Integration Module - Consolidated
Handles Gmail API integration and email synchronization
"""
import os
import email.utils
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

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
        """List Gmail messages"""
        if not self.service:
            self.authenticate()
            
        try:
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            return result.get('messages', [])
        except Exception:
            return []
    
    def get_message(self, message_id: str):
        """Get single Gmail message"""
        if not self.service:
            self.authenticate()
            
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
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
        except Exception:
            return None
    
    def sync_recent_emails(self, db: Session, days_back: int = 7) -> dict:
        """Sync recent emails"""
        if not self.authenticate():
            return {"success": False, "error": "Authentication failed"}
        
        try:
            # Get recent messages
            after_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
            query = f"after:{after_date}"
            
            messages = self.list_messages(query=query, max_results=50)
            new_count = 0
            
            for msg in messages:
                # Check if exists
                existing = db.query(Email).filter(Email.gmail_id == msg['id']).first()
                if existing:
                    continue
                
                # Get full message
                email_data = self.get_message(msg['id'])
                if email_data:
                    # Parse date
                    received_date = datetime.now()
                    if email_data['date']:
                        try:
                            received_date = email.utils.parsedate_to_datetime(email_data['date'])
                        except:
                            pass
                    
                    # Create email record
                    email_record = Email(
                        user_id=str(self.user.id),
                        gmail_id=email_data['id'],
                        subject=email_data['subject'],
                        sender=email_data['from'],
                        recipient=email_data['to'],
                        snippet=email_data['snippet'],
                        labels=email_data['labels'],
                        received_date=received_date
                    )
                    
                    db.add(email_record)
                    new_count += 1
            
            db.commit()
            return {"success": True, "new_emails": new_count}
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}

# Routes
@router.post("/sync")
async def sync_emails(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync emails from Gmail"""
    gmail_service = GmailService(current_user)
    result = gmail_service.sync_recent_emails(db)
    return result

@router.get("/emails")
async def get_emails(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's emails"""
    emails = db.query(Email).filter(
        Email.user_id == current_user.id
    ).limit(limit).all()
    
    return {
        "emails": [
            {
                "id": str(email.id),
                "subject": email.subject,
                "sender": email.sender,
                "snippet": email.snippet,
                "received_date": email.received_date.isoformat() if email.received_date else None
            }
            for email in emails
        ]
    }

# Export router
gmail_router = router