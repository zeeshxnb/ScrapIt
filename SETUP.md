# 🚀 ScrapIt Setup Guide

## Quick Start for Collaborators

### 1. Clone & Setup
```bash
git clone <repo-url>
cd ScrapIt
```

### 2. Backend Setup
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup  
```bash
cd frontend
npm install
```

### 4. Environment Variables
```bash
cp .env.example .env
# Edit .env with your API keys:
# - GOOGLE_CLIENT_ID
# - GOOGLE_CLIENT_SECRET  
# - OPENAI_API_KEY
```

### 5. Run Development Servers

**Backend (Terminal 1):**
```bash
cd backend
python start.py
# → http://localhost:8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm start  
# → http://localhost:3000
```

### 6. Development
- **Edit any file** → **Save** → **Auto-reloads!**
- **No manual refresh needed**
- **See changes instantly**

## 🔑 Required API Keys
- **Google OAuth:** [Google Cloud Console](https://console.cloud.google.com/)
- **OpenAI:** [OpenAI Platform](https://platform.openai.com/)

## 📁 What's Ignored by Git
- `node_modules/` - Auto-installed by npm
- `venv/` - Auto-created Python environment  
- `.env` - Your personal API keys
- `*.db` - Database files