#!/usr/bin/env python3
"""Simple test to debug Azure OpenAI SDK configuration."""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import sys

# Load environment
load_dotenv()

print("=" * 60)
print("Azure OpenAI SDK Configuration Test")
print("=" * 60)

# Get config
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print(f"Endpoint: {endpoint}")
print(f"API Key (first 20): {api_key[:20] if api_key else 'MISSING'}...")
print(f"API Version: {api_version}")
print()

# Try to create client with different configurations
configs = [
    {
        "name": "Regional endpoint as-is",
        "endpoint": endpoint,
        "api_version": api_version,
    },
    {
        "name": "Regional endpoint without trailing slash",
        "endpoint": endpoint.rstrip("/"),
        "api_version": api_version,
    },
    {
        "name": "Regional endpoint with /openai/ path",
        "endpoint": endpoint.rstrip("/") + "/openai/",
        "api_version": api_version,
    },
]

for config in configs:
    print(f"\n[TEST] {config['name']}")
    print(f"   URL: {config['endpoint']}")
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=config['api_version'],
            azure_endpoint=config['endpoint']
        )
        print(f"   [OK] Client created")
        
        # Try to call the API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
        )
        print(f"   [OK] API call successful")
        print(f"   Response: {response.choices[0].message.content[:50]}")
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)[:100]
        print(f"   [ERROR] {error_type}: {error_msg}")

print("\n" + "=" * 60)
