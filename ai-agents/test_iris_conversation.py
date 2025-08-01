#!/usr/bin/env python3
"""
Direct test of Iris conversation - bypass server, test actual agent functionality
"""

import os
import asyncio
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment
load_dotenv()

async def test_iris_conversation():
    """Test real Iris conversation and image generation"""
    
    # Get API key
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("ERROR: No ANTHROPIC_API_KEY found")
        return
    
    # Initialize Claude
    claude = Anthropic(api_key=anthropic_key)
    print("CLAUDE INITIALIZED")
    
    # Mock board context (simulating a real inspiration board)
    mock_context = {
        "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
        "board": {
            "title": "My Dream Kitchen Transformation",
            "room_type": "kitchen",
            "description": "Kitchen design and renovation inspiration",
            "status": "collecting"
        },
        "images": [
            {
                "id": "current_1",
                "title": "Current Kitchen",
                "category": "current",
                "generated_tags": ["current-state", "needs-improvement", "upgrade-potential"],
                "ai_analysis": {
                    "description": "Traditional kitchen with white cabinets, laminate countertops, and basic appliances. Good layout but dated finishes.",
                    "style": "traditional",
                    "features": ["white cabinets", "laminate counters", "tile backsplash"]
                },
                "created_at": "2025-01-30T10:00:00Z"
            },
            {
                "id": "inspiration_1", 
                "title": "Dream Style Inspiration",
                "category": "inspiration",
                "generated_tags": ["inspiration", "design-goals", "style-preference"],
                "ai_analysis": {
                    "description": "Modern farmhouse kitchen with exposed brick wall, butcher block countertops, and black metal fixtures. Warm and inviting atmosphere.",
                    "style": "modern farmhouse",
                    "features": ["exposed brick", "wood countertops", "black fixtures", "open shelving"]
                },
                "created_at": "2025-01-30T10:15:00Z"
            }
        ],
        "conversation_history": []
    }
    
    # Build Iris system prompt
    system_prompt = f"""You are Iris, an expert interior design and home renovation assistant powered by Claude Opus 4. You have persistent memory, full context awareness, and can help create AI-generated vision boards.

CURRENT CONTEXT:
- Homeowner ID: {mock_context['homeowner_id']}
- Board: "{mock_context['board']['title']}" ({mock_context['board']['room_type']})
- Description: {mock_context['board']['description']}
- Images uploaded: {len(mock_context['images'])} images
- Board status: {mock_context['board']['status']}

UPLOADED IMAGES CONTEXT:
{format_images_for_context(mock_context['images'])}

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

    # Test conversations
    test_conversations = [
        "Hi Iris! What images can you see on my board right now?",
        "I love the exposed brick in my inspiration image. Can you tell me more about that style?",
        "Can you create a vision for me that combines my current kitchen with that farmhouse style?",
        "What would it cost to add exposed brick to my kitchen?"
    ]
    
    conversation_history = []
    
    for i, message in enumerate(test_conversations, 1):
        print(f"\n=== CONVERSATION {i} ===")
        print(f"USER: {message}")
        
        # Build messages for Claude
        messages = conversation_history + [{"role": "user", "content": message}]
        
        try:
            response = claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                temperature=0.7,
                system=system_prompt,
                messages=messages
            )
            
            ai_response = response.content[0].text
            print(f"IRIS: {ai_response}")
            
            # Add to conversation history
            conversation_history.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": ai_response}
            ])
            
            # Test image generation trigger
            if "create" in message.lower() or "generate" in message.lower():
                print("\n[IRIS WOULD CALL IMAGE GENERATION API HERE]")
                print("Payload would be:")
                print({
                    "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3",
                    "current_image_id": "current_1",
                    "ideal_image_id": "inspiration_1",
                    "user_preferences": message
                })
        
        except Exception as e:
            print(f"ERROR: {e}")
            break

def format_images_for_context(images):
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
- Style: {analysis.get('style', 'Unknown')}
- Key Features: {', '.join(analysis.get('features', []))}
- Uploaded: {img.get('created_at', 'Unknown time')}""")
    
    return "\n".join(formatted)

if __name__ == "__main__":
    asyncio.run(test_iris_conversation())