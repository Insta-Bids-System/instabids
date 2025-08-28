#!/usr/bin/env python3
"""Final test for CIA agent categorization with proper UUIDs"""
import requests
import json
import uuid

print('Testing CIA agent categorization with proper UUIDs...')

user_id = str(uuid.uuid4())
conv_id = str(uuid.uuid4())

payload = {
    'messages': [{'role': 'user', 'content': 'I need artificial turf installed in my backyard'}],
    'user_id': user_id,
    'conversation_id': conv_id
}

print(f'Using user_id: {user_id}')
print(f'Using conv_id: {conv_id}')

try:
    response = requests.post('http://localhost:8008/api/cia/stream', 
                           json=payload, timeout=30, stream=True)
    print(f'Response status: {response.status_code}')

    full_response = ''
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                if data_str != '[DONE]':
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and data['choices']:
                            content = data['choices'][0].get('delta', {}).get('content', '')
                            full_response += content
                    except:
                        pass

    print(f'\nFull response: {full_response}')
    
    if 'tagged as' in full_response.lower():
        print('\n✅ SUCCESS: Categorization tool executed!')
        # Extract the categorization line
        for line in full_response.split('\n'):
            if 'tagged' in line.lower():
                print(f'   {line.strip()}')
    else:
        print('\n❌ FAILED: No categorization found')
        
except Exception as e:
    print(f'ERROR: {e}')