# 🤖 ScrapIt Chatbot Implementation

The ScrapIt chatbot is a natural language interface for email management, allowing users to interact with their emails through conversational commands.

## ✨ Features

### 🧠 Natural Language Understanding
- **Intent Detection**: Automatically understands user intentions from natural language
- **Entity Extraction**: Extracts relevant information like sender names, categories, etc.
- **Contextual Responses**: Provides relevant suggestions based on email state

### 🗑️ Spam Management
```
User: "Delete my spam emails"
Bot: "I found 15 spam emails. Would you like me to delete them all?"
```

### 🤖 AI Classification
```
User: "Classify my emails"
Bot: "I'll classify your 23 unprocessed emails using AI."
```

### 📊 Statistics & Analytics
```
User: "Show me my email stats"
Bot: "247 total emails, 15 spam, 23 unprocessed. Categories: Work (89), Personal (45)..."
```

### 🔍 Smart Search
```
User: "Find emails from john@example.com"
Bot: "I found 8 emails from john@example.com. Most recent: 'Project Update'..."
```

### 🔄 Email Synchronization
```
User: "Sync my latest emails"
Bot: "I'll sync your latest emails from Gmail."
```

## 🏗️ Architecture

### Core Components

1. **Intent Detection Engine** (`detect_intent_and_entities`)
   - Analyzes user messages to determine intent
   - Extracts relevant entities (sender, category, etc.)
   - Supports 7+ different intents

2. **Message Processing** (`process_chat_message`)
   - Handles conversation flow
   - Generates contextual responses
   - Provides actionable suggestions

3. **Email Summary** (`get_email_summary`)
   - Aggregates email statistics
   - Provides context for AI responses
   - Tracks user email state

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat/chat` | POST | Main chat interface |
| `/chat/summary` | GET | Email summary statistics |
| `/chat/suggestions` | GET | Contextual suggestions |
| `/chat/search` | POST | Advanced email search |
| `/chat/quick-actions` | GET | Quick action buttons |

## 🚀 Usage Examples

### Basic Chat
```python
# POST /chat/chat
{
    "message": "Delete my spam emails",
    "context": []  # Optional chat history
}

# Response
{
    "response": "I found 15 spam emails. Would you like me to delete them all?",
    "action": "delete_spam",
    "data": {"spam_count": 15},
    "suggestions": ["Yes, delete all spam", "Show me the spam first"],
    "quick_actions": [
        {"label": "Yes, delete all spam", "action": "confirm_delete_spam"},
        {"label": "Show me the spam first", "action": "show_spam"}
    ]
}
```

### Email Search
```python
# POST /chat/search
{
    "query": "project update",
    "sender": "john@example.com",
    "category": "work",
    "limit": 20
}

# Response
{
    "results": [
        {
            "id": "123",
            "subject": "Project Update - Q4 Progress",
            "sender": "john@example.com",
            "snippet": "Here's the latest update on our Q4 project...",
            "category": "work",
            "is_spam": false,
            "received_date": "2024-01-15T10:30:00Z"
        }
    ],
    "total_found": 1,
    "query_used": {
        "text": "project update",
        "sender": "john@example.com", 
        "category": "work"
    }
}
```

## 🎯 Supported Intents

| Intent | Trigger Phrases | Action |
|--------|----------------|--------|
| `delete_spam` | "delete spam", "clean spam", "remove spam" | Delete spam emails |
| `show_spam` | "show spam", "list spam", "spam emails" | Display spam emails |
| `classify_emails` | "classify", "process emails", "categorize" | AI email classification |
| `show_stats` | "stats", "summary", "overview", "dashboard" | Show email statistics |
| `search_emails` | "find", "search", "look for", "show me emails" | Search emails |
| `sync_emails` | "sync", "refresh", "update emails" | Sync from Gmail |
| `help` | "help", "what can you do", "commands" | Show help information |
| `general` | Everything else | General conversation |

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Dependencies
```python
openai>=0.27.0
fastapi>=0.68.0
sqlalchemy>=1.4.0
pydantic>=1.8.0
```

## 🧪 Testing

Run the test suite:
```bash
python test_chatbot.py
```

View the demo interface:
```bash
# Open chatbot_demo.html in your browser
open chatbot_demo.html
```

Start the API server:
```bash
cd 01-project-setup
uvicorn main:app --reload
```

Visit the interactive API docs:
```
http://localhost:8000/docs
```

## 🎨 Frontend Integration

The chatbot is designed to work with any frontend framework. Key integration points:

### Chat Interface
```javascript
// Send message to chatbot
const response = await fetch('/chat/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: userMessage,
        context: chatHistory
    })
});

const data = await response.json();
console.log(data.response); // Bot response
console.log(data.suggestions); // Contextual suggestions
```

### Quick Actions
```javascript
// Get contextual quick actions
const actions = await fetch('/chat/quick-actions');
const data = await actions.json();

// Render action buttons
data.actions.forEach(action => {
    const button = document.createElement('button');
    button.textContent = action.label;
    button.onclick = () => performAction(action.id);
});
```

## 🔮 Future Enhancements

- **Multi-language Support**: Support for multiple languages
- **Voice Interface**: Voice-to-text and text-to-speech
- **Advanced Analytics**: More detailed email insights
- **Custom Commands**: User-defined shortcuts and macros
- **Integration Webhooks**: Connect with external services
- **Scheduled Actions**: Automated email management tasks

## 🤝 Contributing

The chatbot is modular and extensible. To add new features:

1. **Add Intent**: Update `detect_intent_and_entities()` function
2. **Add Handler**: Implement logic in `process_chat_message()`
3. **Add Endpoint**: Create new API endpoint if needed
4. **Test**: Add test cases to `test_chatbot.py`

## 📝 Notes

- The chatbot uses OpenAI's GPT-3.5-turbo for general conversation
- Intent detection is rule-based for reliability and speed
- All responses include contextual suggestions for better UX
- The system is designed to be stateless for scalability