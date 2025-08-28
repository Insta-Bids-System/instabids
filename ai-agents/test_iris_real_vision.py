"""
Test IRIS with real OpenAI Vision AI Analysis
"""

import asyncio
import base64
import httpx
import json
import sys
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test with a real base64 image (small 1x1 red pixel for testing)
REAL_IMAGE_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

async def test_iris_vision():
    """Test IRIS image analysis with real OpenAI Vision"""
    
    print("\n" + "="*80)
    print("TESTING IRIS WITH REAL OPENAI VISION AI")
    print("="*80)
    
    # Test 1: Test image upload with vision analysis
    print("\n1. Testing image upload with real vision analysis...")
    
    request_data = {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "message": "Here's a photo of my modern kitchen that needs updating. It has white cabinets and marble countertops.",
        "images": [{
            "filename": "kitchen_modern.jpg",
            "data": REAL_IMAGE_BASE64
        }],
        "session_id": f"vision-test-{int(datetime.now().timestamp())}"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Call IRIS unified chat endpoint
            response = await client.post(
                "http://localhost:8008/api/iris/unified-chat",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n[SUCCESS] Vision Analysis Results:")
                print(f"   Success: {result.get('success')}")
                print(f"   Images Processed: {result.get('images_processed')}")
                
                image_analysis = result.get('image_analysis', {})
                print(f"\n   Image Analysis:")
                print(f"   - Room Type: {image_analysis.get('room_type')}")
                print(f"   - Confidence: {image_analysis.get('confidence')}")
                print(f"   - Auto Tags: {image_analysis.get('auto_tags', [])[:5]}...")
                
                # Check if we got real vision analysis (high confidence)
                confidence = image_analysis.get('confidence', 0)
                if confidence > 0.9:
                    print(f"\n   --> REAL VISION ANALYSIS DETECTED (confidence: {confidence})")
                else:
                    print(f"\n   [WARNING] FALLBACK TO KEYWORD ANALYSIS (confidence: {confidence})")
                
                print(f"\n   Response Preview:")
                print(f"   {result.get('response', '')[:200]}...")
                
            else:
                print(f"\n[ERROR] API Error: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
    
    # Test 2: Test direct vision API endpoint
    print("\n\n2. Testing direct OpenAI Vision API endpoint...")
    
    vision_request = {
        "image_data": REAL_IMAGE_BASE64,
        "analysis_type": "comprehensive",
        "include_suggestions": True
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "http://localhost:8008/api/vision/analyze",
                json=vision_request
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('analysis', {})
                
                print("\n[SUCCESS] Direct Vision API Results:")
                print(f"   Description: {analysis.get('description', '')[:150]}...")
                print(f"   Room Type: {analysis.get('room_type')}")
                print(f"   Style: {analysis.get('style')}")
                print(f"   Key Elements: {analysis.get('key_elements', [])[:5]}")
                print(f"   Suggestions: {result.get('suggestions', [])[:3]}")
                
                # Check if this is real analysis or fallback
                if "API temporarily unavailable" in analysis.get('description', ''):
                    print("\n   [WARNING] OpenAI Vision API unavailable - using fallback")
                else:
                    print("\n   --> REAL OPENAI VISION ANALYSIS SUCCESSFUL!")
                    
            else:
                print(f"\n[ERROR] Vision API Error: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"\n[ERROR] Error calling vision API: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_iris_vision())