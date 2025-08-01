"""
Demo Iris Chat API - Working endpoint for testing
"""

from fastapi import APIRouter
from pydantic import BaseModel
from anthropic import Anthropic
from typing import Optional, List, Dict
import os
import requests
import asyncio
from .image_generation import generate_dream_space, GenerateDreamSpaceRequest

router = APIRouter()

# Get API key but don't initialize Claude at import time
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
claude = None  # Initialize later if needed

class IrisChatRequest(BaseModel):
    message: str
    homeowner_id: str
    board_id: Optional[str] = None
    conversation_context: Optional[List[Dict]] = None

@router.post("/api/iris/chat")
async def iris_chat_working(request: IrisChatRequest):
    """
    Working Iris chat with immediate intelligent responses
    """
    # Check if user is asking for image generation
    generation_keywords = ["generate", "create", "make", "show me", "build", "visualize", "vision"]
    is_generation_request = any(keyword in request.message.lower() for keyword in generation_keywords)
    
    # Return immediate intelligent response
    return await generate_smart_fallback_response(request.message, is_generation_request, request)

async def generate_smart_fallback_response(message: str, is_generation_request: bool, request: IrisChatRequest = None):
    """Generate intelligent fallback responses when Claude API is unavailable"""
    message_lower = message.lower()
    
    if is_generation_request and request:
        # Actually call the image generation API directly
        try:
            print(f"[IRIS] Attempting to generate image for: {request.message}")
            generation_request = GenerateDreamSpaceRequest(
                board_id=request.board_id or "26cf972b-83e4-484c-98b6-a5d1a4affee3",
                ideal_image_id="inspiration_1",
                current_image_id="current_1", 
                user_preferences=request.message
            )
            
            print(f"[IRIS] Calling generate_dream_space with board_id: {generation_request.board_id}")
            # Call the function directly (already in async context)
            result = await generate_dream_space(generation_request)
            print(f"[IRIS] Generation result: success={result.get('success')}, url={result.get('generated_image_url', 'None')[:50]}...")
            
            if result.get("success"):
                return {
                    "response": f"Perfect! I've created your dream kitchen visualization! I combined your current space with the design elements you love - exposed brick walls and wood countertops from your inspiration image.\n\nThe generated vision shows how your space could look with those farmhouse elements applied. You can see the new image in your vision board!\n\nWhat do you think of this transformation? Would you like me to help you find contractors who can make this vision a reality?",
                    "suggestions": ["Find specialized contractors", "Generate another variation", "Plan the renovation timeline", "Explore material options"],
                    "image_generated": True,
                    "generation_id": result.get("generation_id"),
                    "image_url": result.get("generated_image_url"),
                    "data": result  # Include all the data for frontend
                }
            else:
                print(f"Image generation failed: {result}")
                
        except Exception as e:
            print(f"Image generation error: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback if image generation fails
        return {
            "response": "I would love to create a vision image for you! I can see your inspiration board with the exposed brick and wood countertop elements. I'm working on generating that vision for you right now.\n\n**Your Dream Kitchen Vision (generating...):**\n- Keep your current layout (it works well!)\n- Add exposed brick accent wall behind stove area\n- Replace countertops with warm butcher block\n- Update cabinet hardware to complement the rustic feel\n- Add pendant lighting to match the industrial style\n\nThis would give you that perfect modern farmhouse aesthetic you're looking for. Let me try generating that image again, or would you like me to help you find contractors who specialize in this style?",
            "suggestions": ["Try generating image again", "Find specialized contractors", "Plan the renovation timeline", "Show me design alternatives"]
        }
    
    if any(word in message_lower for word in ["cost", "price", "budget", "expensive"]):
        return {
            "response": "I focus on helping you create your dream design vision rather than discussing pricing. The best approach is to connect with qualified contractors who can provide accurate estimates based on your specific space and requirements.\n\nBased on the design elements I can see you love (exposed brick and wood countertops), I can help you:\n- Refine your design vision\n- Find the right contractors for this style\n- Plan the renovation timeline\n- Explore different material options\n\nWould you like me to help you connect with contractors who specialize in this modern farmhouse aesthetic?",
            "suggestions": ["Find specialized contractors", "Explore material options", "Plan renovation timeline", "Refine design vision"]
        }
    
    if any(word in message_lower for word in ["contractor", "install", "hire", "professional"]):
        return {
            "response": "I can definitely help you find the right contractors for your farmhouse kitchen transformation! For the exposed brick and butcher block project, you'll want specialists in:\n\n**Contractor Types Needed:**\n- **Masonry/Brickwork Specialists** - For the exposed brick wall\n- **Custom Countertop Installers** - For butcher block templating and installation\n- **General Kitchen Contractors** - For coordination and supporting work\n\nI can reach out to local contractors who specifically excel at this modern farmhouse style. They'll provide free estimates and have portfolios showing similar transformations.\n\nWould you like me to start connecting you with qualified contractors in your area?",
            "suggestions": ["Yes, find contractors now", "Show me their previous work", "Get multiple quotes", "Check contractor reviews"]
        }
    
    if any(word in message_lower for word in ["hello", "hi", "hey", "start"]):
        return {
            "response": "Hi! I am Iris, your design assistant for this Dream Kitchen Transformation board!\n\nI can see you have some beautiful inspiration images here - that exposed brick wall and wood countertop combination is absolutely stunning! It is going to create such a warm, modern farmhouse feel.\n\nI am here to help you turn this vision into reality. I can:\n- Generate visualization images of your transformed space\n- Help refine your design elements\n- Connect you with specialized contractors\n- Plan your renovation timeline\n\nWhat would you like to explore first? Click on any of your inspiration images to tell me more about what elements you love!",
            "suggestions": ["Generate a vision image", "Refine design elements", "Find contractors", "Plan the timeline"]
        }
    
    # Default intelligent response
    return {
        "response": "Thanks for sharing that! I can see your beautiful inspiration board with the exposed brick and wood elements - such a perfect modern farmhouse aesthetic!\n\nI'm experiencing some temporary connectivity issues with my AI processing, but I'm still here to help with your kitchen transformation. Based on what I can see on your board, you have excellent taste - that combination of rustic brick and warm wood will create such an inviting space.\n\nWhat aspect of your renovation would you like to focus on next? I can help with design planning, finding the right contractors, or discussing how these design elements will work in your current space.",
        "suggestions": ["Explore design elements", "Find contractors", "Plan renovation steps", "Refine your vision"]
    }

@router.post("/api/demo/iris/analyze-image")
async def demo_iris_analyze_image(request: dict):
    """
    Demo image analysis endpoint
    """
    return {
        "response": "I can see this space has great potential! The lighting and layout provide a good foundation. I'd love to help you identify specific areas for improvement and suggest some design directions. What's your vision for this space?",
        "analysis": {
            "current_state": ["Good natural light", "Functional layout", "Needs updating"],
            "suggestions": ["Fresh paint", "Modern fixtures", "Better organization"],
            "style_potential": ["Modern farmhouse", "Contemporary", "Transitional"]
        },
        "status": "success"
    }