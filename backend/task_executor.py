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
    DELETE = "DELETE"
    ARCHIVE = "ARCHIVE"
    LABEL = "LABEL"
    MOVE = "MOVE"
    SEARCH = "SEARCH"
    COMPOSE = "COMPOSE"
    SEND = "SEND"
    MARK_READ = "MARK_READ"
    MARK_UNREAD = "MARK_UNREAD"
    STAR = "STAR"
    UNSTAR = "UNSTAR"

class TaskStep(BaseModel):
    action: str
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
        steps=[step.dict() for step in task_request.steps],
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
    import logging
    
    # Configure logger
    logger = logging.getLogger("task_executor")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    task_id = task.id
    logger.info(f"[Task {task_id}] Starting execution of task: {task.description}")
    
    if task.status == TaskStatus.COMPLETED:
        logger.info(f"[Task {task_id}] Task already completed")
        return {"message": "Task already completed", "task_id": task.id}
    
    if task.status == TaskStatus.FAILED:
        logger.info(f"[Task {task_id}] Task previously failed: {task.error}")
        return {"message": "Task previously failed", "task_id": task.id, "error": task.error}
    
    # Mark task as in progress
    try:
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"[Task {task_id}] Task marked as in progress")
    except Exception as e:
        logger.error(f"[Task {task_id}] Failed to update task status: {str(e)}")
        return {"message": "Failed to update task status", "task_id": task.id, "error": str(e)}
    
    # Send initial notification
    try:
        from notification import notify_task_update
        await notify_task_update(task)
        logger.info(f"[Task {task_id}] Sent initial notification")
    except Exception as e:
        logger.warning(f"[Task {task_id}] Failed to send initial notification: {str(e)}")
    
    # Initialize Gmail service
    gmail_service = GmailService(user)
    
    total_steps = len(task.steps) if task.steps else 0
    completed_steps = 0
    results = {}
    
    logger.info(f"[Task {task_id}] Starting execution of {total_steps} steps")
    
    try:
        for i, step in enumerate(task.steps):
            step_number = i + 1
            action = step.get("action")
            params = step.get("params", {})
            
            if step.get("completed"):
                logger.info(f"[Task {task_id}] Step {step_number}/{total_steps} ({action}) already completed, skipping")
                completed_steps += 1
                continue
            
            logger.info(f"[Task {task_id}] Executing step {step_number}/{total_steps}: {action} with params: {params}")
            
            # Execute the step
            step_result = execute_step(step, gmail_service, db, user)
            logger.info(f"[Task {task_id}] Step {step_number}/{total_steps} completed successfully: {step_result}")
            
            # Update step status
            step["completed"] = True
            step["result"] = step_result
            
            # Add to results
            results[f"step_{step_number}"] = step_result
            
            # Update progress
            completed_steps += 1
            task.progress = int((completed_steps / total_steps) * 100) if total_steps > 0 else 100
            task.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"[Task {task_id}] Progress updated: {task.progress}%")
        
        # Mark task as completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = results
        db.commit()
        logger.info(f"[Task {task_id}] Task marked as completed")
        
        # Send completion notification
        try:
            from notification import notify_task_completion
            await notify_task_completion(task)
            logger.info(f"[Task {task_id}] Sent completion notification")
        except Exception as e:
            logger.warning(f"[Task {task_id}] Failed to send completion notification: {str(e)}")
        
        return {
            "message": "Task completed successfully",
            "task_id": task.id,
            "results": results
        }
        
    except Exception as e:
        # Mark task as failed
        logger.error(f"[Task {task_id}] Task execution failed: {str(e)}")
        task.status = TaskStatus.FAILED
        task.error = str(e)
        task.updated_at = datetime.utcnow()
        db.commit()
        
        # Send failure notification
        try:
            from notification import notify_task_update
            await notify_task_update(task)
            logger.info(f"[Task {task_id}] Sent failure notification")
        except Exception as notif_error:
            logger.warning(f"[Task {task_id}] Failed to send failure notification: {str(notif_error)}")
        
        return {
            "message": "Task failed",
            "task_id": task.id,
            "error": str(e)
        }

def validate_step(step: Dict[str, Any], logger=None, task_id: str = "", step_number: int = 0) -> bool:
    """Validate that a step has all required fields and parameters"""
    action = step.get("action")
    params = step.get("params", {})
    
    if not action:
        if logger:
            logger.error(f"[Task {task_id}] Step {step_number} missing action")
        return False
        
    # Normalize action to uppercase for consistency
    action = action.upper() if action else None
        
    # Check that action is a valid TaskAction
    valid_actions = [e.value for e in TaskAction]
    if action not in valid_actions:
        if logger:
            logger.error(f"[Task {task_id}] Step {step_number} has invalid action: {action}")
        return False
    
    # Validate required parameters for each action type
    if action in ["DELETE", "ARCHIVE", "MARK_READ", "MARK_UNREAD", "STAR", "UNSTAR"]:
        if not params.get("message_ids"):
            if logger:
                logger.error(f"[Task {task_id}] Step {step_number} ({action}) missing required parameter: message_ids")
            return False
    
    if action == "LABEL":
        if not params.get("message_ids"):
            if logger:
                logger.error(f"[Task {task_id}] Step {step_number} (LABEL) missing required parameter: message_ids")
            return False
        if "label_name" not in params:
            if logger:
                logger.error(f"[Task {task_id}] Step {step_number} (LABEL) missing required parameter: label_name")
            return False
    
    if action == "SEARCH":
        if "query" not in params:
            if logger:
                logger.error(f"[Task {task_id}] Step {step_number} (SEARCH) missing required parameter: query")
            return False
    
    return True

def execute_step(step: Dict[str, Any], gmail_service: GmailService, db: Session, user: User) -> Dict[str, Any]:
    """Execute a single task step"""
    action = step.get("action")
    params = step.get("params", {})
    
    # Normalize action to uppercase for consistency
    if action and isinstance(action, str):
        action = action.upper()
    
    if action == "DELETE":
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
                    if hasattr(email, "labels") and email.labels is not None:
                        if "TRASH" not in email.labels:
                            email.labels = list(set(email.labels + ["TRASH"]))
                        if "INBOX" in email.labels:
                            email.labels.remove("INBOX")
        
        db.commit()
        return {"success": success, "count": len(message_ids)}
        
    elif action == "ARCHIVE":
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
                if hasattr(email, "labels") and email.labels is not None and "INBOX" in email.labels:
                    email.labels.remove("INBOX")
        
        db.commit()
        return {"success": success, "count": len(message_ids)}
        
    elif action == "LABEL":
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
            
            if email and hasattr(email, "labels") and email.labels is not None:
                if remove and label_id in email.labels:
                    email.labels.remove(label_id)
                elif not remove and label_id not in email.labels:
                    email.labels.append(label_id)
        
        db.commit()
        return {"success": success, "count": len(message_ids), "label": label_name}
        
    elif action == "SEARCH":
        # Search for emails
        query = params.get("query", "")
        max_results = params.get("max_results", 100)
        
        messages = gmail_service.search_messages(query, max_results=max_results)
        message_ids = [msg["id"] for msg in messages]
        
        return {"success": True, "count": len(message_ids), "message_ids": message_ids}
        
    elif action == "MARK_READ":
        # Mark emails as read
        message_ids = params.get("message_ids", [])
        success = gmail_service.batch_modify_messages(message_ids, remove_label_ids=["UNREAD"])
        return {"success": success, "count": len(message_ids)}
        
    elif action == "MARK_UNREAD":
        # Mark emails as unread
        message_ids = params.get("message_ids", [])
        success = gmail_service.batch_modify_messages(message_ids, add_label_ids=["UNREAD"])
        return {"success": success, "count": len(message_ids)}
        
    elif action == "STAR":
        # Star emails
        message_ids = params.get("message_ids", [])
        success = gmail_service.batch_modify_messages(message_ids, add_label_ids=["STARRED"])
        return {"success": success, "count": len(message_ids)}
        
    elif action == "UNSTAR":
        # Unstar emails
        message_ids = params.get("message_ids", [])
        success = gmail_service.batch_modify_messages(message_ids, remove_label_ids=["STARRED"])
        return {"success": success, "count": len(message_ids)}
        
    else:
        raise ValueError(f"Unsupported action: {action}")

def process_ai_task(task_description: str, user: User, db: Session) -> Dict[str, Any]:
    """Process a task described in natural language using AI"""
    import json
    from openai import OpenAI
    
    # Get email statistics for context
    total_emails = db.query(Email).filter(Email.user_id == user.id).count()
    spam_count = db.query(Email).filter(Email.user_id == user.id, Email.is_spam == True).count()
    unread_count = 0
    inbox_count = 0
    
    try:
        unread_count = db.query(Email).filter(
            Email.user_id == user.id,
            Email.labels.contains(["UNREAD"])
        ).count()
        inbox_count = db.query(Email).filter(
            Email.user_id == user.id,
            Email.labels.contains(["INBOX"])
        ).count()
    except:
        pass  # Ignore if label queries fail
    
    # Try AI-based task parsing first
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Construct the system prompt with available actions and task examples
        system_prompt = f"""
        You are an expert AI assistant that creates executable email management tasks based on user requests.
        
        USER EMAIL STATISTICS:
        - Total emails: {total_emails}
        - Spam emails: {spam_count}
        - Unread emails: {unread_count}
        - Inbox emails: {inbox_count}
        
        AVAILABLE ACTIONS:
        - DELETE: Delete emails (moves to trash by default)
        - ARCHIVE: Archive emails (removes from inbox)
        - LABEL: Apply or remove Gmail labels
        - MARK_READ: Mark emails as read
        - MARK_UNREAD: Mark emails as unread
        - STAR: Star emails
        - UNSTAR: Remove star from emails
        - SEARCH: Search for emails with specific criteria
        
        VALID TASK TYPES:
        - EMAIL_CLEANUP: For tasks that delete or clean up emails
        - EMAIL_ORGANIZATION: For tasks that organize or categorize emails
        - EMAIL_SEARCH: For search-related tasks
        - CUSTOM: For multi-step or complex tasks
        
        Your task is to:
        1. Parse the user's request precisely
        2. Determine exactly which action(s) they want to perform
        3. Identify exactly which emails should be affected using search criteria
        4. Create a detailed task plan with specific steps
        
        PROVIDE YOUR RESPONSE AS JSON with this EXACT structure:
        {{
          "task_type": "EMAIL_CLEANUP|EMAIL_ORGANIZATION|EMAIL_SEARCH|CUSTOM",
          "description": "A clear description of the task",
          "steps": [
            {{
              "action": "One of the AVAILABLE ACTIONS listed above",
              "params": {{
                "query": "Search query to find relevant emails (REQUIRED if message_ids is empty)",
                "message_ids": [], 
                "permanent": false, 
                "label_name": "Name of label (REQUIRED for LABEL action)",
                "remove": false 
              }}
            }}
          ]
        }}
        """
        
        # User message describing the email task
        user_message = f"Task: {task_description}"
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,  # Low temperature for more deterministic responses
            response_format={"type": "json_object"}  # Enforce JSON format
        )
        
        # Parse the response
        task_data = json.loads(response.choices[0].message.content)
        
        # Process each step to translate search queries into message IDs
        processed_steps = []
        for step in task_data.get("steps", []):
            action = step.get("action")
            params = step.get("params", {})
            
            # If there's a query, perform search and get message IDs
            if "query" in params and params["query"]:
                query = params["query"]
                # Create Gmail service instance
                gmail_service = GmailService(user)
                
                # Search for matching messages
                messages = gmail_service.search_messages(query, max_results=500)
                message_ids = [msg["id"] for msg in messages]
                
                if not message_ids:
                    return {"message": f"No emails found matching the search criteria: {query}", "task_created": False}
                
                # Update params with found message IDs
                params["message_ids"] = message_ids
                # Remove the query as we now have message IDs
                params.pop("query", None)
            
            # Create the processed step
            processed_steps.append(
                TaskStep(
                    action=action,
                    params=params
                )
            )
        
        # Create the task request
        task_request = TaskRequest(
            task_type=task_data.get("task_type", TaskType.CUSTOM),
            description=task_data.get("description", task_description),
            steps=processed_steps
        )
        
        # Create and save the task
        task = create_task(db, str(user.id), task_request)
        
        return {
            "message": f"Created task: {task_data.get('description')}",
            "task_id": task.id,
            "task_created": True
        }
    
    except Exception as e:
        print(f"Error using AI for task parsing: {str(e)}")
        
        # Fall back to rule-based parsing for common cases
        task_description_lower = task_description.lower()
        
        # Task type detection
        task_type = TaskType.CUSTOM
        if any(term in task_description_lower for term in ["delete", "remove", "clean", "trash"]):
            task_type = TaskType.EMAIL_CLEANUP
        elif any(term in task_description_lower for term in ["organize", "label", "categorize", "move", "archive"]):
            task_type = TaskType.EMAIL_ORGANIZATION
        elif any(term in task_description_lower for term in ["find", "search", "look for"]):
            task_type = TaskType.EMAIL_SEARCH
        
        # Simple task parsing examples
        if "delete all spam" in task_description_lower or "delete spam" in task_description_lower:
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
                        action="DELETE",
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
            
        elif "archive unread" in task_description_lower or "archive all unread" in task_description_lower:
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
                        action="ARCHIVE",
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
            "message": "I don't know how to perform this task yet. Please try a simpler request or different wording.",
            "task_created": False
        }

# Helper function to determine if a task is simple enough for immediate execution
def is_simple_task(task: Task) -> bool:
    """
    Determine if a task is simple enough to be executed immediately instead of in the background.
    Simple tasks are those with a single step and fewer than 50 emails to process.
    """
    if not task or not task.steps:
        return False
        
    # Complex if more than one step
    if len(task.steps) > 1:
        return False
    
    # Get the step
    step = task.steps[0]
    
    # Get message IDs
    message_ids = step.get("params", {}).get("message_ids", [])
    
    # Simple if fewer than 50 emails to process
    return len(message_ids) < 50

# Export router
task_executor_router = router
