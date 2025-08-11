#!/usr/bin/env python3
"""
Fix duplicate email issues and optimize sync
"""
import requests

def fix_duplicate_emails():
    """Fix the duplicate email problem"""
    
    print("🔧 Fixing Duplicate Email Issues")
    print("=" * 40)
    
    # Get auth token
    try:
        with open('.auth_token', 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("❌ No auth token found. Please authenticate first.")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Check current stats
    print("1. Checking current email stats...")
    try:
        response = requests.get("http://localhost:8000/gmail/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            local_count = data['local_stats']['total_emails']
            gmail_count = data['gmail_stats']['total_emails']
            
            print(f"   📊 Local database: {local_count} emails")
            print(f"   📧 Gmail total: {gmail_count} emails")
            
            if local_count > gmail_count:
                print(f"   ⚠️  Database has MORE emails than Gmail ({local_count} vs {gmail_count})")
                print("   This indicates duplicate entries in the database")
            elif local_count == gmail_count:
                print("   ✅ Counts match - no duplicates detected")
                return True
            else:
                print(f"   📥 Database has fewer emails - {gmail_count - local_count} emails to sync")
        else:
            print(f"   ❌ Error getting stats: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 2: Clean up duplicates
    print("\n2. Cleaning up duplicate emails...")
    try:
        response = requests.post("http://localhost:8000/gmail/cleanup", headers=headers)
        if response.status_code == 200:
            data = response.json()
            duplicates_removed = data.get('duplicates_removed', 0)
            final_count = data.get('final_count', 0)
            
            print(f"   ✅ Cleanup completed!")
            print(f"   🗑️  Removed {duplicates_removed} duplicate emails")
            print(f"   📊 Final count: {final_count} emails")
        else:
            print(f"   ❌ Cleanup failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Cleanup error: {e}")
        return False
    
    # Step 3: Verify fix
    print("\n3. Verifying the fix...")
    try:
        response = requests.get("http://localhost:8000/gmail/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            local_count = data['local_stats']['total_emails']
            gmail_count = data['gmail_stats']['total_emails']
            
            print(f"   📊 Local database: {local_count} emails")
            print(f"   📧 Gmail total: {gmail_count} emails")
            
            if local_count <= gmail_count:
                print("   ✅ Fix successful! No more duplicates.")
                return True
            else:
                print("   ⚠️  Still have more local emails than Gmail")
                return False
        else:
            print(f"   ❌ Error verifying: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Verification error: {e}")
        return False

def optimize_sync_behavior():
    """Provide recommendations for better sync behavior"""
    
    print("\n💡 Sync Optimization Recommendations")
    print("=" * 40)
    
    print("✅ For daily use:")
    print("   • Use incremental sync: {'incremental': true}")
    print("   • This only gets NEW emails since last sync")
    print("   • Much faster and prevents duplicates")
    
    print("\n✅ For full refresh:")
    print("   • First run cleanup to remove duplicates")
    print("   • Then run full sync if needed")
    print("   • Or better: reset database and sync fresh")
    
    print("\n✅ Best practices:")
    print("   • Run cleanup weekly to prevent duplicate buildup")
    print("   • Use incremental sync for regular updates")
    print("   • Only use full sync for initial setup or major issues")

def test_incremental_sync():
    """Test incremental sync to show it works better"""
    
    print("\n🧪 Testing Incremental Sync")
    print("=" * 30)
    
    try:
        with open('.auth_token', 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("❌ No auth token found")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Running incremental sync (only gets new emails)...")
    try:
        payload = {
            "incremental": True,
            "batch_size": 100
        }
        response = requests.post("http://localhost:8000/gmail/sync", 
                               headers={**headers, "Content-Type": "application/json"},
                               json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Incremental sync completed!")
            print(f"   📥 New emails: {data.get('new_emails', 0)}")
            print(f"   🔄 Updated emails: {data.get('updated_emails', 0)}")
            print(f"   ⚡ Much faster than full sync!")
            return True
        else:
            print(f"❌ Incremental sync failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Duplicate Email Fix & Sync Optimization")
    print("This will fix your duplicate email issues")
    print()
    
    if fix_duplicate_emails():
        print("\n🎉 Duplicate emails fixed!")
        optimize_sync_behavior()
        
        print("\n🧪 Want to test incremental sync?")
        test_incremental_sync()
        
        print("\n✅ Your email sync is now optimized!")
        print("Use incremental sync for daily updates to avoid duplicates.")
    else:
        print("\n❌ Fix failed. You may need to reset the database:")
        print("Run: curl -X DELETE http://localhost:8000/gmail/reset -H 'Authorization: Bearer YOUR_TOKEN'")
        print("Then do a fresh full sync.")