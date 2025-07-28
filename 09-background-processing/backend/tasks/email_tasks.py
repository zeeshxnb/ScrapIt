"""
Email Processing Celery Tasks

Background tasks for email synchronization, classification, and management
"""
from celery import Celery, Task
from celery.utils.log import get_task_logger
from typing import List, Dict, Any, Optional
import time
from datetime import datetime, timezone

from ..services.gmail_client import GmailClient
from ..services.llm_client import LLMClient
from ..services.email_clustering import EmailClusterer
from ..models.email import Email
from ..models.user import User
from ..database import get_db_session

logger = get_task_logger(__name__)

# Celery app instance (configured elsewhere)
celery_app = Celery('scrapit')

class CallbackTask(Task):
    """Base task class with callback support"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called on task success"""
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure"""
        logger.error(f"Task {task_id} failed: {exc}")
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update task progress"""
        self.update_state(
            state='PROGRESS',
            meta={
                'current': current,
                'total': total,
                'message': message,
                'percentage': int((current / total) * 100) if total > 0 else 0
            }
        )

@celery_app.task(base=CallbackTask, bind=True)
def sync_user_emails(self, user_id: str, full_sync: bool = False) -> Dict[str, Any]:
    """
    Synchronize emails from Gmail for a user
    
    Args:
        user_id: User identifier
        full_sync: Whether to perform full sync or incremental
        
    Returns:
        Dictionary with sync results
    """
    # TODO: Implement email synchronization
    # Get user from database
    # Initialize Gmail client
    # Determine sync strategy (full vs incremental)
    # Fetch emails from Gmail
    # Store emails in database
    # Update progress throughout
    # Return sync summary
    
    logger.info(f"Starting email sync for user {user_id}, full_sync={full_sync}")
    
    try:
        with get_db_session() as db:
            # Get user and credentials
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Initialize Gmail client
            gmail_client = GmailClient(
                access_token=user.get_decrypted_access_token(),
                refresh_token=user.get_decrypted_refresh_token(),
                user_id=user_id
            )
            
            # Authenticate
            if not gmail_client.authenticate():
                raise Exception("Gmail authentication failed")
            
            # Determine sync parameters
            query = None
            if not full_sync and user.last_sync:
                # Incremental sync - only new emails
                query = f"after:{user.last_sync.strftime('%Y/%m/%d')}"
            
            # Get email list
            self.update_progress(0, 100, "Fetching email list...")
            messages = gmail_client.list_messages(query=query, max_results=1000)
            
            total_messages = len(messages.get('messages', []))
            processed = 0
            
            # Process emails in batches
            batch_size = 50
            for i in range(0, total_messages, batch_size):
                batch = messages['messages'][i:i + batch_size]
                message_ids = [msg['id'] for msg in batch]
                
                # Fetch email details
                email_details = gmail_client.get_messages_batch(message_ids)
                
                # Store emails
                for email_data in email_details:
                    _store_email(db, user_id, email_data)
                    processed += 1
                    
                    # Update progress
                    self.update_progress(
                        processed, 
                        total_messages, 
                        f"Processed {processed}/{total_messages} emails"
                    )
            
            # Update user's last sync time
            user.update_last_sync()
            db.commit()
            
            result = {
                'user_id': user_id,
                'total_processed': processed,
                'full_sync': full_sync,
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Email sync completed for user {user_id}: {processed} emails")
            return result
            
    except Exception as e:
        logger.error(f"Email sync failed for user {user_id}: {str(e)}")
        raise

@celery_app.task(base=CallbackTask, bind=True)
def classify_email_batch(self, email_ids: List[str], user_id: str) -> Dict[str, Any]:
    """
    Classify a batch of emails using AI
    
    Args:
        email_ids: List of email IDs to classify
        user_id: User identifier
        
    Returns:
        Classification results
    """
    # TODO: Implement batch classification
    # Get emails from database
    # Initialize LLM client
    # Classify emails in batches
    # Update email records with results
    # Update progress throughout
    # Return classification summary
    
    logger.info(f"Starting classification for {len(email_ids)} emails")
    
    try:
        with get_db_session() as db:
            # Get emails
            emails = db.query(Email).filter(
                Email.id.in_(email_ids),
                Email.user_id == user_id
            ).all()
            
            if not emails:
                return {'error': 'No emails found for classification'}
            
            # Initialize LLM client
            llm_client = LLMClient(
                provider="openai",  # TODO: Get from config
                api_key="",  # TODO: Get from config
                model="gpt-4"
            )
            
            classified = 0
            total = len(emails)
            
            # Process emails in smaller batches for LLM
            llm_batch_size = 10
            for i in range(0, total, llm_batch_size):
                batch = emails[i:i + llm_batch_size]
                
                # Prepare email data for classification
                email_data = []
                for email in batch:
                    email_data.append({
                        'subject': email.subject or '',
                        'content': email.get_text_content() or '',
                        'sender': email.sender
                    })
                
                # Classify batch
                results = await llm_client.classify_emails_batch(email_data)
                
                # Update email records
                for email, result in zip(batch, results):
                    email.update_classification(
                        category=result.category,
                        confidence=result.confidence,
                        is_spam=(result.category == 'Spam')
                    )
                    classified += 1
                    
                    # Update progress
                    self.update_progress(
                        classified,
                        total,
                        f"Classified {classified}/{total} emails"
                    )
                
                db.commit()
            
            result = {
                'user_id': user_id,
                'total_classified': classified,
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Classification completed: {classified} emails")
            return result
            
    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        raise

@celery_app.task(base=CallbackTask, bind=True)
def cluster_user_emails(self, user_id: str, recalculate: bool = False) -> Dict[str, Any]:
    """
    Cluster user's emails for organization
    
    Args:
        user_id: User identifier
        recalculate: Whether to recalculate existing clusters
        
    Returns:
        Clustering results
    """
    # TODO: Implement email clustering
    # Get user's emails
    # Initialize clustering service
    # Perform clustering analysis
    # Update email cluster assignments
    # Return clustering summary
    
    logger.info(f"Starting email clustering for user {user_id}")
    
    try:
        with get_db_session() as db:
            # Get emails for clustering
            query = db.query(Email).filter(Email.user_id == user_id)
            
            if not recalculate:
                # Only cluster unprocessed emails
                query = query.filter(Email.cluster_id.is_(None))
            
            emails = query.all()
            
            if len(emails) < 10:  # Need minimum emails for clustering
                return {'message': 'Not enough emails for clustering'}
            
            # Initialize clusterer
            clusterer = EmailClusterer()
            
            # Prepare email data
            self.update_progress(0, 100, "Preparing emails for clustering...")
            email_data = []
            for email in emails:
                email_data.append({
                    'id': email.id,
                    'subject': email.subject or '',
                    'content': email.get_text_content() or '',
                    'sender': email.sender
                })
            
            # Perform clustering
            self.update_progress(25, 100, "Performing clustering analysis...")
            clustering_results = clusterer.cluster_emails(email_data)
            
            # Update email records
            self.update_progress(75, 100, "Updating email cluster assignments...")
            cluster_assignments = clustering_results['assignments']
            
            for i, email in enumerate(emails):
                email.cluster_id = cluster_assignments[i]
            
            db.commit()
            
            result = {
                'user_id': user_id,
                'total_clustered': len(emails),
                'num_clusters': clustering_results['n_clusters'],
                'cluster_labels': clustering_results.get('labels', []),
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Clustering completed: {len(emails)} emails in {result['num_clusters']} clusters")
            return result
            
    except Exception as e:
        logger.error(f"Clustering failed: {str(e)}")
        raise

@celery_app.task(base=CallbackTask, bind=True)
def cleanup_old_emails(self, user_id: str, days_old: int = 90) -> Dict[str, Any]:
    """
    Clean up old processed emails to save storage
    
    Args:
        user_id: User identifier
        days_old: Age threshold for cleanup
        
    Returns:
        Cleanup results
    """
    # TODO: Implement email cleanup
    # Find old emails based on criteria
    # Archive or delete based on importance
    # Update statistics
    # Return cleanup summary
    
    logger.info(f"Starting email cleanup for user {user_id}, older than {days_old} days")
    
    try:
        with get_db_session() as db:
            # Find old emails
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            old_emails = db.query(Email).filter(
                Email.user_id == user_id,
                Email.received_date < cutoff_date,
                Email.category.in_(['Promotional', 'Newsletter', 'Spam'])  # Only cleanup non-important
            ).all()
            
            cleaned_count = 0
            total = len(old_emails)
            
            for i, email in enumerate(old_emails):
                # Remove email content but keep metadata
                email.content = None
                email.snippet = f"[Archived - {email.category}]"
                cleaned_count += 1
                
                # Update progress
                self.update_progress(
                    i + 1,
                    total,
                    f"Cleaned {cleaned_count}/{total} emails"
                )
            
            db.commit()
            
            result = {
                'user_id': user_id,
                'emails_cleaned': cleaned_count,
                'cutoff_date': cutoff_date.isoformat(),
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Cleanup completed: {cleaned_count} emails cleaned")
            return result
            
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise

def _store_email(db, user_id: str, email_data: Dict[str, Any]) -> Email:
    """
    Store email data in database
    
    Args:
        db: Database session
        user_id: User identifier
        email_data: Gmail email data
        
    Returns:
        Created Email object
    """
    # TODO: Implement email storage
    # Parse Gmail email data
    # Create Email object
    # Handle duplicates
    # Return created email
    pass