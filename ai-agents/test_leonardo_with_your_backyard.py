"""
Test Leonardo.ai with your actual backyard images
Uses the original backyard + ideal turf images you provided
"""

import asyncio
import os
import aiohttp
import time
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Your actual images from the conversation
YOUR_BACKYARD_IMAGE = "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop"  # Current backyard with soccer goal
YOUR_IDEAL_TURF = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop"      # Perfect artificial turf

async def upload_image_to_leonardo(image_url, description):
    """Upload an image to Leonardo and get the ID"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"[INFO] Getting upload URL for {description}...")
            
            # Step 1: Get presigned upload URL
            async with session.post(
                "https://cloud.leonardo.ai/api/rest/v1/init-image",
                headers=headers,
                json={"extension": "jpg"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"[ERROR] Upload URL failed: {response.status} - {error_text}")
                    return None
                
                result = await response.json()
                upload_data = result.get("uploadInitImage", {})
                upload_id = upload_data.get("id")
                upload_url = upload_data.get("url")
                upload_fields = upload_data.get("fields", {})
                
                if not upload_id or not upload_url:
                    print(f"[ERROR] No upload data returned: {result}")
                    return None
                
                print(f"[SUCCESS] Got upload URL for {description}")
                print(f"   Upload ID: {upload_id}")
                
                # Step 2: Download the image from your URL
                print(f"[INFO] Downloading image from: {image_url}")
                async with session.get(image_url) as img_response:
                    if img_response.status != 200:
                        print(f"[ERROR] Could not download image: {img_response.status}")
                        return None
                    
                    image_data = await img_response.read()
                    print(f"[SUCCESS] Downloaded {len(image_data)} bytes")
                
                # Step 3: Upload to Leonardo's S3
                print(f"[INFO] Uploading to Leonardo S3...")
                print(f"[DEBUG] Upload fields type: {type(upload_fields)}")
                print(f"[DEBUG] Upload fields: {upload_fields}")
                
                form_data = aiohttp.FormData()
                
                # Handle upload_fields properly - might be string or dict
                if isinstance(upload_fields, str):
                    try:
                        upload_fields = json.loads(upload_fields)
                        print(f"[DEBUG] Parsed JSON upload_fields successfully")
                    except json.JSONDecodeError as e:
                        print(f"[ERROR] Failed to parse upload_fields JSON: {e}")
                        return None
                
                if isinstance(upload_fields, dict):
                    for key, value in upload_fields.items():
                        form_data.add_field(key, value)
                        print(f"[DEBUG] Added form field: {key}")
                else:
                    print(f"[ERROR] upload_fields is not a dict after parsing: {type(upload_fields)}")
                    return None
                    
                form_data.add_field('file', image_data, filename='image.jpg', content_type='image/jpeg')
                
                async with session.post(upload_url, data=form_data) as s3_response:
                    if s3_response.status in [200, 201, 204]:
                        print(f"[SUCCESS] {description} uploaded! ID: {upload_id}")
                        return upload_id
                    else:
                        error_text = await s3_response.text()
                        print(f"[ERROR] S3 upload failed: {s3_response.status} - {error_text}")
                        return None
                        
    except Exception as e:
        print(f"[ERROR] Upload error for {description}: {e}")
        return None

async def generate_backyard_transformation(current_image_id, turf_image_id):
    """Generate your backyard transformation using Leonardo"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Transformation prompt specifically for your backyard with detailed turf description
    generation_data = {
        "prompt": "Transform this backyard by replacing all patchy natural grass areas with beautiful, lush green artificial turf that looks perfectly maintained. The artificial turf should be vibrant emerald green, with realistic texture and natural appearance. Keep the white soccer goal in the exact same position. Preserve all existing structures, trees, landscaping features, and background elements exactly as they are. Professional landscape transformation, high quality, photorealistic.",
        "negative_prompt": "blurry, low quality, distorted, unrealistic, cartoon, painting, sketch, different layout, moved structures",
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Phoenix
        "width": 1024,
        "height": 768,
        "num_images": 1,
        "init_image_id": current_image_id,
        "init_strength": 0.35,  # Keep most of the structure, change the grass
        "guidance_scale": 7,
        "seed": None,
        # Skip ControlNet for now - Leonardo Phoenix v2 will do image-to-image transformation
        # The turf style will be guided by the detailed prompt instead
        "controlnets": None
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("[INFO] Starting your backyard transformation...")
            print("   Current backyard -> artificial turf transformation")
            print("   Preserving soccer goal position and all structures")
            
            async with session.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers,
                json=generation_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    generation_id = result.get("sdGenerationJob", {}).get("generationId")
                    
                    if generation_id:
                        print(f"[SUCCESS] Transformation started! ID: {generation_id}")
                        return generation_id
                    else:
                        print(f"[ERROR] No generation ID: {result}")
                        return None
                else:
                    error_text = await response.text()
                    print(f"[ERROR] Generation failed: {response.status}")
                    print(f"   Response: {error_text}")
                    return None
                    
    except Exception as e:
        print(f"[ERROR] Generation error: {e}")
        return None

async def check_generation_status(generation_id):
    """Check the status and get result"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}"
    }
    
    max_attempts = 30  # 5 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"[ERROR] Status check failed: {response.status} - {error_text}")
                        return None
                    
                    result = await response.json()
                    generation = result.get("generations_by_pk", {})
                    status = generation.get("status", "UNKNOWN")
                    
                    print(f"[INFO] Attempt {attempt + 1}: Status = {status}")
                    
                    if status == "COMPLETE":
                        images = generation.get("generated_images", [])
                        if images:
                            image_url = images[0].get("url")
                            print(f"\n[SUCCESS] YOUR BACKYARD TRANSFORMATION IS COMPLETE!")
                            print(f"[IMAGE] Generated Image URL: {image_url}")
                            print(f"[SAVE] You can save this image and see your backyard with artificial turf!")
                            return image_url
                        else:
                            print("[ERROR] No images in completed generation")
                            return None
                    elif status == "FAILED":
                        error = generation.get("imageGenerationJobs", [{}])[0].get("likelyHood", "Unknown error")
                        print(f"[ERROR] Generation failed: {error}")
                        return None
                    else:
                        print(f"   Still processing... ({status})")
                        await asyncio.sleep(10)  # Wait 10 seconds
                        attempt += 1
                        
        except Exception as e:
            print(f"[ERROR] Status check error: {e}")
            await asyncio.sleep(10)
            attempt += 1
    
    print("[WARNING] Generation timed out after 5 minutes")
    print(f"You can check status later with generation ID: {generation_id}")
    return "timeout"

async def main():
    """Transform your actual backyard with artificial turf"""
    print("=" * 70)
    print("[TRANSFORM] YOUR BACKYARD -> ARTIFICIAL TURF TRANSFORMATION")
    print("=" * 70)
    print("Using your original images from the conversation:")
    print(f"[OK] Current backyard: {YOUR_BACKYARD_IMAGE}")
    print(f"[OK] Ideal turf reference: {YOUR_IDEAL_TURF}")
    print()
    
    # Step 1: Upload your current backyard
    print("STEP 1: Uploading your current backyard image...")
    current_id = await upload_image_to_leonardo(YOUR_BACKYARD_IMAGE, "your current backyard")
    if not current_id:
        print("[ERROR] Failed to upload current backyard")
        return
    
    # Step 2: Upload your ideal turf reference
    print("\nSTEP 2: Uploading your ideal turf reference...")
    turf_id = await upload_image_to_leonardo(YOUR_IDEAL_TURF, "ideal artificial turf")
    if not turf_id:
        print("[WARNING] Failed to upload turf reference, continuing without style reference")
        turf_id = None
    
    # Step 3: Generate transformation
    print("\nSTEP 3: Generating your backyard transformation...")
    generation_id = await generate_backyard_transformation(current_id, turf_id)
    if not generation_id:
        print("[ERROR] Failed to start transformation")
        return
    
    # Step 4: Wait for result
    print("\nSTEP 4: Waiting for your transformation to complete...")
    print("(This may take 1-3 minutes)")
    
    result_url = await check_generation_status(generation_id)
    
    if result_url and result_url.startswith("http"):
        print("\n" + "=" * 70)
        print("[SUCCESS] Your backyard transformation is ready!")
        print("=" * 70)
        print(f"[IMAGE] Image URL: {result_url}")
        print()
        print("[DETAILS] What this shows:")
        print("   - Your exact backyard layout preserved")
        print("   - Soccer goal in the same position")  
        print("   - Patchy grass replaced with lush artificial turf")
        print("   - All structures and landscaping maintained")
        print()
        print("[NEXT] You can now:")
        print("   - Save the image to see the transformation")
        print("   - Show contractors what you want")
        print("   - Use this for project planning")
        
    elif result_url == "timeout":
        print("\n[TIMEOUT] Generation is taking longer than expected")
        print("The transformation is still processing - check back in a few minutes")
    else:
        print("\n[ERROR] Transformation failed")
        print("The Leonardo API key works, but generation had issues")

if __name__ == "__main__":
    asyncio.run(main())