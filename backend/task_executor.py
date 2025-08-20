"""
Gmail Task Execution System
Handles complex multi-step email management tasks via Gmail API
"""
import os
import time
import uuid
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
from models import User, Email, Task
from auth import get_current_user
from gmail import GmailService

router = APIRouter()

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    EMAIL_CLEANUP = "email_cleanup"
    EMAIL_ORGANIZATION = "email_organization"
    EMAIL_SEARCH = "email_search"
    EMAIL_COMPOSE = "email_compose"
    EMAIL_SEND = "email_send"
    CUSTOM = "custom"

class TaskAction(str, Enum):
    DELETE = "delete"
    ARCHIVE = "archive"
    LABEL = "label"
    MOVE = "move"
    SEARCH = "search"
    COMPOSE = "compose"
    SEND = "send"
    MARK_READ = "mark_read"
    MARK_UNREAD = "mark_unread"
    STAR = "star"
    UNSTAR = "unstar"

class TaskStep(BaseModel):
    action: TaskAction
    params: Dict[str, Any]
    completed: bool = False
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TaskRequest(BaseModel):
    task_type: TaskType
    description: str
    steps: List[TaskStep]
    priority: int = 1  # 1 (highest) to 5 (lowest)

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    description: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

def create_task(db: Session, user_id: str, task_request: TaskRequest) -> Task:
    """Create a new task in the database"""
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    task = Task(
        id=task_id,
        user_id=user_id,
        type=task_request.task_type,
        description=task_request.description,
        status=TaskStatus.PENDING,
        steps=task_request.dict().get("steps"),
        priority=task_request.priority,
        created_at=now,
        updated_at=now
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task

async def execute_task(db: Session, task: Task, user: User) -> Dict[str, Any]:
    """Execute a task with multiple steps"""
    if task.status == TaskStatus.COMPLETED:
        return {"message": "Task already completed", "task_id": task.id}
    
    if task.status == TaskStatus.FAILED:
        return {"message": "Task previously failed", "task_id": task.id, "error": task.error}
    
    # Mark task as in progress
    task.status = TaskStatus.IN_PROGRESS
    task.updated_at = datetime.utcnow()
    db.commit()
    
    # Send initial notification
    try:
        from notification import notify_task_update
        await notify_task_update(task)
    except Exception as e:
        print(f"Failed to send initial notification: {str(e)}")
    
    # Initialize Gmail service
    gmail_service = GmailService(user)
    
    total_steps = len(task.steps)
    completed_steps = 0
    results = {}
    
    try:
        for i, step in enumerate(task.steps):
            if step.get("completed"):
                completed_steps += 1
                continue
                
            # Execute the step
            step_result = execute_step(step, gmail_service, db, user)
            
            # Update step status
            step["completed"] = True
            step["result"] = step_result
            
            # Add to results
            results[f"step_{i+1}"] = step_result
            
            # Update progress
            completed_steps += 1
            task.progress = int((completed_steps / total_steps) * 100)
            task.updated_at = datetime.utcnow()
            db.commit()
            
            # Send progress notification
            try:
                from notification import notify_task_update
                await notify_task_update(task)
            except Exception as e:
                print(f"Failed to send progress notification: {str(e)}")
            
        # Mark task as completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = results
        db.commit()
        
        # Send completion notification
        try:
            from notification import notify_task_completion
            await notify_task_completion(task)
        except Exception as e:
            print(f"Failed to send completion notification: {str(e)}")
        
        return {
            "message": "Task completed successfully",
            "task_id": task.id,
            "results": results
        }
        
    except Exception as e:
        # Mark task as failed
        task.status = TaskStatus.FAILED
        task.error = str(e)
        task.updated_at = datetime.utcnow()
        db.commit()
        
        # Send failure notification
        try:
            from notification import notify_task_update
            await notify_task_update(task)
        except Exception as notif_error:
            print(f"Failed to send failure notification: {str(notif_error)}")
        
        return {
            "message": "Task failed",
            "task_id": task.id,
            "error": str(e)
        }

def execute_step(step: Dict[str, Any], gmail_service: GmailService, db: Session, user: User) -> Dict[str, Any]:
    """Execute a single task step"""
    action = step.get("action")
    params = step.get("params", {})
    
    if action == TaskAction.DELETE:
        # Delete emails
        message_ids = params.get("message_ids", [])
        permanent = params.get("permanent", False)
        
        if permanent:
            success = gmail_service.batch_delete_messages(message_ids)
        else:
            success = gmail_service.batch_modify_messages(message_ids, add_label_ids=["TRASH"], remove_label_ids=["INBOX"])
            
        # Update local database
        for message_id in message_ids:
            email = db.query(Email).filter(
                Email.gmail_id == message_id,
                Email.user_id == user.id
            ).first()
            
            if email:
                if permanent:
                    db.delete(email)
                else:
                    email.is_deleted = True
                    if "TRASH" not in email.labels:
                        email.labels = list(set(email.labels + ["TRASH"]))
                    if "INBOX" in email.labels:
                        email.labels.remove("INBOX")
        
        db.commit()
        return {"success": success, "count": len(message_ids)}
        
    elif action == TaskAction.ARCHIVE:
        # Archive emails
        message_ids = params.get("message_ids", [])
        success = gmail_service.batch_modify_messages(message_ids, remove_label_ids=["INBOX"])
        
        # Update local database
        for message_id in message_ids:
            email = db.query(Email).filter(
                Email.gmail_id == message_id,
                Email.user_id == user.id
            ).first()
            
            if email:
                email.is_archived = True
                if "INBOX" in email.labels:
                    email.labels.remove("INBOX")
        
        db.commit()
        return {"success": success, "count": len(message_ids)}
        
    elif action == TaskAction.LABEL:
        # Apply labels to emails
        message_ids = params.get("message_ids", [])
        label_name = params.get("label_name")
        remove = params.get("remove", False)
        
        # Ensure label exists
        label_id = gmail_service.ensure_label(label_name)
        
        if remove:
            success = gmail_service.batch_modify_messages(message_ids, remove_label_ids=[label_id])
        else:
            success = gmail_service.batch_modify_messages(message_ids, add_label_ids=[label_id])
            
        # Update local database
        for message_id in message_ids:
            email = db.query(Email).filter(
                Email.gmail_id == message_id,
                Email.user_id == user.id
            ).first()
            
            if email:
                if remove and label_id in email.labels:
                    email.labels.remove(label_id)
                elif not remove and label_id not in email.labels:
                    email.labels.append(label_id)
        
        db.commit()
        return {"success": success, "count": len(message_ids), "label": label_name}
        
    elif action == TaskAction.SEARCH:
        # Search for emails
        query = params.get("query", "")
        max_results = params.get("max_results", 100)
        
        messages = gmail_service.search_messages(query, max_results=max_results)
        message_ids = [msg["id"] for msg in messages]
        
        return {"success": True, "count": len(message_ids), "message_ids": message_ids}
        
    elif action == TaskAction.MARK_READ:
        # Mark emails as read
        message_ids = params.get("message_ids", [])
        success = gmail_service.batch_modify_messages(message_ids, remove_label_ids=["UNREAD"])
        return {"success": success, "count": len(message_ids)}
        
    elif action == TaskAction.MARK_UNREAD:
        # Mark emails as unread
        message_ids = params.get("message_ids", [])
        success = gmail_service.batch_modify_messages(message_ids, add_label_ids=["UNREAD"])
        return {"success": success, "count": len(message_ids)}
        
    else:
        raise ValueError(f"Unsupported action: {action}")

def process_ai_task(task_description: str, user: User, db: Session) -> Dict[str, Any]:
    """Process a task described in natural language using AI"""
    # This would be expanded to use OpenAI to parse the natural language task
    # For now, we'll implement a simple rule-based parser
    
    task_description_lower = task_description.lower()
    
    # Task type detection
    task_type = TaskType.CUSTOM
    if any(term in task_description_lower for term in ["delete", "remove", "clean", "trash"]):
        task_type = TaskType.EMAIL_CLEANUP
    elif any(term in task_description_lower for term in ["organize", "label", "categorize", "move"]):
        task_type = TaskType.EMAIL_ORGANIZATION
    elif any(term in task_description_lower for term in ["find", "search", "look for"]):
        task_type = TaskType.EMAIL_SEARCH
    
    # Simple task parsing examples
    if "delete all spam" in task_description_lower:
        # Find spam emails first
        spam_emails = db.query(Email).filter(
            Email.user_id == user.id,
            Email.is_spam == True
        ).all()
        
        message_ids = [email.gmail_id for email in spam_emails if email.gmail_id]
        
        if not message_ids:
            return {"message": "No spam emails found", "task_created": False}
        
        # Create task
        task_request = TaskRequest(
            task_type=TaskType.EMAIL_CLEANUP,
            description=f"Delete {len(message_ids)} spam emails",
            steps=[
                TaskStep(
                    action=TaskAction.DELETE,
                    params={"message_ids": message_ids, "permanent": False}
                )
            ]
        )
        
        task = create_task(db, str(user.id), task_request)
        return {
            "message": f"Created task to delete {len(message_ids)} spam emails",
            "task_id": task.id,
            "task_created": True
        }
        
    elif "archive unread" in task_description_lower:
        # Find unread emails
        unread_emails = db.query(Email).filter(
            Email.user_id == user.id,
            Email.labels.contains(["UNREAD"])
        ).all()
        
        message_ids = [email.gmail_id for email in unread_emails if email.gmail_id]
        
        if not message_ids:
            return {"message": "No unread emails found", "task_created": False}
        
        # Create task
        task_request = TaskRequest(
            task_type=TaskType.EMAIL_ORGANIZATION,
            description=f"Archive {len(message_ids)} unread emails",
            steps=[
                TaskStep(
                    action=TaskAction.ARCHIVE,
                    params={"message_ids": message_ids}
                )
            ]
        )
        
        task = create_task(db, str(user.id), task_request)
        return {
            "message": f"Created task to archive {len(message_ids)} unread emails",
            "task_id": task.id,
            "task_created": True
        }
        
    # Default response for unsupported tasks
    return {
        "message": "I don't know how to perform this task yet",
        "task_created": False
    }

# Routes
@router.post("/tasks", response_model=TaskResponse)
async def create_task_endpoint(
    task_request: TaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    task = create_task(db, str(current_user.id), task_request)
    
    return TaskResponse(
        task_id=task.id,
        status=task.status,
        description=task.description,
        created_at=task.created_at,
        updated_at=task.updated_at,
        progress=task.progress
    )

@router.post("/tasks/{task_id}/execute", response_model=TaskResponse)
async def execute_task_endpoint(
    task_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a task"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Execute task in background
    background_tasks.add_task(execute_task, db, task, current_user)
    
    # Update task status
    task.status = TaskStatus.IN_PROGRESS
    task.updated_at = datetime.utcnow()
    db.commit()
    
    return TaskResponse(
        task_id=task.id,
        status=TaskStatus.IN_PROGRESS,
        description=task.description,
        created_at=task.created_at,
        updated_at=datetime.utcnow(),
        progress=0
    )

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task status"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        task_id=task.id,
        status=task.status,
        description=task.description,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        progress=task.progress,
        result=task.result,
        error=task.error
    )

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatus] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List tasks"""
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if status:
        query = query.filter(Task.status == status)
    
    tasks = query.order_by(Task.created_at.desc()).limit(limit).all()
    
    return [
        TaskResponse(
            task_id=task.id,
            status=task.status,
            description=task.description,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            progress=task.progress,
            result=task.result,
            error=task.error
        )
        for task in tasks
    ]

@router.post("/ai-task")
async def create_ai_task(
    task_description: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create and execute a task from natural language description"""
    result = process_ai_task(task_description, current_user, db)
    
    if result.get("task_created"):
        task_id = result.get("task_id")
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == current_user.id
        ).first()
        
        if task:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.utcnow()
            db.commit()
            
            # Execute task in background
            background_tasks.add_task(execute_task, db, task, current_user)
            
            return {
                "message": result.get("message"),
                "task_id": task_id,
                "status": "started",
                "description": task.description
            }
    
    return {
        "message": result.get("message", "Failed to create task"),
        "status": "failed_to_create"
    }

@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a task"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed task")
    
    task.status = TaskStatus.CANCELLED
    task.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Task cancelled", "task_id": task_id}

# Export router
task_executor_router = router
