#!/usr/bin/env python3
"""
Fix image handling to upload to Supabase Storage first
"""

import os
from typing import List
import base64
from datetime import datetime
import uuid

async def upload_images_to_storage(supabase_client, user_id: str, images: List[str]) -> List[str]:
    """
    Upload base64 images to Supabase Storage and return URLs
    
    Args:
        supabase_client: Supabase client instance
        user_id: User ID for organizing images
        images: List of base64 encoded images
        
    Returns:
        List of public URLs for the uploaded images
    """
    uploaded_urls = []
    
    for idx, base64_image in enumerate(images):
        try:
            # Decode base64 to bytes
            image_data = base64.b64decode(base64_image)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{user_id}/{timestamp}_{uuid.uuid4().hex[:8]}_{idx}.jpg"
            
            # Upload to Supabase Storage
            response = supabase_client.storage.from_('project-images').upload(
                file_name,
                image_data,
                {
                    "content-type": "image/jpeg",
                    "cache-control": "3600",
                    "upsert": "false"
                }
            )
            
            # Get public URL
            public_url = supabase_client.storage.from_('project-images').get_public_url(file_name)
            uploaded_urls.append(public_url)
            
            print(f"[Upload] Successfully uploaded image {idx + 1}: {public_url}")
            
        except Exception as e:
            print(f"[Upload] Error uploading image {idx + 1}: {e}")
            # Continue with other images even if one fails
            
    return uploaded_urls


def fix_cia_agent_image_handling():
    """
    Show the fix needed in CIA agent
    """
    print("""
FIX FOR CIA AGENT (agents/cia/agent.py):

In handle_conversation method, before line 232:

# Upload images to storage first
if images and len(images) > 0:
    try:
        # Upload to Supabase Storage
        image_urls = await upload_images_to_storage(self.supabase, user_id, images)
        
        # Replace base64 with URLs
        images = image_urls
        
        print(f"[CIA] Uploaded {len(image_urls)} images to storage")
    except Exception as e:
        print(f"[CIA] Error uploading images: {e}")
        # Continue without images if upload fails
        images = []

This ensures:
1. Images are stored in Supabase Storage (persistent)
2. Only URLs are sent to Claude (no token limit issues)
3. URLs can be displayed in the dashboard
4. Images are attached to bid cards properly
""")


if __name__ == "__main__":
    fix_cia_agent_image_handling()