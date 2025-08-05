"""
LangGraph Node Wrappers for Unified COIA Agent
Converts existing COIA implementations into LangGraph-compatible nodes
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import Command

from .unified_state import UnifiedCoIAState, UnifiedCoIAConversationState, create_initial_state
from .agent import CoIAAgent
from .research_based_agent import ResearchBasedCoIAAgent
from .openai_o3_agent import OpenAIO3CoIA
from .supabase_checkpointer_simple import SupabaseCheckpointer

logger = logging.getLogger(__name__)


class CoIANodeWrapper:
    """Base wrapper class for COIA agent nodes"""
    
    def __init__(self):
        """Initialize with environment detection"""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_places_key = os.getenv("GOOGLE_PLACES_API_KEY")
        
        # Initialize agents (lazy loading)
        self._conversation_agent = None
        self._research_agent = None
        self._intelligence_agent = None
        
        # Capability detection
        self.has_playwright = self._check_playwright()
        self.has_google_places = bool(self.google_places_key)
        self.has_memory = self._check_supabase()
    
    def _check_playwright(self) -> bool:
        """Check if Playwright is available"""
        try:
            import playwright
            return True
        except ImportError:
            return False
    
    def _check_supabase(self) -> bool:
        """Check if Supabase credentials are available"""
        return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"))
    
    @property
    def conversation_agent(self) -> CoIAAgent:
        """Lazy load conversation agent"""
        if self._conversation_agent is None:
            self._conversation_agent = CoIAAgent(self.api_key)
        return self._conversation_agent
    
    @property
    def research_agent(self) -> ResearchBasedCoIAAgent:
        """Lazy load research agent"""
        if self._research_agent is None:
            self._research_agent = ResearchBasedCoIAAgent(self.api_key)
        return self._research_agent
    
    @property
    def intelligence_agent(self) -> OpenAIO3CoIA:
        """Lazy load intelligence agent (using Claude Opus 4 instead of O3)"""
        if self._intelligence_agent is None:
            # Use Claude Opus 4 for intelligence mode as O3 from Claude doesn't exist
            self._intelligence_agent = OpenAIO3CoIA(
                api_key=self.api_key,  # Claude API key
                google_places_api_key=self.google_places_key
            )
        return self._intelligence_agent
    
    def _extract_user_message(self, state: UnifiedCoIAState) -> str:
        """Extract the latest user message from state"""
        messages = state.get("messages", [])
        if not messages:
            return ""
        
        # Get the last human message
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                return msg.content
            elif isinstance(msg, HumanMessage):
                return msg.content
        
        return ""
    
    def _update_state_from_response(
        self, 
        state: UnifiedCoIAState, 
        response: str,
        agent_response: Dict[str, Any],
        current_mode: str
    ) -> Dict[str, Any]:
        """Update state based on agent response"""
        updates = {}
        
        # Add response message
        current_messages = state.get("messages", [])
        current_messages.append(AIMessage(content=response))
        updates["messages"] = current_messages
        
        # Update last_updated
        updates["last_updated"] = datetime.now().isoformat()
        
        # Update profile if provided
        profile_progress = agent_response.get("profile_progress", {})
        if profile_progress.get("collectedData"):
            updates["contractor_profile"] = profile_progress["collectedData"]
            updates["profile_completeness"] = profile_progress.get("completeness", 0.0)
        
        # Update business info detection
        if "business_info" in agent_response:
            updates["business_info"] = agent_response["business_info"]
            if agent_response["business_info"].get("company_name"):
                updates["company_name"] = agent_response["business_info"]["company_name"]
            if agent_response["business_info"].get("website"):
                updates["company_website"] = agent_response["business_info"]["website"]
        
        # Check for completion
        if agent_response.get("contractor_id"):
            updates["completion_ready"] = True
            updates["contractor_id"] = agent_response["contractor_id"]
            updates["contractor_created"] = True
            updates["conversion_successful"] = True
        
        # Mode-specific updates
        if current_mode == "research":
            if agent_response.get("research_data"):
                updates["research_findings"] = agent_response["research_data"]
                updates["research_completed"] = True
                updates["website_research_status"] = "completed"
        elif current_mode == "intelligence":
            if agent_response.get("intelligence_data"):
                updates["intelligence_data"] = agent_response["intelligence_data"]
            if agent_response.get("google_places_data"):
                updates["google_places_data"] = agent_response["google_places_data"]
            if agent_response.get("returning_contractor_id"):
                updates["returning_contractor_id"] = agent_response["returning_contractor_id"]
                updates["persistent_memory_loaded"] = True
        
        return updates
    
    def _calculate_profile_completeness(self, profile: Dict[str, Any]) -> float:
        """Calculate profile completeness percentage"""
        required_fields = [
            "company_name", "contact_name", "email", "phone",
            "primary_trade", "years_in_business", "service_areas"
        ]
        
        completed = sum(1 for field in required_fields if profile.get(field))
        return (completed / len(required_fields)) * 100.0
    
    def _determine_next_mode(self, state: UnifiedCoIAState, agent_response: Dict[str, Any]) -> Optional[str]:
        """Determine if we should transition to a different mode"""
        current_mode = state.get("current_mode", "conversation")
        
        # Check for research triggers
        if current_mode == "conversation":
            if (state.get("company_website") and 
                not state.get("research_completed") and 
                self.has_playwright):
                return "research"
        
        # Check for intelligence triggers  
        if current_mode in ["conversation", "research"]:
            if (state.get("company_name") and 
                state.get("business_info") and
                not state.get("intelligence_data") and
                self.has_google_places):
                return "intelligence"
        
        # Check for completion
        if agent_response.get("completed", False):
            return None  # Stay in current mode for completion message
        
        return current_mode  # Stay in current mode


# Node Functions for LangGraph
node_wrapper = CoIANodeWrapper()


async def conversation_node(state: UnifiedCoIAState) -> Command:
    """
    Conversation mode node - handles basic contractor onboarding conversation
    Uses the original CoIA agent implementation
    """
    try:
        logger.info(f"Conversation node processing - Mode: {state.get('current_mode')}")
        
        # Extract user message
        user_message = node_wrapper._extract_user_message(state)
        if not user_message:
            return {"error_state": "No user message found"}
        
        # Create conversation state for the agent
        session_id = state.get("session_id", "unknown")
        contractor_lead_id = state.get("contractor_lead_id")
        
        # Call the conversation agent
        agent_response = await node_wrapper.conversation_agent.process_message(
            session_id=session_id,
            user_message=user_message,
            context={"contractor_lead_id": contractor_lead_id}
        )
        
        if not agent_response.get("response"):
            return {"error_state": f"Conversation agent failed: No response received"}
        
        # Update state based on response
        updates = node_wrapper._update_state_from_response(
            state, 
            agent_response["response"],
            agent_response,
            "conversation"
        )
        
        # Determine next mode
        next_mode = node_wrapper._determine_next_mode(state, agent_response)
        
        if next_mode and next_mode != "conversation":
            # Transition to different mode
            updates["previous_mode"] = "conversation"
            updates["current_mode"] = next_mode
            updates["transition_reason"] = f"Detected {next_mode} opportunity"
            updates["mode_confidence"] = 0.8
            
            return Command(
                goto="mode_detector",  # Let mode detector route to appropriate node
                update=updates
            )
        else:
            # Stay in conversation mode or complete
            if updates.get("completion_ready"):
                updates["current_mode"] = "conversation"  # Ensure we stay for completion
                return Command(goto="END", update=updates)
            else:
                return updates
    
    except Exception as e:
        logger.error(f"Error in conversation node: {e}")
        return {"error_state": f"Conversation node error: {str(e)}"}


async def research_node(state: UnifiedCoIAState) -> Command:
    """
    Research mode node - handles website research and data enrichment
    Uses the research-based CoIA agent implementation  
    """
    try:
        logger.info(f"Research node processing - Company: {state.get('company_name')}")
        
        if not node_wrapper.has_playwright:
            # Fallback to conversation mode if Playwright not available
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": "Playwright not available - fallback to conversation",
                    "mode_confidence": 1.0
                }
            )
        
        # Get company information for research
        company_name = state.get("company_name")
        company_website = state.get("company_website")
        
        if not company_name:
            # Need more info, go back to conversation
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation", 
                    "transition_reason": "Need company name for research",
                    "mode_confidence": 1.0
                }
            )
        
        # Create research context
        research_context = {
            "company_name": company_name,
            "website": company_website,
            "business_info": state.get("business_info", {})
        }
        
        # Call research agent
        agent_response = await node_wrapper.research_agent.process_message(
            session_id=state.get("session_id", "unknown"),
            user_message=f"Research company: {company_name}",
            context=research_context
        )
        
        if not agent_response.get("response"):
            # Research failed, continue with conversation
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": f"Research failed: No response received",
                    "website_research_status": "failed",
                    "mode_confidence": 1.0
                }
            )
        
        # Update state with research results
        updates = node_wrapper._update_state_from_response(
            state,
            agent_response.get("response", "Research completed"),
            agent_response, 
            "research"
        )
        
        # Determine next step
        next_mode = node_wrapper._determine_next_mode(state, agent_response)
        
        if next_mode == "intelligence":
            # Move to intelligence mode
            updates["previous_mode"] = "research"
            updates["current_mode"] = "intelligence"
            updates["transition_reason"] = "Research complete - moving to intelligence enhancement"
            updates["mode_confidence"] = 0.9
            
            return Command(goto="intelligence", update=updates)
        else:
            # Return to conversation with research data
            updates["previous_mode"] = "research"
            updates["current_mode"] = "conversation"
            updates["transition_reason"] = "Research complete - returning to conversation"
            updates["mode_confidence"] = 1.0
            
            return Command(goto="conversation", update=updates)
    
    except Exception as e:
        logger.error(f"Error in research node: {e}")
        return Command(
            goto="conversation",
            update={
                "error_state": f"Research node error: {str(e)}",
                "current_mode": "conversation",
                "website_research_status": "failed"
            }
        )


async def intelligence_node(state: UnifiedCoIAState) -> Command:
    """
    Intelligence mode node - handles advanced data processing and Google Places integration
    Uses the OpenAI O3-based agent (but with Claude Opus 4)
    """
    try:
        logger.info(f"Intelligence node processing - Company: {state.get('company_name')}")
        
        if not node_wrapper.has_google_places:
            # Fallback to conversation if Google Places not available
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": "Google Places API not available - fallback to conversation",
                    "mode_confidence": 1.0
                }
            )
        
        # Get data for intelligence processing
        company_name = state.get("company_name")
        business_info = state.get("business_info", {})
        research_data = state.get("research_findings")
        
        if not company_name:
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": "Need company data for intelligence processing",
                    "mode_confidence": 1.0
                }
            )
        
        # Create intelligence context
        intelligence_context = {
            "company_name": company_name,
            "business_info": business_info,
            "research_data": research_data,
            "contractor_profile": state.get("contractor_profile", {})
        }
        
        # Call intelligence agent
        agent_response = await node_wrapper.intelligence_agent.process_message(
            session_id=state.get("session_id", "unknown"),
            user_message=f"Enhance intelligence for: {company_name}",
            context=intelligence_context
        )
        
        if not agent_response.get("response"):
            # Intelligence failed, continue with conversation
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": f"Intelligence processing failed: No response received",
                    "mode_confidence": 1.0
                }
            )
        
        # Update state with intelligence results
        updates = node_wrapper._update_state_from_response(
            state,
            agent_response.get("response", "Intelligence processing completed"),
            agent_response,
            "intelligence"
        )
        
        # Intelligence processing complete - return to conversation
        updates["previous_mode"] = "intelligence"
        updates["current_mode"] = "conversation"
        updates["transition_reason"] = "Intelligence processing complete - returning to conversation"
        updates["mode_confidence"] = 1.0
        
        return Command(goto="conversation", update=updates)
    
    except Exception as e:
        logger.error(f"Error in intelligence node: {e}")
        return Command(
            goto="conversation",
            update={
                "error_state": f"Intelligence node error: {str(e)}",
                "current_mode": "conversation"
            }
        )


async def mode_detector_node(state: UnifiedCoIAState) -> str:
    """
    Mode detector node - determines which mode to route to based on current state
    This is called for mode transitions and routing decisions
    """
    try:
        current_mode = state.get("current_mode", "conversation")
        
        logger.info(f"Mode detector - Current mode: {current_mode}")
        
        # Always respect explicit mode setting first
        if current_mode in ["conversation", "research", "intelligence"]:
            return current_mode
        
        # Determine mode based on state and capabilities
        company_name = state.get("company_name")
        has_website = bool(state.get("company_website"))
        research_completed = state.get("research_completed", False)
        has_intelligence_data = bool(state.get("intelligence_data"))
        
        # Research mode conditions
        if (company_name and has_website and 
            not research_completed and 
            node_wrapper.has_playwright):
            return "research"
        
        # Intelligence mode conditions
        if (company_name and 
            (research_completed or state.get("business_info")) and
            not has_intelligence_data and
            node_wrapper.has_google_places):
            return "intelligence"
        
        # Default to conversation
        return "conversation"
    
    except Exception as e:
        logger.error(f"Error in mode detector: {e}")
        return "conversation"  # Safe fallback


# Export node functions for graph construction
__all__ = [
    "conversation_node",
    "research_node", 
    "intelligence_node",
    "mode_detector_node",
    "CoIANodeWrapper"
]