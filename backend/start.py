#!/usr/bin/env python3
"""
ScrapIt - Start Server
Simple startup script for development
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting ScrapIt server...")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔍 Health: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )