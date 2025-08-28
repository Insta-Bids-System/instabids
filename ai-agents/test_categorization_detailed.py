"""Detailed categorization test with full logging"""
import requests
import json
import time
import uuid
from datetime import datetime

print("=" * 60)
print(f"CATEGORIZATION TEST - {datetime.now().isoformat()}")
print("=" * 60)

# Test message
message = "I need artificial turf installed in my backyard"
print(f"\nTest message: {message}")

# Unique UUIDs for this test (database expects proper UUIDs)
user_id = str(uuid.uuid4())
conv_id = str(uuid.uuid4())

print(f"User ID: {user_id}")
print(f"Conv ID: {conv_id}")

url = "http://localhost:8008/api/cia/stream"
payload = {
    "messages": [{"role": "user", "content": message}],
    "user_id": user_id,
    "conversation_id": conv_id
}

print(f"\nSending request to: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, stream=True, timeout=10)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        full_response = ""
        chunk_count = 0
        
        for line in response.iter_lines():
            if line:
                chunk_count += 1
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and data['choices']:
                                content = data['choices'][0].get('delta', {}).get('content', '')
                                full_response += content
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
        
        print(f"\nReceived {chunk_count} chunks")
        print(f"Total response length: {len(full_response)} chars")
        
        # Check for categorization
        print("\n" + "=" * 40)
        print("CATEGORIZATION CHECK:")
        print("=" * 40)
        
        if "tagged as" in full_response.lower():
            print("[SUCCESS] Found 'Tagged as' in response!")
            # Find and print the tagged line
            for line in full_response.split('\n'):
                if 'tagged' in line.lower():
                    print(f"Categorization output: {line.strip()}")
        else:
            print("[FAILED] No 'Tagged as' found in response")
            
        print("\n" + "=" * 40)
        print("FULL RESPONSE:")
        print("=" * 40)
        print(full_response)
        
    else:
        print(f"[ERROR] HTTP {response.status_code}")
        print(f"Response body: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"[REQUEST ERROR] {e}")
except Exception as e:
    print(f"[EXCEPTION] {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)