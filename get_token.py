#!/usr/bin/env python3
"""
Simple script to help get your authentication token
"""
import webbrowser
import time

def get_token():
    """Help user get authentication token"""
    
    print("🔐 Getting Your Gmail Authentication Token")
    print("=" * 50)
    
    print("\n📋 STEP 1: Open Authentication URL")
    auth_url = "http://localhost:8000/auth/google-redirect"
    print(f"Opening: {auth_url}")
    
    # Open browser
    webbrowser.open(auth_url)
    
    print("\n📝 STEP 2: Complete OAuth Flow")
    print("1. Browser opened to Google OAuth")
    print("2. Login with your Gmail account")
    print("3. Grant permissions to access Gmail")
    print("4. You'll see a page with your token displayed clearly")
    
    print("\n📋 STEP 3: Copy Your Token")
    print("The page will show your JWT token in a text box")
    print("Copy the entire token (it's very long)")
    
    print("\n🧪 STEP 4: Test Your Token")
    token = input("\nPaste your token here to test it: ").strip()
    
    if token:
        test_token(token)
    else:
        print("❌ No token provided")
        print("\n💡 Manual testing:")
        print("Replace YOUR_TOKEN in this command:")
        print('curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/auth/test-token')

def test_token(token):
    """Test if the token works"""
    
    import requests
    
    print(f"\n🧪 Testing token...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/auth/test-token", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token is valid!")
            print(f"👤 Email: {data['user']['email']}")
            print(f"🆔 User ID: {data['user']['id']}")
            
            # Test Gmail access
            print(f"\n📧 Testing Gmail access...")
            response = requests.get("http://localhost:8000/gmail/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Gmail access working!")
                print(f"📊 Local emails: {data['local_stats']['total_emails']}")
                print(f"📧 Gmail total: {data['gmail_stats']['total_emails']}")
                
                # Test full sync
                print(f"\n🚀 Ready to test full sync!")
                print("Run this command to sync ALL your emails:")
                print(f'curl -X POST "http://localhost:8000/gmail/full-sync" \\')
                print(f'  -H "Authorization: Bearer {token}" \\')
                print(f'  -H "Content-Type: application/json" \\')
                print(f'  -d \'{{"batch_size": 100}}\'')
                
            else:
                print(f"⚠️  Gmail access issue: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"❌ Token invalid: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")

if __name__ == "__main__":
    print("Gmail Token Helper")
    print("Make sure your servers are running:")
    print("- Backend: http://localhost:8000")
    print("- Frontend: http://localhost:3000")
    print()
    
    get_token()