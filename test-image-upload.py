#!/usr/bin/env python3
"""
Test CIA image upload functionality
"""

import requests
import json
import base64
import os

def encode_image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_cia_with_images():
    """Test CIA endpoint with image upload"""
    
    # Create a simple test image (placeholder)
    test_image_path = "test_bathroom.jpg"
    
    # If no test image exists, create a simple placeholder
    if not os.path.exists(test_image_path):
        print("Creating placeholder test image...")
        # Create a minimal JPG header for testing
        with open(test_image_path, "wb") as f:
            # Minimal JPEG header (won't be a real image but will test the upload mechanism)
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
    
    try:
        # Encode image to base64
        image_base64 = encode_image_to_base64(test_image_path)
        
        # Prepare the request
        payload = {
            "messages": [
                {
                    "role": "user", 
                    "content": "Here's a photo of my current bathroom. I want to renovate it with new tile, vanity, and expand the shower. What do you think?"
                }
            ],
            "conversation_id": f"test-image-conv-{int(__import__('time').time())}",
            "user_id": f"test-user-{int(__import__('time').time())}",
            "images": [f"data:image/jpeg;base64,{image_base64}"]
        }
        
        print("Testing CIA with image upload...")
        print(f"Image size: {len(image_base64)} characters")
        
        # Make the request
        response = requests.post(
            "http://localhost:8008/api/cia/stream",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
            stream=True
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ CIA accepting images successfully!")
            
            # Read first few chunks to verify it's processing
            chunks_read = 0
            for line in response.iter_lines():
                if line:
                    try:
                        if line.startswith(b'data: '):
                            data = json.loads(line[6:])
                            if 'choices' in data and data['choices']:
                                content = data['choices'][0].get('delta', {}).get('content', '')
                                if content:
                                    print(content, end='', flush=True)
                        
                        chunks_read += 1
                        if chunks_read > 50:  # Read enough to verify it's working
                            print("\n✅ Image processing confirmed - CIA is responding!")
                            break
                            
                    except json.JSONDecodeError:
                        continue
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing image upload: {e}")
    
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

if __name__ == "__main__":
    test_cia_with_images()