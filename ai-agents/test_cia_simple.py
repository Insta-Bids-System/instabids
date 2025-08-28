#!/usr/bin/env python3
"""
Simple CIA Test - Debug streaming issues
"""

import requests
import json
import os
from config.service_urls import get_backend_url

def test_openai_key():
    """Check if OpenAI API key is available"""
    print("Checking OpenAI API Key...")
    
    # Check environment
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"SUCCESS: OpenAI API key found (length: {len(openai_key)})")
        return True
    else:
        print("ERROR: No OpenAI API key found in environment")
        return False

def test_streaming_with_simple_data():
    """Test streaming with minimal data"""
    print("\nTesting CIA Stream with minimal data...")
    
    payload = {
        "messages": [{"content": "Hello"}],
        "conversation_id": "simple_test",
        "user_id": "550e8400-e29b-41d4-a716-446655440001"
    }
    
    try:
        print("Making request...")
        response = requests.post(
            f"{get_backend_url()}/api/cia/stream",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
            stream=True  # Enable streaming
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\nStreaming response:")
            print("-" * 30)
            
            # Read streaming response
            for i, chunk in enumerate(response.iter_content(chunk_size=1024, decode_unicode=True)):
                if chunk:
                    print(f"Chunk {i+1}: {chunk[:200]}...")
                    if i >= 3:  # Limit output
                        print("(truncated)")
                        break
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("Request timed out (endpoint might be working but slow)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Simple CIA Streaming Test")
    print("=" * 40)
    
    # Check API key first
    if test_openai_key():
        test_streaming_with_simple_data()
    else:
        print("\nCannot test without OpenAI API key")