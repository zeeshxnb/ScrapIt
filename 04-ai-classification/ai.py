"""
AI Classification Module - Consolidated
Handles email classification using OpenAI and clustering
"""
import os
import openai
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_db
from models import User, Email
from auth import get_current_user

router = APIRouter()

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_email(email: Email) -> dict:
    """Classify single email using OpenAI"""
    try:
        prompt = f"""
        Classify this email as one of: work, personal, promotional, spam, newsletter, social
        
        Subject: {email.subject}
        From: {email.sender}
        Content: {email.snippet}
        
        Respond with just the category and confidence (0-1):
        Category: 
        Confidence: 
        Is_Spam: true/false
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse response
        lines = result.split('\n')
        category = "unknown"
        confidence = 0.5
        is_spam = False
        
        for line in lines:
            if line.startswith("Category:"):
                category = line.split(":")[1].strip().lower()
            elif line.startswith("Confidence:"):
                try:
                    confidence = float(line.split(":")[1].strip())
                except:
                    confidence = 0.5
            elif line.startswith("Is_Spam:"):
                is_spam = "true" in line.lower()
        
        return {
            "category": category,
            "confidence": confidence,
            "is_spam": is_spam
        }
        
    except Exception as e:
        return {
            "category": "unknown",
            "confidence": 0.0,
            "is_spam": False,
            "error": str(e)
        }

def classify_emails_batch(db: Session, user_id: str, limit: int = 10) -> dict:
    """Classify unprocessed emails in batch"""
    # Get unprocessed emails
    emails = db.query(Email).filter(
        Email.user_id == user_id,
        Email.is_processed == False
    ).limit(limit).all()
    
    processed = 0
    for email in emails:
        result = classify_email(email)
        
        # Update email with classification
        email.category = result["category"]
        email.confidence_score = result["confidence"]
        email.is_spam = result["is_spam"]
        email.is_processed = True
        
        processed += 1
    
    db.commit()
    
    return {
        "success": True,
        "processed": processed,
        "total_unprocessed": len(emails)
    }

# Routes
@router.post("/classify")
async def classify_emails(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Classify emails using AI"""
    result = classify_emails_batch(db, str(current_user.id))
    return result

@router.get("/categories")
async def get_email_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email categories summary"""
    categories = db.query(Email.category, db.func.count(Email.id)).filter(
        Email.user_id == current_user.id,
        Email.category.isnot(None)
    ).group_by(Email.category).all()
    
    return {
        "categories": [
            {"category": cat, "count": count}
            for cat, count in categories
        ]
    }

@router.get("/spam")
async def get_spam_emails(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spam emails"""
    spam_emails = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.is_spam == True
    ).all()
    
    return {
        "spam_emails": [
            {
                "id": str(email.id),
                "subject": email.subject,
                "sender": email.sender,
                "confidence": email.confidence_score
            }
            for email in spam_emails
        ]
    }

@router.delete("/spam")
async def delete_spam_emails(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all spam emails"""
    spam_count = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.is_spam == True
    ).count()
    
    db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.is_spam == True
    ).update({"is_deleted": True})
    
    db.commit()
    
    return {"deleted_count": spam_count}

# Export router
ai_router = router