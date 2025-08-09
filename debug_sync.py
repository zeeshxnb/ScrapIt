#!/usr/bin/env python3
"""
Debug Gmail sync to see what's actually happening
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def debug_sync():
    """Debug the Gmail sync to see why it's only getting 100 emails"""
    
    print("🔍 Debugging Gmail Sync Issue")
    print("=" * 50)
    
    # First, check current stats
    print("\n1. Current Gmail Stats:")
    try:
        response = requests.get(f"{BASE_URL}/gmail/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Local emails: {data['local_stats']['total_emails']}")
            print(f"   📧 Gmail total: {data['gmail_stats']['total_emails']}")
            print(f"   📈 Coverage: {data['gmail_stats']['sync_coverage']}%")
            print(f"   🔗 Connected: {data['sync_status']['is_connected']}")
        else:
            print(f"   ❌ Stats error: {response.status_code}")
            if response.status_code == 401:
                print("   🔐 You need to authenticate first!")
                return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test different sync methods
    print("\n2. Testing Regular Sync (should be unlimited):")
    try:
        payload = {
            "incremental": False,  # Full sync
            "batch_size": 50       # Small batch for testing
        }
        print(f"   📤 Sending: {payload}")
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/gmail/sync", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data['message']}")
            print(f"   📥 New emails: {data['new_emails']}")
            print(f"   🔄 Updated: {data['updated_emails']}")
            print(f"   📦 Batches: {data.get('total_batches', 'N/A')}")
            print(f"   🏷️  All folders: {data.get('all_folders_synced', 'N/A')}")
            print(f"   🚫 No limits: {data.get('no_limits_applied', 'N/A')}")
            print(f"   ⏱️  Time: {end_time - start_time:.2f}s")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test full-sync endpoint
    print("\n3. Testing Full-Sync Endpoint:")
    try:
        payload = {"batch_size": 50}
        print(f"   📤 Sending: {payload}")
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/gmail/full-sync", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data['message']}")
            print(f"   📥 New emails: {data['new_emails']}")
            print(f"   🔄 Updated: {data['updated_emails']}")
            print(f"   📦 Batches: {data.get('total_batches', 'N/A')}")
            print(f"   🚫 No limits: {data.get('no_limits_applied', 'N/A')}")
            print(f"   ⏱️  Time: {end_time - start_time:.2f}s")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check final stats
    print("\n4. Final Gmail Stats:")
    try:
        response = requests.get(f"{BASE_URL}/gmail/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Local emails: {data['local_stats']['total_emails']}")
            print(f"   📧 Gmail total: {data['gmail_stats']['total_emails']}")
            print(f"   📈 Coverage: {data['gmail_stats']['sync_coverage']}%")
        else:
            print(f"   ❌ Stats error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Analysis:")
    print("- If 'No limits: true' but still only 100 emails, it might be:")
    print("  1. Gmail API returning limited results")
    print("  2. Query not finding more emails")
    print("  3. Rate limiting stopping early")
    print("  4. Database issues")
    print("- Check server logs for more details")

def test_specific_query():
    """Test with a specific query to see if it's a query issue"""
    
    print("\n🔍 Testing Specific Query")
    print("=" * 30)
    
    # Test syncing just inbox
    try:
        payload = {
            "labels": ["INBOX"],
            "batch_size": 50,
            "incremental": False
        }
        print(f"📤 Testing INBOX only: {payload}")
        
        response = requests.post(f"{BASE_URL}/gmail/sync-folders", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ INBOX sync: {data['new_emails']} new emails")
            print(f"🏷️  Labels: {data.get('synced_labels', 'N/A')}")
        else:
            print(f"❌ INBOX sync error: {response.status_code}")
            print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Gmail Sync Debug Tool")
    print("Make sure you're authenticated first!")
    
    debug_sync()
    test_specific_query()
    
    print("\n💡 If still getting 100 emails:")
    print("1. Check server terminal for detailed logs")
    print("2. Try: python test_auth.py to re-authenticate")
    print("3. Check Gmail API quotas in Google Console")
    print("4. Verify your Gmail account has more than 100 emails")