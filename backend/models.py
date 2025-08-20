"""
Database Models - Consolidated
User, Email, and Task models with encryption support
"""
import os
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Float, ForeignKey, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from cryptography.fernet import Fernet

Base = declarative_base()

# Encryption setup
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if ENCRYPTION_KEY:
    try:
        # Use the key from environment (should be base64 encoded)
        cipher_suite = Fernet(ENCRYPTION_KEY.encode())
    except Exception as e:
        print(f"Warning: Invalid encryption key, using fallback: {e}")
        cipher_suite = None
else:
    print("Warning: No ENCRYPTION_KEY found, tokens will be stored in plaintext")
    cipher_suite = None

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    google_id = Column(String(255), unique=True, nullable=False)
    access_token = Column(Text)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    emails = relationship("Email", back_populates="user")
    sender_flags = relationship("SenderFlag", back_populates="user")
    
    def set_access_token(self, token: str):
        """Encrypt and store access token"""
        if cipher_suite and token:
            self.access_token = cipher_suite.encrypt(token.encode()).decode()
        else:
            self.access_token = token
    
    def get_access_token(self) -> str:
        """Decrypt and return access token"""
        if cipher_suite and self.access_token:
            try:
                return cipher_suite.decrypt(self.access_token.encode()).decode()
            except:
                return self.access_token
        return self.access_token or ""
    
    def set_refresh_token(self, token: str):
        """Encrypt and store refresh token"""
        if cipher_suite and token:
            self.refresh_token = cipher_suite.encrypt(token.encode()).decode()
        else:
            self.refresh_token = token
    
    def get_refresh_token(self) -> str:
        """Decrypt and return refresh token"""
        if cipher_suite and self.refresh_token:
            try:
                return cipher_suite.decrypt(self.refresh_token.encode()).decode()
            except:
                return self.refresh_token
        return self.refresh_token or ""

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    gmail_id = Column(String(255), unique=True, nullable=False)
    
    # Email content
    subject = Column(String(1000))
    sender = Column(String(500))
    recipient = Column(String(500))
    content = Column(Text)  # Full email content
    snippet = Column(String(500))  # Preview text
    
    # Metadata
    received_date = Column(DateTime)
    labels = Column(JSON)  # Gmail labels
    
    # AI Classification
    category = Column(String(100))  # work, personal, spam, etc.
    confidence_score = Column(Float)  # AI confidence 0-1
    spam_score = Column(Float)  # Rule-based spam score 0-1
    spam_reason = Column(String(500))  # Why it's considered spam
    sender_risk = Column(String(20))  # low, medium, high
    
    # Status flags
    is_spam = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emails")

class SenderFlag(Base):
    """Track flagged senders and their risk levels"""
    __tablename__ = "sender_flags"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    sender = Column(String(500), nullable=False)
    
    # Flag details
    flag_type = Column(String(20))  # whitelist, blacklist, spam
    risk_level = Column(String(20))  # low, medium, high
    confidence = Column(Float)  # How confident we are in this flag
    
    # Statistics
    total_emails = Column(Integer, default=0)
    spam_emails = Column(Integer, default=0)
    spam_ratio = Column(Float, default=0.0)
    
    # Timestamps
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    flagged_at = Column(DateTime, default=datetime.utcnow)
    
    # User action
    user_confirmed = Column(Boolean, default=False)  # User manually confirmed this flag
    
    # Relationships
    user = relationship("User", back_populates="sender_flags")

# Task model for tracking multi-step operations
class Task(Base):
    """Track complex multi-step tasks for email management"""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Task details
    type = Column(String(50))  # email_cleanup, email_organization, etc.
    description = Column(String(500))
    status = Column(String(20))  # pending, in_progress, completed, failed, cancelled
    steps = Column(JSON)  # List of steps with their status
    priority = Column(Integer, default=1)  # 1 (highest) to 5 (lowest)
    
    # Progress tracking
    progress = Column(Integer, default=0)  # 0-100%
    result = Column(JSON, nullable=True)  # Results from completed task
    error = Column(String(1000), nullable=True)  # Error message if failed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="tasks")