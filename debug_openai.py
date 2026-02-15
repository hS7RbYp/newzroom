#!/usr/bin/env python3
"""Debug Azure OpenAI connectivity"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print the credentials being used
print("=" * 60)
print("Azure OpenAI Credentials")
print("=" * 60)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

print(f"Endpoint: {endpoint}")
print(f"API Key (first 20 chars): {api_key[:20] if api_key else 'NOT SET'}...")
print(f"API Version: {api_version}")

if not endpoint or not api_key:
    print("\n[ERROR] Environment variables not set!")
    exit(1)

# Try to create a client and test
try:
    from openai import AzureOpenAI
    
    print("\nAttempting to create AzureOpenAI client...")
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    print("[OK] Client created successfully")
    
    # Try a simple API call
    print("\nAttempting API call with gpt-4o-mini...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Say 'success' in one word."},
            {"role": "user", "content": "Test"}
        ],
        temperature=0.5,
        max_tokens=10
    )
    
    print(f"[OK] Response received: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
