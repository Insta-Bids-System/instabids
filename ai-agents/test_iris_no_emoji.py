import requests
import json
import time

# Test without emojis to avoid encoding issues
time.sleep(2)

url = "http://localhost:8008/api/iris/chat"
payload = {
    "message": "Generate a kitchen vision",
    "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
    "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3"
}

print("Testing Iris image generation...")
try:
    response = requests.post(url, json=payload, timeout=40)
    print(f"Status Code: {response.status_code}")
    
    if response.ok:
        result = response.json()
        print(f"Response keys: {list(result.keys())}")
        
        # Check all keys
        for key, value in result.items():
            if key == "response":
                print(f"{key}: {str(value)[:100]}...")
            elif key == "suggestions":
                print(f"{key}: {value}")
            else:
                print(f"{key}: {value}")
                
        # Specifically check for image data
        image_generated = result.get("image_generated", False)
        image_url = result.get("image_url", "None")
        generation_id = result.get("generation_id", "None")
        
        print(f"\nImage generation status:")
        print(f"- Generated: {image_generated}")
        print(f"- URL: {image_url}")
        print(f"- ID: {generation_id}")
        
except Exception as e:
    print(f"Error: {e}")