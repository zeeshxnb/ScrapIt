#!/usr/bin/env python3
"""
Test the frontend authentication flow
"""
import requests
import webbrowser
import time

def test_frontend_auth():
    """Test the complete authentication flow"""
    
    print("🌐 Testing Frontend Authentication Flow")
    print("=" * 45)
    
    # Step 1: Check if both servers are running
    print("1. Checking servers...")
    try:
        backend_response = requests.get("http://localhost:8000/health", timeout=3)
        frontend_response = requests.get("http://localhost:3000", timeout=3)
        
        if backend_response.status_code == 200 and frontend_response.status_code == 200:
            print("   ✅ Both servers running")
        else:
            print("   ❌ Server issues")
            return False
    except Exception as e:
        print(f"   ❌ Server connection error: {e}")
        return False
    
    # Step 2: Open frontend in browser
    print("\n2. Opening frontend in browser...")
    print("   🌐 Opening http://localhost:3000")
    webbrowser.open("http://localhost:3000")
    
    print("\n📋 What you should see:")
    print("   • If NOT logged in: Login page with 'Continue with Gmail' button")
    print("   • If logged in: Dashboard with email stats")
    print("   • If loading: Spinner with 'Loading...' text")
    
    print("\n🔐 To authenticate:")
    print("   1. Click 'Continue with Gmail' button")
    print("   2. Login with your Gmail account")
    print("   3. Grant permissions")
    print("   4. You'll be automatically redirected back")
    print("   5. Should see the dashboard")
    
    # Step 3: Test the OAuth URL
    print("\n3. Testing OAuth URL generation...")
    try:
        response = requests.get("http://localhost:8000/auth/google")
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('auth_url', '')
            if 'accounts.google.com' in auth_url:
                print("   ✅ OAuth URL generated correctly")
            else:
                print("   ❌ Invalid OAuth URL")
        else:
            print(f"   ❌ OAuth endpoint error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ OAuth test error: {e}")
    
    print("\n" + "=" * 45)
    print("🎯 Next Steps:")
    print("1. Check your browser at http://localhost:3000")
    print("2. If you see a login page, click 'Continue with Gmail'")
    print("3. If you see a dashboard, you're already logged in!")
    print("4. If you see errors, check the browser console (F12)")
    
    return True

def test_manual_oauth():
    """Manual OAuth test if frontend isn't working"""
    
    print("\n🔧 Manual OAuth Test (if frontend issues)")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/auth/google")
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('auth_url')
            
            print("✅ Manual OAuth URL:")
            print(f"   {auth_url}")
            print("\n📝 Manual steps:")
            print("1. Copy the URL above")
            print("2. Open it in your browser")
            print("3. Login and grant permissions")
            print("4. You'll be redirected to localhost:3000 with a token")
            print("5. The frontend should automatically handle the token")
            
            return auth_url
        else:
            print(f"❌ Failed to get OAuth URL: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("Frontend Authentication Test")
    print("This will test the complete user authentication flow")
    print()
    
    if test_frontend_auth():
        print("\n💡 If the frontend isn't working properly:")
        test_manual_oauth()
    
    print("\n🎉 The authentication should be seamless!")
    print("Users just click 'Continue with Gmail' and they're done.")