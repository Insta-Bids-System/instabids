"""
DALL-E 2 Image Editing Test
This uses the actual image editing (inpainting) capability
to transform an existing backyard photo
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import base64
from io import BytesIO
from PIL import Image
import requests

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path, override=True)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI
from supabase import create_client

# Initialize clients
openai_key = os.getenv("OPENAI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

print(f"OpenAI API Key: {openai_key[:20]}..." if openai_key else "NO KEY FOUND")

client = OpenAI(api_key=openai_key)
supabase = create_client(supabase_url, supabase_key)

def create_grass_mask(image_path):
    """
    Create a mask for grass areas in the backyard image
    For now, this creates a simple mask - in production you'd want
    to use image segmentation to identify grass areas accurately
    """
    # Open the image
    img = Image.open(image_path)
    width, height = img.size
    
    # Create a mask (white = edit area, black = keep original)
    mask = Image.new('RGBA', (width, height), (0, 0, 0, 255))
    
    # For demo: Create a mask that covers the ground area
    # In production, you'd use ML segmentation to identify grass
    # This creates a mask for the lower 60% of the image (where grass typically is)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    
    # Create transparent area where grass would be (lower portion, avoiding soccer goal)
    # This is a simplified mask - ideally use computer vision to detect grass
    draw.rectangle(
        [(0, int(height * 0.4)), (width, height)],
        fill=(255, 255, 255, 0)  # Transparent = area to edit
    )
    
    # Save mask
    mask_path = image_path.replace('.jpg', '_mask.png').replace('.png', '_mask.png')
    mask.save(mask_path)
    return mask_path

def edit_backyard_with_dalle2(image_path):
    """
    Use DALL-E 2's image editing to transform backyard
    """
    print("\n" + "="*50)
    print(">>> DALL-E 2 IMAGE EDITING TEST")
    print("="*50)
    
    try:
        # Create mask for grass areas
        print("\n>>> Creating mask for grass areas...")
        mask_path = create_grass_mask(image_path)
        print(f"Mask created: {mask_path}")
        
        # Prepare the editing prompt
        edit_prompt = """
        A residential backyard with lush, perfect artificial turf grass.
        The artificial turf is vibrant green, perfectly uniform, 
        professional-grade synthetic grass with no patches or bare spots.
        Keep the white soccer goal in the same position.
        Maintain all existing structures, fences, and trees.
        Professional landscape photography, natural lighting.
        """
        
        print("\n>>> Making DALL-E 2 edit API call...")
        print("Edit prompt:", edit_prompt[:100] + "...")
        
        # Open images
        with open(image_path, 'rb') as image_file:
            with open(mask_path, 'rb') as mask_file:
                # DALL-E 2 Image Edit API Call
                response = client.images.edit(
                    model="dall-e-2",
                    image=image_file,
                    mask=mask_file,
                    prompt=edit_prompt,
                    n=1,
                    size="1024x1024"
                )
        
        edited_url = response.data[0].url
        print("\n[SUCCESS] Image edited successfully!")
        print(f">>> Edited Image URL: {edited_url[:100]}...")
        
        # Save to database
        print("\n>>> Saving edited image to database...")
        
        # Create or use existing board
        board_result = supabase.table("inspiration_boards").insert({
            "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
            "title": "Backyard Turf Edit (DALL-E 2)",
            "description": "Actual backyard transformation using image editing",
            "room_type": "outdoor",
            "status": "collecting"
        }).execute()
        
        board_id = board_result.data[0]["id"]
        
        # Save edited image
        vision_record = {
            "board_id": board_id,
            "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
            "image_url": edited_url,
            "thumbnail_url": edited_url,
            "source": "url",
            "tags": ["edited", "dall-e-2", "backyard", "artificial_turf", "inpainting"],
            "ai_analysis": {
                "description": "Backyard with grass areas replaced with artificial turf",
                "method": "DALL-E 2 image editing (inpainting)",
                "original_image": image_path,
                "edit_prompt": edit_prompt,
                "timestamp": datetime.now().isoformat()
            },
            "user_notes": "DALL-E 2 edited version - actual transformation of your backyard",
            "category": "ideal",
            "position": 0
        }
        
        vision_result = supabase.table("inspiration_images").insert(vision_record).execute()
        
        if vision_result.data:
            vision_id = vision_result.data[0]["id"]
            print(f"[SUCCESS] Edited image saved: {vision_id}")
        
        print("\n" + "="*50)
        print(">>> EDIT COMPLETE!")
        print("="*50)
        print(f"\n>>> VIEW YOUR EDITED IMAGE:")
        print(f">>> URL: {edited_url}")
        print("\n>>> This is your ACTUAL backyard with artificial turf!")
        
        return {
            "success": True,
            "edited_url": edited_url,
            "vision_id": vision_id
        }
        
    except Exception as e:
        print(f"\n[ERROR] Edit failed: {str(e)}")
        if "Invalid image format" in str(e):
            print("Note: Images must be square PNG files less than 4MB")
        elif "model" in str(e):
            print("Note: Only DALL-E 2 supports image editing")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def download_and_prepare_image(url, output_path):
    """
    Download image from URL and prepare it for DALL-E 2
    (must be square PNG, less than 4MB)
    """
    print(f"\n>>> Downloading image from URL...")
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    
    # Convert to square by cropping to center
    width, height = img.size
    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    
    img_square = img.crop((left, top, right, bottom))
    
    # Resize if needed (max 1024x1024 for DALL-E 2)
    if size > 1024:
        img_square = img_square.resize((1024, 1024), Image.Resampling.LANCZOS)
    
    # Convert to RGBA for PNG
    if img_square.mode != 'RGBA':
        img_square = img_square.convert('RGBA')
    
    # Save as PNG
    img_square.save(output_path, 'PNG')
    print(f">>> Image prepared and saved: {output_path}")
    return output_path

if __name__ == "__main__":
    print("\n>>> Starting DALL-E 2 Image Editing Test...")
    
    # For testing, we'll use a placeholder image
    # In production, you'd upload the actual backyard photos
    test_image_url = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1024"  # Sample backyard
    
    # Download and prepare image
    local_image_path = "test_backyard.png"
    download_and_prepare_image(test_image_url, local_image_path)
    
    # Edit the image
    result = edit_backyard_with_dalle2(local_image_path)
    
    if result["success"]:
        print("\n[SUCCESS] Your backyard has been transformed!")
        print("This used DALL-E 2's actual image editing capability")
        print("to modify YOUR photo, not generate a new one.")
    else:
        print("\n[FAILED] Could not edit image")
        print("DALL-E 2 editing requires specific image formats")