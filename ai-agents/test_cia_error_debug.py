#!/usr/bin/env python3

import requests
import json
import uuid
import time
from config.service_urls import get_backend_url

def test_cia_debug():
    """Debug test to see exactly what error we're getting"""
    
    print("Testing CIA API to debug specific errors...")
    
    url = f"{get_backend_url()}/api/cia/stream"
    
    test_data = {
        "messages": [{"role": "user", "content": "Hello, I need help with a simple bathroom upgrade"}],
        "conversation_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "max_completion_tokens": 100,
        "model_preference": "gpt-5"
    }
    
    try:
        start_time = time.time()
        
        response = requests.post(
            url,
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"  
            },
            stream=True,
            timeout=5  # Very short timeout to see immediate response
        )
        
        print(f"HTTP Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"ERROR Response: {response.text}")
            return False
        
        # Read streaming response line by line  
        line_count = 0
        lines = []
        
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(f"Raw line {line_count}: {repr(line)}")
                lines.append(line)
                line_count += 1
                
                # Stop after a few lines to prevent hanging
                if line_count >= 3:
                    break
        
        elapsed = time.time() - start_time
        print(f"Time taken: {elapsed:.2f} seconds")
        
        # Analyze what we got
        for line in lines:
            if "technical difficulties" in line.lower():
                print("FOUND: Technical difficulties error")
                return False
            elif "data:" in line and len(line) > 10:
                print("FOUND: Actual streaming data")
                return True
        
        print("UNCLEAR: Got response but not sure if it's working")
        return False
            
    except requests.exceptions.Timeout:
        print("TIMEOUT: Quick timeout hit - server may be hanging")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_cia_debug()