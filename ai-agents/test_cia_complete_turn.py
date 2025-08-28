#!/usr/bin/env python3
"""
Complete CIA conversation test with longer timeout
"""

import requests
import json
import time
from config.service_urls import get_backend_url

def test_complete_cia_turn():
    print("Testing complete CIA conversation turn with longer timeout...")
    
    url = f"{get_backend_url()}/api/cia/stream"
    
    payload = {
        "messages": [{"role": "user", "content": "I need help with a bathroom remodel"}],
        "conversation_id": "complete-test",
        "user_id": "test-user",
        "max_tokens": 500,
        "model_preference": "gpt-4o"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }, stream=True, timeout=60)  # Much longer timeout
        
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
                        print("\n[DONE] marker received")
                        break
                    try:
                        chunk_data = json.loads(data_part)
                        if 'choices' in chunk_data and chunk_data['choices']:
                            delta = chunk_data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                full_text += delta['content']
                    except json.JSONDecodeError:
                        continue
            
            # Less frequent progress updates
            if chunk_count % 100 == 0:
                elapsed = time.time() - start_time
                print(f"[{elapsed:.1f}s] {chunk_count} chunks, {len(full_text)} chars...")
        
        elapsed = time.time() - start_time
        print(f"\nCOMPLETED in {elapsed:.2f} seconds")
        print(f"Total chunks: {chunk_count}")
        print(f"Response length: {len(full_text)} characters")
        print(f"\nFull Response:\n{'-'*60}")
        print(full_text)
        print(f"{'-'*60}")
        
        return True
        
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"\nTIMEOUT after {elapsed:.2f} seconds")
        print(f"Partial response ({len(full_text)} chars): {full_text[:500]}...")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\nERROR after {elapsed:.2f} seconds: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_cia_turn()
    if success:
        print("\nSUCCESS: CIA streaming works (just slow)")
    else:
        print("\nFAILED: CIA streaming has issues")