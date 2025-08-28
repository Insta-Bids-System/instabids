#!/usr/bin/env python3

import requests
import json
import uuid
import time
from config.service_urls import get_backend_url

def test_cia_with_requests():
    """Simple test with requests library instead of aiohttp"""
    
    print("Testing CIA API with requests...")
    
    url = f"{get_backend_url()}/api/cia/stream"
    
    test_data = {
        "messages": [{"role": "user", "content": "I need bathroom work but I'm on a tight budget, only $5000"}],
        "conversation_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "max_completion_tokens": 300,
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
            timeout=10
        )
        
        print(f"HTTP Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"ERROR Response: {response.text}")
            return False
        
        # Read first few lines of streaming response
        line_count = 0
        found_error = False
        found_response = False
        
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(f"Line {line_count}: {line}")
                line_count += 1
                
                # Check for error patterns
                if "technical difficulties" in line.lower():
                    found_error = True
                    print("FOUND ERROR MESSAGE!")
                
                # Check for actual response content
                if "data:" in line and len(line) > 20:
                    found_response = True
                    
                # Only read first 5 lines
                if line_count >= 5:
                    break
        
        elapsed = time.time() - start_time
        print(f"Time taken: {elapsed:.2f} seconds")
        
        if found_error:
            print("FIX FAILED - Still getting technical difficulties")
            return False
        elif found_response:
            print("FIX SUCCESS - Getting actual responses")
            return True
        else:
            print("UNCLEAR - No clear error or response detected")
            return False
            
    except requests.exceptions.Timeout:
        print("TIMEOUT - Request took too long")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_cia_with_requests()
    if success:
        print("\nCIA API appears to be working!")
    else:
        print("\nCIA API still has issues")