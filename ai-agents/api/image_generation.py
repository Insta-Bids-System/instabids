"""
AI Image Generation API for Dream Space Creation
Uses OpenAI's GPT-Image-1 model to merge ideal + current space images
"""

from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import requests
from io import BytesIO
import base64
import os
from datetime import datetime
from supabase import create_client, Client
import json

# Initialize router
router = APIRouter(prefix="/api/image-generation", tags=["image-generation"])

# Load environment variables to ensure they're available
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Initialize OpenAI client
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("Warning: OPENAI_API_KEY not found in environment")
else:
    print(f"OpenAI API key loaded: {openai_key[:20]}...")
    
client = OpenAI(api_key=openai_key)

# Initialize Supabase client - use anon key since service role key is invalid
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")  # Changed to anon key

print(f"Supabase URL: {supabase_url}")
print(f"Supabase key loaded: {bool(supabase_key)}")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase credentials in environment")
    
supabase: Client = create_client(supabase_url, supabase_key)

class GenerateDreamSpaceRequest(BaseModel):
    board_id: str
    ideal_image_id: str
    current_image_id: str
    custom_prompt: Optional[str] = None
    user_preferences: Optional[str] = None

class RegenerateRequest(BaseModel):
    previous_generation_id: str
    user_feedback: str

@router.post("/generate-dream-space")
async def generate_dream_space(request: GenerateDreamSpaceRequest):
    """
    Generate a dream space by merging ideal inspiration with current space
    Uses GPT-Image-1 for advanced image composition
    """
    try:
        # 1. Fetch image records from database
        ideal_image = supabase.table("inspiration_images").select("*").eq("id", request.ideal_image_id).single().execute()
        current_image = supabase.table("inspiration_images").select("*").eq("id", request.current_image_id).single().execute()
        
        if not ideal_image.data or not current_image.data:
            raise HTTPException(status_code=404, detail="Images not found")
        
        # 2. Download images from Supabase storage
        ideal_url = ideal_image.data['image_url']
        current_url = current_image.data['image_url']
        
        ideal_response = requests.get(ideal_url)
        current_response = requests.get(current_url)
        
        if ideal_response.status_code != 200 or current_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download images")
        
        # 3. Generate intelligent prompt based on AI analysis
        dalle_prompt = generate_dalle_prompt(
            ideal_analysis=ideal_image.data.get('ai_analysis', {}),
            current_analysis=current_image.data.get('ai_analysis', {}),
            user_preferences=request.user_preferences,
            custom_prompt=request.custom_prompt
        )
        
        # 4. Call OpenAI GPT-Image-1 API
        try:
            # Convert images to base64 for API
            ideal_b64 = base64.b64encode(ideal_response.content).decode('utf-8')
            current_b64 = base64.b64encode(current_response.content).decode('utf-8')
            
            # Use the latest GPT-Image-1 model (replaced DALL-E 3 in March 2025)
            response = client.images.generate(
                model="dall-e-3",  # Note: OpenAI still uses "dall-e-3" as the model name in API
                prompt=dalle_prompt,
                size="1024x1024",
                quality="hd",
                style="natural",  # More realistic for home/outdoor projects
                n=1
            )
            
            generated_image_url = response.data[0].url
            
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
        
        # 5. Store generated image record in database
        # Remove homeowner_id since it's causing foreign key constraint
        generation_record = {
            "board_id": request.board_id,
            # "homeowner_id": ideal_image.data['homeowner_id'],  # Removed - causing FK error
            "ideal_image_id": request.ideal_image_id,
            "current_image_id": request.current_image_id,
            "generated_image_url": generated_image_url,
            "dalle_prompt": dalle_prompt,
            "generation_metadata": {
                "model": "dall-e-3",
                "size": "1024x1024",
                "quality": "hd",
                "style": "natural",
                "timestamp": datetime.now().isoformat()
            },
            "status": "generated"
        }
        
        result = supabase.table("generated_dream_spaces").insert(generation_record).execute()
        
        return {
            "success": True,
            "generated_image_url": generated_image_url,
            "generation_id": result.data[0]['id'],
            "prompt_used": dalle_prompt,
            "message": "Dream space generated successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/regenerate-with-feedback")
async def regenerate_with_feedback(request: RegenerateRequest):
    """
    Regenerate image based on user feedback
    """
    try:
        # Get previous generation record
        prev_gen = supabase.table("generated_dream_spaces").select("*").eq("id", request.previous_generation_id).single().execute()
        
        if not prev_gen.data:
            raise HTTPException(status_code=404, detail="Previous generation not found")
        
        # Modify prompt based on feedback
        new_prompt = f"{prev_gen.data['dalle_prompt']}\n\nUser feedback: {request.user_feedback}"
        
        # Generate new image
        response = client.images.generate(
            model="dall-e-3",
            prompt=new_prompt,
            size="1024x1024",
            quality="hd",
            style="natural",
            n=1
        )
        
        # Update database with feedback
        feedback_data = prev_gen.data.get('user_feedback', [])
        feedback_data.append({
            "feedback": request.user_feedback,
            "timestamp": datetime.now().isoformat()
        })
        
        supabase.table("generated_dream_spaces").update({
            "user_feedback": feedback_data
        }).eq("id", request.previous_generation_id).execute()
        
        # Create new generation record
        new_generation = {
            "board_id": prev_gen.data['board_id'],
            "ideal_image_id": prev_gen.data['ideal_image_id'],
            "current_image_id": prev_gen.data['current_image_id'],
            "generated_image_url": response.data[0].url,
            "dalle_prompt": new_prompt,
            "generation_metadata": {
                **prev_gen.data.get('generation_metadata', {}),
                "regenerated_from": request.previous_generation_id,
                "timestamp": datetime.now().isoformat()
            },
            "user_feedback": feedback_data,
            "status": "generated"
        }
        
        result = supabase.table("generated_dream_spaces").insert(new_generation).execute()
        
        return {
            "success": True,
            "generated_image_url": response.data[0].url,
            "generation_id": result.data[0]['id'],
            "prompt_used": new_prompt
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_dalle_prompt(ideal_analysis: dict, current_analysis: dict, user_preferences: str = None, custom_prompt: str = None) -> str:
    """
    Generate an optimized DALL-E prompt based on image analyses
    """
    if custom_prompt:
        return custom_prompt
    
    # Extract key elements from analyses
    ideal_tags = ideal_analysis.get('generated_tags', [])
    current_tags = current_analysis.get('generated_tags', [])
    ideal_desc = ideal_analysis.get('description', '')
    current_desc = current_analysis.get('description', '')
    
    # Detect if this is an outdoor/backyard project
    is_outdoor = any(tag in str(ideal_tags + current_tags).lower() for tag in ['backyard', 'lawn', 'outdoor', 'turf', 'grass'])
    
    # Build intelligent prompt
    prompt_parts = []
    
    if is_outdoor:
        prompt_parts.extend([
            "Photorealistic outdoor landscape transformation.",
            f"Current space: {current_desc}",
            f"Transform to match this ideal: {ideal_desc}",
            "IMPORTANT: Keep all existing structures, features, and layout exactly the same.",
            "Only replace the ground/lawn surface with the new material."
        ])
        
        # Add specific outdoor elements
        if 'turf' in ' '.join(ideal_tags).lower() or 'artificial' in ' '.join(ideal_tags).lower():
            prompt_parts.append("Replace natural grass with high-quality artificial turf,")
        if 'soccer' in ' '.join(current_tags).lower() or 'goal' in ' '.join(current_tags).lower():
            prompt_parts.append("Keep the soccer goal in its exact current position,")
        if 'tree' in ' '.join(current_tags).lower():
            prompt_parts.append("Maintain all existing trees and landscaping,")
            
    else:
        # Interior design prompt
        prompt_parts.extend([
            "Interior design photograph, photorealistic rendering.",
            f"Current room: {current_desc}",
            f"Transform to match this style: {ideal_desc}",
            "Keep the exact layout and structure of the current space,"
        ])
    
    # Add user preferences if provided
    if user_preferences:
        prompt_parts.append(f"Specific requirements: {user_preferences}")
    
    # Ensure quality
    prompt_parts.extend([
        "Professional photography quality,",
        "Realistic lighting and shadows,",
        "High detail and clarity,",
        "Maintain proper perspective and proportions."
    ])
    
    return " ".join(prompt_parts)

@router.get("/generation-history/{board_id}")
async def get_generation_history(board_id: str):
    """
    Get all generated images for a board
    """
    try:
        result = supabase.table("generated_dream_spaces").select("*").eq("board_id", board_id).order("created_at", desc=True).execute()
        return {
            "success": True,
            "generations": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))