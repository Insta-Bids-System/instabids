#!/usr/bin/env python3
"""
Test real photo upload to property API to verify OpenAI is working
"""

import requests
import base64
import json
from config.service_urls import get_backend_url

# Create a simple test image (WhatsApp living room with broken blinds simulation)
def create_test_image():
    # Create a small JPG as base64 (actual minimal JPG header)
    jpg_data = base64.b64decode("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=")
    return jpg_data

def test_photo_upload():
    # Create test image
    image_data = create_test_image()
    
    print("Testing photo upload to property API...")
    print("Image size:", len(image_data), "bytes")
    
    # Prepare multipart form data
    files = {
        'file': ('test_living_room.jpg', image_data, 'image/jpeg')
    }
    
    data = {
        'user_id': 'test-user-12345',
        'photo_type': 'documentation'
    }
    
    try:
        # Upload to property API with user_id as query parameter
        response = requests.post(
            f'{get_backend_url()}/api/properties/test-property-123/photos/upload?user_id=test-user-12345',
            files=files,
            data={'photo_type': 'documentation'},
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Photo upload worked!")
            print(f"Photo ID: {result.get('photo_id')}")
            print(f"AI Description: {result.get('ai_description')}")
            print(f"Room Classified: {result.get('room_classified')}")
            print(f"Detected Assets: {result.get('detected_assets')}")
            
            # Check if it used real AI or fallback
            if result.get('ai_classification'):
                classification = result['ai_classification']
                if 'Enhanced fallback' in classification.get('description', ''):
                    print("⚠️  USING FALLBACK - OpenAI not working properly")
                else:
                    print("✅ USING REAL OPENAI - AI analysis working!")
                    
        else:
            print(f"ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Failed to upload photo: {e}")

if __name__ == "__main__":
    test_photo_upload()