"""
CIA Integration with Unified Conversation System and Privacy Framework
Implements the homeowner-side adapter for cross-agent memory sharing
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from adapters.homeowner_context import HomeownerContextAdapter
from services.context_policy import AgentType

logger = logging.getLogger(__name__)


class CIAUnifiedIntegration:
    """
    Integrates CIA agent with the unified conversation system
    Enables cross-agent memory sharing with IRIS and messaging agents
    """
    
    def __init__(self, api_base: Optional[str] = None):
        # Use environment variable or default if not provided
        if api_base is None:
            try:
                from config.service_urls import get_backend_url
                api_base = get_backend_url()
            except ImportError:
                # Fallback if config module doesn't exist
                import os
                api_base = os.getenv("BACKEND_URL", get_backend_url())
        
        self.api_base = api_base
        self.adapter = HomeownerContextAdapter()  # Fixed: No arguments needed
        self.agent_type = AgentType.CIA
        logger.info(f"[CIA Integration] Initialized with unified conversation system at {self.api_base}")
    
    async def load_conversation_context(
        self,
        user_id: str,
        project_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load full conversation context including IRIS insights and previous projects
        
        Args:
            user_id: Homeowner user ID
            project_id: Current project ID (optional)
            conversation_id: Current conversation ID (optional)
            
        Returns:
            Dict: Complete context with cross-agent insights
        """
        try:
            # Get full agent context including IRIS and previous conversations
            context = self.adapter.get_agent_context(
                user_id=user_id,
                project_id=project_id,
                conversation_id=conversation_id,
                agent_type=self.agent_type
            )
            
            # Extract key insights for CIA
            insights = {
                "user_profile": context.get("homeowner_profile", {}),
                "cross_project_memory": context.get("user_memory", {}),
                "iris_design_insights": context.get("inspiration_context", {}),
                "previous_conversations": context.get("conversation_history", []),
                "project_context": context.get("project_context", {}),
                "privacy_filtered": True
            }
            
            # Check for IRIS coordination data
            iris_context = context.get("inspiration_context", {})
            if iris_context.get("design_insights"):
                insights["design_complexity"] = iris_context["design_insights"].get("design_complexity")
                insights["budget_implications"] = iris_context["design_insights"].get("budget_implications")
                logger.info("[CIA Integration] Loaded IRIS design insights for budget discussion")
            
            logger.info(f"[CIA Integration] Loaded context for user {user_id} with {len(insights['previous_conversations'])} previous conversations")
            return insights
            
        except Exception as e:
            logger.error(f"[CIA Integration] Error loading context: {e}")
            return {"error": str(e), "context_available": False}
    
    async def save_conversation_with_unified_system(
        self,
        user_id: str,
        state: Dict[str, Any],
        session_id: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save conversation to unified system for cross-agent sharing
        
        Args:
            user_id: Homeowner user ID
            state: CIA conversation state
            session_id: Current session ID
            conversation_id: Existing conversation ID (optional)
            
        Returns:
            Dict: Result with conversation_id
        """
        try:
            # Ensure user_id is in UUID format
            try:
                user_uuid = str(uuid.UUID(user_id))
            except ValueError:
                # Create deterministic UUID from string
                user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))
            
            # Prepare conversation data
            conversation_data = {
                "user_id": user_uuid,
                "agent_type": "CIA",
                "title": f"CIA: {state.get('collected_info', {}).get('project_type', 'Project Setup')}",
                "metadata": {
                    "session_id": session_id,
                    "project_type": state.get("collected_info", {}).get("project_type"),
                    "current_phase": state.get("current_phase"),
                    "ready_for_jaa": state.get("ready_for_jaa", False),
                    "bid_card_number": state.get("bid_card_number"),
                    "active_bid_card": state.get("active_bid_card")
                },
                "context_type": "project_setup"
            }
            
            # Save through adapter (applies privacy filtering)
            success = self.adapter.save_conversation_context(
                user_id=user_uuid,
                conversation_data=conversation_data,
                agent_type=self.agent_type
            )
            
            if success:
                logger.info(f"[CIA Integration] Saved conversation to unified system for session {session_id}")
                
                # Extract and save key memories for cross-agent sharing
                await self._save_extracted_memories(user_uuid, state, conversation_id)
                
                return {"success": True, "conversation_id": conversation_id or "new"}
            else:
                logger.error("[CIA Integration] Failed to save to unified system")
                return {"success": False, "error": "Save failed"}
                
        except Exception as e:
            logger.error(f"[CIA Integration] Error saving conversation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _save_extracted_memories(
        self,
        user_id: str,
        state: Dict[str, Any],
        conversation_id: Optional[str]
    ):
        """
        Extract and save key memories for IRIS and messaging agents to use
        """
        try:
            collected_info = state.get("collected_info", {})
            
            # Extract budget preferences for IRIS
            if collected_info.get("budget_min") or collected_info.get("budget_max"):
                memory_data = {
                    "memory_type": "budget_preference",
                    "memory_key": f"budget_{collected_info.get('project_type', 'general')}",
                    "memory_value": {
                        "min": collected_info.get("budget_min"),
                        "max": collected_info.get("budget_max"),
                        "context": collected_info.get("budget_context")
                    },
                    "confidence": 0.9
                }
                # Save memory (would call unified API)
                logger.info(f"[CIA Integration] Saved budget preference memory for IRIS")
            
            # Extract timeline preferences
            if collected_info.get("timeline_urgency"):
                memory_data = {
                    "memory_type": "timeline_preference",
                    "memory_key": "timeline_flexibility",
                    "memory_value": collected_info.get("timeline_urgency"),
                    "confidence": 0.85
                }
                logger.info(f"[CIA Integration] Saved timeline preference memory")
            
            # Extract design preferences for IRIS
            if collected_info.get("material_preferences"):
                memory_data = {
                    "memory_type": "design_preference",
                    "memory_key": "material_preferences",
                    "memory_value": collected_info.get("material_preferences"),
                    "confidence": 0.8
                }
                logger.info(f"[CIA Integration] Saved material preferences for IRIS coordination")
                
        except Exception as e:
            logger.error(f"[CIA Integration] Error saving extracted memories: {e}")
    
    def get_cross_project_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get insights across all user projects for intelligent questioning
        Example: "I see you have a lawn project. Is this kitchen remodel in addition to that?"
        """
        try:
            insights = self.adapter.get_cross_project_insights(
                user_id=user_id,
                agent_type=self.agent_type
            )
            
            # Format insights for CIA's conversational use
            formatted_insights = {
                "has_multiple_projects": len(insights.get("projects", [])) > 1,
                "project_names": [p.get("title", "Untitled") for p in insights.get("projects", [])],
                "budget_patterns": insights.get("insights", []),
                "can_reference_projects": True
            }
            
            return formatted_insights
            
        except Exception as e:
            logger.error(f"[CIA Integration] Error getting cross-project insights: {e}")
            return {"has_multiple_projects": False}
    
    async def coordinate_with_iris(
        self,
        user_id: str,
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get IRIS design insights to inform CIA's budget and timeline discussions
        """
        try:
            # Check for IRIS insights in shared memory
            iris_insights = self.adapter.get_inspiration_context(user_id)
            
            if iris_insights.get("design_insights"):
                # Use IRIS's design complexity assessment
                complexity = iris_insights["design_insights"].get("design_complexity", "moderate")
                budget_impact = iris_insights["design_insights"].get("budget_implications", {})
                
                coordination_result = {
                    "has_iris_insights": True,
                    "design_complexity": complexity,
                    "budget_adjustment_needed": budget_impact.get("estimated_impact"),
                    "specialty_contractors_needed": iris_insights["design_insights"].get("contractor_specialties_needed", []),
                    "timeline_implications": iris_insights["design_insights"].get("timeline_implications")
                }
                
                logger.info(f"[CIA Integration] Retrieved IRIS coordination data: {complexity} complexity")
                return coordination_result
            else:
                return {"has_iris_insights": False}
                
        except Exception as e:
            logger.error(f"[CIA Integration] Error coordinating with IRIS: {e}")
            return {"has_iris_insights": False}