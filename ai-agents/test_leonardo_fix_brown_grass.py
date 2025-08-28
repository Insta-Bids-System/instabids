"""
Leonardo test to fix the brown grass issue
Specifically target ALL grass areas (green AND brown) for replacement
"""

import asyncio
import os
import aiohttp
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Updated configs that specifically target ALL grass areas
TEST_CONFIGS = [
    {
        "name": "Target ALL grass - green AND brown dead areas",
        "init_strength": 0.20,
        "guidance_scale": 8,
        "prompt": "Replace ALL grass areas with perfect artificial turf - both the green grass AND the brown dead patchy areas. The entire lawn surface should become uniform emerald green artificial turf. Remove all brown patches, dead grass, weeds, and bare spots. Keep soccer goal, trees, building, driveway exactly the same. Complete lawn transformation to pristine artificial turf.",
        "negative_prompt": "brown grass, dead patches, weeds, bare spots, patchy lawn, mixed grass types, keep brown areas"
    },
    {
        "name": "Emphasize brown area removal", 
        "init_strength": 0.25,
        "guidance_scale": 7,
        "prompt": "Transform the entire lawn surface - replace both green healthy grass AND brown dead dying patches with uniform artificial turf. The brown dead areas must become green turf too. Complete lawn renovation with perfect synthetic grass covering all ground areas. Soccer goal stays in exact position, all structures preserved.",
        "negative_prompt": "brown patches, dead grass, patchy areas, inconsistent grass, leave brown spots"
    },
    {
        "name": "Complete lawn surface replacement",
        "init_strength": 0.22,
        "guidance_scale": 8,
        "prompt": "Replace the entire lawn surface with artificial turf. All grass areas - green, brown, patchy, dead, bare - should become uniform synthetic grass. Perfect emerald green artificial turf covering complete yard. Preserve house, soccer goal, trees, driveway exactly. Focus on making ALL ground vegetation into turf.",
        "negative_prompt": "partial replacement, brown spots remaining, patchy coverage, inconsistent turf"
    }    {
        "name": "Structure preservation + complete turf",
        "init_strength": 0.18,
        "guidance_scale": 9,
        "prompt": "Keep house, soccer goal, trees, driveway identical while replacing ALL lawn areas with artificial turf. Both green grass AND brown dead patches must become uniform synthetic grass. Complete yard renovation with perfect artificial turf. High structure preservation, complete grass replacement.",
        "negative_prompt": "altered buildings, moved structures, brown grass remaining, incomplete turf coverage"
    },
    {
        "name": "Professional turf installation simulation",
        "init_strength": 0.28,
        "guidance_scale": 7,
        "prompt": "Professional artificial turf installation replacing entire existing lawn. Remove all natural grass - green areas, brown dead spots, weeds, bare patches - and install uniform premium synthetic grass. Soccer goal remains in exact location. Perfect landscaping transformation with consistent turf coverage.",
        "negative_prompt": "natural grass remaining, brown patches, uneven coverage, poor installation"
    }
]

async def upload_image(image_path, description):
    """Upload image to Leonardo"""
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://cloud.leonardo.ai/api/rest/v1/init-image",
                headers=headers,
                json={"extension": "jpg"}
            ) as response:
                if response.status != 200:
                    return None
                
                result = await response.json()
                upload_data = result.get("uploadInitImage", {})
                upload_id = upload_data.get("id")
                upload_url = upload_data.get("url")
                upload_fields = upload_data.get("fields", {})                
                with open(image_path, "rb") as f:
                    image_data = f.read()
                
                form_data = aiohttp.FormData()
                if isinstance(upload_fields, str):
                    upload_fields = json.loads(upload_fields)
                for key, value in upload_fields.items():
                    form_data.add_field(key, value)
                form_data.add_field('file', image_data, filename='image.jpg', content_type='image/jpeg')
                
                async with session.post(upload_url, data=form_data) as s3_response:
                    if s3_response.status in [200, 201, 204]:
                        return upload_id
                    return None
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return None

async def generate_transformation(config, image_id):
    """Generate transformation with specific config"""
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    generation_data = {
        "prompt": config["prompt"],
        "negative_prompt": config["negative_prompt"],
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",
        "width": 1024,
        "height": 768,
        "num_images": 1,
        "init_image_id": image_id,
        "init_strength": config["init_strength"],
        "guidance_scale": config["guidance_scale"]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            headers=headers,
            json=generation_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("sdGenerationJob", {}).get("generationId")
            return Noneasync def check_generation_status(generation_id):
    """Wait for generation to complete"""
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
                        return None
                    
                    result = await response.json()
                    generation = result.get("generations_by_pk", {})
                    status = generation.get("status", "UNKNOWN")
                    
                    if status == "COMPLETE":
                        images = generation.get("generated_images", [])
                        if images:
                            return images[0].get("url")
                        return None
                    elif status == "FAILED":
                        return None
                    else:
                        print(".", end="", flush=True)
                        await asyncio.sleep(10)
                        attempt += 1
        except Exception as e:
            await asyncio.sleep(10)
            attempt += 1
    
    return "timeout"

async def main():
    """Test with improved prompts targeting brown grass issue"""
    print("=" * 70)
    print("LEONARDO BROWN GRASS FIX TESTING")
    print("=" * 70)
    print("Targeting ALL grass areas - green AND brown dead patches")
    print()
    
    backyard_path = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\YOUR_ACTUAL_BACKYARD.jpg"    
    if not Path(backyard_path).exists():
        print("[ERROR] Backyard image not found!")
        return
    
    # Upload backyard image
    print("Uploading your actual backyard...")
    image_id = await upload_image(backyard_path, "actual backyard")
    if not image_id:
        print("[ERROR] Failed to upload image")
        return
    
    print(f"[SUCCESS] Uploaded with ID: {image_id}")
    print()
    
    # Store results
    all_results = []
    
    for i, config in enumerate(TEST_CONFIGS):
        print(f"\nTEST {i+1}/{len(TEST_CONFIGS)}: {config['name']}")
        print(f"   Init: {config['init_strength']}, Guide: {config['guidance_scale']}")
        
        generation_id = await generate_transformation(config, image_id)
        if not generation_id:
            print(f"[SKIP] Failed to start generation")
            continue
        
        print("Generating", end="")
        result_url = await check_generation_status(generation_id)
        
        if result_url and result_url.startswith("http"):
            print(f"\n[SUCCESS] Complete!")
            print(f"[URL] {result_url}")
            
            result_info = {
                "config_num": i + 1,
                "config_name": config["name"],
                "init_strength": config["init_strength"],
                "guidance_scale": config["guidance_scale"],
                "url": result_url,
                "focus": "Fix brown grass issue - target ALL lawn areas"
            }
            all_results.append(result_info)
        else:
            print(f"\n[FAILED] Config {i+1} failed")
        
        if i < len(TEST_CONFIGS) - 1:
            print("Waiting 3 seconds...")
            await asyncio.sleep(3)    
    print("\n" + "=" * 70)
    print("BROWN GRASS FIX TESTING COMPLETE!")
    print("=" * 70)
    print(f"\nTested {len(TEST_CONFIGS)} configurations focused on brown grass issue")
    print(f"Successful: {len(all_results)}")
    
    if all_results:
        print("\n[RESULTS - BROWN GRASS FIXES]")
        print("-" * 50)
        for result in all_results:
            print(f"\nConfig {result['config_num']}: {result['config_name']}")
            print(f"  Focus: Target ALL grass areas (green AND brown)")
            print(f"  URL: {result['url']}")
        
        print("\n[EVALUATION CRITERIA]")
        print("Look for:")
        print("1. Are brown/dead areas now GREEN turf?")
        print("2. Is the entire lawn uniform artificial turf?") 
        print("3. Soccer goal in exact same position?")
        print("4. House and structures unchanged?")

if __name__ == "__main__":
    asyncio.run(main())