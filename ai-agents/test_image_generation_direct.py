import requests
import json

# Test the image generation API directly
url = "http://localhost:8008/api/image-generation/generate-dream-space"

payload = {
    "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3",
    "ideal_image_id": "inspiration_1",
    "current_image_id": "current_1",
    "user_preferences": "Generate a modern kitchen with white cabinets and marble countertops"
}

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")