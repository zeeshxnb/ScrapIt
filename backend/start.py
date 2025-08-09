#!/usr/bin/env python3
"""
ScrapIt - Start Server
Simple startup script for development
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 ScrapIt server starting on http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs | Press Ctrl+C to stop")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="warning",  # Reduced logging
        access_log=False      # Disable access logs
    )