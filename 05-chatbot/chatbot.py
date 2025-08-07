"""
Email Management Chatbot - Simple Addition
Allows users to interact with their emails via natural language
"""
import os
import openai
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_db
from models import User, Email
from auth import get_current_user

router = APIRouter()

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    action: str = None
    data: dict = None

def process_chat_message(message: str, user: User, db: Session) -> ChatResponse:
    """Process user's chat message and return appropriate response"""
    
    # Get user's email stats for context
    total_emails = db.query(Email).filter(Email.user_id == user.id).count()
    spam_count = db.query(Email).filter(Email.user_id == user.id, Email.is_spam == True).count()
    unprocessed = db.query(Email).filter(Email.user_id == user.id, Email.is_processed == False).count()
    
    context = f"""
    You are an email management assistant. The user has:
    - {total_emails} total emails
    - {spam_count} spam emails
    - {unprocessed} unprocessed emails
    
    User message: {message}
    
    Respond helpfully about their email management. If they want to:
    - "delete spam" or "clean spam" -> respond with action: "delete_spam"
    - "classify emails" or "process emails" -> respond with action: "classify"
    - "show stats" or "email summary" -> respond with action: "stats"
    - general questions -> just respond conversationally
    
    Keep responses brief and helpful.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": context}],
            max_tokens=150,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Determine if an action should be taken
        action = None
        data = {}
        
        message_lower = message.lower()
        if any(phrase in message_lower for phrase in ["delete spam", "clean spam", "remove spam"]):
            action = "delete_spam"
            data = {"spam_count": spam_count}
        elif any(phrase in message_lower for phrase in ["classify", "process emails", "analyze"]):
            action = "classify"
            data = {"unprocessed": unprocessed}
        elif any(phrase in message_lower for phrase in ["stats", "summary", "overview"]):
            action = "stats"
            data = {
                "total": total_emails,
                "spam": spam_count,
                "unprocessed": unprocessed
            }
        
        return ChatResponse(
            response=ai_response,
            action=action,
            data=data
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"Sorry, I had trouble processing that. Error: {str(e)}"
        )

# Routes
@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with the email management assistant"""
    return process_chat_message(request.message, current_user, db)

@router.get("/suggestions")
async def get_chat_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get suggested chat prompts based on user's email state"""
    
    spam_count = db.query(Email).filter(Email.user_id == current_user.id, Email.is_spam == True).count()
    unprocessed = db.query(Email).filter(Email.user_id == current_user.id, Email.is_processed == False).count()
    
    suggestions = ["Show me my email stats", "Help me organize my inbox"]
    
    if spam_count > 0:
        suggestions.append(f"Delete my {spam_count} spam emails")
    
    if unprocessed > 0:
        suggestions.append(f"Classify my {unprocessed} unprocessed emails")
    
    return {"suggestions": suggestions}

# Export router
chatbot_router = router