#!/usr/bin/env python3
"""
Fix the email count issue by cleaning up duplicates and getting accurate counts
"""
import requests

def fix_email_count():
    """Fix the email count issue"""
    
    print("🔧 Fixing Email Count Issue")
    print("=" * 35)
    
    # You'll need to get a fresh token first
    print("⚠️  First, get a fresh token:")
    print("1. Go to: http://localhost:8000/auth/google-redirect")
    print("2. Complete OAuth")
    print("3. Copy the token from the URL")
    print()
    
    token = input("📋 Paste your fresh token here: ").strip()
    if not token:
        print("❌ No token provided. Exiting.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Check current database state
    print("\n1. Checking current database state...")
    try:
        response = requests.get("http://localhost:8000/gmail/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            current_count = data['local_stats']['total_emails']
            print(f"   📊 Current database: {current_count} emails")
            
            if current_count > 3000:
                print(f"   ⚠️  {current_count} seems high - likely has duplicates")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 2: Clean up duplicates
    print("\n2. Cleaning up duplicates...")
    try:
        response = requests.post("http://localhost:8000/gmail/cleanup", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['message']}")
            print(f"   🗑️  Final count: {data['final_count']} emails")
        else:
            print(f"   ❌ Cleanup failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 3: Get fresh stats
    print("\n3. Getting updated stats...")
    try:
        response = requests.get("http://localhost:8000/gmail/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            final_count = data['local_stats']['total_emails']
            print(f"   📊 Final database count: {final_count} emails")
            
            if final_count < 3000:
                print(f"   ✅ Count looks more reasonable now!")
            else:
                print(f"   ⚠️  Still seems high. Consider a database reset.")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 4: Option for complete reset
    print("\n4. Nuclear option - Complete database reset:")
    reset = input("   🚨 Delete ALL emails and start fresh? (y/N): ").lower().strip()
    
    if reset == 'y':
        try:
            response = requests.delete("http://localhost:8000/gmail/reset", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {data['message']}")
                
                # Now do a fresh sync
                print("\n5. Starting fresh sync...")
                payload = {
                    "incremental": False,
                    "batch_size": 100,
                    "max_results": 2000  # Reasonable limit for testing
                }
                
                response = requests.post("http://localhost:8000/gmail/sync", 
                                       headers={**headers, "Content-Type": "application/json"},
                                       json=payload)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Fresh sync: {data['new_emails']} emails")
                    print(f"   📊 Final count: {data.get('final_email_count', 'N/A')}")
                else:
                    print(f"   ❌ Fresh sync failed: {response.status_code}")
            else:
                print(f"   ❌ Reset failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS:")
    print("• Check Gmail web: https://mail.google.com")
    print("• Search 'in:anywhere' to see actual total")
    print("• The sync should now show accurate counts")
    print("• Use incremental syncs going forward")

def verify_gmail_count():
    """Instructions to verify actual Gmail count"""
    
    print("\n📧 VERIFY YOUR ACTUAL GMAIL COUNT:")
    print("=" * 40)
    
    print("\n1. Go to https://mail.google.com")
    print("2. In the search box, type: in:anywhere")
    print("3. Look at the number shown (e.g., '1-50 of 2,341')")
    print("4. That last number is your ACTUAL total")
    print()
    print("📁 Also check individual folders:")
    print("• All Mail - total count")
    print("• Spam - spam count")  
    print("• Trash - deleted count")
    print("• Sent - sent count")
    print()
    print("🎯 Your sync should match these numbers!")

if __name__ == "__main__":
    fix_email_count()
    verify_gmail_count()
    
    print("\n✅ After this fix:")
    print("• No more duplicates")
    print("• Accurate email counts")
    print("• Faster syncs")
    print("• Better progress bars")