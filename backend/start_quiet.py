#!/usr/bin/env python3
"""
ScrapIt - Quiet Start Server
Minimal output startup script
"""
import uvicorn
import logging

# Suppress most logging
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

if __name__ == "__main__":
    print("🚀 ScrapIt server: http://localhost:8000")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="error",     # Only show errors
        access_log=False,     # No access logs
        reload_dirs=["backend"]  # Only watch backend directory
    )