# 🧪 ScrapIt Backend Testing Guide

## 🎯 **Yes, you can test everything right now!**

Here are 4 different ways to test the backend features:

## **Method 1: Interactive API Documentation** ⭐ (Recommended)

1. **Start the server:**
   ```bash
   python start_server.py
   ```

2. **Visit the interactive docs:**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

3. **Test endpoints directly:**
   - Click on any endpoint
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - See real responses!

## **Method 2: Python Test Scripts**

### **Mock Testing (No API keys needed):**
```bash
python test_with_mock_data.py
```
Tests core logic and structure without external dependencies.

### **Live API Testing:**
```bash
# Start server first
python start_server.py

# Then in another terminal:
python test_backend.py
```
Tests actual HTTP endpoints.

## **Method 3: cURL Commands**

```bash
# Make script executable
chmod +x test_api.sh

# Run tests
./test_api.sh
```

Or manually:
```bash
# Test health
curl http://localhost:8000/health

# Test auth URL
curl http://localhost:8000/auth/google

# Test chatbot (will need auth)
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## **Method 4: Browser Testing**

1. Start server: `python start_server.py`
2. Visit endpoints directly:
   - http://localhost:8000/ (root)
   - http://localhost:8000/health (health check)
   - http://localhost:8000/auth/google (auth URL)

## 🔍 **What You Can Test Right Now**

### ✅ **Working Without Setup:**
- Server health and basic endpoints
- Authentication URL generation
- API structure and documentation
- Core logic (intent detection, etc.)
- Database models and relationships

### ⚠️ **Requires API Keys (.env setup):**
- Google OAuth flow completion
- Gmail email syncing
- OpenAI email classification
- Full chatbot responses

### 🎯 **Full Feature Testing:**
- Email management workflow
- Spam detection and deletion
- AI-powered email categorization
- Natural language chat interface

## 🚀 **Step-by-Step Testing Workflow**

### **Phase 1: Basic Structure** (No setup needed)
```bash
python test_with_mock_data.py
```
✅ Confirms all modules work and logic is sound

### **Phase 2: API Endpoints** (No setup needed)
```bash
python start_server.py
# Visit http://localhost:8000/docs
```
✅ Test all endpoint structures and responses

### **Phase 3: Authentication** (Requires Google OAuth)
1. Set up Google OAuth in .env
2. Test `/auth/google` → `/auth/callback` flow
3. Get JWT token for authenticated requests

### **Phase 4: Full Features** (Requires all API keys)
1. Set up OpenAI API key
2. Test email sync, classification, and chat
3. Full user workflow testing

## 🛠️ **Quick Setup for Full Testing**

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Get Google OAuth credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Add redirect URI: `http://localhost:8000/auth/callback`

3. **Get OpenAI API key:**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Create API key

4. **Update .env file:**
   ```bash
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   OPENAI_API_KEY=your-openai-key
   ```

5. **Test everything:**
   ```bash
   python start_server.py
   # Visit http://localhost:8000/docs
   ```

## 📊 **Expected Test Results**

### **Without API Keys:**
- ✅ Server starts successfully
- ✅ Health check passes
- ✅ Auth URLs generate
- ⚠️ Protected endpoints return 401 (expected)
- ✅ API documentation loads

### **With API Keys:**
- ✅ Full OAuth flow works
- ✅ Email sync retrieves real emails
- ✅ AI classification categorizes emails
- ✅ Chatbot provides intelligent responses
- ✅ Spam detection identifies spam
- ✅ All CRUD operations work

## 🎯 **Bottom Line**

**Yes, you can test everything right now!** The backend is fully functional. You have:

1. **Complete API structure** - All endpoints defined
2. **Working authentication** - Google OAuth flow
3. **Database models** - User and email storage
4. **AI integration** - OpenAI classification
5. **Natural language interface** - Chatbot
6. **Email management** - Sync, categorize, manage

The only thing missing is a frontend UI - but all the backend functionality is there and testable!