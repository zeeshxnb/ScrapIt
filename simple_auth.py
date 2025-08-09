#!/usr/bin/env python3
"""
Simple authentication helper for Gmail sync
"""
import requests
import webbrowser
import time
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def authenticate():
    """Simple authentication flow"""
    
    print("🔐 Gmail Authentication Setup")
    print("=" * 40)
    
    # Step 1: Get auth URL
    print("1. Getting Google OAuth URL...")
    try:
        response = requests.get(f"{BASE_URL}/auth/google")
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('auth_url')
            print(f"✅ Auth URL generated")
            print(f"🌐 Opening browser...")
            
            # Open browser
            webbrowser.open(auth_url)
            
            print("\n📝 INSTRUCTIONS:")
            print("1. Browser opened to Google OAuth")
            print("2. Login with your Gmail account")
            print("3. Grant permissions to access Gmail")
            print("4. You'll be redirected to localhost:3000")
            print("5. Look for '?token=' in the URL")
            print("6. Copy the token value")
            
            return True
        else:
            print(f"❌ Failed to get auth URL: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_token():
    """Test if you have a valid token"""
    
    print("\n🧪 Testing Authentication")
    print("=" * 30)
    
    token = input("📋 Paste your token from the URL (after ?token=): ").strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    # Test the token
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authentication successful!")
            print(f"👤 Email: {data.get('email')}")
            print(f"🆔 User ID: {data.get('id')}")
            
            # Save token for future use
            with open('.auth_token', 'w') as f:
                f.write(token)
            print(f"💾 Token saved to .auth_token file")
            
            # Test Gmail access
            test_gmail_access(token)
            return True
        else:
            print(f"❌ Token invalid: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

def test_gmail_access(token):
    """Test Gmail access with the token"""
    
    print("\n📧 Testing Gmail Access")
    print("=" * 25)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Gmail stats
    try:
        response = requests.get(f"{BASE_URL}/gmail/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gmail connected!")
            print(f"📊 Local emails: {data['local_stats']['total_emails']}")
            print(f"📧 Gmail total: {data['gmail_stats']['total_emails']}")
            print(f"📈 Coverage: {data['gmail_stats']['sync_coverage']}%")
            
            if data['gmail_stats']['total_emails'] > data['local_stats']['total_emails']:
                print(f"🚀 Ready to sync {data['gmail_stats']['total_emails'] - data['local_stats']['total_emails']} more emails!")
        else:
            print(f"⚠️  Gmail access issue: {response.status_code}")
    except Exception as e:
        print(f"❌ Gmail test error: {e}")

def use_saved_token():
    """Use previously saved token"""
    
    try:
        with open('.auth_token', 'r') as f:
            token = f.read().strip()
        
        print("🔑 Using saved token...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Saved token works!")
            print(f"👤 Email: {data.get('email')}")
            test_gmail_access(token)
            return True
        else:
            print("❌ Saved token expired")
            return False
    except FileNotFoundError:
        print("📄 No saved token found")
        return False
    except Exception as e:
        print(f"❌ Error with saved token: {e}")
        return False

def main():
    """Main authentication flow"""
    
    print("Gmail Sync Authentication Helper")
    print("Make sure both servers are running:")
    print("- Backend: http://localhost:8000")
    print("- Frontend: http://localhost:3000")
    print()
    
    # Try saved token first
    if use_saved_token():
        print("\n🎉 You're already authenticated!")
        return
    
    # Start new authentication
    if authenticate():
        print("\n⏳ Waiting for you to complete OAuth...")
        print("After you're redirected, come back here and paste the token.")
        test_token()

if __name__ == "__main__":
    main()