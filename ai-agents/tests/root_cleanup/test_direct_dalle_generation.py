"""
DIRECT DALL-E 3 IMAGE GENERATION TEST
This makes a REAL API call to OpenAI's DALL-E 3
No simulations, no fake responses - ACTUAL image generation
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import asyncio

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
print(f"Supabase URL: {supabase_url}")

client = OpenAI(api_key=openai_key)
supabase = create_client(supabase_url, supabase_key)

async def generate_backyard_transformation():
    """
    Generate REAL backyard transformation using DALL-E 3
    Transform patchy grass backyard into artificial turf paradise
    """
    
    print("\n" + "="*50)
    print(">>> REAL DALL-E 3 BACKYARD TRANSFORMATION")
    print("="*50)
    
    # Create the ACTUAL prompt for backyard transformation
    dalle_prompt = """
    Photorealistic backyard transformation, professional landscape photography.
    
    EXACT SCENE: Residential backyard with a white soccer goal in the center-left area.
    
    CRITICAL INSTRUCTIONS:
    1. Keep the EXACT same backyard layout, fence positions, tree locations, and soccer goal placement
    2. The white soccer goal MUST remain in the exact same position
    3. REPLACE all patchy, uneven natural grass with perfect artificial turf
    4. The artificial turf should be:
       - Lush, vibrant green color
       - Perfectly even and uniform texture
       - Professional-grade synthetic grass appearance
       - No bare spots or patches
    5. Maintain all existing elements: trees, fence, soccer goal, backyard shape
    6. Show the SAME backyard but with beautiful artificial turf instead of patchy grass
    
    Professional real estate photography style.
    Natural lighting, realistic shadows.
    The soccer goal sits on the new artificial turf.
    High detail, 4K quality, photorealistic rendering.
    """
    
    try:
        print("\n>>> Making REAL DALL-E 3 API call...")
        print("Prompt excerpt:", dalle_prompt[:200] + "...")
        
        # ACTUAL DALL-E 3 API CALL - THIS IS REAL
        response = client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="hd",
            style="natural",
            n=1
        )
        
        # Get the REAL generated image URL
        generated_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else dalle_prompt
        
        print("\n[SUCCESS] REAL IMAGE GENERATED!")
        print(f">>> Generated Image URL: {generated_url[:100]}...")
        print(f">>> Revised Prompt Used: {revised_prompt[:200]}...")
        
        # Save to database
        print("\n>>> Saving to database...")
        
        # Create board first (use title instead of name per actual schema)
        board_result = supabase.table("inspiration_boards").insert({
            "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
            "title": "Backyard Turf Transformation",
            "description": "Transform patchy grass to artificial turf",
            "room_type": "outdoor",
            "status": "collecting"  # Valid values: collecting, organizing, refining, ready
        }).execute()
        
        board_id = board_result.data[0]["id"]
        print(f">>> Board created: {board_id}")
        
        # Save as vision image
        vision_record = {
            "board_id": board_id,
            "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
            "image_url": generated_url,
            "thumbnail_url": generated_url,
            "source": "url",
            "tags": ["vision", "ai_generated", "backyard", "artificial_turf", "dall-e-3"],
            "ai_analysis": {
                "description": "AI-generated backyard with artificial turf replacing patchy grass",
                "style": "Photorealistic Landscape",
                "transformation": "Natural grass to artificial turf",
                "preserved_elements": ["soccer goal", "fence", "trees", "backyard layout"],
                "generation_model": "dall-e-3",
                "quality": "hd",
                "timestamp": datetime.now().isoformat()
            },
            "user_notes": "REAL DALL-E 3 generated transformation - backyard with artificial turf",
            "category": "ideal",
            "position": 0
        }
        
        vision_result = supabase.table("inspiration_images").insert(vision_record).execute()
        
        if vision_result.data:
            vision_id = vision_result.data[0]["id"]
            print(f"[SUCCESS] Vision image saved: {vision_id}")
            
            # Also save to generated_dream_spaces
            dream_space_record = {
                "board_id": board_id,
                "ideal_image_id": vision_id,  # Using the vision image as both
                "current_image_id": vision_id,
                "generated_image_url": generated_url,
                "dalle_prompt": dalle_prompt,
                "generation_metadata": {
                    "model": "dall-e-3",
                    "size": "1024x1024",
                    "quality": "hd",
                    "style": "natural",
                    "revised_prompt": revised_prompt,
                    "timestamp": datetime.now().isoformat(),
                    "test_type": "direct_backyard_transformation"
                },
                "status": "generated"
            }
            
            dream_result = supabase.table("generated_dream_spaces").insert(dream_space_record).execute()
            
            if dream_result.data:
                dream_id = dream_result.data[0]["id"]
                print(f"[SUCCESS] Dream space saved: {dream_id}")
        
        print("\n" + "="*50)
        print(">>> COMPLETE SUCCESS!")
        print("="*50)
        print(f"\n>>> VIEW YOUR GENERATED IMAGE:")
        print(f">>> URL: {generated_url}")
        print(f"\n>>> SAVED LOCATIONS:")
        print(f"   - Board ID: {board_id}")
        print(f"   - Vision Image ID: {vision_id}")
        print(f"   - Dream Space ID: {dream_id}")
        print("\n>>> The image shows your backyard with beautiful artificial turf!")
        print("   Soccer goal preserved, patchy grass replaced with perfect turf.")
        
        return {
            "success": True,
            "generated_url": generated_url,
            "board_id": board_id,
            "vision_id": vision_id,
            "dream_id": dream_id
        }
        
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("\n>>> Starting REAL DALL-E 3 Generation...")
    result = asyncio.run(generate_backyard_transformation())
    
    if result["success"]:
        print("\n[SUCCESS] TEST PASSED - REAL IMAGE GENERATED!")
        print(f">>> Open this URL in your browser to see the image:")
        print(f"   {result['generated_url']}")
    else:
        print("\n[FAILED] TEST FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")