"""
Final Leonardo test with focus on perfect turf transformation
Using the backyard image we have available
"""

import asyncio
import os
import aiohttp
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Your actual backyard that we found
BACKYARD_IMAGE = r"C:\Users\Not John Or Justin\Documents\instabids\test-images\real_backyard_current.jpg"

# Best configuration based on requirements
BEST_CONFIG = {
    "name": "Perfect Turf Transformation",
    "init_strength": 0.22,  # Sweet spot for preserving structure
    "guidance_scale": 7.5,
    "prompt": "Replace all grass with perfect artificial turf. Vibrant uniform emerald green synthetic grass, pristine manicured appearance like a golf course. Keep soccer goal exactly in place. Preserve all structures, trees, green trash bin, bushes unchanged. Professional artificial turf installation, photorealistic, high quality.",
    "negative_prompt": "patchy, brown, dead grass, moved objects, changed layout, cartoon, painting"
}

async def upload_local_image(image_path):
    """Upload image to Leonardo"""
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }    
    try:
        async with aiohttp.ClientSession() as session:
            # Get presigned upload URL
            async with session.post(
                "https://cloud.leonardo.ai/api/rest/v1/init-image",
                headers=headers,
                json={"extension": "jpg"}
            ) as response:
                if response.status != 200:
                    print(f"[ERROR] Failed to get upload URL")
                    return None
                
                result = await response.json()
                upload_data = result.get("uploadInitImage", {})
                upload_id = upload_data.get("id")
                upload_url = upload_data.get("url")
                upload_fields = upload_data.get("fields", {})
                
                # Read local image
                with open(image_path, "rb") as f:
                    image_data = f.read()
                
                # Upload to S3
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
async def generate_perfect_turf(image_id):
    """Generate the transformation"""
    LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    generation_data = {
        "prompt": BEST_CONFIG["prompt"],
        "negative_prompt": BEST_CONFIG["negative_prompt"],
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",
        "width": 1024,
        "height": 768,
        "num_images": 1,
        "init_image_id": image_id,
        "init_strength": BEST_CONFIG["init_strength"],
        "guidance_scale": BEST_CONFIG["guidance_scale"]
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
            return None