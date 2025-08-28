"""
Test CIA categorization with the fixed tool via live API
"""

import requests
import json
import time

def test_cia_categorization_fixed():
    """Test CIA with fixed categorization tool"""
    
    print("=" * 80)
    print("TESTING CIA CATEGORIZATION WITH FIXED TOOL")
    print("=" * 80)
    
    # Test payload - correct format for CIA stream
    payload = {
        "user_id": "test-categorization-fix", 
        "conversation_id": "test-fixed-tool",
        "session_id": "test-session-fix",
        "messages": [
            {"role": "user", "content": "I need my fake grass repaired"}
        ]
    }
    
    print(f"Sending: {payload['messages'][0]['content']}")
    print("Expected: LLM must pick 'turf_repair' from our enum list")
    print()
    
    try:
        # Call CIA stream endpoint
        url = "http://localhost:8008/api/cia/stream"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
        
        if response.status_code != 200:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        print("Streaming response:")
        print("-" * 40)
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    try:
                        data = json.loads(line_text[6:])  # Remove 'data: ' prefix
                        if 'content' in data:
                            content = data['content']
                            print(content, end='', flush=True)
                            full_response += content
                        elif 'message' in data:
                            print(f"\n[TOOL MESSAGE] {data['message']}")
                    except json.JSONDecodeError:
                        continue
        
        print("\n" + "-" * 40)
        print("Response completed")
        
        # Check if we see the categorization tool message
        if "Tagged:" in full_response:
            print("\n✓ CATEGORIZATION TOOL TRIGGERED!")
            print("✓ This means LLM was forced to pick from our enum list")
        else:
            print("\n? Categorization tool may not have triggered")
            print("  (Could be due to confidence threshold or other factors)")
        
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend (is Docker running?)")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_cia_categorization_fixed()