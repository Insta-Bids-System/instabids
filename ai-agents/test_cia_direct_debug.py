#!/usr/bin/env python3
"""
Direct CIA endpoint debug test
"""

import requests
import json
import time
from config.service_urls import get_backend_url

def test_cia_direct():
    print("Testing CIA endpoint directly...")
    print("=" * 50)
    
    url = f"{get_backend_url()}/api/cia/stream"
    
    payload = {
        "messages": [{"role": "user", "content": "Hi, just testing"}],
        "conversation_id": "debug-test",
        "user_id": "debug-user",
        "max_tokens": 100,
        "model_preference": "gpt-4o"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        print("\nSending request...")
        response = requests.post(url, json=payload, headers=headers, 
                               stream=True, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return
        
        print("Reading stream...")
        chunk_count = 0
        for line in response.iter_lines():
            chunk_count += 1
            if line:
                line_text = line.decode('utf-8')
                print(f"Chunk {chunk_count}: {line_text[:100]}...")
                
                if chunk_count > 10:  # Limit output
                    print("(Truncating after 10 chunks)")
                    break
        
        response_time = time.time() - start_time
        print(f"\nCompleted in {response_time:.2f}s")
        
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        print(f"TIMEOUT after {response_time:.2f}s")
    except Exception as e:
        response_time = time.time() - start_time
        print(f"ERROR after {response_time:.2f}s: {e}")

def test_backend_health():
    print("\nTesting backend health...")
    try:
        response = requests.get(get_backend_url(), timeout=5)
        print(f"Backend health: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Backend health check failed: {e}")

if __name__ == "__main__":
    test_backend_health()
    test_cia_direct()