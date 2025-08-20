"""
AI Classification Module - Consolidated
Handles email classification using OpenAI and clustering
"""
import os
import openai
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Email
from auth import get_current_user
from gmail import GmailService

router = APIRouter()

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_email(email: Email) -> dict:
    """Classify single email using OpenAI with enhanced spam detection"""
    try:
        # Enhanced prompt for better spam detection
        prompt = f"""
        Analyze this email and provide classification:
        
        Subject: {email.subject}
        From: {email.sender}
        Content: {email.snippet}
        
        Consider these spam indicators:
        - Suspicious sender patterns
        - Promotional language
        - Urgency tactics
        - Suspicious links or attachments
        - Poor grammar/spelling
        - Generic greetings
        
        Respond in this exact format:
        Category: [work/personal/promotional/spam/newsletter/social]
        Confidence: [0.0-1.0]
        Is_Spam: [true/false]
        Spam_Reason: [brief explanation if spam]
        Sender_Risk: [low/medium/high]
        """
        
        response = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse enhanced response
        lines = result.split('\n')
        category = "unknown"
        confidence = 0.5
        is_spam = False
        spam_reason = ""
        sender_risk = "low"
        
        for line in lines:
            if line.startswith("Category:"):
                category = line.split(":", 1)[1].strip().lower()
            elif line.startswith("Confidence:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except:
                    confidence = 0.5
            elif line.startswith("Is_Spam:"):
                is_spam = "true" in line.lower()
            elif line.startswith("Spam_Reason:"):
                spam_reason = line.split(":", 1)[1].strip()
            elif line.startswith("Sender_Risk:"):
                sender_risk = line.split(":", 1)[1].strip().lower()
        
        # Additional rule-based spam detection
        spam_score = calculate_spam_score(email)
        
        # Combine AI and rule-based detection
        if spam_score > 0.7 and not is_spam:
            is_spam = True
            spam_reason = f"Rule-based detection (score: {spam_score:.2f})"
        
        return {
            "category": category,
            "confidence": confidence,
            "is_spam": is_spam,
            "spam_reason": spam_reason,
            "sender_risk": sender_risk,
            "spam_score": spam_score
        }
        
    except Exception as e:
        # Fallback to rule-based detection if AI fails
        spam_score = calculate_spam_score(email)
        return {
            "category": "unknown",
            "confidence": 0.0,
            "is_spam": spam_score > 0.8,
            "spam_reason": f"Rule-based fallback (score: {spam_score:.2f})",
            "sender_risk": "medium" if spam_score > 0.5 else "low",
            "spam_score": spam_score,
            "error": str(e)
        }

def calculate_spam_score(email: Email) -> float:
    """Calculate spam score using rule-based detection"""
    score = 0.0
    
    # Check subject line
    spam_subjects = [
        'urgent', 'act now', 'limited time', 'free', 'winner', 'congratulations',
        'click here', 'buy now', 'discount', 'offer expires', 'no obligation',
        'risk free', 'satisfaction guaranteed', 'money back', 'as seen on',
        'weight loss', 'make money', 'work from home', 'get paid'
    ]
    
    subject_lower = email.subject.lower()
    for spam_word in spam_subjects:
        if spam_word in subject_lower:
            score += 0.2
    
    # Check for excessive caps
    if email.subject.isupper() and len(email.subject) > 10:
        score += 0.3
    
    # Check for excessive punctuation
    if email.subject.count('!') > 2 or email.subject.count('?') > 2:
        score += 0.2
    
    # Check sender patterns
    sender_lower = email.sender.lower()
    
    # Suspicious sender patterns
    if any(pattern in sender_lower for pattern in ['noreply', 'no-reply', 'donotreply']):
        score += 0.1
    
    # Random character patterns
    if len([c for c in email.sender if c.isdigit()]) > len(email.sender) * 0.3:
        score += 0.3
    
    # Check content
    if email.snippet:
        content_lower = email.snippet.lower()
        spam_phrases = [
            'click here', 'act now', 'limited time', 'expires soon',
            'unsubscribe', 'remove me', 'opt out', 'viagra', 'cialis',
            'lose weight', 'make money fast', 'work from home',
            'congratulations you have won', 'claim your prize'
        ]
        
        for phrase in spam_phrases:
            if phrase in content_lower:
                score += 0.15
    
    # Cap the score at 1.0
    return min(score, 1.0)

def analyze_sender_patterns(db: Session, sender: str) -> dict:
    """Analyze sender patterns for risk assessment"""
    # Get all emails from this sender
    sender_emails = db.query(Email).filter(Email.sender == sender).all()
    
    if not sender_emails:
        return {"risk": "unknown", "email_count": 0}
    
    total_emails = len(sender_emails)
    spam_count = sum(1 for email in sender_emails if email.is_spam)
    spam_ratio = spam_count / total_emails if total_emails > 0 else 0
    
    # Calculate risk level
    if spam_ratio > 0.8:
        risk = "high"
    elif spam_ratio > 0.4:
        risk = "medium"
    else:
        risk = "low"
    
    return {
        "risk": risk,
        "email_count": total_emails,
        "spam_count": spam_count,
        "spam_ratio": spam_ratio,
        "first_seen": min(email.received_date for email in sender_emails if email.received_date),
        "last_seen": max(email.received_date for email in sender_emails if email.received_date)
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
    # Get spam emails
    spam_emails = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.is_spam == True
    ).all()
    
    # Get Gmail IDs for Gmail API operations
    gmail_ids = [email.gmail_id for email in spam_emails if email.gmail_id]
    
    # Move to trash in Gmail
    if gmail_ids:
        gmail_service = GmailService(current_user)
        gmail_service.batch_modify_messages(gmail_ids, add_label_ids=["TRASH"], remove_label_ids=["INBOX"])
    
    # Update local database
    spam_count = len(spam_emails)
    for email in spam_emails:
        email.is_deleted = True
        if "TRASH" not in email.labels:
            email.labels = list(set(email.labels + ["TRASH"]))
        if "INBOX" in email.labels:
            email.labels.remove("INBOX")
    
    db.commit()
    
    return {"deleted_count": spam_count}

# Sender Management Routes
@router.get("/senders/analysis")
async def analyze_senders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze all senders for risk patterns"""
    
    # Get all unique senders for this user
    senders = db.query(Email.sender).filter(
        Email.user_id == current_user.id
    ).distinct().all()
    
    sender_analysis = []
    
    for (sender,) in senders:
        analysis = analyze_sender_patterns(db, sender)
        sender_analysis.append({
            "sender": sender,
            **analysis
        })
    
    # Sort by risk level and spam ratio
    sender_analysis.sort(key=lambda x: (
        {"high": 3, "medium": 2, "low": 1, "unknown": 0}[x["risk"]],
        x.get("spam_ratio", 0)
    ), reverse=True)
    
    return {
        "senders": sender_analysis,
        "total_senders": len(sender_analysis),
        "high_risk_count": sum(1 for s in sender_analysis if s["risk"] == "high"),
        "medium_risk_count": sum(1 for s in sender_analysis if s["risk"] == "medium")
    }

@router.post("/senders/flag")
async def flag_sender(
    sender: str,
    flag_type: str,  # whitelist, blacklist, spam
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Flag a sender as whitelist, blacklist, or spam"""
    
    from models import SenderFlag
    
    # Check if flag already exists
    existing_flag = db.query(SenderFlag).filter(
        SenderFlag.user_id == current_user.id,
        SenderFlag.sender == sender
    ).first()
    
    if existing_flag:
        # Update existing flag
        existing_flag.flag_type = flag_type
        existing_flag.user_confirmed = True
        existing_flag.flagged_at = datetime.utcnow()
    else:
        # Create new flag
        analysis = analyze_sender_patterns(db, sender)
        
        new_flag = SenderFlag(
            user_id=current_user.id,
            sender=sender,
            flag_type=flag_type,
            risk_level=analysis.get("risk", "unknown"),
            confidence=0.9,  # High confidence for user actions
            total_emails=analysis.get("email_count", 0),
            spam_emails=analysis.get("spam_count", 0),
            spam_ratio=analysis.get("spam_ratio", 0.0),
            first_seen=analysis.get("first_seen"),
            last_seen=analysis.get("last_seen"),
            user_confirmed=True
        )
        
        db.add(new_flag)
    
    # Update all emails from this sender based on flag
    if flag_type == "spam" or flag_type == "blacklist":
        db.query(Email).filter(
            Email.user_id == current_user.id,
            Email.sender == sender
        ).update({
            "is_spam": True,
            "spam_reason": f"User flagged sender as {flag_type}"
        })
    elif flag_type == "whitelist":
        db.query(Email).filter(
            Email.user_id == current_user.id,
            Email.sender == sender
        ).update({
            "is_spam": False,
            "spam_reason": None
        })
    
    db.commit()
    
    return {
        "message": f"Sender {sender} flagged as {flag_type}",
        "sender": sender,
        "flag_type": flag_type
    }

@router.get("/senders/flags")
async def get_sender_flags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all sender flags for the user"""
    
    from models import SenderFlag
    
    flags = db.query(SenderFlag).filter(
        SenderFlag.user_id == current_user.id
    ).order_by(SenderFlag.flagged_at.desc()).all()
    
    return {
        "flags": [
            {
                "id": flag.id,
                "sender": flag.sender,
                "flag_type": flag.flag_type,
                "risk_level": flag.risk_level,
                "total_emails": flag.total_emails,
                "spam_emails": flag.spam_emails,
                "spam_ratio": flag.spam_ratio,
                "flagged_at": flag.flagged_at.isoformat() if flag.flagged_at else None,
                "user_confirmed": flag.user_confirmed
            }
            for flag in flags
        ],
        "total_flags": len(flags),
        "whitelist_count": sum(1 for f in flags if f.flag_type == "whitelist"),
        "blacklist_count": sum(1 for f in flags if f.flag_type == "blacklist"),
        "spam_count": sum(1 for f in flags if f.flag_type == "spam")
    }

@router.delete("/senders/flags/{flag_id}")
async def remove_sender_flag(
    flag_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a sender flag"""
    
    from models import SenderFlag
    
    flag = db.query(SenderFlag).filter(
        SenderFlag.id == flag_id,
        SenderFlag.user_id == current_user.id
    ).first()
    
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    
    sender = flag.sender
    db.delete(flag)
    db.commit()
    
    return {
        "message": f"Flag removed for sender {sender}",
        "sender": sender
    }

# Bulk Operations Routes
from typing import List
from pydantic import BaseModel
from gmail import GmailService

class BulkRequest(BaseModel):
    email_ids: List[str]
    permanent: bool = False

class SingleEmailRequest(BaseModel):
    email_id: str

@router.post("/bulk/delete")
async def bulk_delete(
    request: BulkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk delete emails"""
    if not request.email_ids or len(request.email_ids) > 1000:
        raise HTTPException(status_code=400, detail="Invalid email IDs")
    
    try:
        count = 0
        gmail_ids = []
        emails_to_update = []
        
        # First collect all emails and their Gmail IDs
        for email_id in request.email_ids:
            email = db.query(Email).filter(
                Email.id == email_id,
                Email.user_id == current_user.id
            ).first()
            if email:
                if email.gmail_id:
                    gmail_ids.append(email.gmail_id)
                emails_to_update.append(email)
                count += 1
        
        # Process Gmail API operations
        gmail_service = GmailService(current_user)
        if gmail_ids:
            if request.permanent:
                success = gmail_service.batch_delete_messages(gmail_ids)
                if not success:
                    raise HTTPException(status_code=502, detail="Failed to delete messages in Gmail")
            else:
                success = gmail_service.batch_modify_messages(gmail_ids, add_label_ids=["TRASH"], remove_label_ids=["INBOX"])
                if not success:
                    raise HTTPException(status_code=502, detail="Failed to move messages to trash in Gmail")
        
        # Update local database
        for email in emails_to_update:
            if request.permanent:
                db.delete(email)
            else:
                email.is_deleted = True
                if "TRASH" not in email.labels:
                    email.labels = list(set(email.labels + ["TRASH"]))
                if "INBOX" in email.labels:
                    email.labels.remove("INBOX")
        
        db.commit()
        return {"message": f"Deleted {count} emails", "count": count}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk/archive")
async def bulk_archive(
    request: BulkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk archive emails"""
    if not request.email_ids or len(request.email_ids) > 1000:
        raise HTTPException(status_code=400, detail="Invalid email IDs")
    
    try:
        count = 0
        gmail_ids = []
        emails_to_update = []
        
        # First collect all emails and their Gmail IDs
        for email_id in request.email_ids:
            email = db.query(Email).filter(
                Email.id == email_id,
                Email.user_id == current_user.id
            ).first()
            if email:
                if email.gmail_id:
                    gmail_ids.append(email.gmail_id)
                emails_to_update.append(email)
                count += 1
        
        # Process Gmail API operations
        gmail_service = GmailService(current_user)
        if gmail_ids:
            success = gmail_service.batch_modify_messages(gmail_ids, remove_label_ids=["INBOX"])
            if not success:
                raise HTTPException(status_code=502, detail="Failed to archive messages in Gmail")
        
        # Update local database
        for email in emails_to_update:
            email.is_archived = True
            if "INBOX" in email.labels:
                email.labels.remove("INBOX")
        
        db.commit()
        return {"message": f"Archived {count} emails", "count": count}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email/delete")
async def delete_email(
    request: SingleEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a single email (move to trash)"""
    try:
        email = db.query(Email).filter(
            Email.id == request.email_id,
            Email.user_id == current_user.id
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
            
        # Move to trash in Gmail
        gmail_service = GmailService(current_user)
        if email.gmail_id:
            success = gmail_service.trash_message(email.gmail_id)
            if not success:
                raise HTTPException(status_code=502, detail="Failed to move message to trash in Gmail")
        
        # Update local database
        email.is_deleted = True
        if "TRASH" not in email.labels:
            email.labels = list(set(email.labels + ["TRASH"]))
        if "INBOX" in email.labels:
            email.labels.remove("INBOX")
        
        db.commit()
        return {"message": "Email moved to trash", "email_id": request.email_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
@router.post("/email/archive")
async def archive_email(
    request: SingleEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive a single email (remove from inbox)"""
    try:
        email = db.query(Email).filter(
            Email.id == request.email_id,
            Email.user_id == current_user.id
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
            
        # Archive in Gmail
        gmail_service = GmailService(current_user)
        if email.gmail_id:
            success = gmail_service.archive_message(email.gmail_id)
            if not success:
                raise HTTPException(status_code=502, detail="Failed to archive message in Gmail")
        
        # Update local database
        email.is_archived = True
        if "INBOX" in email.labels:
            email.labels.remove("INBOX")
        
        db.commit()
        return {"message": "Email archived", "email_id": request.email_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk/classify")
async def bulk_classify(
    request: BulkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk classify emails"""
    if not request.email_ids or len(request.email_ids) > 500:
        raise HTTPException(status_code=400, detail="Invalid email IDs")
    
    try:
        count = 0
        for email_id in request.email_ids:
            email = db.query(Email).filter(
                Email.id == email_id,
                Email.user_id == current_user.id,
                Email.is_processed == False
            ).first()
            
            if email:
                result = classify_email(email)
                email.category = result.get("category", "unknown")
                email.confidence_score = result.get("confidence", 0.0)
                email.is_spam = result.get("is_spam", False)
                email.spam_reason = result.get("spam_reason", "")
                email.sender_risk = result.get("sender_risk", "low")
                email.spam_score = result.get("spam_score", 0.0)
                email.is_processed = True
                count += 1
        
        db.commit()
        return {"message": f"Classified {count} emails", "count": count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Export router
ai_router = router