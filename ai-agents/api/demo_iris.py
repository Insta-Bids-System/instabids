"""
Demo Iris Chat API - Working endpoint for testing
"""

from fastapi import APIRouter
from pydantic import BaseModel
from anthropic import Anthropic
import os

router = APIRouter()

# Initialize Claude with environment variable key
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")
claude = Anthropic(api_key=anthropic_key)

class IrisChatRequest(BaseModel):
    message: str
    homeowner_id: str

@router.post("/api/demo/iris/chat")
async def demo_iris_chat(request: IrisChatRequest):
    """
    Demo Iris chat that actually works with Claude Opus 4
    """
    try:
        # Call Claude Opus 4 with proper system message
        system_message = f"""You are Iris, an AI interior design assistant specializing in home inspiration and renovation guidance. You help homeowners:

1. **Vision Development**: Transform vague ideas into clear, actionable renovation plans
2. **Image Analysis**: Analyze photos to identify current state vs. ideal vision  
3. **Space Planning**: Provide practical layout and design recommendations
4. **Material Guidance**: Suggest specific materials, colors, and finishes
5. **Project Coordination**: Help organize renovation phases and contractor needs

**Your Personality**: 
- Enthusiastic but professional
- Detail-oriented with practical experience
- Encouraging and solution-focused
- Knowledgeable about current design trends and timeless principles

**Context**: You're helping homeowner {request.homeowner_id} with their renovation project. This is within their personal inspiration board workspace where they collect and organize home improvement ideas.

**Response Style**: 
- Ask clarifying questions to understand their vision
- Provide specific, actionable advice
- Mention when photos would be helpful for analysis
- Reference current design trends when relevant
- Keep responses conversational but informative (2-4 sentences usually)

Remember: You have full autonomy within this inspiration board to help them create, organize, and refine their renovation vision."""

        response = claude.messages.create(
            model="claude-3-5-sonnet-20241022",  # Using latest Sonnet instead of Opus 4
            max_tokens=1000,
            system=system_message,
            messages=[
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        )
        
        return {
            "response": response.content[0].text,
            "status": "success"
        }
        
    except Exception as e:
        print(f"Iris chat error: {str(e)}")
        return {
            "response": f"I'm having trouble connecting right now, but I'm excited to help you with your renovation! Can you tell me more about what space you're looking to transform?",
            "status": "error",
            "error": str(e)
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