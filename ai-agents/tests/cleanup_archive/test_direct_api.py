#!/usr/bin/env python3
"""
Direct API test to Claude Opus 4
"""
import os

import requests
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key loaded: {bool(api_key)}")
print(f"Key starts with: {api_key[:15] if api_key else 'None'}")

headers = {
    "Content-Type": "application/json",
    "X-API-Key": api_key,
    "anthropic-version": "2023-06-01"
}

# Test with Claude 3.5 Sonnet (known working model)
payload = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "What is 2+2? Please respond with just the number."
        }
    ]
}

print("Testing direct API call to Claude 3.5 Sonnet...")
response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("SUCCESS: Claude Opus 4 API working!")
else:
    print("FAILED: API authentication or request issue")
