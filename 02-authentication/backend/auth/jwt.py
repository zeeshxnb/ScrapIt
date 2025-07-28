"""
JWT Token Utilities

Handle JWT token creation, validation, and refresh
"""
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any
import os
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    """JWT token management for authentication"""
    
    # Token configuration
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    ALGORITHM = "RS256"
    
    def __init__(self):
        """Initialize JWT manager with RSA keys"""
        self.private_key = os.environ.get('JWT_PRIVATE_KEY')
        self.public_key = os.environ.get('JWT_PUBLIC_KEY')
        
        if not self.private_key or not self.public_key:
            raise ValueError("Missing JWT RSA keys in environment variables")
    
    def create_access_token(self, user_id: str, email: str) -> str:
        """
        Create JWT access token
        
        Args:
            user_id: User's unique identifier
            email: User's email address
            
        Returns:
            Encoded JWT access token
        """
        # TODO: Implement access token creation
        # Create payload with user_id, email, exp, iat, type
        # Set expiration time
        # Encode with private key
        # Return token string
        pass
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create JWT refresh token
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Encoded JWT refresh token
        """
        # TODO: Implement refresh token creation
        # Create payload with user_id, exp, iat, type
        # Set longer expiration time
        # Encode with private key
        # Return token string
        pass
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token payload
            
        Raises:
            JWTError: If token is invalid or expired
        """
        # TODO: Implement token verification
        # Decode token with public key
        # Validate signature and expiration
        # Return payload if valid
        # Raise JWTError if invalid
        pass
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode JWT token without verification (for debugging)
        
        Args:
            token: JWT token to decode
            
        Returns:
            Decoded payload or None if invalid
        """
        # TODO: Implement token decoding
        # Decode without verification
        # Handle malformed tokens
        # Return payload or None
        pass
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if JWT token is expired
        
        Args:
            token: JWT token to check
            
        Returns:
            True if expired, False otherwise
        """
        # TODO: Implement expiration check
        # Decode token
        # Check exp claim against current time
        # Return expiration status
        pass
    
    def get_token_type(self, token: str) -> Optional[str]:
        """
        Get token type from JWT payload
        
        Args:
            token: JWT token
            
        Returns:
            Token type ('access' or 'refresh') or None
        """
        # TODO: Implement token type extraction
        # Decode token
        # Return type from payload
        pass
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create new access token from valid refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token or None if refresh token invalid
        """
        # TODO: Implement access token refresh
        # Verify refresh token
        # Extract user info
        # Create new access token
        # Return new token
        pass
    
    def _create_payload(self, user_id: str, email: str = None, 
                       token_type: str = "access", 
                       expire_delta: timedelta = None) -> Dict[str, Any]:
        """Create JWT payload with standard claims"""
        # TODO: Implement payload creation
        # Set iat (issued at)
        # Set exp (expiration)
        # Set user_id and email
        # Set token type
        # Return payload dict
        pass
    
    def _get_expiration_time(self, token_type: str) -> datetime:
        """Get expiration time based on token type"""
        now = datetime.now(timezone.utc)
        if token_type == "access":
            return now + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == "refresh":
            return now + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            raise ValueError(f"Invalid token type: {token_type}")

# Global JWT manager instance
jwt_manager = JWTManager()