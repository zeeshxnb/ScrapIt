#!/usr/bin/env python3
"""
Quick server test to check if Gmail endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_server():
    """Test if the server is running and endpoints are accessible"""
    
    print("🧪 Testing ScrapIt server...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not reachable: {e}")
        return False
    
    # Test 2: Check if Gmail endpoints exist
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API docs accessible")
        else:
            print(f"⚠️  API docs status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  API docs not accessible: {e}")
    
    # Test 3: Try Gmail stats endpoint (will fail without auth, but should exist)
    try:
        response = requests.get(f"{BASE_URL}/gmail/stats", timeout=5)
        if response.status_code == 401:
            print("✅ Gmail endpoints exist (authentication required)")
        elif response.status_code == 422:
            print("✅ Gmail endpoints exist (validation error)")
        else:
            print(f"⚠️  Gmail stats response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Gmail endpoints not accessible: {e}")
        return False
    
    print("\n🎉 Server test completed!")
    return True

if __name__ == "__main__":
    test_server()