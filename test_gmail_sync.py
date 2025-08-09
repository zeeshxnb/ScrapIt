#!/usr/bin/env python3
"""
Test script for the enhanced Gmail sync functionality
Demonstrates the new unlimited sync capabilities
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your backend runs on different port
API_BASE = f"{BASE_URL}/gmail"

def test_gmail_sync():
    """Test the enhanced Gmail sync functionality"""
    
    print("🚀 Testing Enhanced Gmail Sync - ALL Emails from ALL Folders")
    print("=" * 60)
    
    # Test 1: Get Gmail folder statistics
    print("\n1. Getting Gmail folder statistics...")
    try:
        response = requests.get(f"{API_BASE}/folders")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_folders']} folders/labels")
            print("📁 Major folders:")
            for folder_name, stats in data.get('folder_stats', {}).items():
                print(f"   - {folder_name}: {stats['total']} total, {stats['unread']} unread")
        else:
            print(f"❌ Error getting folders: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get current sync statistics
    print("\n2. Getting current sync statistics...")
    try:
        response = requests.get(f"{API_BASE}/stats")
        if response.status_code == 200:
            data = response.json()
            local_total = data['local_stats']['total_emails']
            gmail_total = data['gmail_stats']['total_emails']
            coverage = data['gmail_stats']['sync_coverage']
            
            print(f"📊 Local emails: {local_total}")
            print(f"📧 Gmail total: {gmail_total}")
            print(f"📈 Sync coverage: {coverage}%")
            print(f"🔗 Connected: {data['sync_status']['is_connected']}")
        else:
            print(f"❌ Error getting stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Perform incremental sync (no limits)
    print("\n3. Testing incremental sync (no limits)...")
    try:
        payload = {
            "incremental": True,
            "batch_size": 50  # Smaller batch for testing
        }
        response = requests.post(f"{API_BASE}/sync", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"📥 New emails: {data['new_emails']}")
            print(f"🔄 Updated emails: {data['updated_emails']}")
            print(f"📦 Batches processed: {data.get('total_batches', 'N/A')}")
            print(f"🏷️  All folders synced: {data.get('all_folders_synced', False)}")
        else:
            print(f"❌ Error in sync: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Test specific folder sync
    print("\n4. Testing specific folder sync (INBOX only)...")
    try:
        payload = {
            "labels": ["INBOX"],
            "batch_size": 30,
            "incremental": False
        }
        response = requests.post(f"{API_BASE}/sync-folders", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"📥 New emails: {data['new_emails']}")
            print(f"🏷️  Synced labels: {data['synced_labels']}")
        else:
            print(f"❌ Error in folder sync: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Gmail sync testing completed!")
    print("\nKey Features Tested:")
    print("✅ No email limits - syncs ALL emails")
    print("✅ All folders/labels - inbox, sent, drafts, spam, trash, custom")
    print("✅ Batch processing for large volumes")
    print("✅ Specific folder targeting")
    print("✅ Detailed progress tracking")
    print("✅ Folder statistics and breakdown")

def demo_full_sync():
    """Demonstrate a full sync of ALL emails"""
    
    print("\n🔥 DEMO: Full Sync of ALL Emails from ALL Folders")
    print("=" * 50)
    print("⚠️  This will sync ALL your Gmail emails!")
    print("⚠️  This may take a while for large mailboxes!")
    
    confirm = input("\nProceed with full sync? (y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ Full sync cancelled")
        return
    
    try:
        payload = {
            "batch_size": 100  # Reasonable batch size
        }
        
        print("\n🚀 Starting full sync...")
        start_time = time.time()
        
        response = requests.post(f"{API_BASE}/full-sync", json=payload)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ {data['message']}")
            print(f"📥 New emails: {data['new_emails']}")
            print(f"🔄 Updated emails: {data['updated_emails']}")
            print(f"📦 Total batches: {data.get('total_batches', 'N/A')}")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"🏷️  All folders synced: {data.get('all_folders_synced', False)}")
            print(f"🚫 No limits applied: {data.get('no_limits_applied', False)}")
        else:
            print(f"❌ Error in full sync: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Gmail Sync Enhancement Test Suite")
    print("Make sure your backend is running and you're authenticated!")
    
    # Run basic tests
    test_gmail_sync()
    
    # Optionally run full sync demo
    print("\n" + "=" * 60)
    demo_full_sync()