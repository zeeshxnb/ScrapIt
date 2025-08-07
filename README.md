# ScrapIt - Email Cleaner

AI-powered email cleaning and organization tool with organized modular structure.

## Project Structure

```
ScrapIt/
├── 01-project-setup/
│   └── main.py              # FastAPI application entry point
├── 02-authentication/
│   └── auth.py              # Google OAuth + JWT authentication
├── 03-gmail-integration/
│   └── gmail.py             # Gmail API integration + email sync
├── 04-ai-classification/
│   └── ai.py                # OpenAI email classification + spam detection
├── 05-chatbot/
│   └── chatbot.py           # Email management chatbot assistant
├── models.py                # All database models (User, Email)
├── database.py              # Database configuration
├── requirements.txt         # Dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Features

- ✅ **Google OAuth Authentication** - Secure login with Gmail access
- ✅ **Gmail Integration** - Sync and manage emails from Gmail API
- ✅ **AI Classification** - OpenAI-powered email categorization
- ✅ **Spam Detection** - Automatic spam identification and removal
- ✅ **Modular Design** - Organized by feature with clear separation

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run the application:**
```bash
python 01-project-setup/main.py
```

## API Endpoints

### Authentication
- `GET /auth/google` - Start Google OAuth flow
- `GET /auth/callback` - OAuth callback handler
- `GET /auth/me` - Get current user info
- `DELETE /auth/logout` - Logout user

### Gmail Integration
- `POST /gmail/sync` - Sync emails from Gmail
- `GET /gmail/emails` - Get user's emails

### AI Classification
- `POST /ai/classify` - Classify emails using AI
- `GET /ai/categories` - Get email categories summary
- `GET /ai/spam` - Get spam emails
- `DELETE /ai/spam` - Delete all spam emails

### Chatbot Assistant
- `POST /chat/chat` - Chat with email management assistant
- `GET /chat/suggestions` - Get suggested chat prompts

## Module Details

### 01-project-setup/main.py
- FastAPI application setup
- Router integration
- CORS configuration
- Health check endpoints

### 02-authentication/auth.py
- Google OAuth 2.0 flow
- JWT token management
- User authentication middleware
- Login/logout endpoints

### 03-gmail-integration/gmail.py
- Gmail API client wrapper
- Email synchronization service
- Message retrieval and parsing
- Email management endpoints

### 04-ai-classification/ai.py
- OpenAI integration for email classification
- Spam detection algorithms
- Batch processing for multiple emails
- Category analysis and reporting

### Core Files
- **models.py** - SQLAlchemy models for User and Email
- **database.py** - Database connection and session management

## Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///scrapit.db

# JWT Authentication
JWT_SECRET_KEY=your-secret-key

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
REDIRECT_URI=http://localhost:8000/auth/callback

# OpenAI
OPENAI_API_KEY=your-openai-key

# Security
ENCRYPTION_KEY=your-encryption-key
```

## Development

The modular structure makes it easy to:
- **Understand** - Each module has a clear purpose
- **Develop** - Work on features independently  
- **Test** - Test modules in isolation
- **Deploy** - Scale individual components
- **Maintain** - Update specific functionality without affecting others

## File Count: 9 files total
- **Before**: 50+ scattered files
- **After**: 8 organized files (84% reduction!)
- **Structure**: Maintained for clarity
- **Functionality**: Complete and consolidated