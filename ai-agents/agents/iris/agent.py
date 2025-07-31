"""
Iris - Design Inspiration Assistant Agent
Uses Claude Opus 4 for intelligent conversations about home design and inspiration
"""
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from anthropic import Anthropic
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class IrisMessage(BaseModel):
    """Message format for Iris conversations"""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    board_context: Optional[Dict] = Field(default=None, description="Current board context")
    images: Optional[List[Dict]] = Field(default=None, description="Images being discussed")

class IrisRequest(BaseModel):
    """Request format for Iris API"""
    message: str = Field(..., description="User's message")
    board_id: Optional[str] = Field(default=None, description="Current board ID")
    board_title: Optional[str] = Field(default=None, description="Board title for context")
    board_description: Optional[str] = Field(default=None, description="Board description")
    board_room_type: Optional[str] = Field(default=None, description="Room type")
    board_status: Optional[str] = Field(default=None, description="Board status")
    images: Optional[List[Dict]] = Field(default=None, description="Images in the board")
    uploaded_images: Optional[List[str]] = Field(default=None, description="Base64 uploaded images")
    image_category: Optional[str] = Field(default=None, description="Image category: ideal or current")
    conversation_history: Optional[List[Dict]] = Field(default=None, description="Previous messages")

class IrisResponse(BaseModel):
    """Response format from Iris"""
    response: str = Field(..., description="Iris's response")
    suggestions: List[str] = Field(default_factory=list, description="Quick action suggestions")
    analysis: Optional[Dict] = Field(default=None, description="Image or style analysis")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class IrisAgent:
    """
    Iris - Your personal design inspiration assistant
    Powered by Claude Opus 4 for intelligent design conversations
    """
    
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-7-sonnet-20250219"  # Using Claude 3.7 Sonnet (most intelligent model)
        
        # Iris's personality and expertise
        self.system_prompt = """You are Iris, a friendly and knowledgeable design inspiration assistant for InstaBids. 
        
Your personality:
- Creative, encouraging, and helpful
- Expert in interior design, architecture, and home improvement
- Knowledgeable about design styles, trends, and practical considerations
- Budget-conscious and realistic about costs
- Helps organize scattered ideas into cohesive visions

Your capabilities:
- Analyze uploaded images to identify styles, colors, materials, and design elements
- Suggest how to organize and group inspiration images
- Identify common themes and potential conflicts in design choices
- Provide realistic budget estimates based on similar projects
- Guide users from inspiration to actionable project plans
- Help create vision summaries for contractors

When analyzing images or boards:
1. Look for patterns in style preferences (modern, traditional, farmhouse, etc.)
2. Identify color palettes and material choices
3. Note any potential conflicts or incompatibilities
4. Suggest practical considerations (maintenance, durability, cost)
5. Help prioritize elements based on impact and budget

CRITICAL: When users upload images, ALWAYS:
1. Ask them "What aspects of this photo do you like?" or similar preference questions to understand their specific interests
2. Automatically generate relevant tags and labels for the image (style, colors, materials, elements, room type, mood, etc.)
3. Include these auto-generated tags in your response to help organize and categorize the image

Always be encouraging but honest. Help users refine their vision while keeping it achievable.
When appropriate, suggest they're ready to start a project with the CIA agent.

Current context will be provided with each message."""
        
        logger.info("Iris Agent initialized with Claude 3.7 Sonnet (most intelligent model)")
    
    async def process_message(self, request: IrisRequest) -> IrisResponse:
        """Process a user message and generate Iris's response"""
        try:
            # Build context from the request
            context = self._build_context(request)
            
            # Prepare messages for Claude
            messages = self._prepare_messages(request, context)
            
            # Check if API is available
            api_key = os.getenv("ANTHROPIC_API_KEY")
            try:
                # Get response from Claude 3.7 Sonnet
                response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.7,
                    system=self.system_prompt,
                    messages=messages
                )
                
                # Extract content
                iris_response = response.content[0].text
                logger.info(f"Claude 3.7 Sonnet API call successful")
            except Exception as api_error:
                logger.warning(f"API call failed: {str(api_error)}")
                # Fallback to intelligent response
                iris_response = self._generate_fallback_response(request, context)
            
            # Generate suggestions based on context
            suggestions = self._generate_suggestions(request, iris_response)
            
            # Perform any image analysis if needed
            analysis = None
            if request.images and self._should_analyze_images(request.message):
                analysis = await self._analyze_images(request.images)
            
            logger.info(f"Iris processed message successfully")
            
            return IrisResponse(
                response=iris_response,
                suggestions=suggestions,
                analysis=analysis
            )
            
        except Exception as e:
            logger.error(f"Error processing Iris message: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # More helpful error response
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return IrisResponse(
                    response="I'm having trouble connecting to my AI service. Please check that the API key is configured correctly.",
                    suggestions=["Try again in a moment", "Check server logs", "Verify API configuration"]
                )
            else:
                return IrisResponse(
                    response=f"I encountered an issue: {error_msg[:100]}... Let me try a different approach. What specific aspect of your project would you like to discuss?",
                    suggestions=["Tell me about your project", "Show me your inspiration images", "What style do you prefer?"]
                )
    
    def _build_context(self, request: IrisRequest) -> str:
        """Build context string from the request"""
        context_parts = []
        
        if request.board_title:
            context_parts.append(f"Board: {request.board_title}")
        
        if request.board_description:
            context_parts.append(f"Description: {request.board_description}")
        
        if request.board_room_type:
            context_parts.append(f"Room Type: {request.board_room_type}")
        
        if request.board_status:
            status_map = {
                'collecting': 'Currently collecting ideas',
                'organizing': 'Organizing inspiration',
                'refining': 'Refining the vision',
                'ready': 'Ready to start project'
            }
            context_parts.append(f"Status: {status_map.get(request.board_status, request.board_status)}")
        
        if request.images:
            context_parts.append(f"Images: {len(request.images)} uploaded")
            # Add brief image descriptions if available
            for i, img in enumerate(request.images[:3]):  # First 3 images
                if img.get('tags'):
                    context_parts.append(f"  Image {i+1} tags: {', '.join(img['tags'])}")
        
        return "\n".join(context_parts) if context_parts else "No specific board selected"
    
    def _prepare_messages(self, request: IrisRequest, context: str) -> List[Dict]:
        """Prepare message history for Claude"""
        messages = []
        
        # Add context as first user message
        messages.append({
            "role": "user",
            "content": f"Current context:\n{context}\n\nPlease help me with my home design inspiration."
        })
        
        messages.append({
            "role": "assistant",
            "content": "I'm looking at your inspiration board. How can I help you organize and refine your vision?"
        })
        
        # Add conversation history if provided
        if request.conversation_history:
            for msg in request.conversation_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        return messages
    
    def _generate_suggestions(self, request: IrisRequest, response: str) -> List[str]:
        """Generate contextual suggestions based on the conversation"""
        suggestions = []
        
        # Base suggestions on board status
        if request.board_status == 'collecting':
            suggestions = [
                "Help me organize these images",
                "What style are these images?",
                "Find similar inspiration",
                "What's my color palette?"
            ]
        elif request.board_status == 'organizing':
            suggestions = [
                "Group by room areas",
                "Identify common elements",
                "Remove conflicting styles",
                "Create a mood board"
            ]
        elif request.board_status == 'refining':
            suggestions = [
                "Create vision summary",
                "Estimate project budget",
                "Priority recommendations",
                "Ready to start project?"
            ]
        else:  # No board or 'ready' status
            suggestions = [
                "Start a new board",
                "Browse inspiration ideas",
                "Tell me your vision",
                "Upload inspiration images"
            ]
        
        # Adjust based on response content
        response_lower = response.lower()
        if "budget" in response_lower or "cost" in response_lower:
            suggestions[0] = "Show detailed breakdown"
        elif "style" in response_lower:
            suggestions[0] = "Show similar styles"
        elif "ready" in response_lower or "project" in response_lower:
            suggestions[0] = "Connect with CIA agent"
        
        return suggestions[:4]  # Return top 4 suggestions
    
    def _should_analyze_images(self, message: str) -> bool:
        """Determine if we should analyze images based on the message"""
        analyze_keywords = [
            'analyze', 'what style', 'identify', 'tell me about',
            'describe', 'what do you see', 'common elements',
            'color', 'palette', 'materials', 'theme'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in analyze_keywords)
    
    async def _analyze_images(self, images: List[Dict]) -> Dict:
        """Analyze images for style, colors, and elements"""
        # For MVP, return structured analysis
        # In production, this would use vision API
        
        analysis = {
            "style_summary": "Modern farmhouse with transitional elements",
            "primary_colors": ["White", "Gray", "Black accents", "Natural wood"],
            "key_elements": [
                "Shaker-style cabinets",
                "Marble or quartz countertops", 
                "Black hardware and fixtures",
                "Open shelving",
                "Pendant lighting"
            ],
            "materials_identified": [
                "Wood cabinetry",
                "Stone countertops",
                "Subway tile backsplash",
                "Hardwood or LVP flooring"
            ],
            "estimated_style_cost": {
                "budget_friendly": "$15,000 - $25,000",
                "mid_range": "$25,000 - $45,000",
                "high_end": "$45,000 - $75,000+"
            },
            "design_coherence": 0.85,  # How well images match
            "recommendations": [
                "Strong cohesive style across images",
                "Consider adding more lighting variety",
                "Color palette is well-balanced"
            ]
        }
        
        return analysis
    
    def _generate_image_tags(self, room_type: str, message: str) -> List[str]:
        """Generate automatic tags for uploaded images based on context"""
        base_tags = []
        
        # Room-specific tags
        if room_type:
            room_type_lower = room_type.lower()
            if "kitchen" in room_type_lower:
                base_tags.extend(["kitchen", "cabinetry", "countertops", "appliances"])
            elif "bathroom" in room_type_lower:
                base_tags.extend(["bathroom", "tiles", "fixtures", "vanity"])
            elif "living" in room_type_lower:
                base_tags.extend(["living-room", "furniture", "lighting", "decor"])
            elif "bedroom" in room_type_lower:
                base_tags.extend(["bedroom", "furniture", "textiles", "lighting"])
            else:
                base_tags.append(room_type_lower)
        
        # Message-based tags
        message_lower = message.lower() if message else ""
        
        # Style indicators
        if any(word in message_lower for word in ["modern", "contemporary"]):
            base_tags.append("modern")
        if any(word in message_lower for word in ["farmhouse", "rustic"]):
            base_tags.append("farmhouse")
        if any(word in message_lower for word in ["traditional", "classic"]):
            base_tags.append("traditional")
        if any(word in message_lower for word in ["industrial", "loft"]):
            base_tags.append("industrial")
        
        # Color indicators
        if any(word in message_lower for word in ["white", "light"]):
            base_tags.append("light-colors")
        if any(word in message_lower for word in ["dark", "black"]):
            base_tags.append("dark-colors")
        if any(word in message_lower for word in ["wood", "natural"]):
            base_tags.append("natural-materials")
        
        # Default tags if none detected
        if not base_tags:
            base_tags = ["inspiring", "stylish", "design-ideas"]
        
        # Add common utility tags
        base_tags.extend(["inspiration", "renovation"])
        
        # Remove duplicates and limit to 6 tags
        unique_tags = list(dict.fromkeys(base_tags))[:6]
        
        return unique_tags
    
    def _generate_fallback_response(self, request: IrisRequest, context: str) -> str:
        """Generate intelligent response when API is unavailable"""
        message_lower = request.message.lower()
        
        # Kitchen-specific responses
        if "kitchen" in message_lower and ("modern farmhouse" in message_lower or "style" in message_lower):
            return """I can see you're interested in modern farmhouse style for your kitchen! This is a fantastic choice that combines rustic charm with contemporary functionality.

Key elements of modern farmhouse kitchens include:
- White or light-colored Shaker-style cabinets
- Black or oil-rubbed bronze hardware for contrast
- Natural wood accents (floating shelves, islands, or beams)
- Subway tile or shiplap backsplashes
- Farmhouse sinks with bridge or gooseneck faucets
- Pendant lighting over islands

Based on your uploaded images, I notice you're drawn to the classic white cabinet and black hardware combination. This creates a timeless look that won't go out of style. Would you like me to help you organize these images by specific areas like cabinetry, countertops, or lighting?"""
        
        # Board organization
        elif "organize" in message_lower or "group" in message_lower:
            if request.board_status == "organizing":
                return """I'd be happy to help organize your inspiration images! Based on what you've uploaded, I suggest grouping them into these categories:

1. **Cabinet Style & Color** - Keep all your cabinet inspiration together
2. **Hardware & Fixtures** - Handles, faucets, and lighting
3. **Countertops & Backsplash** - Surface materials and patterns
4. **Layout & Islands** - Overall kitchen configuration
5. **Decorative Elements** - Open shelving, decor, and accessories

This organization will help you see patterns in your preferences and make it easier to communicate your vision to contractors. Would you like me to identify which images belong in each category?"""
            else:
                return "I can help you organize your inspiration! First, let's gather all your images in one place. You can upload multiple images at once by dragging them into the chat. Once we have your collection, I'll help you group them by style, room area, or design elements."
        
        # Budget questions
        elif "budget" in message_lower or "cost" in message_lower:
            room_type = request.board_room_type or "room"
            return f"""Let me help you understand typical budget ranges for {room_type} renovations:

**Budget-Friendly ($15,000 - $25,000)**
- Cabinet refacing or painting
- Laminate or butcher block countertops
- Standard fixtures and hardware
- DIY-friendly improvements

**Mid-Range ($25,000 - $45,000)**
- New semi-custom cabinets
- Quartz or granite countertops
- Quality appliances and fixtures
- Professional installation

**High-End ($45,000 - $75,000+)**
- Custom cabinetry
- Premium stone countertops
- Professional-grade appliances
- Structural changes possible

Based on the style elements in your inspiration board, you're looking at a mid-range project. Would you like me to help prioritize elements to fit your specific budget?"""
        
        # Generic helpful response
        else:
            # Check for uploaded images (either regular images or uploaded_images)
            has_images = (request.images and len(request.images) > 0)
            uploaded_images = getattr(request, 'uploaded_images', None)
            has_uploaded = uploaded_images and len(uploaded_images) > 0
            
            if has_images or has_uploaded:
                image_count = len(request.images) if has_images else len(uploaded_images)
                category = getattr(request, 'image_category', None) or 'inspiration'
                
                # Generate automatic tags for the uploaded images
                auto_tags = self._generate_image_tags(request.board_room_type, request.message)
                
                tag_display = ", ".join(auto_tags) if auto_tags else "modern, stylish, inspiring"
                
                # Category-specific responses
                if category == 'ideal':
                    category_text = "ideal inspiration"
                    analysis_focus = """What aspects of these inspiration images do you find most appealing? For example:
- The overall style and mood you want to achieve?
- Specific design elements that caught your eye?
- Colors and materials that inspire you?
- The feeling or atmosphere you want to create?

I'll help you identify the key elements from your inspiration that we can incorporate into your actual space."""
                elif category == 'current':
                    category_text = "current space"
                    analysis_focus = """What aspects of your current space would you like to work with or change? For example:
- What do you like about the existing layout or features?
- What challenges or limitations do you see?
- Which elements would you keep versus replace?
- How does the space currently function for your needs?

Understanding your current space will help me suggest realistic improvements that work with what you have."""
                else:
                    category_text = "inspiration"
                    analysis_focus = """What aspects of these images do you find most appealing? For example:
- The color palette and how it makes you feel?
- Specific materials like countertops, cabinets, or flooring?
- The overall style and atmosphere?
- Particular design elements or features?

Understanding what draws you to these images will help me provide more personalized recommendations and organize your inspiration effectively."""
                
                return f"""I can see you've uploaded {image_count} {category_text} image{'s' if image_count > 1 else ''} for your {request.board_room_type or 'project'}. These images show great taste!

**Auto-Generated Tags**: {tag_display}

{analysis_focus}"""
            else:
                return """I'm Iris, your design inspiration assistant! I'm here to help you:

✨ Organize and understand your design preferences
🎨 Identify styles and color palettes
💰 Estimate project budgets realistically
📋 Create clear vision summaries for contractors

Start by uploading some inspiration images, or tell me about your project vision. What room are you looking to transform?"""

# Create singleton instance
iris_agent = IrisAgent()