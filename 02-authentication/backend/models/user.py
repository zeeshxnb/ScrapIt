"""
User Database Model

SQLAlchemy model for user authentication and profile data
"""
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from cryptography.fernet import Fernet
from datetime import datetime, timezone
import uuid
import os
from pydantic import BaseModel
from typing import Optional

Base = declarative_base()

class UserDB(Base):
    """User model for authentication and profile data"""
    
    __tablename__ = "users"
    
    # Primary key and identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    google_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Encrypted OAuth tokens
    access_token = Column(String(1000), nullable=True)  # Encrypted
    refresh_token = Column(String(1000), nullable=True)  # Encrypted
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_google_id', 'google_id'),
    )
    
    def __init__(self, email: str, google_id: str):
        """Initialize user with email and Google ID"""
        self.email = email
        self.google_id = google_id
        self._cipher_suite = self._get_cipher_suite()
    
    def _get_cipher_suite(self) -> Fernet:
        """Get encryption cipher suite"""
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable not set")
        return Fernet(key.encode())

    def encrypt_token(self, token: str) -> str:
        """Encrypt OAuth token for secure storage"""
        if not self._cipher_suite:
            self._cipher_suite = self._get_cipher_suite()
        return self._cipher_suite.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt stored OAuth token"""
        if not self._cipher_suite:
            self._cipher_suite = self._get_cipher_suite()
        return self._cipher_suite.decrypt(encrypted_token.encode()).decode()

    def update_tokens(self, access_token: str, refresh_token: str) -> None:
        """Update OAuth tokens with encryption"""
        self.access_token = self.encrypt_token(access_token)
        self.refresh_token = self.encrypt_token(refresh_token)

    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        from jose import jwt
        try:
            payload = jwt.get_unverified_claims(self.get_decrypted_access_token())
            exp = payload.get('exp')
            if exp is None:
                return True
            return datetime.now(timezone.utc).timestamp() > exp
        except Exception:
            return True

    def get_decrypted_access_token(self) -> str:
        """Get decrypted access token"""
        return self.decrypt_token(self.access_token) if self.access_token else None

    def get_decrypted_refresh_token(self) -> str:
        """Get decrypted refresh token"""
        return self.decrypt_token(self.refresh_token) if self.refresh_token else None
    
    def update_last_sync(self) -> None:
        """Update last sync timestamp"""
        self.last_sync = datetime.now(timezone.utc)
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<User(id={self.id}, email={self.email}, active={self.is_active})>"

class User(BaseModel):
    id: Optional[int]
    email: str
    full_name: Optional[str]
    is_active: bool = True
    is_superuser: bool = False