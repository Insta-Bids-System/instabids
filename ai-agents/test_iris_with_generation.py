import requests
import json

# Test Iris chat with image generation request
url = "http://localhost:8008/api/iris/chat"

# Test 1: Ask for image generation
payload = {
    "message": "Can you generate a vision of my kitchen with modern white cabinets?",
    "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
    "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3"
}

print("Testing image generation request...")
try:
    response = requests.post(url, json=payload, timeout=35)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    # Check if image was actually generated
    if "generated_image_url" in result.get("data", {}):
        print("\n✓ SUCCESS: Image was actually generated!")
        print(f"Image URL: {result['data']['generated_image_url']}")
    else:
        print("\n✗ FAIL: No image was generated, just a text response")
        
except Exception as e:
    print(f"Error: {e}")

# Test 2: Regular conversation
print("\n\nTesting regular conversation...")
payload2 = {
    "message": "What styles work well with small spaces?",
    "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
    "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3"
}

try:
    response = requests.post(url, json=payload2, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")