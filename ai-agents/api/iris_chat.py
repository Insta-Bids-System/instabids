"""
Iris Chat API - Real AI assistant with Claude Opus 4
Provides persistent memory, board ownership, and image context
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import uuid
import requests
import logging
from datetime import datetime
from supabase import create_client, Client
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize clients using environment variables
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")
claude = Anthropic(api_key=anthropic_key)

supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not supabase_url or not supabase_service_key:
    # For development, fallback to anon key if service role key is not available
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    if supabase_url and supabase_anon_key:
        logger.warning("Using SUPABASE_ANON_KEY instead of SERVICE_ROLE_KEY for development")
        supabase: Client = create_client(supabase_url, supabase_anon_key)
    else:
        raise ValueError("SUPABASE_URL and either SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY environment variables are required")
else:
    supabase: Client = create_client(supabase_url, supabase_service_key)

class IrisChatRequest(BaseModel):
    message: str
    homeowner_id: str
    board_id: Optional[str] = None
    conversation_context: Optional[List[Dict]] = None
    image_uploads: Optional[List[str]] = None  # Image IDs if uploading

class IrisChatResponse(BaseModel):
    response: str
    suggestions: List[str]
    board_id: Optional[str] = None
    created_board: bool = False

@router.post("/api/iris/chat", response_model=IrisChatResponse)
async def iris_chat(request: IrisChatRequest):
    """
    Main Iris chat endpoint with full context awareness
    """
    try:
        # 1. Get or create board for this conversation
        board_id = await get_or_create_board(request.homeowner_id, request.board_id, request.message)
        created_board = not request.board_id
        
        # 2. Load full context for this homeowner and board
        context = await build_conversation_context(
            homeowner_id=request.homeowner_id,
            board_id=board_id,
            conversation_context=request.conversation_context or []
        )
        
        # 3. Get Claude Opus 4 response with full context
        claude_response = await get_claude_response(
            message=request.message,
            context=context,
            board_id=board_id
        )
        
        # 4. Save conversation to database
        await save_conversation_turn(
            homeowner_id=request.homeowner_id,
            board_id=board_id,
            user_message=request.message,
            assistant_response=claude_response["response"]
        )
        
        return IrisChatResponse(
            response=claude_response["response"],
            suggestions=claude_response["suggestions"],
            board_id=board_id,
            created_board=created_board
        )
    
    except Exception as e:
        logger.error(f"Error in iris_chat: {e}")
        logger.error(f"Full error details: {repr(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # More informative error response
        error_msg = str(e)
        if "ANTHROPIC_API_KEY" in error_msg:
            response_text = "I'm having trouble connecting to my AI service. Please make sure the API key is configured correctly."
        elif "supabase" in error_msg.lower():
            response_text = "I'm having trouble accessing the database. Please check the connection settings."
        else:
            response_text = f"I encountered an error: {error_msg}. Please try again or contact support if the issue persists."
            
        return IrisChatResponse(
            response=response_text,
            suggestions=["Try again", "Upload images", "Describe your project"],
            board_id=request.board_id,
            created_board=False
        )

@router.post("/api/iris/generate-dream-space")
async def iris_generate_dream_space(request: IrisChatRequest):
    """
    Generate dream space visualization through Iris agent conversation
    """
    try:
        # 1. Build context from board
        context = await build_conversation_context(
            homeowner_id=request.homeowner_id,
            board_id=request.board_id,
            conversation_context=request.conversation_context or []
        )
        
        # 2. Check if we have current and inspiration images
        images = context.get("images", [])
        current_images = [img for img in images if "current" in img.get("tags", [])]
        inspiration_images = [img for img in images if "inspiration" in img.get("tags", []) or "ideal" in img.get("tags", [])]
        
        if not current_images or not inspiration_images:
            return IrisChatResponse(
                response="I need both a current space photo and inspiration images to generate your dream visualization. Could you upload both types of images?",
                suggestions=["Upload current space photo", "Upload inspiration images", "Help me organize images", "Tell me your vision"],
                board_id=request.board_id
            )
        
        # 3. Have Iris confirm generation preferences
        confirmation_prompt = f"""I can see your current {context['board']['room_type']} and your inspiration images. 
        
Before I generate your dream space visualization, let me confirm what you'd like to see:

Current Space: {current_images[0].get('ai_analysis', {}).get('description', 'Your current space')}
Inspiration: {inspiration_images[0].get('ai_analysis', {}).get('description', 'Your inspiration style')}

Would you like me to create a dream visualization that combines these? I can:
- Keep your current layout but apply the inspiration style
- Include specific elements you mentioned: {request.message}
- Generate a realistic transformation

Should I proceed with generating your dream {context['board']['room_type']}?"""
        
        # If user is confirming or requesting generation
        if any(word in request.message.lower() for word in ["yes", "generate", "create", "make", "show me", "proceed"]):
            # 4. Call the image generation API
            try:
                generation_payload = {
                    "board_id": request.board_id,
                    "ideal_image_id": inspiration_images[0]["id"],
                    "current_image_id": current_images[0]["id"],
                    "user_preferences": request.message
                }
                
                # Call the existing image generation endpoint
                response = requests.post(
                    "http://localhost:8008/api/image-generation/generate-dream-space",
                    json=generation_payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 5. Save conversation about the generation
                    await save_conversation_turn(
                        homeowner_id=request.homeowner_id,
                        board_id=request.board_id,
                        user_message=request.message,
                        assistant_response=f"I've generated your dream {context['board']['room_type']} visualization! The image combines your current space with the inspiration elements you love. You can see it in your vision board."
                    )
                    
                    return IrisChatResponse(
                        response=f"✨ I've created your dream {context['board']['room_type']} visualization! \n\nThe generated image shows your current space transformed with the {inspiration_images[0].get('ai_analysis', {}).get('style', 'beautiful')} style from your inspiration. I've saved it to your vision board where you can see all three images together:\n\n• Current Space: Your existing {context['board']['room_type']}\n• Inspiration: Your style goals\n• My Vision: The AI-generated dream transformation\n\nWhat do you think of the result? Would you like me to generate any variations or help you plan the next steps?",
                        suggestions=["I love it! Plan the project", "Generate a variation", "What would this cost?", "Show me similar styles"],
                        board_id=request.board_id
                    )
                else:
                    # Generation failed, but provide helpful response
                    return IrisChatResponse(
                        response="I had some technical difficulty generating the visualization right now, but I can still help you plan your transformation! Based on your current space and inspiration, I can provide detailed renovation recommendations. What specific aspects would you like to focus on?",
                        suggestions=["Tell me renovation steps", "Help with style planning", "Suggest materials", "Estimate timeline"],
                        board_id=request.board_id
                    )
                    
            except Exception as gen_error:
                print(f"Generation error: {gen_error}")
                return IrisChatResponse(
                    response="I'm having trouble with the visualization generation right now, but I can help you plan your renovation in other ways. What specific aspects of the transformation are you most excited about?",
                    suggestions=["Describe your dream outcome", "Plan renovation phases", "Discuss budget", "Find contractors"],
                    board_id=request.board_id
                )
        else:
            # 6. Ask for confirmation or provide guidance
            return IrisChatResponse(
                response=confirmation_prompt,
                suggestions=["Yes, generate my dream space", "Let me add more inspiration", "Tell me about the process", "What will it look like?"],
                board_id=request.board_id
            )
            
    except Exception as e:
        print(f"Dream generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_or_create_board(homeowner_id: str, board_id: Optional[str], message: str) -> str:
    """Get existing board or create new one based on conversation"""
    
    if board_id:
        # Verify board exists and belongs to homeowner
        result = supabase.table("inspiration_boards").select("*").eq("id", board_id).eq("homeowner_id", homeowner_id).execute()
        if result.data:
            return board_id
    
    # Create new board - determine topic from message
    topic = determine_board_topic(message)
    
    new_board = {
        "id": str(uuid.uuid4()),
        "homeowner_id": homeowner_id,
        "title": topic["title"],
        "description": topic["description"],
        "room_type": topic["room_type"],
        "status": "collecting",
        "created_at": datetime.now().isoformat()
    }
    
    result = supabase.table("inspiration_boards").insert(new_board).execute()
    return new_board["id"]

def determine_board_topic(message: str) -> Dict[str, str]:
    """Determine board topic from initial message"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["backyard", "lawn", "grass", "turf", "outdoor"]):
        return {
            "title": "Backyard Transformation",
            "description": "Outdoor space and lawn renovation ideas",
            "room_type": "outdoor_backyard"
        }
    elif any(word in message_lower for word in ["kitchen", "cook", "cabinet", "counter"]):
        return {
            "title": "Kitchen Renovation", 
            "description": "Kitchen design and renovation inspiration",
            "room_type": "kitchen"
        }
    elif any(word in message_lower for word in ["bathroom", "shower", "bath", "tile"]):
        return {
            "title": "Bathroom Renovation",
            "description": "Bathroom design and renovation ideas", 
            "room_type": "bathroom"
        }
    else:
        return {
            "title": "Latest AI Assisted Board",
            "description": "Design inspiration and renovation ideas",
            "room_type": "general"
        }

async def build_conversation_context(homeowner_id: str, board_id: str, conversation_context: List[Dict]) -> Dict[str, Any]:
    """Build complete context for Claude including board images and history"""
    
    # Get board details
    board_result = supabase.table("inspiration_boards").select("*").eq("id", board_id).execute()
    board = board_result.data[0] if board_result.data else None
    
    # Get all images for this board
    images_result = supabase.table("inspiration_images").select("*").eq("board_id", board_id).execute()
    images = images_result.data or []
    
    # Get conversation history for this board
    history_result = supabase.table("inspiration_conversations").select("*").eq("board_id", board_id).order("created_at").execute()
    history = history_result.data or []
    
    return {
        "homeowner_id": homeowner_id,
        "board": board,
        "images": images,
        "conversation_history": history,
        "current_conversation": conversation_context
    }

async def get_claude_response(message: str, context: Dict[str, Any], board_id: str) -> Dict[str, Any]:
    """Get response from Claude Opus 4 with full context"""
    
    # Check if user is requesting image generation
    generation_keywords = ["generate", "create", "make", "show me", "build", "visualize", "vision"]
    is_generation_request = any(keyword in message.lower() for keyword in generation_keywords)
    
    images = context.get("images", [])
    current_images = [img for img in images if "current" in img.get("generated_tags", []) or "current-state" in img.get("generated_tags", [])]
    inspiration_images = [img for img in images if "inspiration" in img.get("generated_tags", []) or "ideal" in img.get("generated_tags", [])]
    
    # If user wants generation and we have the required images, attempt generation
    if is_generation_request and current_images and inspiration_images:
        try:
            generation_result = await attempt_image_generation(
                board_id=board_id,
                current_image=current_images[0],
                inspiration_image=inspiration_images[0],
                user_message=message,
                context=context
            )
            
            if generation_result["success"]:
                return {
                    "response": generation_result["response"],
                    "suggestions": ["What do you think of this vision?", "Generate a variation", "Plan the next steps", "Estimate costs"]
                }
        except Exception as gen_error:
            logger.error(f"Image generation failed: {gen_error}")
            # Continue with normal response
    
    # Build system prompt with context
    system_prompt = build_iris_system_prompt(context)
    
    # Build conversation history for Claude
    claude_messages = build_claude_messages(context, message)
    
    try:
        logger.info(f"Calling Claude API with message: {message[:100]}...")
        logger.info(f"System prompt length: {len(system_prompt)}")
        logger.info(f"Message count: {len(claude_messages)}")
        
        response = claude.messages.create(
            model="claude-3-5-sonnet-20241022",  # Latest Claude model
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=claude_messages
        )
        
        ai_response = response.content[0].text
        logger.info(f"Claude response received: {ai_response[:100]}...")
        
        # Generate contextual suggestions
        suggestions = generate_contextual_suggestions(context, message, ai_response)
        
        return {
            "response": ai_response,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Claude API error: {str(e)}")
        logger.error(f"Full error details: {repr(e)}")
        # Return a more helpful error message
        return {
            "response": f"I apologize, but I'm having trouble connecting to my AI service right now. Error: {str(e)}. Please try again in a moment, or let me know if you need help with something specific about your {context.get('board', {}).get('room_type', 'project')}.",
            "suggestions": ["Try again", "Tell me your vision", "Upload images", "Describe your project"]
        }

def build_iris_system_prompt(context: Dict[str, Any]) -> str:
    """Build system prompt for Iris with full context"""
    
    board = context.get("board", {})
    images = context.get("images", [])
    
    return f"""You are Iris, an expert interior design and home renovation assistant powered by Claude Opus 4. You have persistent memory, full context awareness, and can help create AI-generated vision boards.

CURRENT CONTEXT:
- Homeowner ID: {context['homeowner_id']}
- Board: "{board.get('title', 'Unknown')}" ({board.get('room_type', 'general')})
- Description: {board.get('description', 'Design project')}
- Images uploaded: {len(images)} images
- Board status: {board.get('status', 'collecting')}

UPLOADED IMAGES CONTEXT:
{format_images_for_context(images)}

YOUR CAPABILITIES:
1. **Board Ownership**: You can see and reference ALL images uploaded to this board
2. **Persistent Memory**: You remember the entire conversation history  
3. **Image Analysis**: You can analyze and understand design elements in uploaded images
4. **Vision Generation**: You can create AI-generated dream space visualizations using DALL-E 3
5. **Project Planning**: You provide practical renovation advice and timelines
6. **Style Understanding**: You can identify and explain design styles, materials, and colors

IMAGE GENERATION CAPABILITY:
- When the user has both current space and inspiration images, you can generate a dream visualization
- To generate, the user needs to say things like "generate", "create", "show me", "make a vision"
- You'll combine their current space with their inspiration style preferences
- The generated image appears in their vision board as "My Vision"

BEHAVIORAL GUIDELINES:
- Be warm, helpful, and conversational - you're their design partner
- When users click images, acknowledge what you see and understand
- Help them articulate their vision by asking about specific elements they like
- Offer to generate dream visualizations when you have enough context
- Provide practical advice about materials, costs, and implementation
- Reference specific details from their uploaded images in your responses

IMPORTANT: You are NOT giving canned responses. Each interaction should be unique and tailored to what the user is showing and telling you. If asked about your capabilities, explain that you can see their images, understand their style preferences, and generate new vision boards."""

def format_images_for_context(images: List[Dict]) -> str:
    """Format image information for Claude context"""
    if not images:
        return "No images uploaded yet."
    
    formatted = []
    for img in images:
        tags = ", ".join(img.get("generated_tags", []) or [])
        analysis = img.get("ai_analysis", {})
        category = img.get("category", "unknown")
        
        formatted.append(f"""
Image: {img.get('title', 'Untitled')}
- Category: {category}
- Tags: {tags}
- Analysis: {analysis.get('description', 'No analysis available')}
- Uploaded: {img.get('created_at', 'Unknown time')}""")
    
    return "\n".join(formatted)

def build_claude_messages(context: Dict[str, Any], current_message: str) -> List[Dict]:
    """Build conversation history for Claude"""
    messages = []
    
    # Add conversation history
    for turn in context.get("conversation_history", []):
        if turn.get("user_message"):
            messages.append({"role": "user", "content": turn["user_message"]})
        if turn.get("assistant_response"):
            messages.append({"role": "assistant", "content": turn["assistant_response"]})
    
    # Add current conversation context
    for msg in context.get("current_conversation", []):
        if msg.get("role") in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current message
    messages.append({"role": "user", "content": current_message})
    
    return messages

def generate_contextual_suggestions(context: Dict[str, Any], message: str, response: str) -> List[str]:
    """Generate contextual suggestions based on conversation state"""
    
    board = context.get("board", {})
    images = context.get("images", [])
    room_type = board.get("room_type", "general")
    
    # Base suggestions by room type
    if room_type == "outdoor_backyard":
        base_suggestions = [
            "Help me organize these images",
            "What style works best for outdoor spaces?", 
            "Generate a dream space visualization",
            "Estimate project timeline"
        ]
    elif room_type == "kitchen":
        base_suggestions = [
            "Analyze my style preferences",
            "Suggest complementary elements",
            "Create a vision board",
            "Plan renovation phases"
        ]
    else:
        base_suggestions = [
            "Tell me what you love about these images",
            "Help categorize my inspiration",
            "Create a project summary",
            "Find similar styles"
        ]
    
    # Add image-specific suggestions if images exist
    if len(images) >= 2:
        base_suggestions.insert(0, "Generate dream space by merging images")
    elif len(images) == 1:
        base_suggestions.insert(0, "Help me analyze this image")
    else:
        base_suggestions.insert(0, "Upload inspiration images")
    
    return base_suggestions[:4]  # Limit to 4 suggestions

async def attempt_image_generation(board_id: str, current_image: Dict, inspiration_image: Dict, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Attempt to generate a dream space visualization"""
    
    try:
        # Call the existing image generation API
        generation_payload = {
            "board_id": board_id,
            "ideal_image_id": inspiration_image["id"],
            "current_image_id": current_image["id"],
            "user_preferences": user_message
        }
        
        logger.info(f"Calling image generation API with payload: {generation_payload}")
        
        response = requests.post(
            "http://localhost:8008/api/image-generation/generate-dream-space",
            json=generation_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            room_type = context.get('board', {}).get('room_type', 'space')
            
            return {
                "success": True,
                "response": f"✨ I've created your dream {room_type} visualization! \n\nI combined your current space with the {inspiration_image.get('ai_analysis', {}).get('style', 'beautiful')} elements from your inspiration image. The generated vision shows how your space could look with those design elements applied.\n\nYou can see the new vision in your board alongside your current and inspiration images. What do you think of this transformation? Would you like me to generate any variations or help you plan the implementation?"
            }
        else:
            logger.error(f"Image generation API failed with status {response.status_code}: {response.text}")
            return {
                "success": False,
                "response": "I'm having trouble generating the visualization right now, but I can help you plan your transformation in other ways. What specific elements from your inspiration image would you like to incorporate?"
            }
            
    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        return {
            "success": False,
            "response": "I had trouble creating the visualization, but I can still help you plan your renovation. Based on your current space and inspiration, what specific changes are you most excited about?"
        }

async def save_conversation_turn(homeowner_id: str, board_id: str, user_message: str, assistant_response: str):
    """Save conversation turn to database"""
    
    conversation_data = {
        "id": str(uuid.uuid4()),
        "homeowner_id": homeowner_id,
        "board_id": board_id,
        "user_message": user_message,
        "assistant_response": assistant_response,
        "created_at": datetime.now().isoformat()
    }
    
    try:
        supabase.table("inspiration_conversations").insert(conversation_data).execute()
    except Exception as e:
        logger.error(f"Error saving conversation: {str(e)}")
        # Don't fail the request if conversation saving fails

class ImageAnalysisRequest(BaseModel):
    image_urls: List[str]
    category: str  # 'ideal' or 'current'
    filenames: List[str]
    analysis_prompt: str
    board_info: Optional[Dict[str, Any]] = None

class ImageAnalysisResponse(BaseModel):
    content: List[Dict[str, Any]]
    tags: List[str]
    analysis: Dict[str, Any]

@router.post("/api/iris/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze uploaded images using Claude Vision API
    """
    try:
        # Prepare messages for Claude with vision capabilities
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": request.analysis_prompt
                    }
                ]
            }
        ]
        
        # Add each image URL to the message
        for url in request.image_urls:
            messages[0]["content"].append({
                "type": "image",
                "source": {
                    "type": "url",
                    "url": url
                }
            })
        
        # Call Claude with vision capabilities
        response = claude.messages.create(
            model="claude-3-5-sonnet-20241022",  # This model supports vision
            max_tokens=1500,
            temperature=0.7,
            messages=messages
        )
        
        # Extract response text
        response_text = response.content[0].text
        
        # Generate appropriate tags based on category
        if request.category == 'ideal':
            tags = [
                "inspiration",
                "design-goals", 
                "style-preference",
                "dream-elements",
                "wishlist"
            ]
        else:
            tags = [
                "current-state",
                "needs-improvement",
                "upgrade-potential",
                "existing-space",
                "before-photo"
            ]
        
        # Add more specific tags based on room type
        if request.board_info and request.board_info.get('room_type'):
            room_type = request.board_info['room_type']
            if room_type == 'kitchen':
                tags.extend(['kitchen-design', 'culinary-space'])
            elif room_type == 'bathroom':
                tags.extend(['bathroom-design', 'spa-retreat'])
            elif room_type == 'outdoor_backyard':
                tags.extend(['outdoor-living', 'landscape-design'])
        
        return ImageAnalysisResponse(
            content=[{"text": response_text}],
            tags=tags,
            analysis={
                "category": request.category,
                "filenames": request.filenames,
                "timestamp": datetime.now().isoformat(),
                "model": "claude-3-5-sonnet-20241022"
            }
        )
        
    except Exception as e:
        print(f"Image analysis error: {str(e)}")
        # Return a fallback response
        fallback_text = f"""I can see you've uploaded {len(request.image_urls)} {request.category} image(s). 
        
While I'm having trouble with detailed analysis right now, I can help you organize and understand these images.

What specific elements or features in these images appeal to you most? This will help me provide better recommendations for your {request.board_info.get('room_type', 'project') if request.board_info else 'project'}."""
        
        return ImageAnalysisResponse(
            content=[{"text": fallback_text}],
            tags=["pending-analysis", request.category],
            analysis={
                "category": request.category,
                "filenames": request.filenames,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )