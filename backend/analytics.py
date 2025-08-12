"""
ScrapIt - Analytics Module
Provides detailed analytics and time-series data for email management
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, or_, case
from database import get_db
from models import Email, User
from gmail import GmailService
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
    days: int = Query(7, description="Number of days to analyze; use 0 for lifetime"),
    tz_offset: int = Query(0, description="Client timezone offset in minutes (Date.getTimezoneOffset())"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for the selected period. days=0 means lifetime."""
    end_date = datetime.now()
    start_date = None if days <= 0 else (end_date - timedelta(days=days))
    
    # Base query for user's emails
    base_query = db.query(Email).filter(Email.user_id == current_user.id)
    period_query = base_query if start_date is None else base_query.filter(Email.received_date >= start_date)
    
    # Totals
    period_emails = period_query.count()
    spam_emails = period_query.filter(Email.is_spam == True).count()
    # Unprocessed: no category and (no labels or empty)
    unprocessed_emails = period_query.filter(
        Email.category.is_(None),
        or_(Email.labels.is_(None), Email.labels == [])
    ).count()
    
    # Time-series data
    daily_stats = []
    if start_date is None:
        # Lifetime: aggregate monthly
        ym_expr = func.strftime('%Y-%m', Email.received_date)
        months = db.query(
            ym_expr.label('ym'),
            func.count(Email.id).label('cnt'),
            func.sum(case((Email.is_spam == True, 1), else_=0)).label('spam')
        ).filter(Email.user_id == current_user.id).group_by(ym_expr).order_by(ym_expr).all()
        for m in months:
            daily_stats.append({
                "date": f"{m.ym}-01",
                "emails": int(m.cnt),
                "spam": int(m.spam or 0)
            })
    else:
        if days >= 300:
            # About a year: monthly buckets
            ym_expr = func.strftime('%Y-%m', Email.received_date)
            rows = db.query(
                ym_expr.label('ym'),
                func.count(Email.id).label('cnt'),
                func.sum(case((Email.is_spam == True, 1), else_=0)).label('spam')
            ).filter(
                Email.user_id == current_user.id,
                Email.received_date >= start_date
            ).group_by(ym_expr).order_by(ym_expr).all()
            for r in rows:
                daily_stats.append({
                    "date": f"{r.ym}-01",
                    "emails": int(r.cnt),
                    "spam": int(r.spam or 0)
                })
        elif days >= 60:
            # 2+ months: weekly buckets (Sunday-start using %W week number)
            yw_expr = func.strftime('%Y-%W', Email.received_date)
            rows = db.query(
                yw_expr.label('yw'),
                func.count(Email.id).label('cnt'),
                func.sum(case((Email.is_spam == True, 1), else_=0)).label('spam')
            ).filter(
                Email.user_id == current_user.id,
                Email.received_date >= start_date
            ).group_by(yw_expr).order_by(yw_expr).all()
            for r in rows:
                year, week = r.yw.split('-')
                # Approximate start date of week as year-week Monday
                daily_stats.append({
                    "date": f"{year}-W{week}",
                    "emails": int(r.cnt),
                    "spam": int(r.spam or 0)
                })
        else:
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
    
    # Categories: merge AI categories + user labels within period
    categories_map: Dict[str, int] = {}
    # From explicit categories
    for cat, cnt in db.query(Email.category, func.count(Email.id)).filter(
        Email.user_id == current_user.id,
        Email.category.isnot(None),
        True if start_date is None else Email.received_date >= start_date
    ).group_by(Email.category):
        name = 'Uncategorized' if (cat or '').lower() == 'unknown' else cat
        categories_map[name] = categories_map.get(name, 0) + cnt
    # From labels – approximate: count every label string seen in labels JSON
    # Build label id -> name map and limit to user labels
    label_name_by_id = {}
    user_label_ids = set()
    try:
        glabels = GmailService(current_user).get_labels()
        for lbl in glabels or []:
            label_name_by_id[lbl.get('id')] = lbl.get('name')
            if lbl.get('type') == 'user':
                user_label_ids.add(lbl.get('id'))
    except Exception:
        pass

    label_rows = db.query(Email.labels, func.count(Email.id)).filter(
        Email.user_id == current_user.id,
        Email.labels.isnot(None),
        True if start_date is None else Email.received_date >= start_date
    ).group_by(Email.labels).all()
    for labels_json, cnt in label_rows:
        try:
            for label in labels_json or []:
                if not label:
                    continue
                if label in {"UNREAD", "STARRED", "YELLOW_STAR"}:
                    continue
                # Normalize Gmail category labels
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
                # Use user label names when available, otherwise system mapping
                if label in user_label_ids:
                    name = label_name_by_id.get(label, label)
                else:
                    name = system_map.get(label, label)
                categories_map[name] = categories_map.get(name, 0) + cnt
        except Exception:
            continue
    # Build list sorted desc and consolidate small ones into 'Other'
    sorted_items = sorted(categories_map.items(), key=lambda kv: kv[1], reverse=True)
    top_items = sorted_items[:12]
    other_total = sum(v for _, v in sorted_items[12:])
    categories = [
        {
            "name": k,
            "value": v,
            "percentage": round((v / period_emails) * 100, 1) if period_emails > 0 else 0
        } for k, v in top_items
    ]
    if other_total > 0:
        categories.append({
            "name": "Other",
            "value": other_total,
            "percentage": round((other_total / period_emails) * 100, 1) if period_emails > 0 else 0
        })
    
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
    
    # Processing efficiency (functional)
    processed_emails = max(period_emails - unprocessed_emails, 0)
    processing_rate = round((processed_emails / period_emails) * 100, 1) if period_emails > 0 else 0
    label_coverage = round((db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.labels.isnot(None),
        True if start_date is None else Email.received_date >= start_date
    ).count() / period_emails) * 100, 1) if period_emails > 0 else 0
    
    # Recent activity (last 24 hours)
    recent_cutoff = datetime.now() - timedelta(hours=24)
    # Our Email model doesn't have processed_date; approximate using received_date
    recent_processed = base_query.filter(
        Email.received_date >= recent_cutoff
    ).count()
    
    recent_spam_deleted = base_query.filter(
        and_(
            Email.is_spam == True,
            Email.received_date >= recent_cutoff
        )
    ).count()
    
    return {
        "summary": {
            "period_emails": period_emails,
            "spam_emails": spam_emails,
            "unprocessed_emails": unprocessed_emails,
            "processed_emails": processed_emails,
            "processing_rate": processing_rate,
            "label_coverage": label_coverage,
            "period_days": 0 if start_date is None else days
        },
        "time_series": {
            "daily_volume": daily_stats,
            "period_days": days
        },
        "categories": categories,
        "top_senders": [],
        "efficiency": {
            "processed_rate": processing_rate,
            "label_coverage": label_coverage,
            "recent_processed": recent_processed,
            "recent_spam_deleted": recent_spam_deleted
        },
        "insights": {
            "peak_email_hour": _peak_hour(period_query, tz_offset),
            "busiest_day": _busiest_day(period_query, tz_offset),
            "weekend_percentage": _weekend_pct(period_query, tz_offset)
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
    
    # Recent activity by most recent emails, infer action
    recent_items = db.query(Email).filter(
        Email.user_id == current_user.id
    ).order_by(desc(Email.received_date)).limit(limit).all()
    
    activities = []
    for email in recent_items:
        if email.is_deleted:
            activity_type = "deleted"
        elif email.is_spam:
            activity_type = "spam_deleted"
        elif email.category or (email.labels and len(email.labels) > 0):
            activity_type = "classified"
        else:
            activity_type = "received"
        
        activities.append({
            "type": activity_type,
            "description": (
                f"Deleted email from {email.sender[:30]}{'...' if len(email.sender) > 30 else ''}" if activity_type == 'deleted' else
                f"Deleted spam email from {email.sender[:30]}{'...' if len(email.sender) > 30 else ''}" if activity_type == 'spam_deleted' else
                f"Classified email from {email.sender[:30]}{'...' if len(email.sender) > 30 else ''}" if activity_type == 'classified' else
                f"Received email from {email.sender[:30]}{'...' if len(email.sender) > 30 else ''}"
            ),
            "category": email.category,
            "timestamp": email.received_date.isoformat() if email.received_date else None,
            "time_ago": _get_time_ago(email.received_date) if email.received_date else "Unknown"
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

def _peak_hour(query, tz_offset_minutes: int) -> str:
    hours = [
        (h, query.filter(func.strftime('%H', Email.received_date) == f"{h:02d}").count())
        for h in range(24)
    ]
    if not hours:
        return "-"
    # shift by client offset (minutes east negative getTimezoneOffset)
    shift = -int(tz_offset_minutes // 60)
    shifted = [((h + shift) % 24, c) for h, c in hours]
    best = max(shifted, key=lambda x: x[1])[0]
    hour12 = (best % 12) or 12
    ampm = "AM" if best < 12 else "PM"
    return f"{hour12}:00 {ampm}"

def _busiest_day(query, tz_offset_minutes: int) -> str:
    days = [
        (d, query.filter(func.strftime('%w', Email.received_date) == str(d)).count()) for d in range(7)
    ]
    if not days:
        return "-"
    # shift by number of days due to timezone offset (round hours/24)
    shift_days = -int(round(tz_offset_minutes / 60 / 24))
    shifted = [(((d + shift_days) % 7), c) for d, c in days]
    names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return names[max(shifted, key=lambda x: x[1])[0]]

def _weekend_pct(query, tz_offset_minutes: int) -> int:
    total = query.count()
    if total == 0:
        return 0
    weekend = query.filter(or_(func.strftime('%w', Email.received_date) == '0', func.strftime('%w', Email.received_date) == '6')).count()
    return int(round((weekend / total) * 100))