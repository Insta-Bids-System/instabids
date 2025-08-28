"""
Stronger prompts to force replacement of brown grass areas
"""

import asyncio
import os
import aiohttp
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Even stronger prompts targeting brown grass
STRONGER_CONFIGS = [
    {
        "name": "FORCE brown area replacement",
        "init_strength": 0.28,
        "guidance_scale": 9,
        "prompt": "REMOVE ALL brown dead grass patches and replace with green artificial turf. Every brown dying area must become bright green synthetic grass. No brown patches allowed - all lawn areas become uniform emerald artificial turf. Complete grass removal and turf installation. Soccer goal stays in place.",
        "negative_prompt": "any brown grass, dead patches, brown spots, dying grass, keep any brown areas, partial coverage"
    },
    {
        "name": "Professional turf installation over ALL grass", 
        "init_strength": 0.26,
        "guidance_scale": 8,
        "prompt": "Professional artificial turf installation removes every bit of existing grass - green grass, brown grass, dead patches, weeds, bare spots. Install uniform premium synthetic grass over entire lawn area. All brown dying areas become vibrant green turf. Complete lawn renovation.",
        "negative_prompt": "brown grass visible, dead spots remaining, incomplete installation, patchy turf"
    },
    {
        "name": "Eliminate brown completely",
        "init_strength": 0.30,
        "guidance_scale": 7,
        "prompt": "Transform lawn by eliminating all brown dead grass and replacing with artificial turf. No brown patches should remain - all become green synthetic grass. Uniform emerald artificial turf covering complete yard. Brown dead areas specifically targeted for replacement.",
        "negative_prompt": "brown patches left, dead grass remaining, incomplete transformation, mixed grass types"
    }
]

async def run_stronger_test():
    """Run tests with stronger brown grass targeting"""
    
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    backyard_path = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\YOUR_ACTUAL_BACKYARD.jpg"
    
    headers = {"Authorization": f"Bearer {LEONARDO_API_KEY}", "Content-Type": "application/json"}
    
    print("=" * 70)
    print("STRONGER BROWN GRASS ELIMINATION TESTS")
    print("=" * 70)
    print()
    
    results = []
    
    for i, config in enumerate(STRONGER_CONFIGS):
        print(f"TEST {i+1}: {config['name']}")
        print(f"Init: {config['init_strength']}, Guidance: {config['guidance_scale']}")
        print()
        
        try:
            async with aiohttp.ClientSession() as session:                # Upload image
                async with session.post(
                    "https://cloud.leonardo.ai/api/rest/v1/init-image",
                    headers=headers,
                    json={"extension": "jpg"}
                ) as response:
                    if response.status != 200:
                        print(f"[SKIP] Upload failed for test {i+1}")
                        continue
                    
                    result = await response.json()
                    upload_data = result.get("uploadInitImage", {})
                    upload_id = upload_data.get("id")
                    upload_url = upload_data.get("url")
                    upload_fields = upload_data.get("fields", {})
                    
                    with open(backyard_path, "rb") as f:
                        image_data = f.read()
                    
                    form_data = aiohttp.FormData()
                    if isinstance(upload_fields, str):
                        upload_fields = json.loads(upload_fields)
                    for key, value in upload_fields.items():
                        form_data.add_field(key, value)
                    form_data.add_field('file', image_data, filename='image.jpg', content_type='image/jpeg')
                    
                    async with session.post(upload_url, data=form_data) as s3_response:
                        if s3_response.status not in [200, 201, 204]:
                            print(f"[SKIP] S3 upload failed for test {i+1}")
                            continue
                
                print(f"[SUCCESS] Uploaded for test {i+1}")
                
                # Generate
                generation_data = {
                    "prompt": config["prompt"],
                    "negative_prompt": config["negative_prompt"],
                    "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",
                    "width": 1024,
                    "height": 768,
                    "num_images": 1,
                    "init_image_id": upload_id,
                    "init_strength": config["init_strength"],
                    "guidance_scale": config["guidance_scale"]
                }                
                async with session.post(
                    "https://cloud.leonardo.ai/api/rest/v1/generations",
                    headers=headers,
                    json=generation_data
                ) as gen_response:
                    if gen_response.status != 200:
                        print(f"[SKIP] Generation failed for test {i+1}")
                        continue
                    
                    gen_result = await gen_response.json()
                    generation_id = gen_result.get("sdGenerationJob", {}).get("generationId")
                    
                    if not generation_id:
                        print(f"[SKIP] No generation ID for test {i+1}")
                        continue
                    
                    print(f"Generation {i+1} started: {generation_id}")
                    print("Waiting", end="")
                    
                    # Poll for result
                    for attempt in range(30):
                        await asyncio.sleep(8)
                        print(".", end="", flush=True)
                        
                        async with session.get(
                            f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                            headers=headers
                        ) as status_response:
                            if status_response.status == 200:
                                status_result = await status_response.json()
                                generation = status_result.get("generations_by_pk", {})
                                status = generation.get("status", "UNKNOWN")
                                
                                if status == "COMPLETE":
                                    images = generation.get("generated_images", [])
                                    if images:
                                        image_url = images[0].get("url")
                                        print(f"\n[SUCCESS] Test {i+1} complete!")
                                        print(f"[URL] {image_url}")
                                        results.append({
                                            "test": i+1,
                                            "name": config["name"],
                                            "url": image_url,
                                            "focus": "Eliminate brown grass"
                                        })
                                        break
                                elif status == "FAILED":
                                    print(f"\n[FAILED] Test {i+1} generation failed")
                                    break
                    else:
                        print(f"\n[TIMEOUT] Test {i+1} timed out")
        
        except Exception as e:
            print(f"[ERROR] Test {i+1} exception: {e}")
        
        print("\n" + "-" * 50)
    
    # Results summary
    print(f"\nSTRONGER BROWN GRASS TESTS COMPLETE!")
    print(f"Successful results: {len(results)}")
    
    if results:
        print("\n[RESULTS - STRONGER BROWN GRASS TARGETING]")
        for result in results:
            print(f"\nTest {result['test']}: {result['name']}")
            print(f"URL: {result['url']}")
        
        print(f"\n[EVALUATION] Look for:")
        print("1. Are brown/dead patches now GREEN turf?")
        print("2. Complete uniform artificial turf coverage?")
        print("3. Soccer goal position preserved?")

if __name__ == "__main__":
    asyncio.run(run_stronger_test())