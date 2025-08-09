#!/usr/bin/env python3
"""
Test authentication and Gmail access
"""
import requests
import webbrowser
from urllib.parse import urlencode

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test the authentication flow"""
    
    print("🔐 Testing Gmail Authentication Flow")
    print("=" * 40)
    
    # Step 1: Get auth URL
    try:
        response = requests.get(f"{BASE_URL}/auth/google")
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('auth_url')
            if auth_url:
                print("✅ Auth URL generated")
                print(f"🌐 Opening browser: {auth_url[:50]}...")
                
                # Open browser for user to authenticate
                webbrowser.open(auth_url)
                
                print("\n📝 After authenticating in browser:")
                print("1. You'll be redirected to a callback URL")
                print("2. Copy the 'code' parameter from the URL")
                print("3. Use it to complete authentication")
                
                return True
            else:
                print("❌ No auth URL in response")
                return False
        else:
            print(f"❌ Auth endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Auth request failed: {e}")
        return False

def test_with_code():
    """Test authentication with code"""
    
    code = input("\n🔑 Enter the authorization code from the callback URL: ").strip()
    
    if not code:
        print("❌ No code provided")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/auth/callback?code={code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Authentication successful!")
            print(f"👤 User: {data.get('user', {}).get('email', 'Unknown')}")
            
            # Test Gmail access
            test_gmail_access()
            
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Callback request failed: {e}")

def test_gmail_access():
    """Test Gmail endpoints after authentication"""
    
    print("\n📧 Testing Gmail Access...")
    
    # Test Gmail stats
    try:
        response = requests.get(f"{BASE_URL}/gmail/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ Gmail stats accessible")
            print(f"📊 Local emails: {data['local_stats']['total_emails']}")
            print(f"📧 Gmail total: {data['gmail_stats']['total_emails']}")
        else:
            print(f"⚠️  Gmail stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Gmail stats error: {e}")
    
    # Test Gmail folders
    try:
        response = requests.get(f"{BASE_URL}/gmail/folders")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gmail folders: {data['total_folders']} found")
        else:
            print(f"⚠️  Gmail folders: {response.status_code}")
    except Exception as e:
        print(f"❌ Gmail folders error: {e}")

if __name__ == "__main__":
    print("Gmail Authentication & Access Test")
    print("Make sure your server is running on localhost:8000")
    print("Make sure you have GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env")
    
    if test_auth_flow():
        test_with_code()
    
    print("\n🎉 Test completed!")