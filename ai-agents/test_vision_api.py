"""
Test the vision API endpoint through the backend
"""

import requests
import json

# Test with a simple base64 image (1x1 red pixel)
REAL_IMAGE_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

vision_request = {
    "image_data": REAL_IMAGE_BASE64,
    "analysis_type": "comprehensive",
    "include_suggestions": True
}

print("Testing Vision API endpoint at http://localhost:8008/api/vision/analyze...")

try:
    response = requests.post(
        "http://localhost:8008/api/vision/analyze",
        json=vision_request,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        analysis = result.get('analysis', {})
        
        print("\n[SUCCESS] Vision API Response:")
        print(f"  Description: {analysis.get('description', '')[:200]}...")
        print(f"  Room Type: {analysis.get('room_type')}")
        print(f"  Style: {analysis.get('style')}")
        print(f"  Key Elements: {analysis.get('key_elements', [])[:5]}")
        print(f"  Suggestions: {result.get('suggestions', [])[:3]}")
        
        if "API temporarily unavailable" in analysis.get('description', ''):
            print("\n[WARNING] Vision API returned fallback response")
        else:
            print("\n[SUCCESS] Real OpenAI Vision analysis completed!")
            
    else:
        print(f"\n[ERROR] API returned status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n[ERROR] Failed to call API: {e}")