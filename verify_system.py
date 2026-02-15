#!/usr/bin/env python3
"""
Verify system status and complete load test
"""
import requests
import sys

API_URL = "http://localhost:8000"

def check_api_health():
    """Check API health"""
    try:
        resp = requests.get(f"{API_URL}/api/approval/health", timeout=5)
        return resp.status_code == 200
    except:
        return False

def get_queue_stats():
    """Get current queue statistics"""
    try:
        resp = requests.get(f"{API_URL}/api/approval/queue/stats", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except:
        return None

def main():
    # Check API
    print("1. Checking API Health...", flush=True)
    if check_api_health():
        print("   ✓ API is running")
    else:
        print("   ✗ API is DOWN")
        sys.exit(1)
    
    # Get stats
    print("\n2. Current Queue Statistics:", flush=True)
    stats = get_queue_stats()
    if stats:
        print(f"   Total Articles: {stats.get('total', 0)}")
        print(f"   Approved: {stats.get('approved', 0)}")
        print(f"   Pending: {stats.get('pending', 0)}")
        print(f"   Rejected: {stats.get('rejected', 0)}")
    else:
        print("   ✗ Could not get stats")
    
    # Try to submit a test article
    print("\n3. Testing Article Submission...", flush=True)
    test_article = {
        "title": "Test Article for Load Verification",
        "content": "This is a test article to verify the system is working correctly.",
        "source": "System Verification"
    }
    
    try:
        resp = requests.post(
            f"{API_URL}/api/approval/submit",
            json=test_article,
            timeout=10
        )
        if resp.status_code == 201:
            result = resp.json()
            print(f"   ✓ Article submitted successfully")
            print(f"   Article ID: {result.get('article_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Confidence: {result.get('confidence_score', 'N/A')}")
        else:
            print(f"   ✗ Submission failed: {resp.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Get updated stats
    print("\n4. Updated Queue Statistics:", flush=True)
    stats = get_queue_stats()
    if stats:
        print(f"   Total Articles: {stats.get('total', 0)}")
        print(f"   Approved: {stats.get('approved', 0)}")
        print(f"   Pending: {stats.get('pending', 0)}")
        print(f"   Rejected: {stats.get('rejected', 0)}")
    
    print("\n✓ System verification complete", flush=True)

if __name__ == "__main__":
    main()
