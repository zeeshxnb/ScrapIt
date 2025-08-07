"""
Chat Interface API Routes

Endpoints for the chat interface and task management
"""
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, Body, BackgroundTasks
from pydantic import BaseModel

# Import services
# Note: These imports will need to be updated based on your project structure
from ..services.chat_interface import ChatInterface, TaskItem
from ..services.llm_client import LLMClient, LLMProvider
from ..config.settings import get_settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Models for request/response
class ChatMessageRequest(BaseModel):
    """Chat message from user"""
    message: str
    conversation_id: str = None

class TaskResponse(BaseModel):
    """Task extracted from chat"""
    id: str
    description: str
    type: str
    parameters: Dict[str, Any]
    status: str

class ChatResponse(BaseModel):
    """Response to chat message"""
    message: str
    tasks: List[TaskResponse] = []
    conversation_id: str

class TaskConfirmationRequest(BaseModel):
    """Request to confirm tasks"""
    task_ids: List[str]
    conversation_id: str

class TaskExecutionResponse(BaseModel):
    """Response after task execution"""
    completed: List[TaskResponse]
    failed: List[TaskResponse]
    summary: str

# In-memory store for demo purposes
# In production, this would be a database
conversations = {}
tasks = {}

# Get LLM client
def get_llm_client():
    """Get LLM client from settings"""
    settings = get_settings()
    
    # Using OpenAI o1 model
    provider = "openai"
    api_key = settings.openai_api_key
    model = "o1"
    
    return LLMClient(provider=provider, api_key=api_key, model=model)

# Get chat interface
def get_chat_interface():
    """Get chat interface with LLM client"""
    llm_client = get_llm_client()
    return ChatInterface(llm_client=llm_client)

@router.post("/message", response_model=ChatResponse)
async def process_chat_message(
    request: ChatMessageRequest,
    chat_interface: ChatInterface = Depends(get_chat_interface)
):
    """
    Process a chat message from the user
    
    Extract tasks from the message and return them for confirmation
    """
    try:
        # Process message and extract tasks
        extracted_tasks = await chat_interface.process_user_message(request.message)
        
        # Generate confirmation message
        confirmation = await chat_interface.get_task_confirmation(extracted_tasks)
        
        # Create or update conversation
        conversation_id = request.conversation_id or f"conv_{len(conversations) + 1}"
        
        # Store tasks and conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversations[conversation_id].append({
            "role": "user",
            "content": request.message
        })
        
        conversations[conversation_id].append({
            "role": "assistant",
            "content": confirmation
        })
        
        # Store tasks
        for task in extracted_tasks:
            tasks[task.id] = task
        
        # Prepare response
        task_responses = [TaskResponse(**task.to_dict()) for task in extracted_tasks]
        
        return ChatResponse(
            message=confirmation,
            tasks=task_responses,
            conversation_id=conversation_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.post("/tasks/confirm", response_model=TaskExecutionResponse)
async def confirm_tasks(
    request: TaskConfirmationRequest,
    background_tasks: BackgroundTasks,
    chat_interface: ChatInterface = Depends(get_chat_interface)
):
    """
    Confirm and execute tasks
    
    Execute the confirmed tasks and return results
    """
    try:
        # Get tasks by ID
        confirmed_tasks = [tasks.get(task_id) for task_id in request.task_ids if task_id in tasks]
        
        if not confirmed_tasks:
            raise HTTPException(status_code=404, detail="No valid tasks found")
        
        # Execute tasks
        results = await chat_interface.execute_tasks(confirmed_tasks)
        
        # Update conversation
        if request.conversation_id in conversations:
            conversations[request.conversation_id].append({
                "role": "user",
                "content": "Yes, please proceed with these tasks."
            })
            
            conversations[request.conversation_id].append({
                "role": "assistant",
                "content": results["summary"]
            })
        
        # Prepare response
        completed_tasks = [TaskResponse(**task) for task in results["completed"]]
        failed_tasks = [TaskResponse(**task) for task in results["failed"]]
        
        return TaskExecutionResponse(
            completed=completed_tasks,
            failed=failed_tasks,
            summary=results["summary"]
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tasks: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=List[Dict[str, str]])
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history
    
    Return the history of messages for a conversation
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversations[conversation_id]