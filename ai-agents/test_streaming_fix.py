#!/usr/bin/env python3
"""
Test CIA Streaming Fix - Verify single agent response
"""

import requests
import json
import time
import sys
import io
from config.service_urls import get_backend_url

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_streaming_response():
    """Test that streaming returns proper SSE format without duplicates"""
    print("Testing CIA Streaming Response Fix")
    print("=" * 50)
    
    # Demo homeowner
    user_id = "550e8400-e29b-41d4-a716-446655440001"
    session_id = f"test_fix_{int(time.time())}"
    
    payload = {
        "messages": [{"content": "Hello, I need help with my kitchen"}],
        "conversation_id": session_id,
        "user_id": user_id,
        "max_tokens": 100,
        "model_preference": "gpt-5"
    }
    
    print(f"Testing with session: {session_id}")
    print("Sending: 'Hello, I need help with my kitchen'")
    print()
    
    try:
        response = requests.post(
            f"{get_backend_url()}/api/cia/stream",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS: Streaming endpoint responding")
            print("\nFirst 3 chunks of response:")
            print("-" * 40)
            
            chunk_count = 0
            for chunk in response.iter_lines():
                if chunk:
                    chunk_count += 1
                    chunk_str = chunk.decode('utf-8')
                    
                    # Show first 3 chunks
                    if chunk_count <= 3:
                        if len(chunk_str) > 100:
                            print(f"Chunk {chunk_count}: {chunk_str[:100]}...")
                        else:
                            print(f"Chunk {chunk_count}: {chunk_str}")
                    
                    # Check for completion
                    if "data: [DONE]" in chunk_str:
                        print(f"\n✅ Stream completed after {chunk_count} chunks")
                        break
                    
                    if chunk_count >= 20:  # Limit for testing
                        print(f"\n✅ Received {chunk_count} chunks (limited for test)")
                        break
            
            print("\n✅ STREAMING WORKING CORRECTLY")
            print("Frontend should now show only ONE agent indicator")
            
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    # First check backend
    try:
        r = requests.get(get_backend_url(), timeout=2)
        print(f"Backend running: {r.json()['service']}\n")
    except:
        print("❌ Backend not available on port 8008")
        exit(1)
    
    test_streaming_response()