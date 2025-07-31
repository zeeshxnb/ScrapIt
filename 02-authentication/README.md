# Authentication Module

This module provides authentication logic for ScrapIt, including JWT and OAuth (Google) support.

## Structure
- `backend/auth/jwt.py`: JWT token utilities
- `backend/auth/oauth.py`: Google OAuth utilities
- `backend/models/user.py`: User model

## Usage
- Import and use the authentication utilities in your FastAPI app.
- Configure secrets in your `.env` file.

# 02 - Authentication System

## Overview
Implement Google OAuth authentication with JWT token management for secure user sessions.

## Tasks to Complete
- [ ] Set up Google OAuth configuration
- [ ] Build user authentication database models
- [ ] Create JWT token utilities
- [ ] Implement auth endpoints

## Files to Create

### Backend Files
- `backend/app/models/user.py` - User database model
- `backend/app/auth/oauth.py` - Google OAuth client setup
- `backend/app/auth/jwt.py` - JWT token utilities
- `backend/app/auth/routes.py` - Authentication endpoints
- `backend/app/database.py` - Database connection setup
- `tests/test_auth.py` - Authentication tests

### Frontend Files
- `frontend/src/components/Login.tsx` - Login component
- `frontend/src/hooks/useAuth.tsx` - Authentication hook
- `frontend/src/services/auth.ts` - Auth API calls
- `frontend/src/contexts/AuthContext.tsx` - Auth state management

## Key Implementation Points

### Google OAuth Setup
- Create project in Google Cloud Console
- Configure OAuth consent screen
- Generate client ID and secret
- Set redirect URIs for development and production

### Database Model
- User ID (UUID primary key)
- Email, Google ID
- Encrypted access/refresh tokens
- Timestamps for created_at, last_sync

### JWT Implementation
- Use RS256 algorithm for security
- Include user ID and email in payload
- Set appropriate expiration times
- Implement refresh token rotation

## Tips
- Store OAuth secrets in environment variables
- Encrypt tokens before database storage
- Implement proper error handling for OAuth failures
- Use secure HTTP-only cookies for JWT storage
- Add CORS configuration for frontend communication