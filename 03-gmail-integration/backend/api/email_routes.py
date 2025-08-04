"""
Email API Routes

FastAPI routes for email management
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timezone, timedelta

from ..services.email_sync import EmailSyncService
from ..services.gmail_client import GmailClient
from ..models.email import Email
from ..database import get_db
from ...auth.jwt import get_current_user

# Create router
router = APIRouter(prefix="/api/emails", tags=["emails"])

# Setup logger
logger = logging.getLogger(__name__)

# Background sync status
sync_status = {}

@router.get("/", response_model=Dict[str, Any])
async def get_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_spam: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user emails with filtering and pagination
    
    Args:
        skip: Number of emails to skip
        limit: Maximum number of emails to return
        category: Filter by category
        is_spam: Filter by spam status
        search: Search in subject and content
        start_date: Filter by start date
        end_date: Filter by end date
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dictionary with emails and count
    """
    try:
        # Build query
        query = db.query(Email).filter(Email.user_id == current_user["id"])
        
        # Apply filters
        if category:
            query = query.filter(Email.category == category)
            
        if is_spam is not None:
            query = query.filter(Email.is_spam == is_spam)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Email.subject.ilike(search_term)) | 
                (Email.content.ilike(search_term)) |
                (Email.sender.ilike(search_term))
            )
            
        if start_date:
            query = query.filter(Email.received_date >= start_date)
            
        if end_date:
            query = query.filter(Email.received_date <= end_date)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and order by received date (newest first)
        emails = query.order_by(Email.received_date.desc()).offset(skip).limit(limit).all()
        
        # Convert to dict
        email_list = [email.to_dict() for email in emails]
        
        return {
            "emails": email_list,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting emails: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving emails: {str(e)}")

@router.get("/{email_id}", response_model=Dict[str, Any])
async def get_email(
    email_id: str = Path(..., title="The ID of the email to get"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a single email by ID
    
    Args:
        email_id: Email ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Email object
    """
    try:
        # Get email from database
        email = db.query(Email).filter(
            Email.id == email_id,
            Email.user_id == current_user["id"]
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
            
        return email.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting email {email_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving email: {str(e)}")

@router.post("/sync", response_model=Dict[str, Any])
async def sync_emails(
    background_tasks: BackgroundTasks,
    days_back: int = Query(30, ge=1, le=365),
    batch_size: int = Query(100, ge=10, le=500),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start email synchronization in background
    
    Args:
        background_tasks: FastAPI background tasks
        days_back: Number of days to sync back
        batch_size: Number of emails to process in each batch
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dictionary with sync status
    """
    try:
        # Check if sync is already running for this user
        if current_user["id"] in sync_status and sync_status[current_user["id"]]["running"]:
            return {
                "success": True,
                "message": "Sync already in progress",
                "status": sync_status[current_user["id"]]
            }
        
        # Initialize sync status
        sync_status[current_user["id"]] = {
            "running": True,
            "progress": 0,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "processed": 0,
                "new": 0,
                "updated": 0,
                "failed": 0
            }
        }
        
        # Start background sync
        background_tasks.add_task(
            run_email_sync,
            db,
            current_user["id"],
            current_user["access_token"],
            current_user["refresh_token"],
            days_back,
            batch_size
        )
        
        return {
            "success": True,
            "message": "Email sync started",
            "status": sync_status[current_user["id"]]
        }
        
    except Exception as e:
        logger.error(f"Error starting email sync: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting email sync: {str(e)}")

@router.get("/sync/status", response_model=Dict[str, Any])
async def get_sync_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get email sync status
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dictionary with sync status
    """
    # Return status if exists, otherwise return default
    if current_user["id"] in sync_status:
        return {
            "success": True,
            "status": sync_status[current_user["id"]]
        }
    else:
        return {
            "success": True,
            "status": {
                "running": False,
                "progress": 0,
                "stats": {}
            }
        }

@router.post("/{email_id}/update-category", response_model=Dict[str, Any])
async def update_email_category(
    email_id: str = Path(..., title="The ID of the email to update"),
    category: str = Query(..., title="New category"),
    confidence: float = Query(1.0, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update email category
    
    Args:
        email_id: Email ID
        category: New category
        confidence: Classification confidence
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated email object
    """
    try:
        # Get email from database
        email = db.query(Email).filter(
            Email.id == email_id,
            Email.user_id == current_user["id"]
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
            
        # Update category
        email.update_classification(category, confidence)
        
        # Commit changes
        db.commit()
            
        return {
            "success": True,
            "message": f"Email category updated to {category}",
            "email": email.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating email category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating email category: {str(e)}")

@router.post("/{email_id}/mark-spam", response_model=Dict[str, Any])
async def mark_email_as_spam(
    email_id: str = Path(..., title="The ID of the email to mark as spam"),
    is_spam: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Mark email as spam or not spam
    
    Args:
        email_id: Email ID
        is_spam: Spam status
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated email object
    """
    try:
        # Get email from database
        email = db.query(Email).filter(
            Email.id == email_id,
            Email.user_id == current_user["id"]
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
            
        # Update spam status
        if email.category:
            email.update_classification(email.category, email.confidence_score or 1.0, is_spam)
        else:
            email.is_spam = is_spam
            email.processed_at = datetime.now(timezone.utc)
        
        # Commit changes
        db.commit()
            
        return {
            "success": True,
            "message": f"Email marked as {'spam' if is_spam else 'not spam'}",
            "email": email.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking email as spam: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error marking email as spam: {str(e)}")

# Background task for email synchronization
def run_email_sync(
    db: Session,
    user_id: str,
    access_token: str,
    refresh_token: str,
    days_back: int,
    batch_size: int
):
    """
    Run email synchronization in background
    
    Args:
        db: Database session
        user_id: User ID
        access_token: Gmail API access token
        refresh_token: Gmail API refresh token
        days_back: Number of days to sync back
        batch_size: Number of emails to process in each batch
    """
    try:
        # Create sync service
        sync_service = EmailSyncService(db, user_id, access_token, refresh_token)
        
        # Define progress callback
        def update_progress(progress: int, stats: Dict[str, Any]):
            if user_id in sync_status:
                sync_status[user_id]["progress"] = progress
                sync_status[user_id]["stats"] = stats
        
        # Run sync
        result = sync_service.sync_emails(
            days_back=days_back,
            batch_size=batch_size,
            progress_callback=update_progress
        )
        
        # Update status
        if user_id in sync_status:
            sync_status[user_id]["running"] = False
            sync_status[user_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
            sync_status[user_id]["success"] = result.get("success", False)
            
            if "error" in result:
                sync_status[user_id]["error"] = result["error"]
        
    except Exception as e:
        logger.error(f"Error in background sync: {str(e)}")
        
        # Update status with error
        if user_id in sync_status:
            sync_status[user_id]["running"] = False
            sync_status[user_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
            sync_status[user_id]["success"] = False
            sync_status[user_id]["error"] = str(e)