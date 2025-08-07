"""
ScrapIt - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import consolidated modules
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_dir)

# Import from the consolidated modules
sys.path.append(os.path.join(parent_dir, '02-authentication'))
from auth import auth_router

sys.path.append(os.path.join(parent_dir, '03-gmail-integration'))
from gmail import gmail_router

sys.path.append(os.path.join(parent_dir, '04-ai-classification'))
from ai import ai_router

sys.path.append(os.path.join(parent_dir, '05-chatbot'))
from chatbot import chatbot_router

app = FastAPI(
    title="ScrapIt - Email Cleaner",
    description="AI-powered email cleaning and organization",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(gmail_router, prefix="/gmail", tags=["gmail"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])
app.include_router(chatbot_router, prefix="/chat", tags=["chatbot"])

@app.get("/")
async def root():
    return {"message": "ScrapIt API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)