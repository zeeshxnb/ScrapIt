"""
Email Synchronization Service

Service for synchronizing emails between Gmail and local database
"""
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import logging
from typing import List, Dict, Any, Optional, Tuple
from .gmail_client import GmailClient
from ..models.email import Email

logger = logging.getLogger(__name__)

class EmailSyncService:
    """Service for synchronizing emails between Gmail and database"""
    
    # Default sync parameters
    DEFAULT_BATCH_SIZE = 100
    DEFAULT_SYNC_DAYS = 30
    
    def __init__(self, db: Session, user_id: str, access_token: str, refresh_token: str):
        """
        Initialize sync service
        
        Args:
            db: Database session
            user_id: User ID for database operations
            access_token: Gmail API access token
            refresh_token: Gmail API refresh token
        """
        self.db = db
        self.user_id = user_id
        self.gmail_client = GmailClient(access_token, refresh_token, user_id)
        
    def sync_emails(self, days_back: int = DEFAULT_SYNC_DAYS, 
                   batch_size: int = DEFAULT_BATCH_SIZE,
                   progress_callback=None) -> Dict[str, Any]:
        """
        Synchronize emails from Gmail to database
        
        Args:
            days_back: Number of days to sync back
            batch_size: Number of emails to process in each batch
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary with sync statistics
        """
        logger.info(f"Starting email sync for user {self.user_id}")
        
        # Initialize Gmail client
        if not self.gmail_client.authenticate():
            logger.error("Failed to authenticate Gmail client")
            return {"success": False, "error": "Authentication failed"}
        
        # Build date query for Gmail
        after_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y/%m/%d")
        query = f"after:{after_date}"
        
        # Get total count estimate
        initial_result = self.gmail_client.list_messages(query=query, max_results=1)
        total_estimate = initial_result.get('resultSizeEstimate', 0)
        
        logger.info(f"Found approximately {total_estimate} emails to sync")
        
        # Initialize counters
        stats = {
            "total": total_estimate,
            "processed": 0,
            "new": 0,
            "updated": 0,
            "failed": 0,
            "batches": 0
        }
        
        # Process emails in batches
        page_token = None
        continue_sync = True
        
        while continue_sync:
            try:
                # Get batch of message IDs
                result = self.gmail_client.list_messages(
                    query=query, 
                    max_results=batch_size,
                    page_token=page_token
                )
                
                messages = result.get('messages', [])
                if not messages:
                    break
                    
                # Get message details in batch
                message_ids = [msg['id'] for msg in messages]
                message_details = self.gmail_client.get_messages_batch(message_ids)
                
                # Process each message
                batch_stats = self._process_message_batch(message_details)
                
                # Update stats
                stats["processed"] += len(message_details)
                stats["new"] += batch_stats["new"]
                stats["updated"] += batch_stats["updated"]
                stats["failed"] += batch_stats["failed"]
                stats["batches"] += 1
                
                # Report progress if callback provided
                if progress_callback:
                    progress = min(100, int((stats["processed"] / total_estimate) * 100)) if total_estimate > 0 else 0
                    progress_callback(progress, stats)
                
                # Check if there are more messages
                page_token = result.get('nextPageToken')
                if not page_token:
                    continue_sync = False
                    
                logger.info(f"Processed batch {stats['batches']}: {len(message_details)} emails")
                
            except Exception as e:
                logger.error(f"Error during sync: {str(e)}")
                stats["error"] = str(e)
                continue_sync = False
        
        logger.info(f"Email sync completed. Stats: {stats}")
        return {
            "success": True,
            "stats": stats
        }
    
    def sync_single_email(self, gmail_id: str) -> Optional[Email]:
        """
        Sync a single email by Gmail ID
        
        Args:
            gmail_id: Gmail message ID
            
        Returns:
            Email object if successful, None otherwise
        """
        try:
            # Initialize Gmail client if needed
            if not self.gmail_client.authenticate():
                logger.error("Failed to authenticate Gmail client")
                return None
            
            # Get message details
            message = self.gmail_client.get_message(gmail_id)
            if not message:
                logger.error(f"Failed to get message {gmail_id}")
                return None
                
            # Process message
            email = self._process_message(message)
            return email
            
        except Exception as e:
            logger.error(f"Error syncing single email {gmail_id}: {str(e)}")
            return None
    
    def _process_message_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Process a batch of messages
        
        Args:
            messages: List of message data from Gmail API
            
        Returns:
            Dictionary with batch processing statistics
        """
        stats = {"new": 0, "updated": 0, "failed": 0}
        
        for message in messages:
            try:
                result = self._process_message(message)
                if result == "new":
                    stats["new"] += 1
                elif result == "updated":
                    stats["updated"] += 1
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                stats["failed"] += 1
                
        # Commit all changes for the batch
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing batch: {str(e)}")
            self.db.rollback()
            stats["failed"] = len(messages)
            stats["new"] = 0
            stats["updated"] = 0
            
        return stats
    
    def _process_message(self, message: Dict[str, Any]) -> str:
        """
        Process a single message and store in database
        
        Args:
            message: Message data from Gmail API
            
        Returns:
            "new" if created, "updated" if updated
        """
        gmail_id = message.get('id')
        
        # Check if email already exists
        existing_email = self.db.query(Email).filter(
            Email.user_id == self.user_id,
            Email.gmail_id == gmail_id
        ).first()
        
        if existing_email:
            # Update existing email
            self._update_email_from_message(existing_email, message)
            result = "updated"
        else:
            # Create new email
            existing_email = self._create_email_from_message(message)
            self.db.add(existing_email)
            result = "new"
            
        return result
    
    def _create_email_from_message(self, message: Dict[str, Any]) -> Email:
        """
        Create Email object from Gmail message
        
        Args:
            message: Message data from Gmail API
            
        Returns:
            Email object
        """
        # Extract basic fields
        gmail_id = message.get('id')
        thread_id = message.get('thread_id')
        subject = message.get('subject', '')
        sender = message.get('from', '')
        recipient = message.get('to', '')
        snippet = message.get('snippet', '')
        
        # Parse date
        date_str = message.get('date')
        received_date = datetime.now(timezone.utc)
        if date_str:
            try:
                import email.utils
                received_date = email.utils.parsedate_to_datetime(date_str)
            except Exception as e:
                logger.warning(f"Error parsing date {date_str}: {str(e)}")
        
        # Extract content
        content = ""
        if 'body' in message and 'plain' in message['body']:
            content = message['body']['plain']
        elif 'body' in message and 'html' in message['body']:
            content = message['body']['html']
        
        # Extract labels
        labels = message.get('label_ids', [])
        
        # Create email object
        email = Email(
            user_id=self.user_id,
            gmail_id=gmail_id,
            thread_id=thread_id,
            subject=subject,
            sender=sender,
            recipient=recipient,
            content=content,
            snippet=snippet,
            received_date=received_date,
            labels=labels
        )
        
        return email
    
    def _update_email_from_message(self, email: Email, message: Dict[str, Any]) -> None:
        """
        Update existing Email object from Gmail message
        
        Args:
            email: Existing Email object
            message: Message data from Gmail API
        """
        # Update labels
        email.labels = message.get('label_ids', email.labels)
        
        # Only update content if it was empty before
        if not email.content and 'body' in message:
            if 'plain' in message['body']:
                email.content = message['body']['plain']
            elif 'html' in message['body']:
                email.content = message['body']['html']
                
        # Update other fields if needed
        if not email.subject:
            email.subject = message.get('subject', '')
        
        if not email.snippet:
            email.snippet = message.get('snippet', '')
            
        # Update processed_at timestamp
        email.processed_at = datetime.now(timezone.utc)