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
    """Create JWT token with longer expiration for production"""
    # Use 24 hours for production instead of 30 minutes
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> str:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def refresh_google_token(refresh_token: str) -> dict:
    """Refresh Google access token using refresh token"""
    if not refresh_token:
        raise HTTPException(status_code=400, detail="No refresh token available")
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        
        # Create credentials with refresh token
        credentials = Credentials(
            token=None,  # Will be refreshed
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )
        
        # Refresh the token
        credentials.refresh(Request())
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token or refresh_token,  # Keep old if no new one
            'expires_at': credentials.expiry.isoformat() if credentials.expiry else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token refresh failed: {str(e)}")

def get_google_auth_url() -> str:
    """Get Google OAuth URL"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }
    
    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/userinfo.email',
                    'openid',
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.modify'],
            redirect_uri=REDIRECT_URI
        )
        
        # Force fresh consent to get refresh token
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent',  # This forces Google to show consent screen and provide refresh token
            include_granted_scopes='true'  # Include previously granted scopes
        )
        return auth_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

def exchange_code_for_tokens(code: str) -> dict:
    """Exchange OAuth code for tokens"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
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
        scopes=['https://www.googleapis.com/auth/userinfo.email',
                'openid',
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify'],
        redirect_uri=REDIRECT_URI
    )
    
    try:
        # Force access_type=offline to get refresh token
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Validate we got tokens
        if not credentials.token:
            raise Exception("No access token received")
        
        # Get user info
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'user_info': user_info,
            'expires_at': credentials.expiry.isoformat() if credentials.expiry else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {str(e)}")

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
@router.get("/login")
async def login():
    """Start Google OAuth - alias for /google"""
    auth_url = get_google_auth_url()
    return {"auth_url": auth_url}

@router.get("/google")
async def google_auth():
    """Start Google OAuth"""
    auth_url = get_google_auth_url()
    return {"auth_url": auth_url}

@router.get("/google-redirect")
async def google_auth_redirect():
    """Direct redirect to Google OAuth"""
    from fastapi.responses import RedirectResponse
    auth_url = get_google_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def google_callback(code: str = None, error: str = None, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    from fastapi.responses import RedirectResponse
    
    # Handle OAuth errors (user denied access, etc.)
    if error:
        print(f"OAuth error: {error}")
        return RedirectResponse(url=f"http://localhost:3000/login?error=access_denied")
    
    if not code:
        print("No authorization code received")
        return RedirectResponse(url=f"http://localhost:3000/login?error=no_code")
    
    try:
        print(f"Processing OAuth callback with code: {code[:20]}...")
        
        # Exchange code for tokens
        token_data = exchange_code_for_tokens(code)
        user_info = token_data['user_info']
        
        print(f"OAuth successful for user: {user_info.get('email')}")
        
        # Find or create user
        user = db.query(User).filter(User.google_id == user_info['id']).first()
        
        if not user:
            print(f"Creating new user: {user_info['email']}")
            user = User(
                email=user_info['email'],
                google_id=user_info['id']
            )
            db.add(user)
        else:
            print(f"Existing user found: {user.email}")
        
        # Update tokens
        user.set_access_token(token_data['access_token'])
        if token_data.get('refresh_token'):
            user.set_refresh_token(token_data['refresh_token'])
            print("Refresh token updated")
        else:
            print("No refresh token received (user may have already granted access)")
        
        db.commit()
        
        # Create JWT with longer expiration for production
        jwt_token = create_jwt_token(str(user.id))
        
        print(f"JWT token created, redirecting to frontend...")
        
        # Redirect to frontend with token
        return RedirectResponse(url=f"http://localhost:3000/?token={jwt_token}")
        
    except Exception as e:
        print(f"OAuth callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Redirect to frontend with error
        return RedirectResponse(url=f"http://localhost:3000/login?error=auth_failed")

@router.post("/callback")
async def google_callback_post(request: dict, db: Session = Depends(get_db)):
    """Handle Google OAuth callback via POST (for testing)"""
    try:
        code = request.get('code')
        if not code:
            raise HTTPException(status_code=400, detail="No code provided")
            
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
        if token_data.get('refresh_token'):
            user.set_refresh_token(token_data['refresh_token'])
        db.commit()
        
        # Create JWT
        jwt_token = create_jwt_token(str(user.id))
        
        return {
            "success": True,
            "token": jwt_token,
            "user": {
                "id": str(user.id),
                "email": user.email
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    # Try to fetch profile name from Google if possible
    display_name = None
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials(
            token=current_user.get_access_token(),
            refresh_token=current_user.get_refresh_token(),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
        )
        service = build('oauth2', 'v2', credentials=creds)
        info = service.userinfo().get().execute()
        display_name = info.get('name')
    except Exception:
        pass
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": display_name,
        "created_at": current_user.created_at.isoformat()
    }

@router.get("/test-token")
async def test_token(current_user: User = Depends(get_current_user)):
    """Test if token is working"""
    return {
        "success": True,
        "message": "Token is valid!",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email
        }
    }

@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Refresh Google access token"""
    try:
        refresh_token = current_user.get_refresh_token()
        if not refresh_token:
            raise HTTPException(status_code=400, detail="No refresh token available")
        
        token_data = refresh_google_token(refresh_token)
        
        # Update user tokens
        current_user.set_access_token(token_data['access_token'])
        if token_data.get('refresh_token') != refresh_token:
            current_user.set_refresh_token(token_data['refresh_token'])
        
        db.commit()
        
        return {
            "success": True,
            "message": "Token refreshed successfully",
            "expires_at": token_data.get('expires_at')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}

# Export router
auth_router = router