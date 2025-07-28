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
        # TODO: Implement text extraction
        # Remove HTML tags
        # Clean up formatting
        # Return plain text
        pass
    
    def get_sender_domain(self) -> str:
        """
        Extract domain from sender email address
        
        Returns:
            Domain part of sender email
        """
        # TODO: Implement domain extraction
        # Parse email address
        # Extract domain part
        # Handle edge cases
        pass
    
    def get_sender_name(self) -> Optional[str]:
        """
        Extract sender name from email address
        
        Returns:
            Sender display name or None
        """
        # TODO: Implement name extraction
        # Parse "Name <email@domain.com>" format
        # Return display name
        pass
    
    def is_promotional(self) -> bool:
        """
        Check if email has promotional indicators
        
        Returns:
            True if email appears promotional
        """
        # TODO: Implement promotional detection
        # Check for promotional keywords
        # Analyze sender patterns
        # Check labels for promotional indicators
        pass
    
    def has_attachments(self) -> bool:
        """
        Check if email has attachments
        
        Returns:
            True if email has attachments
        """
        # TODO: Implement attachment detection
        # Check Gmail labels or metadata
        # Return attachment status
        pass
    
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
        # TODO: Implement serialization
        # Convert all fields to dict
        # Handle datetime serialization
        # Include computed fields
        pass
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Email(id={self.id}, sender={self.sender}, subject={self.subject[:50]}...)>"