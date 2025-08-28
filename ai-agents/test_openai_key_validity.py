#!/usr/bin/env python3
"""
Test if the OpenAI API key is valid
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory
root_env = Path(__file__).parent.parent / '.env'
if root_env.exists():
    load_dotenv(root_env, override=True)
else:
    load_dotenv(override=True)

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {api_key[:20]}...{api_key[-10:]}")

# Test with OpenAI
from openai import OpenAI

try:
    client = OpenAI(api_key=api_key)
    
    # Simple test call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'test successful'"}],
        max_tokens=10
    )
    
    print("SUCCESS: OpenAI API key is valid!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"ERROR: OpenAI API key is invalid!")
    print(f"Error: {e}")
    sys.exit(1)