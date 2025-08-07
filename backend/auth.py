"""
Authentication Module - Consolidated
Handles Google OAuth, JWT tokens, and user management
"""
import os
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from database import get_db
from models import User

router = APIRouter()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

# Google OAuth Configuration  
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")

def create_jwt_token(user_id: str) -> str:
    """Create JWT token"""
    expire = datetime.utcnow() + timedelta(minutes=30)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> str:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None

def get_google_auth_url() -> str:
    """Get Google OAuth URL"""
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/userinfo.email'],
        redirect_uri=REDIRECT_URI
    )
    
    auth_url, _ = flow.authorization_url(access_type='offline')
    return auth_url

def exchange_code_for_tokens(code: str) -> dict:
    """Exchange OAuth code for tokens"""
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/userinfo.email'],
        redirect_uri=REDIRECT_URI
    )
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Get user info
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    
    return {
        'access_token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'user_info': user_info
    }

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current user from JWT"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    
    token = auth_header.split(" ")[1]
    user_id = verify_jwt_token(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Routes
@router.get("/google")
async def google_auth():
    """Start Google OAuth"""
    auth_url = get_google_auth_url()
    return {"auth_url": auth_url}

@router.get("/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        token_data = exchange_code_for_tokens(code)
        user_info = token_data['user_info']
        
        # Find or create user
        user = db.query(User).filter(User.google_id == user_info['id']).first()
        
        if not user:
            user = User(
                email=user_info['email'],
                google_id=user_info['id']
            )
            db.add(user)
        
        # Update tokens
        user.set_access_token(token_data['access_token'])
        user.set_refresh_token(token_data['refresh_token'])
        db.commit()
        
        # Create JWT
        jwt_token = create_jwt_token(str(user.id))
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user_email": user.email
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat()
    }

@router.delete("/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}

# Export router
auth_router = router