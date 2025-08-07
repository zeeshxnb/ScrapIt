#!/usr/bin/env python3
"""
Database Setup Script for ScrapIt
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from models import Base, User, Email
from database import engine

def setup_database():
    """Initialize the database with tables"""
    print("🗄️  Setting up ScrapIt database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection test passed")
        
        print("\n📊 Database Schema:")
        print("- Users table: Authentication and user data")
        print("- Emails table: Email storage with encryption")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Checking environment configuration...")
    
    required_vars = [
        "JWT_SECRET_KEY",
        "GOOGLE_CLIENT_ID", 
        "GOOGLE_CLIENT_SECRET",
        "OPENAI_API_KEY",
        "ENCRYPTION_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith("your-"):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing or placeholder environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please update your .env file with real values")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def main():
    """Main setup function"""
    print("🚀 ScrapIt Setup")
    print("=" * 50)
    
    # Check environment
    env_ok = check_environment()
    
    # Setup database
    db_ok = setup_database()
    
    print("\n" + "=" * 50)
    if db_ok:
        print("✅ Setup completed successfully!")
        
        if not env_ok:
            print("\n⚠️  IMPORTANT: Update your .env file before running the app")
            print("You need to set up:")
            print("1. Google OAuth credentials")
            print("2. OpenAI API key")
            print("3. Secure JWT and encryption keys")
        
        print("\n🚀 Next steps:")
        print("1. Update .env with your API keys")
        print("2. Run: uvicorn main:app --reload")
        print("3. Visit: http://localhost:8000")
        
    else:
        print("❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()