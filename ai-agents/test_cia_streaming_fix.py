#!/usr/bin/env python3
"""
Test CIA Streaming - Identify and Fix Timeout Issues
"""

import asyncio
import json
import requests
from datetime import datetime

def test_cia_streaming_endpoint():
    """Test the CIA streaming endpoint directly"""
    print("Testing CIA streaming endpoint...")
    
    url = "http://localhost:8008/api/cia/stream"
    payload = {
        "messages": [{"role": "user", "content": "I need help with a small kitchen project"}],
        "user_id": "test-user-streaming",
        "conversation_id": "test-conversation-streaming"
    }
    
    try:
        print(f"Sending request to {url}")
        print(f"Payload: {payload}")
        
        # Use stream=True to handle Server-Sent Events
        response = requests.post(
            url, 
            json=payload, 
            stream=True,
            timeout=30  # 30 second timeout to test if it responds quickly
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Endpoint responded successfully!")
            
            # Read the first few streaming chunks
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"Chunk {chunk_count}: {decoded_line[:100]}...")
                    chunk_count += 1
                    
                    # Stop after 5 chunks to avoid long test
                    if chunk_count >= 5:
                        print("Stopping after 5 chunks to avoid long test")
                        break
        else:
            print(f"ERROR: Endpoint failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("TIMEOUT: Request timed out after 30 seconds - this confirms the timeout issue")
    except Exception as e:
        print(f"ERROR: Error testing endpoint: {e}")

def test_cia_opening_message():
    """Test simpler CIA endpoint first"""
    print("\nTesting CIA opening message endpoint...")
    
    try:
        response = requests.get("http://localhost:8008/api/cia/opening-message", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Opening message endpoint works!")
            print(f"Message: {data.get('message', '')[:100]}...")
        else:
            print(f"ERROR: Opening message failed: {response.status_code}")
    except Exception as e:
        print(f"ERROR: Error testing opening message: {e}")

def main():
    """Run streaming tests"""
    print("CIA Streaming Test Suite")
    print("=" * 50)
    
    # Test simple endpoint first
    test_cia_opening_message()
    
    # Test streaming endpoint
    test_cia_streaming_endpoint()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()