"""
Test Leonardo.ai Integration for Iris System
Tests the complete workflow from image upload to transformation generation
"""

import asyncio
import json
import os
import time
from typing import List

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8008"
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")

# Test images (using the actual backyard images from the user)
TEST_IMAGES = {
    "current_backyard": {
        "url": "https://example.com/current-backyard.jpg",  # Replace with actual URL
        "tags": ["current", "backyard", "before", "patchy-grass"],
        "title": "Current Backyard with Patchy Grass",
        "description": "Existing backyard with soccer goal and patchy grass areas"
    },
    "ideal_turf": {
        "url": "https://example.com/ideal-turf.jpg",  # Replace with actual URL
        "tags": ["turf", "artificial-grass", "texture", "green"],
        "title": "Ideal Artificial Turf Texture",
        "description": "High-quality artificial turf texture reference"
    },
    "style_reference": {
        "url": "https://example.com/style-backyard.jpg",  # Replace with actual URL
        "tags": ["style", "inspiration", "landscape", "modern"],
        "title": "Modern Backyard Style",
        "description": "Overall style and aesthetic reference"
    }
}

def test_leonardo_api_key():
    """Test if Leonardo API key is configured"""
    print("\n1. Testing Leonardo API Key Configuration...")
    
    if not LEONARDO_API_KEY:
        print("❌ LEONARDO_API_KEY not found in environment variables")
        print("   Please set it in your .env file")
        return False
    
    print(f"✅ Leonardo API Key found: {LEONARDO_API_KEY[:10]}...")
    return True

def test_upload_and_classify(image_data: dict, board_id: str = "test-board-001"):
    """Test image upload and classification"""
    print(f"\n2. Testing Image Upload & Classification: {image_data['title']}")
    
    payload = {
        "image_url": image_data["url"],
        "tags": image_data["tags"],
        "board_id": board_id,
        "title": image_data["title"],
        "description": image_data["description"]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/leonardo/upload-and-classify",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Image uploaded successfully")
            print(f"   Leonardo ID: {result.get('leonardo_id')}")
            print(f"   Classification: {result.get('classification')}")
            print(f"   Purpose: {result.get('purpose')}")
            print(f"   ControlNet Config: {result.get('controlnet_config')}")
            return result
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_multi_reference_generation(board_id: str, base_image_id: str, reference_ids: List[str]):
    """Test multi-reference image generation"""
    print("\n3. Testing Multi-Reference Generation...")
    
    payload = {
        "board_id": board_id,
        "base_image_id": base_image_id,
        "reference_image_ids": reference_ids,
        "prompt": """Transform backyard with artificial turf.
        Replace all patchy grass with lush artificial turf.
        Keep soccer goal and all structures in exact positions.
        Professional landscape transformation, photorealistic.""",
        "user_preferences": "Make it look natural and family-friendly"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/leonardo/generate-multi-reference",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation started successfully")
            print(f"   Generation ID: {result.get('generation_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            return result.get('generation_id')
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return None

def test_check_generation_status(generation_id: str):
    """Check generation status"""
    print(f"\n4. Checking Generation Status: {generation_id}")
    
    max_attempts = 30  # 30 attempts * 2 seconds = 60 seconds max
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/leonardo/status/{generation_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                progress = result.get('progress')
                
                print(f"   Attempt {attempt + 1}: Status={status}, Progress={progress}%")
                
                if status == "completed":
                    print(f"✅ Generation completed!")
                    print(f"   Generated images: {result.get('generated_images')}")
                    return result
                elif status == "failed":
                    print(f"❌ Generation failed: {result.get('error')}")
                    return None
                
                # Still processing, wait and retry
                time.sleep(2)
                attempt += 1
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return None
    
    print("⏱️ Generation timed out after 60 seconds")
    return None

def test_backyard_transformation(board_id: str):
    """Test the specialized backyard transformation endpoint"""
    print("\n5. Testing Backyard Transformation Endpoint...")
    
    payload = {
        "board_id": board_id,
        "user_preferences": "Natural looking artificial turf with vibrant green color"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/leonardo/generate-backyard-transformation",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backyard transformation started")
            print(f"   Generation ID: {result.get('generation_id')}")
            print(f"   Image Classification:")
            classification = result.get('image_classification', {})
            print(f"     - Current: {classification.get('current')}")
            print(f"     - Turf References: {classification.get('turf_references')}")
            print(f"     - Style References: {classification.get('style_references')}")
            return result.get('generation_id')
        else:
            print(f"❌ Transformation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Transformation error: {e}")
        return None

def main():
    """Run complete Leonardo integration test"""
    print("=" * 60)
    print("LEONARDO.AI INTEGRATION TEST FOR IRIS SYSTEM")
    print("=" * 60)
    
    # Test 1: Check API key
    if not test_leonardo_api_key():
        print("\n⚠️ Please configure LEONARDO_API_KEY before continuing")
        return
    
    # Test 2: Upload and classify images
    board_id = f"test-board-{int(time.time())}"
    uploaded_images = {}
    
    for image_key, image_data in TEST_IMAGES.items():
        result = test_upload_and_classify(image_data, board_id)
        if result:
            uploaded_images[image_key] = result
        else:
            print(f"\n⚠️ Failed to upload {image_key}, skipping further tests")
            return
    
    # Test 3: Multi-reference generation
    if len(uploaded_images) >= 2:
        # Use current backyard as base, others as references
        base_id = "base-image-id"  # Would come from database
        reference_ids = ["ref-1", "ref-2"]  # Would come from database
        
        generation_id = test_multi_reference_generation(
            board_id,
            base_id,
            reference_ids
        )
        
        if generation_id:
            # Test 4: Check generation status
            result = test_check_generation_status(generation_id)
            
            if result and result.get('status') == 'completed':
                print("\n" + "=" * 60)
                print("✅ LEONARDO INTEGRATION TEST SUCCESSFUL!")
                print("=" * 60)
                print("\nGenerated Images:")
                for url in result.get('generated_images', []):
                    print(f"  - {url}")
            else:
                print("\n❌ Generation did not complete successfully")
        else:
            print("\n❌ Failed to start generation")
    else:
        print("\n⚠️ Not enough images uploaded for multi-reference test")
    
    # Test 5: Backyard transformation endpoint
    print("\n" + "=" * 60)
    print("TESTING SPECIALIZED BACKYARD TRANSFORMATION")
    print("=" * 60)
    
    transform_id = test_backyard_transformation(board_id)
    if transform_id:
        result = test_check_generation_status(transform_id)
        if result and result.get('status') == 'completed':
            print("\n✅ Backyard transformation completed successfully!")
        else:
            print("\n❌ Backyard transformation did not complete")

if __name__ == "__main__":
    # Note: This test requires the backend to be running
    print("\nℹ️ Make sure the backend is running: cd ai-agents && python main.py")
    print("ℹ️ Also ensure LEONARDO_API_KEY is set in your .env file")
    print("")
    
    input("Press Enter to start the test...")
    main()