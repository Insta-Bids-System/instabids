"""
Iterative Leonardo testing until PERFECT artificial turf transformation
Will test multiple configurations and save all results for comparison
"""

import asyncio
import os
import aiohttp
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment
load_dotenv()

# Test configurations to iterate through
TEST_CONFIGS = [
    {
        "name": "Config 1: Minimal change, preserve everything",
        "init_strength": 0.15,
        "guidance_scale": 9,
        "prompt": "Replace only the patchy grass areas with perfect artificial turf. Keep the white soccer goal in exact position. Preserve all structures, trees, fences, and background exactly as they are. The turf should be vibrant green, perfectly uniform, realistic artificial grass texture. Professional landscape photo, high quality.",
        "negative_prompt": "blurry, distorted, moved objects, changed structures, different layout"
    },
    {
        "name": "Config 2: Slightly stronger, texture focus", 
        "init_strength": 0.20,
        "guidance_scale": 8,
        "prompt": "Transform the lawn to lush artificial turf with perfect green color and realistic synthetic grass texture. White soccer goal must stay in exact same position. All trees, structures, fences unchanged. Focus on making the turf look professionally installed, vibrant emerald green, uniform height, pristine condition. Photorealistic result.",
        "negative_prompt": "cartoon, painting, sketch, moved goal, altered structures, wrong perspective"
    },
    {
        "name": "Config 3: Balanced transformation",
        "init_strength": 0.25,
        "guidance_scale": 7,
        "prompt": "Professional artificial turf installation replacing all grass. Beautiful emerald green synthetic grass, perfectly manicured appearance, realistic texture. Soccer goal remains exactly where it is. Trees, fence, house, all structures preserved. Make the turf look like premium quality artificial grass, uniform and pristine. High-end landscape photography.",
        "negative_prompt": "low quality, unrealistic, objects moved, layout changed, blurry"
    },
    {
        "name": "Config 4: Stronger with detail emphasis",
        "init_strength": 0.30,
        "guidance_scale": 6,
        "prompt": "High-end artificial turf transformation of backyard. Premium synthetic grass in vibrant green, looks freshly installed. Every blade uniform height. Soccer goal untouched in original position. Preserve exact layout of yard, trees, structures. Focus on making artificial turf look incredibly realistic and well-maintained. Professional landscape result.",
        "negative_prompt": "amateur, distorted, moved elements, changed composition"
    },
    {
        "name": "Config 5: Maximum quality focus",
        "init_strength": 0.35,
        "guidance_scale": 7,
        "prompt": "Luxury artificial turf installation, emerald green synthetic grass covering entire lawn area. Looks like $50,000 professional installation. Soccer goal exactly where it was. All structures, trees, fences remain unchanged. The artificial turf should look incredibly realistic, perfectly uniform, pristine condition. Premium landscaping photography.",
        "negative_prompt": "cheap, fake looking, distorted, moved objects, altered scene"
    }
]

async def upload_local_image(image_path, description):
    """Upload a local image file to Leonardo"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    if not Path(image_path).exists():
        print(f"[ERROR] Image not found: {image_path}")
        print(f"Please save your images first!")
        return None
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"[INFO] Uploading {description} from {image_path}...")
            
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
                
                # Step 2: Read the local image file
                with open(image_path, "rb") as f:
                    image_data = f.read()
                print(f"[SUCCESS] Read {len(image_data)} bytes from local file")
                
                # Step 3: Upload to Leonardo's S3
                print(f"[INFO] Uploading to Leonardo S3...")
                
                form_data = aiohttp.FormData()
                
                # Handle upload_fields
                if isinstance(upload_fields, str):
                    upload_fields = json.loads(upload_fields)
                
                if isinstance(upload_fields, dict):
                    for key, value in upload_fields.items():
                        form_data.add_field(key, value)
                
                form_data.add_field('file', image_data, filename='image.jpg', content_type='image/jpeg')
                
                async with session.post(upload_url, data=form_data) as s3_response:
                    if s3_response.status in [200, 201, 204]:
                        print(f"[SUCCESS] {description} uploaded! ID: {upload_id}")
                        return upload_id
                    else:
                        error_text = await s3_response.text()
                        print(f"[ERROR] S3 upload failed: {s3_response.status}")
                        return None                        
    except Exception as e:
        print(f"[ERROR] Upload error for {description}: {e}")
        return None

async def generate_turf_transformation(config, current_image_id):
    """Generate transformation with specific configuration"""
    
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
        "init_image_id": current_image_id,
        "init_strength": config["init_strength"],
        "guidance_scale": config["guidance_scale"],
        "seed": None
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"[INFO] Testing: {config['name']}")
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
                        print(f"[SUCCESS] Generation started! ID: {generation_id}")
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
    
    max_attempts = 30
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
                        print(f"[ERROR] Status check failed: {response.status}")
                        return None
                    
                    result = await response.json()
                    generation = result.get("generations_by_pk", {})
                    status = generation.get("status", "UNKNOWN")
                    
                    if status == "COMPLETE":
                        images = generation.get("generated_images", [])
                        if images:
                            image_url = images[0].get("url")
                            return image_url
                        else:
                            print("[ERROR] No images in completed generation")
                            return None
                    elif status == "FAILED":
                        error = generation.get("imageGenerationJobs", [{}])[0].get("likelyHood", "Unknown error")
                        print(f"[ERROR] Generation failed: {error}")
                        return None
                    else:
                        # Don't print every check, just dots
                        print(".", end="", flush=True)
                        await asyncio.sleep(10)
                        attempt += 1
                        
        except Exception as e:
            print(f"[ERROR] Status check error: {e}")
            await asyncio.sleep(10)
            attempt += 1
    
    print("\n[WARNING] Generation timed out")
    return "timeout"

async def main():
    """Main testing loop - iterate until perfect"""
    print("=" * 70)
    print("LEONARDO PERFECT TURF TRANSFORMATION TESTING")
    print("=" * 70)
    print()
    
    # Local image paths - YOUR ACTUAL IMAGES  
    backyard_path = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\YOUR_ACTUAL_BACKYARD.jpg"
    turf_path = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\YOUR_IDEAL_TURF.jpg"
    
    # Check if images exist
    if not Path(backyard_path).exists() or not Path(turf_path).exists():
        print("[ERROR] Images not found!")
        print()
        print("Please save your images from the chat:")
        print(f"1. Save current backyard as: {backyard_path}")
        print(f"2. Save ideal turf as: {turf_path}")
        print()
        print("Then run this script again.")
        return
    
    print("[SUCCESS] Found both images locally!")
    print(f"  Current backyard: {backyard_path}")
    print(f"  Ideal turf: {turf_path}")
    print()
    
    # Upload current backyard
    print("STEP 1: Uploading your actual backyard image...")
    current_id = await upload_local_image(backyard_path, "your actual backyard")
    if not current_id:
        print("[ERROR] Failed to upload backyard image")
        return
    
    # Create results directory
    results_dir = Path(r"C:\Users\Not John Or Justin\Documents\instabids\test-images\results")
    results_dir.mkdir(exist_ok=True)
    
    # Store results
    all_results = []
    
    print("\nSTEP 2: Testing multiple configurations...")
    print("-" * 50)    
    for i, config in enumerate(TEST_CONFIGS):
        print(f"\nTEST {i+1}/{len(TEST_CONFIGS)}: {config['name']}")
        
        # Generate with this configuration
        generation_id = await generate_turf_transformation(config, current_id)
        if not generation_id:
            print(f"[SKIP] Failed to start generation for config {i+1}")
            continue
        
        # Wait for result
        print("Waiting for generation to complete", end="")
        result_url = await check_generation_status(generation_id)
        
        if result_url and result_url.startswith("http"):
            print(f"\n[SUCCESS] Generation complete!")
            
            # Save result info
            result_info = {
                "config_num": i + 1,
                "config_name": config["name"],
                "init_strength": config["init_strength"],
                "guidance_scale": config["guidance_scale"],
                "url": result_url,
                "timestamp": datetime.now().isoformat()
            }
            all_results.append(result_info)
            
            print(f"[RESULT] View at: {result_url}")
            print(f"[SAVED] Result #{i+1} recorded")
        else:
            print(f"\n[FAILED] Config {i+1} did not produce result")        
        # Brief pause between tests
        if i < len(TEST_CONFIGS) - 1:
            print("\nWaiting 5 seconds before next test...")
            await asyncio.sleep(5)
    
    # Save all results to file
    results_file = results_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETE!")
    print("=" * 70)
    print(f"\nTested {len(TEST_CONFIGS)} configurations")
    print(f"Successful: {len(all_results)}")
    print(f"\nResults saved to: {results_file}")
    
    if all_results:
        print("\n[RESULTS SUMMARY]")
        print("-" * 50)
        for result in all_results:
            print(f"\nConfig {result['config_num']}: {result['config_name']}")
            print(f"  Init: {result['init_strength']}, Guide: {result['guidance_scale']}")
            print(f"  URL: {result['url']}")
        
        print("\n[NEXT STEPS]")
        print("1. Review each generated image in Leonardo app")
        print("2. Identify which configuration works best")
        print("3. We can fine-tune the best one further")
        print("4. Or try completely different parameters")

if __name__ == "__main__":
    asyncio.run(main())