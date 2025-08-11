"""
ScrapIt - Analytics Module
Provides detailed analytics and time-series data for email management
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from database import get_db
from models import Email, User
from auth import get_current_user

router = APIRouter()

@router.get("/test")
async def test_analytics():
    """Simple test endpoint to verify analytics module is working"""
    return {
        "message": "Analytics API is working!",
        "timestamp": datetime.now().isoformat(),
        "endpoints": ["/overview", "/trends", "/activity"]
    }

@router.get("/overview")
async def get_analytics_overview(
    days: int = Query(7, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics overview with time-series data"""
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Base query for user's emails
    base_query = db.query(Email).filter(Email.user_id == current_user.id)
    
    # Total stats
    total_emails = base_query.count()
    spam_emails = base_query.filter(Email.is_spam == True).count()
    unprocessed_emails = base_query.filter(Email.is_processed == False).count()
    
    # Time-series data (daily email volume)
    daily_stats = []
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        day_total = base_query.filter(
            and_(
                Email.received_date >= day_start,
                Email.received_date < day_end
            )
        ).count()
        
        day_spam = base_query.filter(
            and_(
                Email.received_date >= day_start,
                Email.received_date < day_end,
                Email.is_spam == True
            )
        ).count()
        
        daily_stats.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "emails": day_total,
            "spam": day_spam
        })
    
    # Category distribution
    category_stats = db.query(
        Email.category,
        func.count(Email.id).label('count')
    ).filter(
        Email.user_id == current_user.id,
        Email.category.isnot(None)
    ).group_by(Email.category).all()
    
    categories = [
        {
            "name": cat.category.title() if cat.category else "Uncategorized",
            "value": cat.count,
            "percentage": round((cat.count / total_emails) * 100, 1) if total_emails > 0 else 0
        }
        for cat in category_stats
    ]
    
    # Top senders
    sender_stats = db.query(
        Email.sender,
        func.count(Email.id).label('count')
    ).filter(
        Email.user_id == current_user.id
    ).group_by(Email.sender).order_by(desc('count')).limit(10).all()
    
    top_senders = [
        {
            "name": sender.sender[:50] + "..." if len(sender.sender) > 50 else sender.sender,
            "emails": sender.count
        }
        for sender in sender_stats
    ]
    
    # Processing efficiency
    processed_emails = total_emails - unprocessed_emails
    processing_rate = round((processed_emails / total_emails) * 100, 1) if total_emails > 0 else 0
    spam_detection_rate = round((spam_emails / total_emails) * 100, 1) if total_emails > 0 else 0
    
    # Recent activity (last 24 hours)
    recent_cutoff = datetime.now() - timedelta(hours=24)
    recent_processed = base_query.filter(
        Email.processed_date >= recent_cutoff
    ).count() if base_query.filter(Email.processed_date.isnot(None)).count() > 0 else 0
    
    recent_spam_deleted = base_query.filter(
        and_(
            Email.is_spam == True,
            Email.processed_date >= recent_cutoff
        )
    ).count() if base_query.filter(Email.processed_date.isnot(None)).count() > 0 else 0
    
    return {
        "summary": {
            "total_emails": total_emails,
            "spam_emails": spam_emails,
            "unprocessed_emails": unprocessed_emails,
            "processing_rate": processing_rate,
            "spam_detection_rate": spam_detection_rate,
            "avg_daily_emails": round(total_emails / max(days, 1), 1)
        },
        "time_series": {
            "daily_volume": daily_stats,
            "period_days": days
        },
        "categories": categories,
        "top_senders": top_senders,
        "efficiency": {
            "processing_accuracy": processing_rate,
            "spam_detection_accuracy": spam_detection_rate,
            "recent_processed": recent_processed,
            "recent_spam_deleted": recent_spam_deleted
        },
        "insights": {
            "peak_email_hour": "9:00 AM",  # Could be calculated from actual data
            "busiest_day": "Tuesday",      # Could be calculated from actual data
            "avg_response_time": "2.3 hours",  # Placeholder
            "weekend_percentage": 12        # Placeholder
        }
    }

@router.get("/trends")
async def get_email_trends(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email trends and patterns over time"""
    
    # Parse period
    period_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365
    }
    
    days = period_map.get(period, 30)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Base query
    base_query = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.received_date >= start_date
    )
    
    # Weekly aggregation for longer periods
    if days > 30:
        # Group by week
        weekly_stats = []
        weeks = days // 7
        
        for i in range(weeks):
            week_start = start_date + timedelta(weeks=i)
            week_end = week_start + timedelta(weeks=1)
            
            week_total = base_query.filter(
                and_(
                    Email.received_date >= week_start,
                    Email.received_date < week_end
                )
            ).count()
            
            week_spam = base_query.filter(
                and_(
                    Email.received_date >= week_start,
                    Email.received_date < week_end,
                    Email.is_spam == True
                )
            ).count()
            
            weekly_stats.append({
                "period": week_start.strftime("%Y-W%U"),
                "start_date": week_start.strftime("%Y-%m-%d"),
                "emails": week_total,
                "spam": week_spam,
                "spam_rate": round((week_spam / week_total) * 100, 1) if week_total > 0 else 0
            })
        
        return {
            "period": period,
            "granularity": "weekly",
            "data": weekly_stats
        }
    else:
        # Daily aggregation for shorter periods
        daily_stats = []
        
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_total = base_query.filter(
                and_(
                    Email.received_date >= day_start,
                    Email.received_date < day_end
                )
            ).count()
            
            day_spam = base_query.filter(
                and_(
                    Email.received_date >= day_start,
                    Email.received_date < day_end,
                    Email.is_spam == True
                )
            ).count()
            
            daily_stats.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "emails": day_total,
                "spam": day_spam,
                "spam_rate": round((day_spam / day_total) * 100, 1) if day_total > 0 else 0
            })
        
        return {
            "period": period,
            "granularity": "daily", 
            "data": daily_stats
        }

@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(10, description="Number of recent activities to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent email processing activity"""
    
    # Get recently processed emails
    recent_processed = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.processed_date.isnot(None)
    ).order_by(desc(Email.processed_date)).limit(limit).all()
    
    activities = []
    for email in recent_processed:
        activity_type = "spam_deleted" if email.is_spam else "classified"
        
        activities.append({
            "type": activity_type,
            "description": f"{'Deleted spam email' if email.is_spam else 'Classified email'} from {email.sender[:30]}{'...' if len(email.sender) > 30 else ''}",
            "category": email.category,
            "timestamp": email.processed_date.isoformat() if email.processed_date else None,
            "time_ago": _get_time_ago(email.processed_date) if email.processed_date else "Unknown"
        })
    
    return {
        "activities": activities,
        "total_count": len(activities)
    }

def _get_time_ago(timestamp: datetime) -> str:
    """Convert timestamp to human-readable time ago format"""
    if not timestamp:
        return "Unknown"
    
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"