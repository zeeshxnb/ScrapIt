"""
Sender Tracking Model

SQLAlchemy model for tracking email senders and their reputation
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
import uuid
from typing import Dict, Optional, List
import re

Base = declarative_base()

class Sender(Base):
    """Sender model for tracking email senders and reputation"""
    
    __tablename__ = "senders"
    
    # Primary key and relationships
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Sender identification
    email_address = Column(String(500), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    display_name = Column(String(500), nullable=True)
    
    # Email statistics
    total_emails = Column(Integer, default=0, nullable=False)
    spam_count = Column(Integer, default=0, nullable=False)
    ham_count = Column(Integer, default=0, nullable=False)  # Legitimate emails
    
    # Reputation and flags
    reputation_score = Column(Float, default=0.5, nullable=False)  # 0.0 to 1.0
    is_whitelisted = Column(Boolean, default=False, nullable=False)
    is_blacklisted = Column(Boolean, default=False, nullable=False)
    auto_flagged = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    first_seen = Column(DateTime(timezone=True), nullable=False, default=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=False, default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    # user = relationship("User", back_populates="senders")
    # emails = relationship("Email", back_populates="sender_info")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_sender_user_email', 'user_id', 'email_address', unique=True),
        Index('idx_sender_domain_reputation', 'domain', 'reputation_score'),
        Index('idx_sender_reputation_flags', 'reputation_score', 'is_blacklisted', 'auto_flagged'),
        CheckConstraint('reputation_score >= 0.0 AND reputation_score <= 1.0', name='check_reputation_range'),
        CheckConstraint('spam_count >= 0', name='check_spam_count_positive'),
        CheckConstraint('ham_count >= 0', name='check_ham_count_positive'),
        CheckConstraint('total_emails >= spam_count + ham_count', name='check_total_emails_consistency'),
    )
    
    def __init__(self, user_id: str, email_address: str, display_name: str = None):
        """Initialize sender with required fields"""
        self.user_id = user_id
        self.email_address = email_address.lower()
        self.domain = self._extract_domain(email_address)
        self.display_name = display_name
        self.reputation_score = 0.5  # Neutral starting reputation
    
    def calculate_reputation_score(self) -> float:
        """
        Calculate reputation score based on multiple factors
        
        Returns:
            Reputation score between 0.0 and 1.0
        """
        # TODO: Implement reputation calculation
        # Factor 1: Spam ratio (lower is better)
        # Factor 2: Consistency of sending patterns
        # Factor 3: Domain reputation
        # Factor 4: User feedback history
        # Factor 5: Time since first contact (older = more trusted)
        # Factor 6: Volume patterns (sudden spikes = suspicious)
        # Combine factors with weights
        # Return normalized score
        pass
    
    def update_spam_stats(self, is_spam: bool) -> None:
        """
        Update spam statistics and recalculate reputation
        
        Args:
            is_spam: Whether the email is spam
        """
        # TODO: Implement stats update
        # Increment appropriate counter
        # Update total emails
        # Recalculate reputation score
        # Update last_seen timestamp
        # Check if auto-flagging needed
        pass
    
    def should_auto_flag(self) -> bool:
        """
        Determine if sender should be automatically flagged as spam
        
        Returns:
            True if sender should be auto-flagged
        """
        # TODO: Implement auto-flag logic
        # Check spam ratio threshold
        # Check reputation score threshold
        # Consider recent activity patterns
        # Check if already whitelisted
        # Return flagging decision
        pass
    
    def get_sending_pattern(self) -> Dict[str, any]:
        """
        Analyze sender's email sending patterns
        
        Returns:
            Dictionary with pattern analysis
        """
        # TODO: Implement pattern analysis
        # Calculate average emails per day/week
        # Identify sending time patterns
        # Analyze volume spikes
        # Check consistency over time
        # Return pattern summary
        pass
    
    def is_suspicious_sender(self) -> bool:
        """
        Check if sender exhibits suspicious behavior
        
        Returns:
            True if sender appears suspicious
        """
        # TODO: Implement suspicion detection
        # Check for suspicious domain patterns
        # Analyze email address format
        # Check reputation score
        # Look for rapid volume increases
        # Check against known spam patterns
        pass
    
    def get_spam_ratio(self) -> float:
        """
        Get ratio of spam emails to total emails
        
        Returns:
            Spam ratio between 0.0 and 1.0
        """
        if self.total_emails == 0:
            return 0.0
        return self.spam_count / self.total_emails
    
    def get_days_since_first_seen(self) -> int:
        """
        Get number of days since first email from this sender
        
        Returns:
            Days since first contact
        """
        if not self.first_seen:
            return 0
        
        now = datetime.now(timezone.utc)
        delta = now - self.first_seen
        return delta.days
    
    def is_recent_sender(self, days: int = 7) -> bool:
        """
        Check if sender is recent (first seen within specified days)
        
        Args:
            days: Number of days to consider recent
            
        Returns:
            True if sender is recent
        """
        return self.get_days_since_first_seen() <= days
    
    def update_last_seen(self) -> None:
        """Update last seen timestamp"""
        self.last_seen = datetime.now(timezone.utc)
    
    def whitelist(self) -> None:
        """Add sender to whitelist"""
        self.is_whitelisted = True
        self.is_blacklisted = False
        self.auto_flagged = False
        self.reputation_score = max(self.reputation_score, 0.8)  # Boost reputation
    
    def blacklist(self) -> None:
        """Add sender to blacklist"""
        self.is_blacklisted = True
        self.is_whitelisted = False
        self.auto_flagged = True
        self.reputation_score = min(self.reputation_score, 0.2)  # Lower reputation
    
    def reset_flags(self) -> None:
        """Reset all flags to neutral state"""
        self.is_whitelisted = False
        self.is_blacklisted = False
        self.auto_flagged = False
        self.reputation_score = 0.5  # Reset to neutral
    
    def _extract_domain(self, email_address: str) -> str:
        """Extract domain from email address"""
        # TODO: Implement domain extraction
        # Parse email address
        # Extract domain part
        # Handle edge cases
        # Return domain string
        pass
    
    def _calculate_domain_reputation(self) -> float:
        """Calculate reputation based on domain"""
        # TODO: Implement domain reputation
        # Check against known good/bad domains
        # Consider domain age and patterns
        # Return domain reputation score
        pass
    
    def _analyze_volume_patterns(self) -> Dict[str, any]:
        """Analyze email volume patterns for anomalies"""
        # TODO: Implement volume analysis
        # Query recent email history
        # Detect sudden spikes
        # Calculate normal volume ranges
        # Return pattern analysis
        pass
    
    def to_dict(self) -> Dict[str, any]:
        """
        Convert sender to dictionary for API serialization
        
        Returns:
            Dictionary representation
        """
        # TODO: Implement serialization
        # Convert all fields to dict
        # Include computed fields
        # Handle datetime serialization
        pass
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Sender(email={self.email_address}, reputation={self.reputation_score:.2f}, spam_ratio={self.get_spam_ratio():.2f})>"