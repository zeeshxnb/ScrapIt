"""
Email Database Model

SQLAlchemy model for storing email data and metadata
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, Float, Integer, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
import uuid
import re
from typing import Dict, List, Optional

Base = declarative_base()

class Email(Base):
    """Email model for storing Gmail data and AI analysis results"""
    
    __tablename__ = "emails"
    
    # Primary key and relationships
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Gmail identifiers
    gmail_id = Column(String(255), nullable=False, index=True)
    thread_id = Column(String(255), nullable=True, index=True)
    
    # Email content
    subject = Column(String(1000), nullable=True, index=True)
    sender = Column(String(500), nullable=False, index=True)
    recipient = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)  # Full email body
    snippet = Column(String(500), nullable=True)  # Email preview
    
    # Metadata
    received_date = Column(DateTime(timezone=True), nullable=False, index=True)
    labels = Column(JSON, nullable=True)  # Gmail labels array
    
    # AI Analysis results
    category = Column(String(100), nullable=True, index=True)
    confidence_score = Column(Float, nullable=True)
    is_spam = Column(Boolean, default=False, index=True)
    cluster_id = Column(Integer, nullable=True, index=True)
    
    # Processing timestamps
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    # user = relationship("User", back_populates="emails")
    # classifications = relationship("Classification", back_populates="email")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_email_user_gmail', 'user_id', 'gmail_id', unique=True),
        Index('idx_email_user_received', 'user_id', 'received_date'),
        Index('idx_email_sender_category', 'sender', 'category'),
        Index('idx_email_spam_processed', 'is_spam', 'processed_at'),
        # Full-text search indexes (PostgreSQL specific)
        # Index('idx_email_content_fts', 'content', postgresql_using='gin'),
        # Index('idx_email_subject_fts', 'subject', postgresql_using='gin'),
    )
    
    def __init__(self, user_id: str, gmail_id: str, **kwargs):
        """Initialize email with required fields"""
        self.user_id = user_id
        self.gmail_id = gmail_id
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def get_text_content(self) -> str:
        """
        Extract plain text content from email
        
        Returns:
            Plain text content without HTML tags
        """
        if not self.content:
            return ""
            
        # If content is already plain text, return it
        if "<html" not in self.content.lower() and "<body" not in self.content.lower():
            return self.content
            
        # Otherwise, try to extract text from HTML
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space
            lines = (line.strip() for line in text.splitlines())
            
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception:
            # If HTML parsing fails, return original content with basic HTML tag removal
            import re
            text = re.sub(r'<[^>]+>', ' ', self.content)
            return re.sub(r'\s+', ' ', text).strip()
    
    def get_sender_domain(self) -> str:
        """
        Extract domain from sender email address
        
        Returns:
            Domain part of sender email
        """
        if not self.sender:
            return ""
            
        try:
            # Extract email from "Name <email@domain.com>" format
            import re
            email_match = re.search(r'<([^>]+)>', self.sender)
            
            if email_match:
                email = email_match.group(1)
            else:
                # If no angle brackets, assume the whole string is an email
                email = self.sender
                
            # Extract domain part
            domain_match = re.search(r'@([^>]+)$', email)
            if domain_match:
                return domain_match.group(1).lower()
            else:
                return ""
                
        except Exception:
            return ""
    
    def get_sender_name(self) -> Optional[str]:
        """
        Extract sender name from email address
        
        Returns:
            Sender display name or None
        """
        if not self.sender:
            return None
            
        try:
            # Extract name from "Name <email@domain.com>" format
            import re
            name_match = re.match(r'^([^<]+)<', self.sender)
            
            if name_match:
                name = name_match.group(1).strip()
                return name if name else None
            else:
                # If no angle brackets, check if it's just an email
                if '@' in self.sender:
                    return None
                else:
                    return self.sender.strip()
                    
        except Exception:
            return None
    
    def is_promotional(self) -> bool:
        """
        Check if email has promotional indicators
        
        Returns:
            True if email appears promotional
        """
        if not self.subject and not self.content and not self.labels:
            return False
            
        # Check labels first (most reliable)
        if self.labels and isinstance(self.labels, list):
            promo_labels = ['CATEGORY_PROMOTIONS', 'CATEGORY_MARKETING']
            if any(label in self.labels for label in promo_labels):
                return True
                
        # Check for promotional keywords in subject
        if self.subject:
            promo_keywords = [
                'offer', 'sale', 'discount', 'deal', 'promo', 'promotion', 
                'subscribe', 'newsletter', 'off', 'save', 'limited time',
                'exclusive', 'free', 'buy', 'shop', 'click', 'order now'
            ]
            
            subject_lower = self.subject.lower()
            if any(keyword in subject_lower for keyword in promo_keywords):
                return True
                
        # Check sender domain against common marketing domains
        domain = self.get_sender_domain()
        if domain:
            marketing_domains = [
                'mailchimp.com', 'sendgrid.net', 'campaign-', 'marketing',
                'newsletter', 'info@', 'noreply@', 'promotions', 'offers'
            ]
            
            if any(marker in domain for marker in marketing_domains):
                return True
                
        # Check content for promotional patterns
        if self.content:
            content_sample = self.content[:1000].lower()  # Check first 1000 chars for performance
            
            # Look for call-to-action phrases
            cta_phrases = [
                'click here', 'learn more', 'sign up', 'subscribe', 'buy now',
                'limited time', 'special offer', 'discount', 'unsubscribe'
            ]
            
            if any(phrase in content_sample for phrase in cta_phrases):
                return True
                
        return False
    
    def has_attachments(self) -> bool:
        """
        Check if email has attachments
        
        Returns:
            True if email has attachments
        """
        # Check labels for attachment indicators
        if self.labels and isinstance(self.labels, list):
            if 'HAS_ATTACHMENT' in self.labels:
                return True
                
        # Check content for attachment indicators
        if self.content:
            attachment_indicators = [
                'Content-Disposition: attachment',
                'filename=',
                'Content-Type: application/'
            ]
            
            for indicator in attachment_indicators:
                if indicator in self.content:
                    return True
                    
        return False
    
    def get_age_days(self) -> int:
        """
        Get email age in days
        
        Returns:
            Number of days since email was received
        """
        if not self.received_date:
            return 0
        
        now = datetime.now(timezone.utc)
        delta = now - self.received_date
        return delta.days
    
    def is_recent(self, days: int = 7) -> bool:
        """
        Check if email is recent
        
        Args:
            days: Number of days to consider recent
            
        Returns:
            True if email is within specified days
        """
        return self.get_age_days() <= days
    
    def update_classification(self, category: str, confidence: float, is_spam: bool = False) -> None:
        """
        Update AI classification results
        
        Args:
            category: Email category
            confidence: Classification confidence score
            is_spam: Whether email is spam
        """
        self.category = category
        self.confidence_score = confidence
        self.is_spam = is_spam
        self.processed_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict:
        """
        Convert email to dictionary for API serialization
        
        Returns:
            Dictionary representation of email
        """
        # Format datetime objects
        received_date_str = None
        if self.received_date:
            received_date_str = self.received_date.isoformat()
            
        processed_at_str = None
        if self.processed_at:
            processed_at_str = self.processed_at.isoformat()
            
        created_at_str = None
        if self.created_at:
            created_at_str = self.created_at.isoformat()
        
        # Create base dictionary
        result = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "gmail_id": self.gmail_id,
            "thread_id": self.thread_id,
            "subject": self.subject,
            "sender": self.sender,
            "recipient": self.recipient,
            "snippet": self.snippet,
            "received_date": received_date_str,
            "labels": self.labels,
            "category": self.category,
            "confidence_score": self.confidence_score,
            "is_spam": self.is_spam,
            "cluster_id": self.cluster_id,
            "processed_at": processed_at_str,
            "created_at": created_at_str,
        }
        
        # Add computed fields
        result["sender_domain"] = self.get_sender_domain()
        result["sender_name"] = self.get_sender_name()
        result["is_promotional"] = self.is_promotional()
        result["has_attachments"] = self.has_attachments()
        result["age_days"] = self.get_age_days()
        
        # Don't include full content by default (can be large)
        # Add a preview instead
        if self.content:
            preview_length = 500
            content_preview = self.content[:preview_length]
            if len(self.content) > preview_length:
                content_preview += "..."
            result["content_preview"] = content_preview
        else:
            result["content_preview"] = None
            
        return result
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Email(id={self.id}, sender={self.sender}, subject={self.subject[:50]}...)>"