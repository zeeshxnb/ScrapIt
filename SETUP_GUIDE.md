# 🚀 ScrapIt Setup Guide

## Prerequisites

Before you can use ScrapIt, you need to set up a few external services:

### 1. 🔑 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URI: `http://localhost:8000/auth/callback`
   - Copy the Client ID and Client Secret

### 2. 🤖 OpenAI API Setup

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Go to "API Keys" section
4. Create a new API key
5. Copy the API key (starts with `sk-`)

### 3. 📝 Update Environment Variables

Edit your `.env` file with the real values:

```bash
# Replace these with your actual values:
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
OPENAI_API_KEY=sk-your-actual-openai-key
```

## 🏃‍♂️ Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup database:**
   ```bash
   python setup_database.py
   ```

3. **Update .env file** with your API keys (see above)

4. **Start the server:**
   ```bash
   cd 01-project-setup
   uvicorn main:app --reload
   ```

5. **Visit the app:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## 🔄 How It Works

### Authentication Flow
1. User clicks "Login with Google"
2. Redirected to Google OAuth
3. User grants Gmail permissions
4. Redirected back with access token
5. Token encrypted and stored in database

### Email Processing
1. **Sync**: Fetch emails from Gmail API
2. **Classify**: Use OpenAI to categorize emails
3. **Clean**: Identify and manage spam
4. **Chat**: Natural language interface for management

### Chatbot Usage
```
User: "Delete my spam emails"
Bot: "I found 15 spam emails. Would you like me to delete them all?"

User: "Show me my email stats"  
Bot: "247 total emails, 15 spam, 23 unprocessed..."

User: "Find emails from john@example.com"
Bot: "I found 8 emails from john@example.com..."
```

## 🛡️ Security Features

- **Token Encryption**: All OAuth tokens encrypted at rest
- **JWT Authentication**: Secure session management
- **Environment Variables**: Sensitive data in .env file
- **CORS Protection**: Configured for localhost development

## 🧪 Testing

Test the API endpoints:
```bash
# Test basic functionality
python test_chatbot.py

# View interactive demo
open chatbot_demo.html
```

## 📁 Project Structure

```
ScrapIt/
├── 01-project-setup/main.py    # FastAPI app
├── 02-authentication/auth.py   # Google OAuth
├── 03-gmail-integration/gmail.py # Gmail API
├── 04-ai-classification/ai.py  # OpenAI integration
├── 05-chatbot/chatbot.py       # Natural language interface
├── models.py                   # Database models
├── database.py                 # Database setup
└── .env                        # Configuration
```

## 🚨 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Make sure you're in the right directory
   - Check Python path in imports

2. **Database errors**
   - Run `python setup_database.py` again
   - Check file permissions

3. **OAuth errors**
   - Verify redirect URI matches exactly
   - Check client ID/secret are correct

4. **OpenAI errors**
   - Verify API key is valid
   - Check you have credits/usage available

### Getting Help

1. Check the logs in terminal
2. Visit http://localhost:8000/docs for API testing
3. Ensure all environment variables are set correctly

## 🎯 Next Steps

Once setup is complete:
1. Build a proper frontend UI
2. Add more email management features
3. Implement scheduled email processing
4. Add email templates and automation