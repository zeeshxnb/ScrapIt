# ScrapIt - AI-Powered Email Cleaner

Clean your inbox in minutes, not hours. ScrapIt uses AI to automatically classify, organize, and clean your emails with natural language commands.

## Features

* **AI Classification** - Automatically categorize emails using OpenAI
* **Smart Spam Detection** - Identify and remove spam with high accuracy
* **Natural Language Chat** - Manage emails by talking to AI assistant
* **Analytics Dashboard** - Insights into your email patterns
* **Gmail Integration** - Seamless sync with your Gmail account
* **Bulk Operations** - Clean thousands of emails with one click

## Architecture

```
scrapit/
├── backend/           # FastAPI backend
│   ├── main.py       # App entry point
│   ├── auth.py       # Google OAuth
│   ├── gmail.py      # Gmail API integration
│   ├── ai.py         # AI classification & spam detection
│   ├── chatbot.py    # Natural language interface
│   ├── models.py     # Database models
│   └── database.py   # Database setup
├── frontend/         # React frontend
└── .env             # Environment variables
```

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python start.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Environment Setup

```bash
# Copy and update with your API keys
cp .env.example .env
```

Required API keys:

* **Google OAuth** - For Gmail access
* **OpenAI API** - For AI classification

## Usage

1. **Login** with Google to connect your Gmail
2. **Sync** emails from your inbox
3. **Classify** emails automatically with AI
4. **Chat** with the assistant: "Delete my spam emails"
5. **Analyze** your email patterns and cleanup progress

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, OpenAI, Google APIs
**Frontend:** React, TypeScript, Tailwind CSS
**Database:** SQLite (dev) / PostgreSQL (prod)

## API Endpoints

* `GET /` - Health check
* `POST /auth/google` - Start OAuth flow
* `POST /gmail/sync` - Sync emails
* `POST /ai/classify` - Classify emails
* `POST /chat/chat` - Chat with AI
* `GET /docs` - Interactive API documentation

## Security

* OAuth tokens encrypted at rest
* JWT session management
* Environment-based configuration
* CORS protection
