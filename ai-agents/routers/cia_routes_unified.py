"""
CIA Routes - Universal Streaming Endpoint with ALL Features
Owner: Agent 1 (Frontend Flow)
Version: GPT-5 Vision Enabled
"""

import logging
import os
import json
import asyncio
from datetime import datetime
from typing import Any, Optional, List, Dict
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import re
from dotenv import load_dotenv

# Load environment variables from root .env
root_env = Path(__file__).parent.parent.parent / '.env'
if root_env.exists():
    load_dotenv(root_env, override=True)

# Import CIA agent and related models
from agents.cia.agent import CustomerInterfaceAgent
from agents.cia.prompts import OPENING_MESSAGE
from database_simple import db
from services.llm_cost_tracker import LLMCostTracker
from config.service_urls import get_backend_url

logger = logging.getLogger(__name__)

def extract_exact_dates(text: str) -> dict:
    """Extract exact dates from user text for bid deadlines and project completion"""
    import datetime as dt
    from dateutil import parser
    
    text_lower = text.lower()
    dates = {}
    
    # Pattern: "bids by [date]" or "all bids by [date]"  
    bid_deadline_patterns = [
        r"(?:all )?bids? (?:in )?by (.*?)(?:[,.]|$)",
        r"need (?:all )?bids? by (.*?)(?:[,.]|$)",
        r"(?:want|need) (?:to get|to have) (?:all )?bids? by (.*?)(?:[,.]|$)",
        r"bids? (?:must be )?in by (.*?)(?:[,.]|$)"
    ]
    
    # Pattern: "done by [date]" or "finished by [date]" or "completed by [date]"
    project_deadline_patterns = [
        r"(?:done|finished|completed) by (.*?)(?:[,.]|$)",
        r"(?:must be|needs to be|has to be) (?:done|finished|completed) by (.*?)(?:[,.]|$)",
        r"(?:project|work) (?:done|finished|completed) by (.*?)(?:[,.]|$)",
        r"before (.*?)(?:[,.]|$)",
        r"by (.*?)(?:[,.]|$)" # Generic "by" pattern - less specific
    ]
    
    # Event-driven deadlines
    event_patterns = [
        r"before (?:my|our|the) (wedding|party|event|holiday|vacation|move|moving) (?:on )?(.*?)(?:[,.]|$)",
        r"for (?:my|our|the) (wedding|party|event|holiday) (?:on )?(.*?)(?:[,.]|$)"
    ]
    
    def parse_date_text(date_text: str) -> tuple[dt.date, bool, str]:
        """Parse date text and return (date, is_hard_deadline, context)"""
        date_text = date_text.strip()
        if not date_text:
            return None, False, ""
        
        # Hard deadline indicators
        hard_indicators = ["must", "has to", "needs to", "required", "deadline", "storm", "emergency"]
        is_hard = any(indicator in text_lower for indicator in hard_indicators)
        
        try:
            # Handle relative dates like "Friday", "next week", "Christmas"
            if "friday" in date_text.lower():
                # Find next Friday
                today = dt.date.today()
                days_ahead = (4 - today.weekday()) % 7  # Friday is 4
                if days_ahead == 0:  # Today is Friday
                    days_ahead = 7  # Next Friday
                return today + dt.timedelta(days=days_ahead), is_hard, date_text
            
            elif "christmas" in date_text.lower():
                current_year = dt.date.today().year
                christmas = dt.date(current_year, 12, 25)
                if christmas < dt.date.today():
                    christmas = dt.date(current_year + 1, 12, 25)
                return christmas, is_hard, "Christmas"
            
            elif "wedding" in date_text.lower():
                # Extract wedding date if mentioned
                wedding_match = re.search(r"(?:on )?([\w\s,]+?)(?:\s|$)", date_text)
                if wedding_match:
                    wedding_text = wedding_match.group(1)
                    try:
                        wedding_date = parser.parse(wedding_text).date()
                        return wedding_date, True, f"wedding on {wedding_text}"
                    except:
                        pass
                
            else:
                # Try to parse as standard date
                parsed_date = parser.parse(date_text).date()
                return parsed_date, is_hard, date_text
                
        except Exception as e:
            logger.debug(f"Could not parse date: '{date_text}' - {e}")
            
        return None, is_hard, date_text
    
    # Extract bid collection deadlines
    for pattern in bid_deadline_patterns:
        match = re.search(pattern, text_lower)
        if match:
            date_text = match.group(1)
            parsed_date, is_hard, context = parse_date_text(date_text)
            if parsed_date:
                dates["bid_collection_deadline"] = parsed_date.isoformat()
                dates["deadline_hard"] = is_hard
                dates["deadline_context"] = f"bids needed by {context}"
                break
    
    # Extract project completion deadlines  
    for pattern in project_deadline_patterns:
        match = re.search(pattern, text_lower)
        if match:
            date_text = match.group(1)
            parsed_date, is_hard, context = parse_date_text(date_text)
            if parsed_date:
                dates["project_completion_deadline"] = parsed_date.isoformat()
                if "deadline_hard" not in dates:  # Don't override bid deadline hardness
                    dates["deadline_hard"] = is_hard
                if "deadline_context" not in dates:
                    dates["deadline_context"] = f"completion by {context}"
                break
    
    # Extract event-driven deadlines
    for pattern in event_patterns:
        match = re.search(pattern, text_lower)
        if match:
            event_type = match.group(1)
            date_text = match.group(2) if len(match.groups()) > 1 else ""
            parsed_date, is_hard, context = parse_date_text(date_text)
            if parsed_date:
                dates["project_completion_deadline"] = parsed_date.isoformat()
                dates["deadline_hard"] = True  # Events are usually hard deadlines
                dates["deadline_context"] = f"before {event_type} on {context}"
                break
    
    return dates

# Create router
router = APIRouter()

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    images: Optional[list[str]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    rfi_context: Optional[dict] = None  # For RFI-triggered conversations

class ChatResponse(BaseModel):
    response: str
    session_id: str
    current_phase: str
    ready_for_jaa: bool
    missing_fields: list[str]
    collected_info: Optional[dict[str, Any]] = None
    messages: Optional[list[dict[str, Any]]] = None

class SSEChatRequest(BaseModel):
    messages: list
    conversation_id: str
    user_id: str
    max_tokens: Optional[int] = 500
    model_preference: Optional[str] = "gpt-5"
    project_id: Optional[str] = None  # Support project context
    rfi_context: Optional[dict] = None  # Support RFI context
    images: Optional[list[str]] = None  # Support image uploads
    session_id: Optional[str] = None  # Support session tracking

class IrisProjectProposal(BaseModel):
    user_id: str
    iris_session_id: str
    source_context: str  # "inspiration", "house_analysis", or "combined"
    
    project_proposal: dict  # Contains all IRIS analysis
    design_preferences: Optional[dict] = None
    current_state_analysis: Optional[dict] = None
    inspiration_summary: Optional[dict] = None
    
    next_steps: list[str]
    confidence_score: float
    
    # Context preservation
    iris_conversation_id: Optional[str] = None
    unified_memory_refs: Optional[list[str]] = None

# Global CIA agent instance (initialized in main.py)
cia_agent: Optional[CustomerInterfaceAgent] = None

# Cost tracking instance
cost_tracker = LLMCostTracker()

def set_cia_agent(agent: CustomerInterfaceAgent):
    """Set the CIA agent instance"""
    global cia_agent
    cia_agent = agent

@router.get("/opening-message")
async def get_opening_message():
    """Get the pre-loaded opening message for the chat UI"""
    return {
        "success": True,
        "message": OPENING_MESSAGE,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/conversation/{session_id}")
async def get_cia_conversation_history(session_id: str):
    """Get conversation history for a session"""
    try:
        # Load conversation state from database
        conversation_state = await db.load_conversation_state(session_id)

        if not conversation_state:
            return {
                "success": True,
                "messages": [],
                "session_id": session_id,
                "total_messages": 0
            }

        # Extract messages from conversation state
        state = conversation_state.get("state", {})

        # Handle case where state might be a JSON string
        if isinstance(state, str):
            try:
                state = json.loads(state)
            except:
                state = {}

        messages = state.get("messages", []) if isinstance(state, dict) else []

        # Convert to frontend-compatible format
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": str(len(formatted_messages) + 1),
                "role": msg.get("role", "assistant"),
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", conversation_state.get("created_at", "")),
                "images": msg.get("images", [])
            })

        return {
            "success": True,
            "messages": formatted_messages,
            "session_id": session_id,
            "total_messages": len(formatted_messages),
            "last_updated": conversation_state.get("updated_at"),
            "project_id": state.get("collected_info", {}).get("project_id")
        }

    except Exception as e:
        print(f"Error loading conversation history: {e}")
        return {
            "success": False,
            "error": str(e),
            "messages": [],
            "session_id": session_id,
            "total_messages": 0
        }

@router.post("/stream")
async def cia_universal_stream(request: SSEChatRequest):
    """
    Universal CIA Streaming Chat Endpoint
    Features:
    - GPT-5 with vision support
    - Full project context loading
    - RFI context handling
    - Image analysis and processing  
    - Real-time SSE streaming
    - Complete CIA agent integration
    - Supabase state persistence
    """
    logger.info(f"CIA universal stream called with message: {request.messages[-1] if request.messages else 'no message'}")
    
    if not cia_agent:
        logger.error("CIA agent not initialized")
        raise HTTPException(
            status_code=503, 
            detail="CIA agent not initialized. Check OpenAI API key configuration."
        )
    
    async def generate_universal_sse_stream():
        try:
            logger.info("Starting universal SSE stream generation")
            
            # Extract user info with enhanced session handling
            if not request.user_id or request.user_id == "00000000-0000-0000-0000-000000000000":
                user_id = "00000000-0000-0000-0000-000000000000" 
                session_id = request.conversation_id or f"anon_{datetime.now().timestamp()}"
            else:
                user_id = request.user_id
                session_id = request.conversation_id or f"auth_{user_id}_{datetime.now().timestamp()}"
            
            # Extract latest message and images
            latest_message = ""
            images = []
            if request.messages:
                last_msg = request.messages[-1]
                latest_message = last_msg.get("content", "")
                # First check for images in the message
                images = last_msg.get("images", [])
            
            # If no images in message, check request level (where they're actually sent)
            if not images and request.images:
                images = request.images
                logger.info(f"Found {len(images)} images at request level")
            
            logger.info(f"Processing message: {latest_message[:100]} with {len(images)} images")
            
            # === PROJECT CONTEXT LOADING ===
            project_id = request.project_id
            bid_card_context = None
            if project_id:
                try:
                    logger.info(f"Loading project context for: {project_id}")
                    # Use async to avoid blocking
                    bid_card_result = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: db.client.table("bid_cards").select("*").eq("id", project_id).execute()
                    )
                    if bid_card_result.data:
                        bid_card_context = bid_card_result.data[0]
                        logger.info(f"Loaded bid card: {bid_card_context.get('bid_card_number')}")
                        
                        # Verify user access if authenticated
                        if user_id != "00000000-0000-0000-0000-000000000000":
                            # Use async to avoid blocking
                            homeowner_result = await asyncio.get_event_loop().run_in_executor(
                                None,
                                lambda: db.client.table("homeowners").select("id").eq("user_id", user_id).execute()
                            )
                            if homeowner_result.data:
                                user_id = homeowner_result.data[0]["id"]
                                if bid_card_context.get("user_id") != user_id:
                                    yield f"data: {json.dumps({'error': 'Bid card access denied'})}\n\n"
                                    return
                                logger.info(f"Verified bid card access for homeowner {user_id}")
                except Exception as e:
                    logger.warning(f"Project context loading error: {e}")
            
            # === RFI CONTEXT HANDLING ===
            if request.rfi_context:
                logger.info(f"RFI context detected: {request.rfi_context}")
                rfi_msg = format_rfi_context_message(request.rfi_context)
                latest_message = f"{rfi_msg}\n\n{latest_message}"
                
                # Handle RFI photo uploads
                if images and request.rfi_context.get("bid_card_id"):
                    await handle_rfi_photo_upload(
                        bid_card_id=request.rfi_context["bid_card_id"],
                        rfi_id=request.rfi_context.get("rfi_id"),
                        photos=images,
                        user_id=user_id
                    )
            
            # === IMAGE ANALYSIS INTEGRATION ===
            image_context = ""
            if images and not request.rfi_context:  # Only analyze non-RFI images
                try:
                    from agents.cia.image_integration import cia_image_integration
                    
                    # Analyze images for bid card context
                    project_context = {
                        "property_area": bid_card_context.get("project_type", "Unknown") if bid_card_context else "Unknown",
                        "user_notes": latest_message
                    }
                    
                    analysis_results = await cia_image_integration.analyze_images_with_context(
                        images, project_context
                    )
                    
                    # Format analysis for conversation context
                    image_context = cia_image_integration.format_image_context_for_conversation(analysis_results)
                    logger.info(f"Image analysis completed: {image_context}")
                    
                    # If we have a potential bid card ID, update it with image data
                    if hasattr(request, 'potential_bid_card_id') and request.potential_bid_card_id:
                        # Get the image URLs from the upload system
                        # (assuming images are already uploaded to Supabase Storage)
                        image_urls = images  # These should be URLs after upload
                        await cia_image_integration.update_potential_bid_card_with_images(
                            request.potential_bid_card_id,
                            image_urls,
                            analysis_results
                        )
                    
                except Exception as e:
                    logger.error(f"Image analysis failed: {e}")
                    image_context = f"Images uploaded ({len(images)} files) - analysis pending"
            
            # === FULL CIA AGENT INTEGRATION ===
            # Load existing conversation state
            existing_conversation = await db.load_conversation_state(session_id)
            if existing_conversation:
                # Extract state - could be nested or at top level
                if "state" in existing_conversation:
                    existing_state = existing_conversation.get("state", {})
                else:
                    existing_state = existing_conversation
                    
                logger.info(f"Loaded existing state for session {session_id}")
                logger.info(f"State type: {type(existing_state)}")
                logger.info(f"State keys: {existing_state.keys() if isinstance(existing_state, dict) else 'Not a dict'}")
                
                # Check for messages in both locations
                messages_found = False
                if isinstance(existing_state, dict) and "messages" in existing_state:
                    logger.info(f"Found {len(existing_state['messages'])} messages in state")
                    messages_found = True
                elif isinstance(existing_conversation, dict) and "messages" in existing_conversation:
                    logger.info(f"Found {len(existing_conversation['messages'])} messages at top level")
                    # Move messages to state for consistency
                    if isinstance(existing_state, dict):
                        existing_state["messages"] = existing_conversation["messages"]
                        messages_found = True
                
                if not messages_found:
                    logger.info("No messages found in loaded conversation")
            else:
                existing_state = None
                logger.info(f"Starting new conversation for session {session_id}")
            
            # Enhance state with context
            if existing_state and bid_card_context:
                existing_state["bid_card_context"] = bid_card_context
                existing_state["project_id"] = project_id
            elif bid_card_context:
                existing_state = {
                    "bid_card_context": bid_card_context,
                    "project_id": project_id
                }
            
            # === SIMPLIFIED GPT-4O STREAMING ===
            from openai import AsyncOpenAI
            skip_state_management = False  # Initialize flag
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("No OpenAI API key found")
                yield f"data: {json.dumps({'error': 'No OpenAI API key configured'})}\n\n"
                return
            
            logger.info(f"Creating OpenAI client for GPT-4o streaming")
            openai_client = AsyncOpenAI(api_key=api_key)
            
            # Prepare content for OpenAI chat completions
            input_content = []
            
            # Add text content
            input_content.append({
                "type": "text", 
                "text": latest_message
            })
            
            # Add image content if provided (OpenAI format)
            if images:
                for image_url in images:
                    # Ensure proper data URI format for OpenAI
                    if not image_url.startswith("data:"):
                        image_url = f"data:image/jpeg;base64,{image_url}"
                    input_content.append({
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    })
                logger.info(f"Added {len(images)} images to OpenAI input")
            
            # Get the proper CIA system prompt
            from agents.cia.prompts import SYSTEM_PROMPT
            
            # Use regular conversational prompt for GPT-4o (no JSON requirement)
            system_prompt = SYSTEM_PROMPT
            
            # Add context but NOT conversation history (since we'll add it as messages)
            enhanced_prompt = system_prompt
            
            if bid_card_context:
                enhanced_prompt += f"\n\nProject Context: Working on {bid_card_context.get('project_type', 'project')} for bid card {bid_card_context.get('bid_card_number', 'N/A')}"
            
            if image_context:
                enhanced_prompt += f"\n\nImage Analysis: {image_context}"
            
            # Stream response using GPT-4o (simplified for reliability)
            accumulated_response = ""
            model_used = "gpt-4o"
            
            logger.info("Starting GPT-4o streaming...")
            
            # Build messages array with conversation history
            messages = []
            
            # Add system message
            messages.append({
                "role": "system",
                "content": enhanced_prompt
            })
            
            # Add conversation history if available
            if existing_state and "messages" in existing_state:
                logger.info(f"Loading {len(existing_state['messages'])} messages from conversation history")
                # Log each message for debugging
                for i, msg in enumerate(existing_state["messages"], 1):
                    logger.info(f"History message {i}: role={msg.get('role')}, content_preview={msg.get('content', '')[:100]}...")
                    if msg.get("role") in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg.get("content", "")
                        })
                logger.info(f"Total messages in array after loading history: {len(messages)}")
            else:
                logger.info("No conversation history found in state")
            
            # Add current user message
            # If we have images, use the structured content, otherwise just the text
            if images:
                messages.append({
                    "role": "user",
                    "content": input_content
                })
            else:
                messages.append({
                    "role": "user",
                    "content": latest_message
                })
            
            # Log the messages being sent to GPT-4o for debugging
            logger.info(f"Sending {len(messages)} messages to GPT-4o")
            logger.info(f"System message length: {len(messages[0]['content']) if messages else 0} chars")
            if len(messages) > 1:
                logger.info(f"Conversation has {len(messages) - 1} additional messages")
                # Log first few messages for debugging (not full content to avoid spam)
                for i, msg in enumerate(messages[1:4], 1):  # Show first 3 non-system messages
                    logger.info(f"Message {i}: {msg['role']} - {msg['content'][:50] if msg.get('content') else 'No content'}...")
            
            # Use GPT-4o with Chat Completions API (reliable streaming)
            response_stream = await openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_completion_tokens=500,
                    temperature=0.7,
                    stream=True
                )
            
            logger.info("GPT-4o stream created successfully")
            
            # REAL STREAMING - Forward chunks immediately
            async for chunk in response_stream:
                # Forward OpenAI streaming chunks immediately - NO DELAYS
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        # Forward chunk immediately to client
                        chunk_data = {
                            "choices": [{
                                "delta": {"content": delta.content},
                                "index": 0
                            }],
                            "model": model_used
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                        
                        # Accumulate for logging
                        accumulated_response += delta.content
            
            logger.info(f"GPT-4o streaming completed successfully ({len(accumulated_response)} chars)")
            
            # Track costs for GPT-4o usage (estimate tokens since streaming doesn't provide usage)
            logger.info("COST_TRACKING_DEBUG: About to track GPT-4o costs")
            try:
                # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
                input_text = " ".join([msg.get("content", "") for msg in messages if isinstance(msg.get("content"), str)])
                estimated_input_tokens = len(input_text) // 4
                estimated_output_tokens = len(accumulated_response) // 4
                
                # Track the cost (import cost_tracker)
                from services.llm_cost_tracker import cost_tracker
                cost_tracker.track_llm_call_sync(
                    agent_name="CIA",
                    provider="openai", 
                    model="gpt-4o",
                    input_tokens=estimated_input_tokens,
                    output_tokens=estimated_output_tokens,
                    duration_ms=0,  # Duration not available for streaming
                    context={
                        "user_id": user_id,
                        "conversation_id": session_id,
                        "streaming": True,
                        "estimated": True
                    }
                )
                logger.info(f"Cost tracking logged for GPT-4o: ~{estimated_input_tokens}+{estimated_output_tokens} tokens")
            except Exception as track_error:
                logger.warning(f"Cost tracking failed: {track_error}")
                    
            except Exception as stream_error:
                logger.error(f"Streaming error: {stream_error}")
                yield f"data: {json.dumps({'error': f'Streaming failed: {str(stream_error)}'})}\n\n"
                return
                        
            # === SAVE TO UNIFIED SYSTEM (AFTER STREAMING COMPLETES) ===
            # Save to unified conversation system directly using database
            def save_to_unified_direct():
                    try:
                        import uuid
                        from datetime import datetime
                        from database import db
                        
                        # Ensure UUIDs are valid format
                        def ensure_uuid(value):
                            if not value:
                                return str(uuid.uuid4())
                            try:
                                # Try to parse as UUID to validate format
                                uuid.UUID(str(value))
                                return str(value)
                            except:
                                # If not valid UUID, create deterministic one from string
                                return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(value)))
                        
                        conv_uuid = ensure_uuid(session_id)
                        user_uuid = ensure_uuid(user_id)
                        
                        # Check if conversation exists
                        conv_result = db.client.table("unified_conversations").select("*").eq("id", conv_uuid).execute()
                        
                        if not conv_result.data:
                            # Create conversation
                            conv_data = {
                                "id": conv_uuid,
                                "tenant_id": "00000000-0000-0000-0000-000000000000",
                                "created_by": user_uuid,
                                "conversation_type": "project_setup",
                                "entity_id": user_uuid,
                                "entity_type": "homeowner", 
                                "title": f"CIA Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                                "status": "active",
                                "metadata": {"session_id": session_id, "project_id": project_id},
                                "created_at": datetime.utcnow().isoformat(),
                                "updated_at": datetime.utcnow().isoformat()
                            }
                            db.client.table("unified_conversations").insert(conv_data).execute()
                            logger.info(f"Created unified conversation: {conv_uuid}")
                        
                        # Save user message
                        user_msg_data = {
                            "id": str(uuid.uuid4()),
                            "conversation_id": conv_uuid,
                            "sender_type": "user",
                            "sender_id": user_uuid,
                            "content": latest_message,
                            "content_type": "text",
                            "metadata": {
                                "has_images": len(images) > 0 if images else False,
                                "project_id": project_id,
                                "rfi_context": bool(request.rfi_context)
                            },
                            "created_at": datetime.utcnow().isoformat()
                        }
                        
                        db.client.table("unified_messages").insert(user_msg_data).execute()
                        logger.info("User message saved to unified_messages")
                        
                        # Save assistant response
                        assistant_msg_data = {
                            "id": str(uuid.uuid4()),
                            "conversation_id": conv_uuid,
                            "sender_type": "agent",
                            "sender_id": None,
                            "agent_type": "CIA",
                            "content": accumulated_response,
                            "content_type": "text",
                            "metadata": {
                                "model_used": "gpt-4o",
                                "streaming": True,
                                "vision_used": len(images) > 0 if images else False
                            },
                            "created_at": datetime.utcnow().isoformat()
                        }
                        
                        db.client.table("unified_messages").insert(assistant_msg_data).execute()
                        logger.info(f"Assistant response saved to unified_messages ({len(accumulated_response)} chars)")
                        
                    except Exception as e:
                        logger.error(f"Failed to save to unified system: {e}")
                    
                    # Save images to potential bid card if present
                    if images and session_id:
                        try:
                            from .cia_photo_handler import save_images_to_potential_bid_card
                            photo_save_task = asyncio.create_task(
                                save_images_to_potential_bid_card(session_id, user_id, images)
                            )
                            logger.info(f"Started photo save task for {len(images)} images")
                        except Exception as photo_error:
                            logger.error(f"Error saving photos: {photo_error}")
            
            # === POST-STREAMING PROCESSING ===
            # Execute after streaming completes successfully
            
            # === ENHANCED STATE PERSISTENCE ===
            # Call CIA agent for state management (with timeout to prevent hanging)
            logger.info("Starting CIA agent state management...")
            if cia_agent and not skip_state_management:
                try:
                    # Add timeout to prevent hanging
                    result = await asyncio.wait_for(
                        cia_agent.handle_conversation(
                            user_id=user_id,
                            message=latest_message,
                            images=images,
                            session_id=session_id,
                            existing_state=existing_state,
                            project_id=project_id
                        ),
                        timeout=120.0  # Increased timeout for GPT-5 extraction
                    )
                    logger.info("CIA agent state management completed successfully")
                except asyncio.TimeoutError:
                    logger.warning("CIA agent state management timed out after 120s")
                except Exception as state_error:
                    logger.error(f"CIA agent state management error: {state_error}")
            
            # Save to unified system synchronously
            if not skip_state_management:
                try:
                    # Call the synchronous save function directly
                    save_to_unified_direct()
                    logger.info("Unified system save completed")
                except Exception as save_error:
                    logger.error(f"Failed to save to unified system: {save_error}")
            else:
                logger.info("Skipping unified system save to prevent hanging")
            
            # === BID CARD CREATION ===
            # Create/update potential bid card after conversation
            try:
                logger.info(f"Creating/updating bid card for session {session_id}")
                
                # Call the working bid card update function
                await update_potential_bid_card_from_conversation(
                    session_id=session_id,
                    user_id=user_id,
                    latest_message=latest_message,
                    conversation_state=None,
                    llm_response=response_text
                )
                
                logger.info("Bid card creation/update completed")
            except Exception as bid_error:
                logger.error(f"Bid card creation error: {bid_error}")
                # Don't fail the whole stream for bid card issues
            
            # Success path - DONE marker will be sent in finally block
            logger.info("Streaming completed successfully - DONE marker will be sent in finally block")
                
        except Exception as stream_error:
            logger.error(f"GPT-4o streaming error: {stream_error}")
            yield f"data: {json.dumps({'error': f'GPT-4o error: {str(stream_error)}'})}\n\n"
            
        except Exception as e:
            error_msg = f"Universal CIA streaming error: {str(e)}"
            logger.error(error_msg)
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
        
        finally:
            # CRITICAL: Always send [DONE] marker to complete the stream
            logger.info("Sending [DONE] marker in finally block to ensure stream completion")
            yield "data: [DONE]\n\n"
            logger.info("Stream definitively completed with [DONE] marker")
    
    return StreamingResponse(
        generate_universal_sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    )

@router.post("/chat/rfi/{rfi_id}")
async def cia_chat_with_rfi_context(rfi_id: str, chat_data: ChatMessage):
    """Start a CIA chat with RFI context pre-loaded - redirects to universal stream"""
    try:
        # Get RFI context from the RFI API
        rfi_response = requests.get(f"{get_backend_url()}/api/rfi/{rfi_id}/context")
        
        if rfi_response.status_code != 200:
            raise HTTPException(status_code=404, detail="RFI not found")
        
        rfi_data = rfi_response.json()
        
        if not rfi_data.get("success"):
            raise HTTPException(status_code=500, detail="Failed to get RFI context")
        
        # Convert to SSE request format with RFI context
        sse_request = SSEChatRequest(
            messages=[{"content": chat_data.message, "images": chat_data.images or []}],
            conversation_id=chat_data.session_id or f"rfi_{rfi_id}_{datetime.now().timestamp()}",
            user_id=chat_data.user_id or "00000000-0000-0000-0000-000000000000",
            project_id=chat_data.project_id,
            rfi_context=rfi_data["context"]
        )
        
        # Use the universal streaming endpoint
        return await cia_universal_stream(sse_request)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting RFI chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/receive-iris-proposal")
async def receive_iris_project_proposal(proposal: IrisProjectProposal):
    """
    Receive project proposal from IRIS agent and start CIA implementation planning
    
    This endpoint enables seamless transition from IRIS inspiration/house analysis
    to CIA project implementation planning with full context preservation.
    """
    logger.info(f"Receiving IRIS project proposal for homeowner: {proposal.user_id}")
    logger.info(f"Source context: {proposal.source_context}")
    logger.info(f"Confidence score: {proposal.confidence_score}")
    
    try:
        # Generate unique session ID for this IRIS → CIA transition
        session_id = f"iris_cia_{proposal.iris_session_id}_{datetime.now().timestamp()}"
        
        # Create project ID for tracking this transition
        import uuid
        project_id = str(uuid.uuid4())
        
        # Format IRIS context into CIA-friendly initial message
        iris_context_message = format_iris_context_for_cia(proposal)
        
        # Create initial CIA request with IRIS context pre-loaded
        cia_request = SSEChatRequest(
            messages=[{
                "content": iris_context_message,
                "role": "system",  # System message to provide context
                "metadata": {
                    "source": "iris_transition",
                    "iris_session_id": proposal.iris_session_id,
                    "confidence_score": proposal.confidence_score
                }
            }],
            conversation_id=session_id,
            user_id=proposal.user_id,
            project_id=project_id
        )
        
        # Start CIA conversation in "implementation planning" phase
        logger.info(f"Starting CIA implementation planning for project: {project_id}")
        
        # Save IRIS context to database for CIA agent access
        await save_iris_context_to_database(
            session_id=session_id,
            project_id=project_id,
            user_id=proposal.user_id,
            iris_data=proposal
        )
        
        # Save IRIS data for CIA conversation - NO auto bid card creation
        # The CIA agent will create the bid card through natural conversation
        
        # **CRITICAL**: Start actual CIA conversation with IRIS context
        # This ensures the homeowner sees the IRIS context when they arrive
        try:
            if cia_agent:
                # Create conversational welcome that acknowledges IRIS work
                welcome_message = f"""Hi! I can see you've been working with IRIS on your project inspiration and analysis. That's fantastic! 

Let me take a look at everything we've discovered together and help you turn this into a detailed project plan that contractors can bid on.

{iris_context_message}

This is a great foundation! Now let's work together to refine these details and create a comprehensive bid card. What aspects would you like to focus on or adjust first?"""
                
                # Start CIA conversation with IRIS context
                initial_result = await cia_agent.handle_conversation(
                    user_id=proposal.user_id,
                    message="[IRIS Transition] Ready to begin implementation planning",
                    session_id=session_id,
                    project_id=project_id,
                    existing_state=None  # Will load IRIS context from database
                )
                
                # Save the initial conversation with IRIS context
                await db.save_conversation_state(
                    user_id=proposal.user_id,
                    thread_id=session_id,
                    agent_type="CIA", 
                    state=initial_result.get("state", {})
                )
                
                logger.info(f"CIA conversation initialized with IRIS context for session {session_id}")
            else:
                logger.warning("CIA agent not available - conversation will start with saved context only")
                
        except Exception as conversation_error:
            logger.error(f"Error starting CIA conversation with IRIS context: {conversation_error}")
            # Don't fail the endpoint - homeowner can still start conversation manually
        
        return {
            "success": True,
            "homeowner_session_id": session_id,
            "project_id": project_id,
            "message": f"IRIS project context transferred to CIA. Conversational bid card creation ready.",
            "next_action": "continue_cia_conversation",
            "cia_endpoint": f"/api/cia/stream",
            "conversation_ready": True,
            "initial_context": {
                "phase": "implementation_planning",
                "source": proposal.source_context,
                "next_steps_count": len(proposal.next_steps),
                "iris_context_loaded": True,
                "conversation_started": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing IRIS project proposal: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process IRIS proposal: {str(e)}")

def format_rfi_context_message(rfi_context: dict) -> str:
    """Format RFI context into a message for the CIA agent"""
    contractor_name = rfi_context.get("contractor_name", "A contractor")
    request_type = rfi_context.get("request_type", "information")
    specific_items = rfi_context.get("specific_items", [])
    custom_message = rfi_context.get("custom_message", "")
    priority = rfi_context.get("priority", "medium")
    project_details = rfi_context.get("project_details", {})
    guidance = rfi_context.get("guidance", {})
    
    # Build the context message
    context_msg = f"""[RFI CONTEXT] {contractor_name} has requested {request_type} for your {project_details.get('type', 'project')}.

They need the following information:
"""
    
    # Add specific items
    for i, item in enumerate(specific_items, 1):
        context_msg += f"{i}. {item}\n"
    
    # Add custom message if provided
    if custom_message:
        context_msg += f"\nAdditional notes from contractor: {custom_message}\n"
    
    # Add priority indication
    if priority in ["high", "urgent"]:
        context_msg += f"\n[PRIORITY: {priority.upper()}] This information is needed urgently.\n"
    
    # Add guidance introduction
    if guidance.get("introduction"):
        context_msg += f"\n{guidance['introduction']}\n"
    
    return context_msg

async def handle_rfi_photo_upload(
    bid_card_id: str,
    rfi_id: Optional[str],
    photos: List[str],
    user_id: str
) -> None:
    """Handle RFI photo uploads - update bid card and trigger JAA"""
    try:
        logger.info(f"Handling RFI photo upload for bid card {bid_card_id}")
        
        # Get current bid card
        bid_card_result = db.client.table("bid_cards").select("*").eq("id", bid_card_id).single().execute()
        
        if not bid_card_result.data:
            logger.error(f"Bid card {bid_card_id} not found")
            return
        
        bid_card = bid_card_result.data
        bid_document = bid_card.get("bid_document", {})
        
        # Ensure all_extracted_data exists
        if "all_extracted_data" not in bid_document:
            bid_document["all_extracted_data"] = {}
        
        # Ensure images array exists
        if "images" not in bid_document["all_extracted_data"]:
            bid_document["all_extracted_data"]["images"] = []
        
        # Add RFI photos to bid card
        for photo_url in photos:
            photo_entry = {
                "url": photo_url,
                "source": "rfi_response",
                "rfi_id": rfi_id,
                "uploaded_at": datetime.utcnow().isoformat(),
                "uploaded_by": user_id
            }
            bid_document["all_extracted_data"]["images"].append(photo_entry)
        
        # Update bid card with new photos
        update_result = db.client.table("bid_cards").update({
            "bid_document": bid_document,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", bid_card_id).execute()
        
        if update_result.data:
            logger.info(f"Updated bid card {bid_card_id} with {len(photos)} RFI photos")
            
            # Call JAA service to notify contractors
            try:
                jaa_response = requests.put(
                    f"{get_backend_url()}/jaa/update/{bid_card_id}",
                    json={
                        "update_type": "rfi_photos_added",
                        "photos_count": len(photos),
                        "rfi_id": rfi_id,
                        "source": "CIA_RFI_response"
                    },
                    timeout=120
                )
                
                if jaa_response.status_code == 200:
                    logger.info(f"JAA notified about RFI photos for bid card {bid_card_id}")
                else:
                    logger.warning(f"JAA notification failed: {jaa_response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning("JAA notification timed out but photos were saved")
            except Exception as jaa_error:
                logger.error(f"JAA notification error: {jaa_error}")
        
        # Update RFI status if we have an RFI ID
        if rfi_id:
            try:
                db.client.table("rfi_requests").update({
                    "status": "homeowner_responded",
                    "responded_at": datetime.utcnow().isoformat(),
                    "metadata": {"photos_uploaded": len(photos)}
                }).eq("id", rfi_id).execute()
                logger.info(f"Updated RFI {rfi_id} status to homeowner_responded")
            except Exception as rfi_error:
                logger.error(f"Failed to update RFI status: {rfi_error}")
                
    except Exception as e:
        logger.error(f"Error handling RFI photo upload: {e}")

def format_iris_context_for_cia(proposal: IrisProjectProposal) -> str:
    """Format IRIS project proposal into CIA-friendly context message"""
    
    context_sections = [
        f"[IRIS PROJECT TRANSITION] Homeowner project analysis from {proposal.source_context} completed.",
        f"Confidence Score: {proposal.confidence_score:.1%}",
        ""
    ]
    
    # Add project proposal details
    if proposal.project_proposal:
        context_sections.append("🏗️ PROJECT PROPOSAL:")
        for key, value in proposal.project_proposal.items():
            if value:
                context_sections.append(f"• {key.replace('_', ' ').title()}: {value}")
        context_sections.append("")
    
    # Add design preferences if available
    if proposal.design_preferences:
        context_sections.append("🎨 DESIGN PREFERENCES:")
        for key, value in proposal.design_preferences.items():
            if value:
                context_sections.append(f"• {key.replace('_', ' ').title()}: {value}")
        context_sections.append("")
    
    # Add current state analysis
    if proposal.current_state_analysis:
        context_sections.append("📋 CURRENT STATE ANALYSIS:")
        for key, value in proposal.current_state_analysis.items():
            if value:
                context_sections.append(f"• {key.replace('_', ' ').title()}: {value}")
        context_sections.append("")
    
    # Add inspiration summary
    if proposal.inspiration_summary:
        context_sections.append("💡 INSPIRATION SUMMARY:")
        for key, value in proposal.inspiration_summary.items():
            if value:
                context_sections.append(f"• {key.replace('_', ' ').title()}: {value}")
        context_sections.append("")
    
    # Add next steps
    if proposal.next_steps:
        context_sections.append("🚀 RECOMMENDED NEXT STEPS:")
        for i, step in enumerate(proposal.next_steps, 1):
            context_sections.append(f"{i}. {step}")
        context_sections.append("")
    
    # Add transition note
    context_sections.extend([
        "🔄 TRANSITION NOTE:",
        "IRIS has completed the inspiration and analysis phase. The homeowner is now ready",
        "to begin detailed project planning and contractor matching. Please help them:",
        "• Refine project specifications",
        "• Set realistic timelines and budgets", 
        "• Prepare for contractor bidding process",
        "• Address any remaining questions or concerns",
        "",
        "How would you like to proceed with your project planning?"
    ])
    
    return "\n".join(context_sections)

async def save_iris_context_to_database(
    session_id: str,
    project_id: str, 
    user_id: str,
    iris_data: IrisProjectProposal
) -> None:
    """Save IRIS context to database for CIA agent access"""
    try:
        logger.info(f"Saving IRIS context for session {session_id}")
        
        # Save to CIA conversation state
        initial_state = {
            "phase": "implementation_planning",
            "source": "iris_transition",
            "iris_session_id": iris_data.iris_session_id,
            "confidence_score": iris_data.confidence_score,
            "project_id": project_id,
            "user_id": user_id,
            "iris_context": {
                "project_proposal": iris_data.project_proposal,
                "design_preferences": iris_data.design_preferences,
                "current_state_analysis": iris_data.current_state_analysis,
                "inspiration_summary": iris_data.inspiration_summary,
                "next_steps": iris_data.next_steps,
                "source_context": iris_data.source_context
            },
            "messages": [],
            "collected_info": {
                "project_id": project_id,
                "phase": "implementation_planning",
                "iris_transition": True
            }
        }
        
        # Save conversation state with proper conversation_type
        await db.save_conversation_state(
            user_id=user_id,
            thread_id=session_id, 
            agent_type="CIA",
            state=initial_state
        )
        
        # Also save to unified conversations system with required fields
        try:
            unified_conversation = {
                "conversation_type": "iris_cia_transition",
                "title": f"IRIS → CIA Project Planning",
                "status": "active",
                "metadata": {
                    "user_id": user_id,
                    "agent_type": "CIA",
                    "source": "iris_transition",
                    "project_id": project_id,
                    "iris_session_id": iris_data.iris_session_id
                }
            }
            
            # Save to unified_conversations
            db.client.table("unified_conversations").insert(unified_conversation).execute()
            logger.info(f"Saved unified conversation record for IRIS transition {session_id}")
        except Exception as unified_error:
            logger.warning(f"Could not save to unified_conversations: {unified_error}")
            # Don't fail the whole operation
        
        # Save IRIS transition record
        iris_transition_record = {
            "id": f"{session_id}_iris_transition",
            "cia_session_id": session_id,
            "iris_session_id": iris_data.iris_session_id,
            "project_id": project_id,
            "user_id": user_id,
            "source_context": iris_data.source_context,
            "confidence_score": iris_data.confidence_score,
            "transition_timestamp": datetime.utcnow().isoformat(),
            "iris_data": iris_data.dict(),
            "status": "active"
        }
        
        # Save to iris_cia_transitions table (create if doesn't exist)
        try:
            db.client.table("iris_cia_transitions").insert(iris_transition_record).execute()
            logger.info(f"Saved IRIS transition record for session {session_id}")
        except Exception as table_error:
            logger.warning(f"Could not save to iris_cia_transitions table: {table_error}")
            # Save to a generic transitions table as fallback
            try:
                transition_record = {
                    "id": f"{session_id}_transition",
                    "transition_type": "iris_to_cia",
                    "source_session": iris_data.iris_session_id,
                    "destination_session": session_id,
                    "user_id": user_id,
                    "project_id": project_id,
                    "data": iris_data.dict(),
                    "created_at": datetime.utcnow().isoformat()
                }
                db.client.table("agent_transitions").insert(transition_record).execute()
                logger.info(f"Saved transition to fallback table for session {session_id}")
            except Exception as fallback_error:
                logger.error(f"Failed to save transition record: {fallback_error}")
        
        logger.info(f"Successfully saved IRIS context for CIA session {session_id}")
        
    except Exception as e:
        logger.error(f"Error saving IRIS context to database: {e}")
        raise

async def update_potential_bid_card_from_conversation(
    session_id: str,
    user_id: str,
    latest_message: str,
    conversation_state: Optional[dict],
    llm_response: str
) -> None:
    """
    Update or create potential bid card with information extracted from conversation
    This provides real-time bid card building during CIA conversations
    """
    logger.info(f"=== POTENTIAL BID CARD UPDATE CALLED ===")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Latest message: {latest_message[:100] if latest_message else 'None'}...")
    
    try:
        import aiohttp
        
        # Check if potential bid card exists for this conversation
        existing_result = db.client.table("cia_conversation_tracking").select("potential_bid_card_id").eq("conversation_id", session_id).execute()
        
        bid_card_id = None
        if existing_result.data:
            bid_card_id = existing_result.data[0]["potential_bid_card_id"]
            logger.info(f"Found existing potential bid card {bid_card_id} for conversation {session_id}")
        else:
            # Create new potential bid card
            logger.info(f"Creating new potential bid card for conversation {session_id}")
            async with aiohttp.ClientSession() as http_session:
                create_payload = {
                    "conversation_id": session_id,
                    "session_id": session_id,
                    "user_id": user_id,
                    "title": "New Project"
                }
                
                async with http_session.post(
                    f"{get_backend_url()}/api/cia/potential-bid-cards",
                    json=create_payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        bid_card_id = result["id"]
                        logger.info(f"Created potential bid card {bid_card_id}")
                    else:
                        response_text = await resp.text()
                        logger.warning(f"Failed to create potential bid card: {resp.status} - {response_text}")
                        return
        
        if not bid_card_id:
            return
        
        # Extract information from conversation using simple patterns
        fields_to_update = extract_fields_from_conversation(latest_message, llm_response, conversation_state)
        
        # Update each field that was found
        async with aiohttp.ClientSession() as http_session:
            for field_name, field_value in fields_to_update.items():
                if field_value:  # Only update non-empty values
                    update_payload = {
                        "field_name": field_name,
                        "field_value": field_value,
                        "source": "conversation"
                    }
                    
                    async with http_session.put(
                        f"{get_backend_url()}/api/cia/potential-bid-cards/{bid_card_id}/field",
                        json=update_payload,
                        timeout=aiohttp.ClientTimeout(total=3)
                    ) as resp:
                        if resp.status == 200:
                            logger.info(f"Updated field {field_name} = {field_value}")
                        else:
                            logger.warning(f"Failed to update field {field_name}: {resp.status}")
        
        logger.info(f"Potential bid card {bid_card_id} updated with {len(fields_to_update)} fields")
        
    except Exception as e:
        logger.error(f"Error updating potential bid card: {e}")
        # Don't raise - this is a nice-to-have feature

def extract_fields_from_conversation(
    user_message: str,
    ai_response: str,
    conversation_state: Optional[Dict]
) -> Dict[str, Any]:
    """
    Extract structured fields from conversation using simple pattern matching
    This is a lightweight extraction - not meant to be perfect, just helpful
    """
    fields = {}
    
    # Combine user message and AI response for analysis
    full_text = f"{user_message} {ai_response}".lower()
    
    # Simple pattern matching for common fields
    import re
    
    # Project type detection
    project_types = {
        "kitchen": ["kitchen", "cabinet", "countertop", "appliance"],
        "bathroom": ["bathroom", "shower", "tub", "toilet", "vanity"],
        "roofing": ["roof", "shingle", "gutter", "leak"],
        "flooring": ["floor", "carpet", "hardwood", "tile", "laminate"],
        "landscaping": ["yard", "garden", "lawn", "landscaping", "backyard", "deck", "patio"],
        "painting": ["paint", "painting", "wall", "ceiling"],
        "plumbing": ["plumb", "pipe", "water", "drain", "faucet"],
        "electrical": ["electric", "wiring", "outlet", "light", "switch"]
    }
    
    for project_type, keywords in project_types.items():
        if any(keyword in full_text for keyword in keywords):
            fields["project_type"] = project_type
            break
    
    # Service type detection - CRITICAL for JAA workflow
    if any(word in full_text for word in ["install", "installing", "new", "add", "adding", "put in", "putting in"]):
        fields["service_type"] = "installation"
    elif any(word in full_text for word in ["repair", "repairing", "fix", "fixing", "broken", "not working", "damaged"]):
        fields["service_type"] = "repair"
    elif any(word in full_text for word in ["replace", "replacing", "upgrade", "upgrading", "renovate", "renovating", "remodel", "remodeling", "update", "updating"]):
        fields["service_type"] = "renovation"
    elif any(word in full_text for word in ["maintain", "maintenance", "service", "servicing", "tune up", "check up", "clean"]):
        fields["service_type"] = "maintenance"
    elif any(word in full_text for word in ["labor only", "materials provided", "supply materials", "have materials"]):
        fields["service_type"] = "labor_only"
    elif any(word in full_text for word in ["new construction", "building", "construct", "from scratch"]):
        fields["service_type"] = "new_construction"
    
    # Urgency detection - improved logic
    if any(word in full_text for word in ["emergency", "asap", "immediately", "today", "tomorrow"]):
        fields["urgency_level"] = "emergency"
    elif any(word in full_text for word in ["urgent", "this week", "few days"]):
        fields["urgency_level"] = "urgent"
    elif any(word in full_text for word in ["month", "weeks", "standard"]):
        fields["urgency_level"] = "standard"
    elif any(word in full_text for word in ["flexible", "no rush", "when convenient", "whenever"]):
        fields["urgency_level"] = "flexible"
    
    # EXACT DATE EXTRACTION - New functionality
    fields.update(extract_exact_dates(full_text))
    
    # ZIP code extraction
    zip_match = re.search(r'\b\d{5}(?:-\d{4})?\b', user_message)
    if zip_match:
        fields["zip_code"] = zip_match.group()
    
    # Email extraction
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_message)
    if email_match:
        fields["email_address"] = email_match.group()
    
    # Contractor size preference - fixed to match user preferences
    if any(word in full_text for word in ["handyman", "neighbor", "small", "tier 1", "tier_1"]):
        fields["contractor_size_preference"] = "tier_1_handyman"
    elif any(word in full_text for word in ["tier 2", "tier_2", "owner operator", "owner-operator"]):
        fields["contractor_size_preference"] = "tier_2_owner_operator"
    elif any(word in full_text for word in ["tier 3", "tier_3", "regional", "professional", "company", "team"]):
        fields["contractor_size_preference"] = "tier_3_regional"
    elif any(word in full_text for word in ["tier 4", "tier_4", "big", "large", "national"]):
        fields["contractor_size_preference"] = "tier_4_national"
    
    # Project description (use the user's most recent message if it's descriptive)
    if len(user_message) > 20:  # Substantial description
        fields["project_description"] = user_message
    
    # Project name generation - CRITICAL for JAA workflow
    project_type = fields.get("project_type", "")
    service_type = fields.get("service_type", "")
    
    if project_type and service_type:
        # Create intelligent project name
        if service_type == "installation":
            fields["project_name"] = f"{project_type.title()} Installation"
        elif service_type == "repair":
            fields["project_name"] = f"{project_type.title()} Repair"
        elif service_type == "renovation":
            fields["project_name"] = f"{project_type.title()} Renovation"
        elif service_type == "maintenance":
            fields["project_name"] = f"{project_type.title()} Maintenance"
        elif service_type == "labor_only":
            fields["project_name"] = f"{project_type.title()} Labor"
        elif service_type == "new_construction":
            fields["project_name"] = f"New {project_type.title()} Construction"
        else:
            fields["project_name"] = f"{project_type.title()} Project"
    elif project_type:
        fields["project_name"] = f"{project_type.title()} Project"
    else:
        fields["project_name"] = "Home Improvement Project"
    
    # Get additional info from conversation state if available
    if conversation_state:
        collected_info = conversation_state.get("collected_info", {})
        state_fields = conversation_state.get("state", {}) if isinstance(conversation_state.get("state"), dict) else {}
        
        # Map from CIA state to our field names
        if collected_info.get("budget_min"):
            fields["budget_context"] = f"Budget range: ${collected_info['budget_min']} - ${collected_info.get('budget_max', 'flexible')}"
        
        if collected_info.get("timeline_start"):
            fields["timeline"] = collected_info["timeline_start"]
    
    return fields

# Note: Automatic bid card creation removed - CIA creates bid cards through natural conversation