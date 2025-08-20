"""
ScrapIt - Main Application Entry Point
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Import modules
from auth import auth_router
from gmail import gmail_router  
from ai import ai_router
from chatbot import chatbot_router
from analytics import router as analytics_router
from task_executor import task_executor_router
from notification import notification_router

app = FastAPI(
    title="ScrapIt",
    description="AI-powered email cleaning and organization",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "file://", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(gmail_router, prefix="/gmail", tags=["gmail"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])
app.include_router(chatbot_router, prefix="/chat", tags=["chatbot"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(task_executor_router, prefix="/tasks", tags=["tasks"])
app.include_router(notification_router, prefix="/notifications", tags=["notifications"])

@app.get("/")
async def root():
    return {"message": "ScrapIt API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)