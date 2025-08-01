import requests
import json

# Test with simpler message to debug
url = "http://localhost:8008/api/iris/chat"

payload = {
    "message": "Generate a kitchen vision",
    "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
    "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3"
}

print("Sending request...")
try:
    response = requests.post(url, json=payload, timeout=35)
    print(f"Status Code: {response.status_code}")
    
    if response.ok:
        result = response.json()
        print(f"Response keys: {result.keys()}")
        print(f"Full response: {json.dumps(result, indent=2)}")
        
        # Check specific fields
        if "image_generated" in result:
            print(f"\nImage generated: {result['image_generated']}")
        if "image_url" in result:
            print(f"Image URL: {result['image_url']}")
        if "generation_id" in result:
            print(f"Generation ID: {result['generation_id']}")
            
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")