#!/usr/bin/env python3
"""
Simple single-turn CIA test to identify the exact problem
"""

import requests
import json
import time
from config.service_urls import get_backend_url

def test_single_turn():
    print("Testing single CIA conversation turn...")
    
    url = f"{get_backend_url()}/api/cia/stream"
    
    payload = {
        "messages": [{"role": "user", "content": "I need help with a bathroom remodel"}],
        "conversation_id": "single-test",
        "user_id": "test-user",
        "max_tokens": 200,
        "model_preference": "gpt-4o"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }, stream=True, timeout=15)  # Shorter timeout
        
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return
        
        print("Reading stream...")
        full_text = ""
        chunk_count = 0
        
        for line in response.iter_lines():
            chunk_count += 1
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data_part = line_text[6:]
                    if data_part.strip() == '[DONE]':
                        break
                    try:
                        chunk_data = json.loads(data_part)
                        if 'choices' in chunk_data and chunk_data['choices']:
                            delta = chunk_data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                full_text += delta['content']
                                print(f".", end="", flush=True)  # Progress indicator
                    except json.JSONDecodeError:
                        continue
            
            if chunk_count % 50 == 0:  # Progress every 50 chunks
                elapsed = time.time() - start_time
                print(f"\n[{elapsed:.1f}s] Processed {chunk_count} chunks...")
        
        elapsed = time.time() - start_time
        print(f"\n\nCOMPLETED in {elapsed:.2f} seconds")
        print(f"Response length: {len(full_text)} characters")
        print(f"Response: {full_text[:300]}{'...' if len(full_text) > 300 else ''}")
        
        return True
        
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"\nTIMEOUT after {elapsed:.2f} seconds")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\nERROR after {elapsed:.2f} seconds: {e}")
        return False

if __name__ == "__main__":
    success = test_single_turn()
    if success:
        print("\n✅ CIA streaming works - just slow")
    else:
        print("\n❌ CIA streaming has issues")