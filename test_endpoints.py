#!/usr/bin/env python3
"""Test different endpoint formats for Azure OpenAI."""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print("=" * 70)
print("Testing Azure OpenAI Endpoint Formats")
print("=" * 70)

# Test different endpoint formats
endpoints = [
    ("Regional (current)", "https://eastus.api.cognitive.microsoft.com/"),
    ("Instance-specific (.openai.azure.com)", "https://aan-dev-openai.openai.azure.com/"),
    ("Instance with region (.eastus.openai.azure.com)", "https://aan-dev-openai.eastus.openai.azure.com/"),
    ("Instance with region pattern 2", "https://aan-dev-openai.eastus.api.cognitive.microsoft.com/"),
]

for name, endpoint in endpoints:
    print(f"\n[TEST] {name}")
    print(f"  Endpoint: {endpoint}")
    
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        print(f"  Client: [OK]")
        
        #Try API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10,
        )
        print(f"  API Call: [OK]")
        print(f"  Success! Response: {response.choices[0].message.content[:40]}")
        break  # Stop on first success
        
    except Exception as e:
        error_type = type(e).__name__
        msg = str(e)[:80]
        print(f"  {error_type}: {msg}")

print("\n" + "=" * 70)
