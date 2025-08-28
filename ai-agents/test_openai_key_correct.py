#!/usr/bin/env python3
"""
Test the correct OpenAI API key from base .env file
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import time

def test_openai_key():
    print("Testing OpenAI API Key from base .env file")
    print("=" * 50)
    
    # Load from root .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    print(f"Loading .env from: {env_path}")
    load_dotenv(env_path, override=True)
    
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        print("ERROR: No OPENAI_API_KEY found in .env")
        return False
    
    print(f"Using key: {key[:20]}...")
    
    try:
        client = OpenAI(api_key=key)
        
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Say 'API key working!' and nothing else."}
            ],
            max_tokens=10,
            timeout=15
        )
        end_time = time.time()
        
        message = response.choices[0].message.content
        response_time = end_time - start_time
        
        print(f"SUCCESS: {message}")
        print(f"Response time: {response_time:.2f} seconds")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage.total_tokens} tokens")
        
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    test_openai_key()