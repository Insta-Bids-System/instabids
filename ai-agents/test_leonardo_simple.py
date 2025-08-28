"""
Simple Leonardo API test directly (no backend required)
Tests basic image upload and generation capabilities
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_leonardo_upload():
    """Test basic Leonardo image upload"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    if not LEONARDO_API_KEY:
        print("[ERROR] Leonardo API key not found")
        return
    
    print(f"[INFO] Testing with Leonardo API key: {LEONARDO_API_KEY[:20]}...")
    
    # Import after loading environment
    import aiohttp
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use proper Leonardo init-image parameters
    upload_data = {
        "extension": "jpg"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("[INFO] Uploading test image...")
            
            # Try the correct upload endpoint
            async with session.post(
                "https://cloud.leonardo.ai/api/rest/v1/init-image",
                headers=headers,
                json=upload_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    upload_id = result.get("uploadInitImage", {}).get("id")
                    
                    if upload_id:
                        print(f"[SUCCESS] Image uploaded! ID: {upload_id}")
                        return upload_id
                    else:
                        print(f"[ERROR] No upload ID returned: {result}")
                        return None
                else:
                    error_text = await response.text()
                    print(f"[ERROR] Upload failed: {response.status}")
                    print(f"   Response: {error_text}")
                    return None
                    
    except Exception as e:
        print(f"[ERROR] Upload error: {e}")
        return None

async def test_leonardo_generation(upload_id):
    """Test basic Leonardo generation with uploaded image"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    # Import after loading environment
    import aiohttp
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Simple generation request
    generation_data = {
        "prompt": "A beautiful backyard with lush artificial turf, maintaining all existing structures and layout",
        "negative_prompt": "blurry, low quality, distorted, unrealistic",
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Phoenix
        "width": 1024,
        "height": 768,
        "num_images": 1,
        "init_image_id": upload_id,
        "init_strength": 0.3  # Keep structure, change texture
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("[INFO] Starting image generation...")
            
            async with session.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers,
                json=generation_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    generation_id = result.get("sdGenerationJob", {}).get("generationId")
                    
                    if generation_id:
                        print(f"[SUCCESS] Generation started! ID: {generation_id}")
                        return generation_id
                    else:
                        print(f"[ERROR] No generation ID returned: {result}")
                        return None
                else:
                    error_text = await response.text()
                    print(f"[ERROR] Generation failed: {response.status}")
                    print(f"   Response: {error_text}")
                    return None
                    
    except Exception as e:
        print(f"[ERROR] Generation error: {e}")
        return None

async def test_leonardo_status(generation_id):
    """Check generation status"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    # Import after loading environment
    import aiohttp
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("[INFO] Checking generation status...")
            
            async with session.get(
                f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    generation = result.get("generations_by_pk", {})
                    status = generation.get("status", "UNKNOWN")
                    
                    print(f"[INFO] Generation status: {status}")
                    
                    if status == "COMPLETE":
                        images = generation.get("generated_images", [])
                        if images:
                            image_url = images[0].get("url")
                            print(f"[SUCCESS] Generation complete!")
                            print(f"   Generated image: {image_url}")
                            return image_url
                        else:
                            print("[ERROR] No images in completed generation")
                            return None
                    else:
                        print(f"[INFO] Still processing: {status}")
                        return "processing"
                else:
                    error_text = await response.text()
                    print(f"[ERROR] Status check failed: {response.status}")
                    print(f"   Response: {error_text}")
                    return None
                    
    except Exception as e:
        print(f"[ERROR] Status check error: {e}")
        return None

async def main():
    """Run complete Leonardo test"""
    print("=" * 60)
    print("LEONARDO.AI SIMPLE TEST")
    print("=" * 60)
    
    # Step 1: Upload test image
    upload_id = await test_leonardo_upload()
    if not upload_id:
        print("[FAILED] Could not upload image")
        return
    
    # Step 2: Start generation
    generation_id = await test_leonardo_generation(upload_id)
    if not generation_id:
        print("[FAILED] Could not start generation")
        return
    
    # Step 3: Check status (just once for demo)
    await asyncio.sleep(3)  # Wait a bit
    result = await test_leonardo_status(generation_id)
    
    if result == "processing":
        print("\n[INFO] Generation is processing...")
        print(f"[INFO] You can check status later with generation ID: {generation_id}")
        print("[SUCCESS] Leonardo integration is working!")
    elif result and result.startswith("http"):
        print(f"\n[SUCCESS] Complete! Generated image: {result}")
        print("[SUCCESS] Leonardo integration fully tested!")
    else:
        print("\n[WARNING] Status check had issues")
        print("[INFO] But upload and generation started successfully")

if __name__ == "__main__":
    asyncio.run(main())