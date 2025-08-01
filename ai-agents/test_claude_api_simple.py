#!/usr/bin/env python3
"""
Simple test of Claude API authentication
"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic

def test_claude_api():
    """Test basic Claude API call"""
    
    # Load environment variables
    load_dotenv(override=True)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    print(f"API Key loaded: {api_key[:15]}... (length: {len(api_key) if api_key else 0})")
    
    if not api_key:
        print("ERROR: No API key found")
        return
    
    try:
        client = Anthropic(api_key=api_key)
        
        print("Making test API call...")
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=50,
            messages=[{
                "role": "user", 
                "content": "Say hello"
            }]
        )
        
        print("SUCCESS!")
        print(f"Response: {response.content[0].text}")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_claude_api()