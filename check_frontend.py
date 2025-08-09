#!/usr/bin/env python3
"""
Check if the frontend is handling authentication properly
"""
import requests

def check_frontend():
    """Check frontend status"""
    
    print("🌐 Checking Frontend Status")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ Frontend is running on port 3000")
            print("📄 Frontend loaded successfully")
            
            # Check if it's a React app
            if "react" in response.text.lower() or "root" in response.text:
                print("⚛️  React app detected")
            
            print("\n💡 Next steps:")
            print("1. Open http://localhost:3000 in your browser")
            print("2. Look for a login button or authentication")
            print("3. If you see a token in the URL (?token=...), copy it")
            print("4. Or run: python simple_auth.py")
            
        else:
            print(f"❌ Frontend error: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        print("💡 Try starting the frontend:")
        print("   cd frontend && npm start")

def check_backend():
    """Check backend status"""
    
    print("\n🔧 Checking Backend Status")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is running on port 8000")
            
            # Check auth endpoints
            response = requests.get("http://localhost:8000/auth/login")
            if response.status_code == 200:
                print("✅ Auth endpoints working")
            else:
                print("⚠️  Auth endpoints issue")
                
        else:
            print(f"❌ Backend error: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        print("💡 Try starting the backend:")
        print("   cd backend && python start.py")

if __name__ == "__main__":
    print("ScrapIt System Check")
    check_frontend()
    check_backend()
    
    print("\n🎯 Quick Authentication:")
    print("Run: python simple_auth.py")
    print("This will guide you through the OAuth flow step by step.")