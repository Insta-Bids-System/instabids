"""
Leonardo.ai Backyard Transformation - Iterate Until Perfect
Keep testing different parameters until we get the perfect turf transformation
"""

import asyncio
import os
import aiohttp
import time
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

# TEST CONFIGURATIONS TO TRY
TEST_CONFIGS = [
    {
        "name": "Config 1: Low strength, high guidance",
        "init_strength": 0.25,  # Keep more of original
        "guidance_scale": 8,
        "prompt": "Transform this backyard lawn by replacing all patchy and dead grass with perfect artificial turf. The turf should be lush, vibrant emerald green, uniform and pristine like a golf course. Keep the white soccer goal, all buildings, trees, bushes, borders and structures exactly as they are. Only change the grass texture to artificial turf. Photorealistic quality.",
        "negative_prompt": "cartoon, painting, moved objects, different layout, brown grass, patches"
    },
    {
        "name": "Config 2: Medium strength, detailed prompt",
        "init_strength": 0.35,
        "guidance_scale": 7,
        "prompt": "Replace only the patchy yellow-brown grass areas with beautiful artificial turf. Make the turf vibrant green, perfectly uniform, no dead spots. Preserve exact positions of: white soccer goal, green bin, rounded bushes, trees, mulch bed, gray building. Professional landscape photo.",
        "negative_prompt": "illustration, unrealistic, moved structures, brown patches, dead grass"
    },
    {
        "name": "Config 3: Higher strength, texture focus",
        "init_strength": 0.4,
        "guidance_scale": 6,
        "prompt": "Artificial turf installation in backyard. Replace all natural grass with synthetic turf. Bright green, perfect texture, no brown spots. Keep all existing elements in place. Professional installation photo.",
        "negative_prompt": "painting, cartoon, moved items, patchy grass"
    }
]

# Your actual backyard images (we'll need to handle these properly)
BACKYARD_DESCRIPTION = """
Current backyard with:
- Patchy/dying grass with brown spots
- White soccer goal in background
- Green bin on left
- Rounded shrubs
- Trees in back
- Mulch bed on right
"""

TURF_DESCRIPTION = """
Perfect artificial turf:
- Vibrant emerald green
- Uniform texture
- No patches
- Golf course quality
"""async def upload_image_from_url_or_file(source, description):
    """Upload an image from URL or local file to Leonardo"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"[INFO] Getting upload URL for {description}...")
            
            # Get presigned upload URL
            async with session.post(
                "https://cloud.leonardo.ai/api/rest/v1/init-image",
                headers=headers,
                json={"extension": "jpg"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"[ERROR] Failed to get upload URL: {error_text}")
                    return None
                
                result = await response.json()
                upload_data = result.get("uploadInitImage", {})
                upload_id = upload_data.get("id")
                upload_url = upload_data.get("url")
                upload_fields = upload_data.get("fields", {})                
                if not upload_id or not upload_url:
                    print(f"[ERROR] No upload data returned")
                    return None
                
                print(f"[SUCCESS] Got upload URL, ID: {upload_id}")
                
                # Get image data (from URL or file)
                image_data = None
                if source.startswith("http"):
                    # Download from URL
                    async with session.get(source) as img_response:
                        if img_response.status == 200:
                            image_data = await img_response.read()
                else:
                    # Read from local file
                    if os.path.exists(source):
                        with open(source, 'rb') as f:
                            image_data = f.read()
                    else:
                        print(f"[ERROR] File not found: {source}")
                        return None
                
                if not image_data:
                    print(f"[ERROR] Could not get image data")
                    return None
                    
                print(f"[INFO] Got {len(image_data)} bytes of image data")                
                # Upload to S3
                form_data = aiohttp.FormData()
                
                # Parse fields if needed
                if isinstance(upload_fields, str):
                    upload_fields = json.loads(upload_fields)
                
                for key, value in upload_fields.items():
                    form_data.add_field(key, value)
                    
                form_data.add_field('file', image_data, filename='image.jpg', content_type='image/jpeg')
                
                async with session.post(upload_url, data=form_data) as s3_response:
                    if s3_response.status in [200, 201, 204]:
                        print(f"[SUCCESS] Uploaded {description}")
                        return upload_id
                    else:
                        error = await s3_response.text()
                        print(f"[ERROR] S3 upload failed: {error}")
                        return None
                        
    except Exception as e:
        print(f"[ERROR] Upload error: {e}")
        return None
async def generate_transformation(current_id, config):
    """Generate transformation with specific config"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    generation_data = {
        "prompt": config["prompt"],
        "negative_prompt": config["negative_prompt"],
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Phoenix
        "width": 1024,
        "height": 768,
        "num_images": 1,
        "init_image_id": current_id,
        "init_strength": config["init_strength"],
        "guidance_scale": config["guidance_scale"],
        "seed": None,
        "controlnets": None
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"\n[INFO] Testing {config['name']}")
            print(f"   Init strength: {config['init_strength']}")
            print(f"   Guidance: {config['guidance_scale']}")            
            async with session.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers,
                json=generation_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    generation_id = result.get("sdGenerationJob", {}).get("generationId")
                    
                    if generation_id:
                        print(f"[SUCCESS] Generation started: {generation_id}")
                        return generation_id
                    else:
                        print(f"[ERROR] No generation ID returned")
                        return None
                else:
                    error = await response.text()
                    print(f"[ERROR] Generation failed: {error}")
                    return None
                    
    except Exception as e:
        print(f"[ERROR] Generation error: {e}")
        return Noneasync def check_generation(generation_id):
    """Check generation status and get result"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    headers = {"Authorization": f"Bearer {LEONARDO_API_KEY}"}
    
    max_attempts = 20
    attempt = 0
    
    while attempt < max_attempts:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        print(f"[ERROR] Status check failed")
                        return None
                    
                    result = await response.json()
                    generation = result.get("generations_by_pk", {})
                    status = generation.get("status", "UNKNOWN")
                    
                    if status == "COMPLETE":
                        images = generation.get("generated_images", [])
                        if images:
                            image_url = images[0].get("url")
                            print(f"[SUCCESS] Generation complete!")
                            print(f"[URL] {image_url}")
                            return image_url
                        return None                    elif status == "FAILED":
                        print(f"[ERROR] Generation failed")
                        return None
                    else:
                        print(f"   Status: {status}")
                        await asyncio.sleep(10)
                        attempt += 1
                        
        except Exception as e:
            print(f"[ERROR] Status check error: {e}")
            await asyncio.sleep(10)
            attempt += 1
    
    print("[WARNING] Generation timed out")
    return None

async def test_all_configs():
    """Test all configurations until we get the perfect result"""
    
    print("=" * 70)
    print("LEONARDO BACKYARD TRANSFORMATION - TESTING CONFIGURATIONS")
    print("=" * 70)
    print("\nGoal: Transform patchy grass to perfect artificial turf")
    print("Requirements:")
    print("  - Keep soccer goal in exact position")
    print("  - Preserve all structures")
    print("  - Make turf look realistic and uniform")
    print("=" * 70)    
    # YOUR ACTUAL BACKYARD IMAGES
    # Save your images to these locations:
    BACKYARD_IMAGE = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\backyard_current.jpg"
    TURF_IMAGE = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\turf_ideal.jpg"
    
    print("\n[STEP 1] Uploading your backyard image...")
    current_id = await upload_image_from_url_or_file(BACKYARD_IMAGE, "Current backyard")
    
    if not current_id:
        print("[FATAL] Could not upload backyard image")
        return
    
    print("\n[STEP 2] Testing different configurations...")
    print("We'll keep trying until we get the perfect transformation!\n")
    
    results = []
    
    for i, config in enumerate(TEST_CONFIGS):
        print(f"\n{'='*50}")
        print(f"TEST {i+1}/{len(TEST_CONFIGS)}")
        print(f"{'='*50}")
        
        # Generate with this config
        gen_id = await generate_transformation(current_id, config)
        
        if gen_id:
            # Wait for result
            print("[INFO] Waiting for generation...")
            result_url = await check_generation(gen_id)            
            if result_url:
                results.append({
                    "config": config["name"],
                    "url": result_url,
                    "init_strength": config["init_strength"],
                    "guidance": config["guidance_scale"]
                })
                print(f"\n[RESULT] View this result at: {result_url}")
                print("[CHECK] Does this look correct?")
                print("  - Is the grass now perfect artificial turf?")
                print("  - Is the soccer goal in the same position?")
                print("  - Are all structures preserved?")
            else:
                print("[FAILED] This configuration didn't work")
        else:
            print("[FAILED] Could not start generation")
        
        # Small delay between tests
        await asyncio.sleep(5)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if results:
        print(f"\n[COMPLETED] Generated {len(results)} transformations")
        print("\nResults:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['config']}")
            print(f"   Strength: {r['init_strength']}, Guidance: {r['guidance']}")
            print(f"   URL: {r['url']}")
    else:
        print("\n[ERROR] No successful generations")
        print("Need to adjust parameters and try again")
    
    print("\n[NEXT STEPS]")
    print("1. Check each generated image")
    print("2. Identify which config works best")
    print("3. If none are perfect, we'll create new configs")
    print("4. Keep iterating until we get the perfect transformation!")

if __name__ == "__main__":
    asyncio.run(test_all_configs())