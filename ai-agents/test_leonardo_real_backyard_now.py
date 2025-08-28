"""
Test Leonardo with YOUR ACTUAL backyard images
This will iterate through different configurations until we get the perfect turf transformation
"""

import asyncio
import os
import aiohttp
import json
from dotenv import load_dotenv
import base64

# Load environment
load_dotenv()

# TEST CONFIGURATIONS - We'll try these in order until one works perfectly
CONFIGS = [
    {
        "name": "Ultra Low Strength - Maximum Preservation",
        "init_strength": 0.15,  # Very minimal changes
        "guidance_scale": 9,
        "prompt": "Backyard with perfect artificial turf lawn. Replace only the grass texture with vibrant green synthetic turf. Keep white soccer goal, green bin, building, trees, shrubs, mulch bed exactly as shown. Ultra-realistic photo.",
    },
    {
        "name": "Low Strength - Grass Focus",  
        "init_strength": 0.20,
        "guidance_scale": 8,
        "prompt": "Professional artificial turf installation. Transform patchy dead grass to perfect emerald green synthetic turf. Preserve exact layout: soccer goal position, all structures, trees. Photorealistic result.",
    },
    {
        "name": "Balanced - Texture Replace",
        "init_strength": 0.25,
        "guidance_scale": 7,
        "prompt": "Artificial turf replacement in residential backyard. Change only grass areas from patchy brown to uniform green artificial turf. Keep all objects in exact positions. Professional landscape photo.",
    }
]async def test_with_local_images():
    """Test using images saved locally from the user's message"""
    
    print("=" * 70)
    print("LEONARDO BACKYARD TURF TRANSFORMATION TEST")
    print("=" * 70)
    print("\nUSING YOUR ACTUAL BACKYARD IMAGES")
    print("Goal: Transform your patchy grass to perfect artificial turf")
    print("=" * 70)
    
    # Check if images exist
    backyard_path = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\backyard_current.jpg"
    turf_path = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\turf_ideal.jpg"
    
    if not os.path.exists(backyard_path):
        print(f"\n[ERROR] Cannot find your backyard image at: {backyard_path}")
        print("\nPLEASE SAVE YOUR IMAGES:")
        print("1. Save your backyard image (with soccer goal) as:")
        print(f"   {backyard_path}")
        print("2. Save the turf reference image as:")
        print(f"   {turf_path}")
        return
    
    print(f"\n[OK] Found backyard image: {backyard_path}")
    
    # Read the image
    with open(backyard_path, 'rb') as f:
        backyard_data = f.read()
    
    print(f"[OK] Loaded {len(backyard_data)} bytes")
    
    # Now upload to Leonardo
    await upload_and_test_configs(backyard_data)async def upload_and_test_configs(image_data):
    """Upload image and test all configurations"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # First, get upload URL
        print("\n[STEP 1] Getting Leonardo upload URL...")
        
        async with session.post(
            "https://cloud.leonardo.ai/api/rest/v1/init-image",
            headers=headers,
            json={"extension": "jpg"}
        ) as response:
            
            if response.status != 200:
                print(f"[ERROR] Failed to get upload URL: {response.status}")
                return
            
            result = await response.json()
            upload_data = result.get("uploadInitImage", {})
            upload_id = upload_data.get("id")
            upload_url = upload_data.get("url")
            upload_fields = upload_data.get("fields", {})
            
            print(f"[SUCCESS] Got upload ID: {upload_id}")        
        # Upload to S3
        print("[STEP 2] Uploading your backyard image to Leonardo...")
        
        form_data = aiohttp.FormData()
        
        if isinstance(upload_fields, str):
            upload_fields = json.loads(upload_fields)
        
        for key, value in upload_fields.items():
            form_data.add_field(key, value)
        
        form_data.add_field('file', image_data, filename='backyard.jpg', content_type='image/jpeg')
        
        async with session.post(upload_url, data=form_data) as s3_response:
            if s3_response.status not in [200, 201, 204]:
                print(f"[ERROR] Upload failed: {s3_response.status}")
                return
        
        print(f"[SUCCESS] Your backyard image uploaded!")
        
        # Now test each configuration
        print("\n[STEP 3] Testing different transformation configs...")
        print("We'll keep trying until we get the perfect result!\n")
        
        for i, config in enumerate(CONFIGS, 1):
            print(f"\n{'='*50}")
            print(f"CONFIG {i}/{len(CONFIGS)}: {config['name']}")
            print(f"{'='*50}")
            
            await test_single_config(session, upload_id, config, headers)