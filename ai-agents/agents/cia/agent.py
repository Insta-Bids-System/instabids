"""
Clean CIA Agent - Using OpenAI tool calling with real-time bid card updates
"""
import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv

# KEEP THE WORKING PARTS!
from services.universal_session_manager import universal_session_manager
from agents.cia.potential_bid_card_integration import PotentialBidCardManager
from agents.cia.schemas import BidCardUpdate
from agents.cia.store import CIAStore

load_dotenv()
logger = logging.getLogger(__name__)


class CustomerInterfaceAgent:
    """Clean CIA implementation with real-time bid card updates"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI and existing systems"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # KEEP THESE - They work!
        self.memory = universal_session_manager  
        self.bid_cards = PotentialBidCardManager()  # This updates the UI!
        self.store = CIAStore()
        
        # Define the extraction tool for OpenAI
        self.tools = [{
            "type": "function",
            "function": {
                "name": "update_bid_card",
                "description": "Update the potential bid card with extracted information. Call this whenever you learn new project details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_type": {
                            "type": "string",
                            "description": "Type of project: kitchen, bathroom, lawn, roofing, plumbing, etc."
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["emergency", "urgent", "week", "month", "flexible"],
                            "description": "How urgent is the project"
                        },
                        "scope_details": {
                            "type": "string",
                            "description": "Detailed description of the work needed"
                        },
                        "location": {
                            "type": "string",
                            "description": "Full address or location details"
                        },
                        "zip_code": {
                            "type": "string",
                            "description": "5-digit zip code"
                        },
                        "budget_min": {
                            "type": "number",
                            "description": "Minimum budget if mentioned"
                        },
                        "budget_max": {
                            "type": "number",
                            "description": "Maximum budget if mentioned"
                        },
                        "timeline": {
                            "type": "string",
                            "description": "When they want the project done"
                        },
                        "property_type": {
                            "type": "string",
                            "description": "Single family home, condo, commercial, etc."
                        },
                        "special_requirements": {
                            "type": "string",
                            "description": "Permits, HOA approval, special access, etc."
                        },
                        "materials": {
                            "type": "string",
                            "description": "Specific materials or brands requested"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address for bid delivery"
                        },
                        "contractor_preferences": {
                            "type": "string",
                            "description": "Preferences for contractor size, local, etc."
                        }
                    }
                }
            }
        }]
    
    async def handle_conversation(
        self,
        user_id: str,
        message: str,
        session_id: str,
        conversation_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main conversation handler with real-time bid card updates
        THIS IS WHAT CONNECTS TO YOUR UI!
        """
        try:
            # 1. Get or create session with memory
            session = await self.memory.get_or_create_session(user_id, session_id, agent_type="CIA")
            
            # 2. Get user context and other projects
            context = await self.store.get_user_context(user_id)
            other_projects = await self.store.get_other_projects(user_id)
            
            # 3. Ensure we have a conversation in the database
            if not conversation_id:
                conversation_id = await self.store.ensure_conversation_exists(user_id, session_id)
            
            # 4. Get or create potential bid card (THIS IS CRITICAL FOR UI!)
            bid_card_id = session.get("bid_card_id")
            if not bid_card_id:
                logger.info(f"Creating new potential bid card for session {session_id}")
                bid_card_id = await self.bid_cards.create_potential_bid_card(
                    conversation_id=conversation_id,
                    session_id=session_id,
                    user_id=user_id
                )
                if bid_card_id:
                    session["bid_card_id"] = bid_card_id
                    logger.info(f"Created potential bid card: {bid_card_id}")
                else:
                    logger.error("Failed to create potential bid card!")
            
            # 5. Build conversation history for OpenAI
            messages = self._build_messages(session, context, other_projects, message)
            
            # 6. Call OpenAI with tool for extraction
            logger.info("Calling OpenAI GPT-4o with extraction tool")
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",  # Let model decide when to extract
                temperature=0.3,
                max_tokens=500
            )
            
            # 7. Process tool calls - THIS UPDATES THE BID CARD IN REAL-TIME!
            extracted_data = {}
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    if tool_call.function.name == "update_bid_card":
                        extracted_data = json.loads(tool_call.function.arguments)
                        logger.info(f"Extracted data: {extracted_data}")
                        
                        # UPDATE EACH FIELD IN THE BID CARD (UI SEES THIS!)
                        if bid_card_id:
                            update = BidCardUpdate(**extracted_data)
                            bid_card_fields = update.to_bid_card_fields()
                            
                            for field_name, field_value in bid_card_fields.items():
                                if field_value is not None:
                                    success = await self.bid_cards.update_bid_card_field(
                                        bid_card_id=bid_card_id,
                                        field_name=field_name,
                                        field_value=field_value,
                                        confidence=0.9
                                    )
                                    if success:
                                        logger.info(f"Updated bid card field {field_name}: {field_value}")
                                    else:
                                        logger.error(f"Failed to update field {field_name}")
            
            # 8. Get the response text
            response_text = response.choices[0].message.content or "I'm processing that information."
            
            # 9. Get updated bid card status for UI
            bid_card_status = None
            completion_percentage = 0
            if bid_card_id:
                bid_card_status = await self.bid_cards.get_bid_card_status(bid_card_id)
                if bid_card_status:
                    # Calculate completion based on filled fields
                    completion_percentage = bid_card_status.get("completion_percentage", 0)
                    logger.info(f"Bid card completion: {completion_percentage}%")
            
            # 10. Save conversation to memory
            await self.memory.save_message(user_id, session_id, "CIA", message, response_text)
            
            # 11. Save to database
            await self.store.save_conversation_turn(
                conversation_id=conversation_id,
                user_message=message,
                agent_response=response_text,
                extracted_data=extracted_data,
                user_id=user_id,
                session_id=session_id
            )
            
            # 12. Return response with bid card info for UI
            return {
                "response": response_text,
                "success": True,
                "session_id": session_id,
                "conversation_id": conversation_id,
                "bid_card_id": bid_card_id,  # UI needs this!
                "extracted_data": extracted_data,  # What we just extracted
                "completion_percentage": completion_percentage,  # UI progress bar!
                "bid_card_status": bid_card_status,  # Full bid card state
                "fields_extracted": len([v for v in extracted_data.values() if v]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in CIA conversation: {str(e)}", exc_info=True)
            return {
                "response": "I'm having trouble processing that. Could you please try again?",
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    def _build_messages(
        self, 
        session: Dict,
        context: Dict,
        other_projects: List,
        current_message: str
    ) -> List[Dict]:
        """Build message history for OpenAI"""
        
        # System prompt
        system_prompt = self._get_system_prompt(context, other_projects)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history from session
        if "messages" in session:
            for msg in session["messages"][-10:]:  # Last 10 messages for context
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": current_message})
        
        return messages
    
    def _get_system_prompt(self, context: Dict, other_projects: List) -> str:
        """Generate system prompt with context"""
        
        # Check for other projects
        other_projects_text = ""
        if other_projects:
            projects = ", ".join([p.get("project_type", "project") for p in other_projects[:3]])
            other_projects_text = f"\n\nUser has other active projects: {projects}. If relevant, ask if this is related."
        
        # Check if returning user
        context_text = ""
        if not context.get("new_user"):
            context_text = "\n\nThis is a returning user. Be warm and reference previous conversations if relevant."
        
        return f"""You are the Customer Interface Agent (CIA) for InstaBids, helping homeowners describe their home improvement projects.

YOUR MAIN JOB: Extract project information naturally through conversation and call the update_bid_card function whenever you learn new details.

CONVERSATION RULES:
1. Be friendly, professional, and helpful
2. Extract information naturally - don't make it feel like an interrogation
3. For EMERGENCIES (flooding, fire, damage): Be brief, get location and contact immediately
4. For normal projects: Focus on understanding what they need done
5. NEVER push for budget - only note it if they volunteer the information
6. Ask one question at a time
7. Call update_bid_card AS SOON as you identify any project information

EXTRACTION PRIORITIES:
- Emergency: project_type, urgency=emergency, location, email (skip everything else)
- Normal: project_type, scope_details, timeline, location
- Nice to have: budget, materials, contractor preferences

IMPORTANT: 
- Call update_bid_card with whatever fields you've identified, even if partial
- Don't wait to collect all information before calling the tool
- Multiple calls are fine as you learn more
{other_projects_text}{context_text}

Remember: The user can see their bid card building in real-time, so update it frequently!"""