#!/usr/bin/env python3
"""
Test the current token and Gmail sync
"""
import requests

def test_token():
    """Test the current token"""
    
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0NmQyZmQ1NS04NGU0LTQyNmYtYThlNy1jZWY4YTBlYzhhYmMiLCJleHAiOjE3NTQ3MTM3ODJ9.CdYRjj48_gV0thHvIMZLXI0iGSackHA10bT9hEPW24g"
    
    print("🧪 Testing Your Fresh Token")
    print("=" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Verify token
    print("1. Testing token validity...")
    try:
        response = requests.get("http://localhost:8000/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Token valid!")
            print(f"   👤 Email: {data['email']}")
        else:
            print(f"   ❌ Token invalid: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Test Gmail access
    print("\n2. Testing Gmail access...")
    try:
        response = requests.get("http://localhost:8000/gmail/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Gmail connected!")
            print(f"   📊 Local emails: {data['local_stats']['total_emails']}")
            print(f"   📧 Gmail total: {data['gmail_stats']['total_emails']}")
            print(f"   📈 Coverage: {data['gmail_stats']['sync_coverage']}%")
        else:
            print(f"   ❌ Gmail access issue: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Gmail error: {e}")
    
    # Test 3: Quick incremental sync
    print("\n3. Testing quick incremental sync...")
    try:
        payload = {
            "incremental": True,
            "batch_size": 50
        }
        response = requests.post("http://localhost:8000/gmail/sync", 
                               headers={**headers, "Content-Type": "application/json"},
                               json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sync successful!")
            print(f"   📥 New emails: {data['new_emails']}")
            print(f"   🔄 Updated: {data['updated_emails']}")
            print(f"   🏷️  All folders: {data.get('all_folders_synced', 'N/A')}")
        else:
            print(f"   ❌ Sync error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Sync error: {e}")
    
    print("\n🎉 Your token is working!")
    print("Now go to http://localhost:3000 and you should see the dashboard!")
    
    return True

if __name__ == "__main__":
    test_token()