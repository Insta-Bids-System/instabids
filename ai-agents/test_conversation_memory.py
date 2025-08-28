#!/usr/bin/env python3
"""
Test conversation memory and context retention
"""

import requests
import json
import uuid

def test_simple_memory():
    """Test basic conversation memory"""
    user_id = str(uuid.uuid4())
    conv_id = f"memory-test-{int(time.time())}"
    url = "http://localhost:8008/api/cia/stream"
    
    # Test proper message structure
    messages = [
        {"role": "user", "content": "I need my roof repaired, there's a leak"},
        {"role": "assistant", "content": "I'm sorry to hear about the leak. Let's get this sorted out. Could you tell me your location?"},
        {"role": "user", "content": "I'm in 90210 and this is urgent"}
    ]
    
    print("Testing conversation with proper message structure:")
    print("Messages being sent:")
    for i, msg in enumerate(messages):
        print(f"{i+1}. {msg['role']}: {msg['content']}")
    
    payload = {
        "messages": messages,
        "user_id": user_id,
        "conversation_id": conv_id
    }
    
    print(f"\nPayload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        full_response = ""
        print(f"\nAI Response: ", end="", flush=True)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str.strip() != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                content = data['choices'][0].get('delta', {}).get('content', '')
                                full_response += content
                                print(content, end='', flush=True)
                        except:
                            pass
        
        print(f"\n\nFull response: {full_response}")
        
        # Check if it remembers the roof leak and urgency
        if "roof" in full_response.lower() and ("urgent" in full_response.lower() or "90210" in full_response):
            print("SUCCESS: Conversation memory working!")
            return True
        else:
            print("ISSUE: Conversation memory not working properly")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    import time
    test_simple_memory()