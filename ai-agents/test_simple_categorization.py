"""Simple categorization test"""
import requests
import json

# Test artificial turf installation
message = "I need artificial turf installed in my backyard"
print(f"Testing: {message}")

url = "http://localhost:8008/api/cia/stream"
payload = {
    "messages": [{"role": "user", "content": message}],
    "user_id": "test-user-simple",
    "conversation_id": "test-conv-simple"
}

response = requests.post(url, json=payload, stream=True)
full_response = ""

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

# Check for categorization
if "tagged as" in full_response.lower():
    print("[SUCCESS] Categorization tool was called!")
    # Find the tagged line
    for line in full_response.split('\n'):
        if 'tagged' in line.lower():
            print(f"Tool output: {line}")
else:
    print("[FAILED] No categorization evidence found")
    print(f"Response preview: {full_response[:300]}")