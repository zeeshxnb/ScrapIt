"""
Database Models - Consolidated
All database models for ScrapIt
"""
import uuid
import os
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from cryptography.fernet import Fernet

Base = declarative_base()

# Encryption for sensitive data
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

class User(Base):
    """User with encrypted OAuth tokens"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    google_id = Column(String(255), unique=True, index=True, nullable=False)
    access_token = Column(Text, nullable=False)  # Encrypted
    refresh_token = Column(Text, nullable=False)  # Encrypted
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    emails = relationship("Email", back_populates="user")
    
    def set_access_token(self, token: str):
        self.access_token = cipher_suite.encrypt(token.encode()).decode()
    
    def get_access_token(self) -> str:
        return cipher_suite.decrypt(self.access_token.encode()).decode()
    
    def set_refresh_token(self, token: str):
        self.refresh_token = cipher_suite.encrypt(token.encode()).decode()
    
    def get_refresh_token(self) -> str:
        return cipher_suite.decrypt(self.refresh_token.encode()).decode()

class Email(Base):
    """Email with AI classification"""
    __tablename__ = "emails"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    gmail_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Email content
    subject = Column(String(1000), nullable=True)
    sender = Column(String(500), nullable=False, index=True)
    recipient = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    snippet = Column(String(500), nullable=True)
    received_date = Column(DateTime, nullable=False, index=True)
    labels = Column(JSON, nullable=True)
    
    # AI classification
    category = Column(String(100), nullable=True, index=True)
    confidence_score = Column(Float, nullable=True)
    is_spam = Column(Boolean, default=False, index=True)
    is_processed = Column(Boolean, default=False, index=True)
    
    # Status flags
    is_deleted = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emails")
    
    def __init__(self, user_id: str, gmail_id: str, **kwargs):
        self.user_id = user_id
        self.gmail_id = gmail_id
        for key, value in kwargs.items():
            setattr(self, key, value)