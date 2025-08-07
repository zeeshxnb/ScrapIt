#!/usr/bin/env python3
"""
Start the ScrapIt server for testing
"""
import os
import sys
import uvicorn

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    print("🚀 Starting ScrapIt server...")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔍 Alternative docs: http://localhost:8000/redoc")
    print("⚡ Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop")
    
    # Change to the main app directory
    os.chdir("01-project-setup")
    
    # Start the server
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )