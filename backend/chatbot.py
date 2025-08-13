"""
Enhanced Email Management Chatbot
Allows users to interact with their emails via natural language with advanced features
"""
import os
from openai import OpenAI
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import json

from database import get_db
from gmail import GmailService
from models import User, Email
from auth import get_current_user

router = APIRouter()

# OpenAI setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _format_plain_text(text: str) -> str:
    """Convert common markdown patterns to clean plain text for chat bubbles."""
    if not text:
        return ""
    cleaned = text
    # Remove bold/italic markers and headings
    cleaned = cleaned.replace('**', '')
    cleaned = cleaned.replace('*', '')
    cleaned = cleaned.replace('### ', '')
    cleaned = cleaned.replace('## ', '')
    cleaned = cleaned.replace('# ', '')
    # Collapse excess newlines
    while '\n\n\n' in cleaned:
        cleaned = cleaned.replace('\n\n\n', '\n\n')
    return cleaned.strip()

class ChatRequest(BaseModel):
    message: str
    context: Optional[List[dict]] = None  # Chat history for context

class ChatResponse(BaseModel):
    response: str
    action: Optional[str] = None
    data: Optional[dict] = None
    suggestions: List[str] = []
    quick_actions: List[dict] = []

class EmailSummary(BaseModel):
    total: int
    spam: int
    unprocessed: int
    categories: dict
    recent_senders: List[dict]
    oldest_unread: Optional[dict]

def get_email_summary(user: User, db: Session) -> EmailSummary:
    """Get comprehensive email summary for the user"""
    
    # Use local database count; Gmail totals differ by folders and include sent/trash
    total_emails = db.query(Email).filter(Email.user_id == user.id).count()
    
    # Database counts for processed emails
    spam_count = db.query(Email).filter(Email.user_id == user.id, Email.is_spam == True).count()
    # Consider emails with category or any labels as processed
    unprocessed = db.query(Email).filter(
        Email.user_id == user.id,
        Email.is_processed == False,
        Email.category.is_(None),
        or_(Email.labels.is_(None), Email.labels == [])
    ).count()
    
    # Categories: merge explicit categories and Gmail labels for better coverage
    categories: dict = {}
    # 1) From AI categories
    for category, count in db.query(Email.category, func.count(Email.id)).filter(
        Email.user_id == user.id,
        Email.category.isnot(None)
    ).group_by(Email.category):
        categories[category] = categories.get(category, 0) + count
    # 2) From Gmail labels (translate label IDs to human names)
    label_name_by_id = {}
    user_label_ids = set()
    try:
        service = GmailService(user)
        for lbl in service.get_labels() or []:
            label_id = lbl.get('id')
            label_name_by_id[label_id] = lbl.get('name')
            if lbl.get('type') == 'user':
                user_label_ids.add(label_id)
    except Exception:
        pass

    for labels_json, count in db.query(Email.labels, func.count(Email.id)).filter(
        Email.user_id == user.id,
        Email.labels.isnot(None)
    ).group_by(Email.labels):
        try:
            for label in labels_json or []:
                if not label:
                    continue
                # Only include USER-created labels to avoid massive Gmail auto categories
                if label not in user_label_ids:
                    continue
                # Translate to label name if we have it
                name = label_name_by_id.get(label, label)
                # Normalize Gmail system category labels
                system_map = {
                    'INBOX': 'Inbox',
                    'SPAM': 'Spam',
                    'TRASH': 'Trash',
                    'SENT': 'Sent',
                    'DRAFT': 'Draft',
                    'CATEGORY_UPDATES': 'Updates',
                    'CATEGORY_PERSONAL': 'Personal',
                    'CATEGORY_FORUMS': 'Forums',
                    'CATEGORY_PROMOTIONS': 'Promotions',
                    'CATEGORY_SOCIAL': 'Social',
                    'IMPORTANT': 'Important',
                }
                normalized = system_map.get(name, name)
                # Skip noisy flags that shouldn't be categories
                skip = {"UNREAD", "STARRED", "YELLOW_STAR"}
                if isinstance(normalized, str) and normalized.upper() in skip:
                    continue
                # Clean up generic "Label_123..." to "Custom Label"
                if isinstance(normalized, str) and normalized.upper().startswith('LABEL_'):
                    normalized = 'Custom Label'
                categories[normalized] = categories.get(normalized, 0) + count
        except Exception:
            continue
    
    # Top senders
    sender_results = db.query(Email.sender, func.count(Email.id)).filter(
        Email.user_id == user.id
    ).group_by(Email.sender).order_by(desc(func.count(Email.id))).limit(5).all()
    
    recent_senders = [{"sender": sender, "count": count} for sender, count in sender_results]
    
    # Oldest unread email
    oldest_unread = db.query(Email).filter(
        Email.user_id == user.id,
        Email.is_processed == False
    ).order_by(Email.received_date).first()
    
    oldest_unread_dict = None
    if oldest_unread:
        oldest_unread_dict = {
            "subject": oldest_unread.subject,
            "sender": oldest_unread.sender,
            "received_date": oldest_unread.received_date.isoformat() if oldest_unread.received_date else None
        }
    
    return EmailSummary(
        total=total_emails,
        spam=spam_count,
        unprocessed=unprocessed,
        categories=categories,
        recent_senders=recent_senders,
        oldest_unread=oldest_unread_dict
    )

def detect_intent_and_entities(message: str) -> dict:
    """Detect user intent and extract entities from the message"""
    message_lower = message.lower()
    
    # Intent detection
    intent = "general"
    entities = {}
    
    # Spam-related intents
    if any(phrase in message_lower for phrase in ["delete spam", "clean spam", "remove spam", "clear spam", "delete my spam"]):
        intent = "delete_spam"
    elif any(phrase in message_lower for phrase in ["show spam", "list spam", "spam emails", "show me spam"]):
        intent = "show_spam"
    
    # Classification intents
    elif any(phrase in message_lower for phrase in ["classify", "process emails", "analyze emails", "categorize"]):
        intent = "classify_emails"
    
    # Stats and summary intents
    elif any(phrase in message_lower for phrase in ["stats", "summary", "overview", "dashboard", "report"]):
        intent = "show_stats"
    
    # Search intents
    elif any(phrase in message_lower for phrase in ["find", "search", "look for", "show me emails"]):
        intent = "search_emails"
        # Extract search terms
        if "from" in message_lower:
            # Extract sender
            words = message_lower.split()
            try:
                from_index = words.index("from")
                if from_index + 1 < len(words):
                    entities["sender"] = words[from_index + 1]
            except ValueError:
                pass
    
    # Sync intents
    elif any(phrase in message_lower for phrase in ["sync", "refresh", "update emails", "get new emails"]):
        intent = "sync_emails"
    
    # Help intents
    elif any(phrase in message_lower for phrase in ["help", "what can you do", "commands", "options"]):
        intent = "help"
    
    return {"intent": intent, "entities": entities}

def process_chat_message(message: str, user: User, db: Session, context: List[dict] = None) -> ChatResponse:
    """Enhanced chat message processing with intent detection and actions"""
    
    # Get email summary
    email_summary = get_email_summary(user, db)
    
    # Detect intent and entities
    intent_data = detect_intent_and_entities(message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]
    
    # Build context for AI
    system_context = f"""
    You are an intelligent email management assistant. The user has:
    - {email_summary.total} total emails
    - {email_summary.spam} spam emails
    - {email_summary.unprocessed} unprocessed emails
    - Categories: {email_summary.categories}
    - Top senders: {[s['sender'] for s in email_summary.recent_senders[:3]]}

    Output style rules (always follow):
    - Use short, skimmable lines with hyphen bullets
    - Bold only labels/titles (e.g., **Category Name**), keep numbers unbolded
    - Sort category lines in descending count, cap to top 12, then show "**Other Categories:**" with a few more
    - Prefer user-created labels over Gmail's auto labels; do not list flags like UNREAD/STARRED
    - Avoid headings beyond simple bolded titles; avoid code blocks
    - Keep the answer fully self-contained and avoid truncation

    User intent detected: {intent}
    User message: {message}
    """
    
    # Handle specific intents
    action = None
    data = {}
    suggestions = []
    quick_actions = []
    
    if intent == "delete_spam":
        if email_summary.spam > 0:
            action = "delete_spam"
            data = {"spam_count": email_summary.spam}
            ai_response = f"I found {email_summary.spam} spam emails. Would you like me to delete them all?"
            quick_actions = [
                {"label": "Yes, delete all spam", "action": "confirm_delete_spam"},
                {"label": "Show me the spam first", "action": "show_spam"}
            ]
        else:
            ai_response = "Great news! You don't have any spam emails to delete."
    
    elif intent == "show_spam":
        action = "show_spam"
        data = {"spam_count": email_summary.spam}
        ai_response = f"Here are your {email_summary.spam} spam emails:" if email_summary.spam > 0 else "You don't have any spam emails."
    
    elif intent == "classify_emails":
        if email_summary.unprocessed > 0:
            action = "classify_emails"
            data = {"unprocessed": email_summary.unprocessed}
            ai_response = f"I'll classify your {email_summary.unprocessed} unprocessed emails using AI."
            quick_actions = [{"label": "Start classification", "action": "confirm_classify"}]
        else:
            ai_response = "All your emails are already classified!"
    
    elif intent == "show_stats":
        action = "show_stats"
        data = email_summary.dict()
        # Build a concise, ordered plain-text summary (no markdown), avoid truncation
        categories_items = sorted(
            [(k, v) for k, v in email_summary.categories.items() if k],
            key=lambda kv: kv[1],
            reverse=True,
        )
        inbox_count = 0
        for name, cnt in categories_items:
            if str(name).lower() == "inbox":
                inbox_count = cnt
                break
        top_n = 12
        top_lines = [f"- **{name}**: {cnt}" for name, cnt in categories_items[:top_n]]
        other_lines = [f"- **{name}**: {cnt}" for name, cnt in categories_items[top_n:top_n+8]]  # cap output
        header = [
            f"- **Total Emails**: {email_summary.total}",
            f"- **Spam Emails**: {email_summary.spam}",
            f"- **Unprocessed Emails**: {email_summary.unprocessed}",
            f"- **Emails in Inbox**: {inbox_count}",
            "",
            "**Categories (top first):**",
        ]
        if not top_lines:
            top_lines = ["- No categories detected"]
        if other_lines:
            other_header = ["", "**Other Categories:**"]
        else:
            other_header = []
        ai_response = "\n".join(header + top_lines + other_header + other_lines)
    
    elif intent == "sync_emails":
        action = "sync_emails"
        ai_response = "I'll sync your latest emails from Gmail."
        quick_actions = [{"label": "Sync now", "action": "confirm_sync"}]
    
    elif intent == "search_emails":
        action = "search_emails"
        data = entities
        if "sender" in entities:
            ai_response = f"Searching for emails from {entities['sender']}..."
        else:
            ai_response = "What would you like to search for? You can search by sender, subject, or content."
    
    elif intent == "help":
        ai_response = """I can help you manage your emails! Here's what I can do:
        
• **Clean up**: "Delete my spam emails"
• **Organize**: "Classify my emails" 
• **Search**: "Find emails from john@example.com"
• **Stats**: "Show me my email summary"
• **Sync**: "Get my latest emails"
        
Just ask me naturally - I understand conversational language!"""
        
        suggestions = [
            "Show me my email stats",
            "Delete spam emails", 
            "Classify unprocessed emails",
            "Sync my latest emails"
        ]
    
    else:
        # Use AI for general conversation
        try:
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": message}
                ],
                max_tokens=200,
                temperature=0.7,
            )
            content = response.choices[0].message.content or ""
            # Normalize markdown to plain text
            ai_response = _format_plain_text(content)
        except Exception:
            ai_response = (
                "I'm having trouble processing that right now. Could you try rephrasing?"
            )
    
    
    # Add contextual suggestions
    if not suggestions:
        if email_summary.spam > 0:
            suggestions.append(f"Delete {email_summary.spam} spam emails")
        if email_summary.unprocessed > 0:
            suggestions.append(f"Classify {email_summary.unprocessed} emails")
        if email_summary.total > 0:
            suggestions.append("Show email statistics")
    
    return ChatResponse(
        response=ai_response,
        action=action,
        data=data,
        suggestions=suggestions[:3],  # Limit to 3 suggestions
        quick_actions=quick_actions
    )

# Routes
@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced chat with the email management assistant"""
    return process_chat_message(request.message, current_user, db, request.context)

@router.get("/summary", response_model=EmailSummary)
async def get_email_summary_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive email summary"""
    return get_email_summary(current_user, db)

@router.get("/suggestions")
async def get_chat_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get contextual chat suggestions based on user's email state"""
    
    email_summary = get_email_summary(current_user, db)
    
    suggestions = []
    
    # Priority suggestions based on email state
    if email_summary.spam > 0:
        suggestions.append(f"Delete my {email_summary.spam} spam emails")
    
    if email_summary.unprocessed > 0:
        suggestions.append(f"Classify my {email_summary.unprocessed} unprocessed emails")
    
    if email_summary.total > 100:
        suggestions.append("Help me organize my inbox")
    
    # Always available suggestions
    suggestions.extend([
        "Show me my email statistics",
        "Sync my latest emails",
        "What can you help me with?"
    ])
    
    return {"suggestions": suggestions[:5]}  # Limit to 5 suggestions

@router.post("/search")
async def search_emails(
    query: str,
    sender: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search emails with various filters"""
    
    # Build query
    email_query = db.query(Email).filter(Email.user_id == current_user.id)
    
    if sender:
        email_query = email_query.filter(Email.sender.ilike(f"%{sender}%"))
    
    if category:
        email_query = email_query.filter(Email.category == category)
    
    if query:
        email_query = email_query.filter(
            Email.subject.ilike(f"%{query}%") | 
            Email.snippet.ilike(f"%{query}%")
        )
    
    emails = email_query.order_by(desc(Email.received_date)).limit(limit).all()
    
    return {
        "results": [
            {
                "id": str(email.id),
                "subject": email.subject,
                "sender": email.sender,
                "snippet": email.snippet[:100] + "..." if email.snippet and len(email.snippet) > 100 else email.snippet,
                "category": email.category,
                "is_spam": email.is_spam,
                "received_date": email.received_date.isoformat() if email.received_date else None
            }
            for email in emails
        ],
        "total_found": len(emails),
        "query_used": {
            "text": query,
            "sender": sender,
            "category": category
        }
    }

@router.get("/quick-actions")
async def get_quick_actions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quick action buttons based on current email state"""
    
    email_summary = get_email_summary(current_user, db)
    
    actions = []
    
    if email_summary.spam > 0:
        actions.append({
            "id": "delete_spam",
            "label": f"Delete {email_summary.spam} Spam Emails",
            "icon": "🗑️",
            "type": "destructive"
        })
    
    if email_summary.unprocessed > 0:
        actions.append({
            "id": "classify_emails", 
            "label": f"Classify {email_summary.unprocessed} Emails",
            "icon": "🤖",
            "type": "primary"
        })
    
    actions.extend([
        {
            "id": "sync_emails",
            "label": "Sync Latest Emails",
            "icon": "🔄",
            "type": "secondary"
        },
        {
            "id": "go_to_ai",
            "label": "Go to AI Assistant",
            "icon": "💬", 
            "type": "secondary"
        }
    ])
    
    return {"actions": actions}


@router.get("/self-test")
async def chatbot_self_test(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run a deterministic self-test of core intents without external AI calls."""
    test_messages = [
        "delete spam",
        "classify emails",
        "show stats",
        "sync emails",
        "help",
    ]
    results = []
    for msg in test_messages:
        try:
            resp = process_chat_message(msg, current_user, db)
            results.append({
                "message": msg,
                "response": resp.response,
                "action": resp.action,
                "has_quick_actions": bool(resp.quick_actions),
                "suggestions": resp.suggestions,
            })
        except Exception as e:
            results.append({"message": msg, "error": str(e)})
    return {"ok": True, "cases": results}

# Export router
chatbot_router = router