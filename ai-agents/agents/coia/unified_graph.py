"""
Unified COIA LangGraph Implementation
Creates a single agent with multiple modes and conditional entry points
"""

import os
import logging
from typing import Dict, Any, Optional, Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.types import Command

from .unified_state import UnifiedCoIAState, create_initial_state
from .supabase_checkpointer import create_supabase_checkpointer
from .langgraph_nodes import (
    conversation_node,
    research_node,
    intelligence_node,
    mode_detector_node
)

logger = logging.getLogger(__name__)


class UnifiedCoIAGraph:
    """
    Unified COIA agent implemented as a LangGraph workflow
    Supports multiple entry points and dynamic mode switching
    """
    
    def __init__(self, checkpointer: Optional[BaseCheckpointSaver] = None):
        """Initialize the unified COIA graph"""
        self.checkpointer = checkpointer
        self.graph = None
        self.app = None
    
    async def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        if self.graph is not None:
            return self.graph
        
        logger.info("Building unified COIA graph...")
        
        # Create the state graph
        graph = StateGraph(UnifiedCoIAState)
        
        # Add nodes
        graph.add_node("mode_detector", mode_detector_node)
        graph.add_node("conversation", conversation_node)
        graph.add_node("research", research_node)
        graph.add_node("intelligence", intelligence_node)
        
        # Set conditional entry point based on interface and state
        graph.set_conditional_entry_point(
            self._determine_entry_point,
            {
                "conversation": "conversation",
                "research": "research",
                "intelligence": "intelligence",
                "mode_detector": "mode_detector"
            }
        )
        
        # Add conditional edges from mode_detector
        graph.add_conditional_edges(
            "mode_detector",
            self._route_from_mode_detector,
            {
                "conversation": "conversation",
                "research": "research", 
                "intelligence": "intelligence",
                "end": END
            }
        )
        
        # Add conditional edges from conversation node
        graph.add_conditional_edges(
            "conversation",
            self._route_from_conversation,
            {
                "continue": "conversation",
                "research": "research",
                "intelligence": "intelligence",
                "mode_detector": "mode_detector",
                "end": END
            }
        )
        
        # Add conditional edges from research node
        graph.add_conditional_edges(
            "research",
            self._route_from_research,
            {
                "conversation": "conversation",
                "intelligence": "intelligence",
                "mode_detector": "mode_detector",
                "end": END
            }
        )
        
        # Add conditional edges from intelligence node
        graph.add_conditional_edges(
            "intelligence",
            self._route_from_intelligence,
            {
                "conversation": "conversation",
                "mode_detector": "mode_detector",
                "end": END
            }
        )
        
        self.graph = graph
        logger.info("Unified COIA graph built successfully")
        return graph
    
    async def compile(self) -> Any:
        """Compile the graph into an executable application"""
        if self.app is not None:
            return self.app
        
        if self.graph is None:
            await self.build_graph()
        
        # Use provided checkpointer or create default Supabase one
        checkpointer = self.checkpointer
        if checkpointer is None:
            checkpointer = await create_supabase_checkpointer()
        
        # Compile the graph
        self.app = self.graph.compile(checkpointer=checkpointer)
        logger.info("Unified COIA graph compiled successfully")
        return self.app
    
    def _determine_entry_point(self, state: UnifiedCoIAState) -> str:
        """
        Determine entry point based on interface and current state
        This enables different interfaces to start in different modes
        """
        try:
            interface = state.get("interface", "chat")
            current_mode = state.get("current_mode", "conversation")
            
            logger.info(f"Determining entry point - Interface: {interface}, Mode: {current_mode}")
            
            # Interface-based entry points
            if interface == "research_portal":
                # Research portal should start in research mode if company name available
                if state.get("company_name"):
                    return "research"
                else:
                    return "conversation"  # Need to collect company info first
            
            elif interface == "intelligence_dashboard":
                # Intelligence dashboard should start in intelligence mode if data available
                if state.get("company_name") and (state.get("business_info") or state.get("research_completed")):
                    return "intelligence"
                else:
                    return "mode_detector"  # Let mode detector decide next step
            
            elif interface == "chat":
                # Chat interface - use mode detector for smart routing
                if current_mode in ["conversation", "research", "intelligence"]:
                    return current_mode
                else:
                    return "mode_detector"
            
            # Default entry point
            return "conversation"
        
        except Exception as e:
            logger.error(f"Error in entry point determination: {e}")
            return "conversation"  # Safe fallback
    
    def _route_from_mode_detector(self, state: UnifiedCoIAState) -> str:
        """Route from mode detector to appropriate node"""
        try:
            current_mode = state.get("current_mode", "conversation")
            
            # Check for completion
            if state.get("completion_ready") or state.get("contractor_created"):
                return "end"
            
            # Route to appropriate mode
            if current_mode == "research":
                return "research"
            elif current_mode == "intelligence":
                return "intelligence"
            else:
                return "conversation"
        
        except Exception as e:
            logger.error(f"Error routing from mode detector: {e}")
            return "conversation"
    
    def _route_from_conversation(self, state: UnifiedCoIAState) -> str:
        """Route from conversation node based on response"""
        try:
            # Check for completion first
            if state.get("completion_ready") or state.get("contractor_created"):
                return "end"
            
            # Check for mode transitions
            current_mode = state.get("current_mode", "conversation")
            previous_mode = state.get("previous_mode")
            
            # If mode changed, route accordingly
            if current_mode != "conversation":
                if current_mode == "research":
                    return "research"
                elif current_mode == "intelligence":
                    return "intelligence"
                else:
                    return "mode_detector"
            
            # Check for error state
            if state.get("error_state"):
                logger.warning(f"Error state detected: {state.get('error_state')}")
                return "end"
            
            # Continue conversation by default
            return "continue"
        
        except Exception as e:
            logger.error(f"Error routing from conversation: {e}")
            return "end"
    
    def _route_from_research(self, state: UnifiedCoIAState) -> str:
        """Route from research node based on results"""
        try:
            # Check for completion
            if state.get("completion_ready") or state.get("contractor_created"):
                return "end"
            
            # Check current mode after research
            current_mode = state.get("current_mode", "conversation")
            
            if current_mode == "intelligence":
                return "intelligence"
            elif current_mode == "conversation":
                return "conversation"
            else:
                return "mode_detector"
        
        except Exception as e:
            logger.error(f"Error routing from research: {e}")
            return "conversation"
    
    def _route_from_intelligence(self, state: UnifiedCoIAState) -> str:
        """Route from intelligence node based on results"""
        try:
            # Check for completion
            if state.get("completion_ready") or state.get("contractor_created"):
                return "end"
            
            # Intelligence typically returns to conversation
            current_mode = state.get("current_mode", "conversation")
            
            if current_mode == "conversation":
                return "conversation"
            else:
                return "mode_detector"
        
        except Exception as e:
            logger.error(f"Error routing from intelligence: {e}")
            return "conversation"


# Factory functions for different interface types
async def create_chat_interface_graph(checkpointer: Optional[BaseCheckpointSaver] = None) -> Any:
    """Create COIA graph optimized for chat interface"""
    graph = UnifiedCoIAGraph(checkpointer)
    return await graph.compile()


async def create_research_interface_graph(checkpointer: Optional[BaseCheckpointSaver] = None) -> Any:
    """Create COIA graph optimized for research portal interface"""
    graph = UnifiedCoIAGraph(checkpointer)
    return await graph.compile()


async def create_intelligence_interface_graph(checkpointer: Optional[BaseCheckpointSaver] = None) -> Any:
    """Create COIA graph optimized for intelligence dashboard interface"""
    graph = UnifiedCoIAGraph(checkpointer)
    return await graph.compile()


# Main interface for creating the unified COIA system
async def create_unified_coia_system(checkpointer: Optional[BaseCheckpointSaver] = None) -> Any:
    """
    Create the unified COIA system that can handle all interfaces
    This is the main entry point for the consolidated agent
    """
    logger.info("Creating unified COIA system...")
    
    try:
        graph = UnifiedCoIAGraph(checkpointer)
        app = await graph.compile()
        
        logger.info("Unified COIA system created successfully")
        return app
    
    except Exception as e:
        logger.error(f"Failed to create unified COIA system: {e}")
        raise


# Helper functions for invoking the unified system
async def invoke_coia_chat(
    app: Any,
    user_message: str,
    session_id: str,
    contractor_lead_id: Optional[str] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """Invoke COIA for chat interface"""
    
    config = {
        "configurable": {
            "thread_id": f"chat_{session_id}",
            "checkpoint_ns": "coia_chat"
        }
    }
    
    initial_state = create_initial_state(
        session_id=session_id,
        interface="chat",
        contractor_lead_id=contractor_lead_id,
        original_project_id=project_id
    ).to_langgraph_state()
    
    # Add the user message
    from langchain_core.messages import HumanMessage
    initial_state["messages"] = [HumanMessage(content=user_message)]
    
    result = await app.ainvoke(initial_state, config)
    return result


async def invoke_coia_research(
    app: Any,
    company_data: Dict[str, Any],
    session_id: str
) -> Dict[str, Any]:
    """Invoke COIA for research portal interface"""
    
    config = {
        "configurable": {
            "thread_id": f"research_{session_id}",
            "checkpoint_ns": "coia_research"
        }
    }
    
    initial_state = create_initial_state(
        session_id=session_id,
        interface="research_portal"
    ).to_langgraph_state()
    
    # Set company data for research
    initial_state["company_name"] = company_data.get("name")
    initial_state["company_website"] = company_data.get("website")
    initial_state["business_info"] = company_data
    
    from langchain_core.messages import HumanMessage
    initial_state["messages"] = [HumanMessage(content=f"Research company: {company_data.get('name')}")]
    
    result = await app.ainvoke(initial_state, config)
    return result


async def invoke_coia_intelligence(
    app: Any,
    contractor_data: Dict[str, Any],
    session_id: str
) -> Dict[str, Any]:
    """Invoke COIA for intelligence dashboard interface"""
    
    config = {
        "configurable": {
            "thread_id": f"intelligence_{session_id}",
            "checkpoint_ns": "coia_intelligence"
        }
    }
    
    initial_state = create_initial_state(
        session_id=session_id,
        interface="intelligence_dashboard"
    ).to_langgraph_state()
    
    # Set contractor data for intelligence processing
    initial_state["company_name"] = contractor_data.get("company_name")
    initial_state["contractor_profile"] = contractor_data
    initial_state["business_info"] = contractor_data.get("business_info", {})
    initial_state["research_completed"] = bool(contractor_data.get("research_data"))
    
    from langchain_core.messages import HumanMessage
    initial_state["messages"] = [HumanMessage(content=f"Enhance intelligence for: {contractor_data.get('company_name')}")]
    
    result = await app.ainvoke(initial_state, config)
    return result


# Export main functions
__all__ = [
    "UnifiedCoIAGraph",
    "create_unified_coia_system",
    "create_chat_interface_graph",
    "create_research_interface_graph", 
    "create_intelligence_interface_graph",
    "invoke_coia_chat",
    "invoke_coia_research",
    "invoke_coia_intelligence"
]