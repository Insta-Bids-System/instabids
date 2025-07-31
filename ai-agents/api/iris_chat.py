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
from datetime import datetime
from supabase import create_client, Client
from anthropic import Anthropic

router = APIRouter()

# Initialize clients using environment variables
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")
claude = Anthropic(api_key=anthropic_key)

supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not supabase_url or not supabase_service_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")
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
        print(f"Iris chat error: {str(e)}")
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
    
    # Build system prompt with context
    system_prompt = build_iris_system_prompt(context)
    
    # Build conversation history for Claude
    claude_messages = build_claude_messages(context, message)
    
    try:
        response = claude.messages.create(
            model="claude-3-5-sonnet-20241022",  # Latest Claude model
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=claude_messages
        )
        
        ai_response = response.content[0].text
        
        # Generate contextual suggestions
        suggestions = generate_contextual_suggestions(context, message, ai_response)
        
        return {
            "response": ai_response,
            "suggestions": suggestions
        }
        
    except Exception as e:
        print(f"Claude API error: {str(e)}")
        # Fallback response
        return {
            "response": f"I understand you're working on your {context['board']['room_type'] if context.get('board') else 'space'}. I'm having technical difficulties right now, but I can still help you organize your ideas. What specific aspect would you like to focus on?",
            "suggestions": ["Tell me your vision", "Help organize ideas", "Analyze uploaded images", "Create project plan"]
        }

def build_iris_system_prompt(context: Dict[str, Any]) -> str:
    """Build system prompt for Iris with full context"""
    
    board = context.get("board", {})
    images = context.get("images", [])
    
    return f"""You are Iris, an expert interior design and home renovation assistant. You have persistent memory and full context awareness.

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
3. **Image Analysis**: You can analyze and categorize uploaded images
4. **Tag Management**: You help homeowners tag and organize their inspiration
5. **Vision Creation**: You can generate dream spaces by merging current + ideal images
6. **Project Planning**: You provide practical renovation advice

BEHAVIORAL GUIDELINES:
- Always acknowledge images you can see on the board
- Ask clarifying questions about image categorization (current vs ideal)
- Provide specific, actionable design advice
- Help organize and tag images for better project planning
- Offer to generate visualizations when appropriate
- Be conversational but professional

Remember: You have full access to this homeowner's board and all previously uploaded images. Reference them specifically in your responses."""

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
        print(f"Error saving conversation: {str(e)}")
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