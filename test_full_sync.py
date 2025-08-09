#!/usr/bin/env python3
"""
Test the full sync functionality to ensure it gets ALL emails
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_full_sync():
    """Test that full sync actually gets all emails"""
    
    print("🔥 Testing FULL SYNC - Should get ALL emails")
    print("=" * 50)
    
    # Get initial stats
    print("1. Initial Gmail Stats:")
    try:
        response = requests.get(f"{BASE_URL}/gmail/stats")
        if response.status_code == 200:
            data = response.json()
            initial_local = data['local_stats']['total_emails']
            gmail_total = data['gmail_stats']['total_emails']
            print(f"   📊 Local emails: {initial_local}")
            print(f"   📧 Gmail total: {gmail_total}")
            print(f"   📈 Coverage: {data['gmail_stats']['sync_coverage']}%")
            
            if initial_local >= gmail_total:
                print("   ✅ Already fully synced!")
                return
        else:
            print(f"   ❌ Stats error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test full sync with explicit parameters
    print("\n2. Running FULL SYNC (no limits, all folders):")
    try:
        payload = {
            "incremental": False,    # FULL sync
            "max_results": None,     # NO limits
            "batch_size": 100
        }
        print(f"   📤 Parameters: {payload}")
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/gmail/sync", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['message']}")
            print(f"   📥 New emails: {data['new_emails']}")
            print(f"   🔄 Updated: {data['updated_emails']}")
            print(f"   📦 Batches: {data.get('total_batches', 'N/A')}")
            print(f"   🏷️  All folders: {data.get('all_folders_synced', 'N/A')}")
            print(f"   🚫 No limits: {data.get('no_limits_applied', 'N/A')}")
            print(f"   🔍 Query: {data.get('query_used', 'N/A')}")
            print(f"   ⏱️  Duration: {end_time - start_time:.2f}s")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Check final stats
    print("\n3. Final Gmail Stats:")
    try:
        response = requests.get(f"{BASE_URL}/gmail/stats")
        if response.status_code == 200:
            data = response.json()
            final_local = data['local_stats']['total_emails']
            gmail_total = data['gmail_stats']['total_emails']
            coverage = data['gmail_stats']['sync_coverage']
            
            print(f"   📊 Local emails: {final_local}")
            print(f"   📧 Gmail total: {gmail_total}")
            print(f"   📈 Coverage: {coverage}%")
            
            # Analysis
            print(f"\n📈 RESULTS:")
            print(f"   📥 Emails added: {final_local - initial_local}")
            if coverage >= 99:
                print("   🎉 SUCCESS: Nearly complete sync!")
            elif coverage >= 90:
                print("   ✅ GOOD: Most emails synced")
            elif final_local > initial_local:
                print("   ⚠️  PARTIAL: Some emails synced, but not all")
            else:
                print("   ❌ ISSUE: No new emails synced")
                
        else:
            print(f"   ❌ Stats error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_frontend_behavior():
    """Test what happens when frontend calls with no parameters (like before)"""
    
    print("\n4. Testing Frontend-style Call (no parameters):")
    try:
        # This simulates what the frontend was doing before
        response = requests.post(f"{BASE_URL}/gmail/sync")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['message']}")
            print(f"   📥 New emails: {data['new_emails']}")
            print(f"   🔄 Sync type: {data.get('sync_type', 'N/A')}")
            print(f"   🚫 No limits: {data.get('no_limits_applied', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("Full Sync Test - Verify ALL emails are synced")
    print("Make sure you're authenticated first!")
    
    test_full_sync()
    test_frontend_behavior()
    
    print("\n💡 Key Points:")
    print("- Default is now FULL sync (not incremental)")
    print("- No limits applied by default")
    print("- Frontend now sends explicit parameters")
    print("- Should sync ALL emails from ALL folders")