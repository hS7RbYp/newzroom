#!/usr/bin/env python3
import requests
import sys

API_URL = "http://localhost:8000"

try:
    print(f"Testing connection to {API_URL}/api/approval/health...")
    resp = requests.get(f"{API_URL}/api/approval/health", timeout=5)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")
except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: {e}")
except Exception as e:
    print(f"Error: {e}")
    
# Also try to get stats
try:
    print(f"\nGetting queue stats...")
    resp = requests.get(f"{API_URL}/api/approval/queue/stats", timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Data: {resp.json()}")
except Exception as e:
    print(f"Stats Error: {e}")
