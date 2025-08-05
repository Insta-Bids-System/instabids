"""
Unified COIA API Router
Provides REST API endpoints for the consolidated COIA agent with multiple interfaces
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from agents.coia.unified_graph import (
    create_unified_coia_system,
    invoke_coia_chat,
    invoke_coia_research,
    invoke_coia_intelligence
)
from agents.coia.supabase_checkpointer import create_supabase_checkpointer

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/coia", tags=["Unified COIA"])

# Global app instance (initialized on first request)
_unified_coia_app = None


async def get_unified_coia_app():
    """Get or create the unified COIA application"""
    global _unified_coia_app
    
    if _unified_coia_app is None:
        logger.info("Initializing unified COIA system...")
        try:
            checkpointer = await create_supabase_checkpointer()
            _unified_coia_app = await create_unified_coia_system(checkpointer)
            logger.info("Unified COIA system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize unified COIA system: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize COIA system")
    
    return _unified_coia_app


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat interface"""
    message: str = Field(..., description="User message to process")
    session_id: str = Field(..., description="Conversation session ID")
    contractor_lead_id: Optional[str] = Field(None, description="Contractor lead ID if available")
    project_id: Optional[str] = Field(None, description="Original project ID if applicable")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ResearchRequest(BaseModel):
    """Request model for research portal interface"""
    company_data: Dict[str, Any] = Field(..., description="Company information to research")
    session_id: str = Field(..., description="Research session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class IntelligenceRequest(BaseModel):
    """Request model for intelligence dashboard interface"""
    contractor_data: Dict[str, Any] = Field(..., description="Contractor data to enhance")
    session_id: str = Field(..., description="Intelligence session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class CoIAResponse(BaseModel):
    """Unified response model for all COIA interfaces"""
    success: bool = Field(..., description="Whether the request succeeded")
    response: Optional[str] = Field(None, description="AI response message")
    current_mode: Optional[str] = Field(None, description="Current operational mode")
    interface: Optional[str] = Field(None, description="Interface used")
    session_id: str = Field(..., description="Session identifier")
    
    # State information
    contractor_profile: Optional[Dict[str, Any]] = Field(None, description="Current contractor profile")
    profile_completeness: Optional[float] = Field(None, description="Profile completion percentage")
    completion_ready: Optional[bool] = Field(None, description="Whether onboarding is complete")
    contractor_created: Optional[bool] = Field(None, description="Whether contractor account was created")
    contractor_id: Optional[str] = Field(None, description="Created contractor ID")
    
    # Mode-specific data
    research_completed: Optional[bool] = Field(None, description="Whether research was completed")
    research_findings: Optional[Dict[str, Any]] = Field(None, description="Research results")
    intelligence_data: Optional[Dict[str, Any]] = Field(None, description="Intelligence enhancement data")
    
    # Metadata
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    transition_reason: Optional[str] = Field(None, description="Reason for mode transition")
    error_details: Optional[str] = Field(None, description="Error details if any")


# Chat Interface Endpoints
@router.post("/chat", response_model=CoIAResponse)
async def chat_conversation(request: ChatRequest) -> CoIAResponse:
    """
    Handle chat interface conversations
    Primary interface for contractor onboarding conversations
    """
    try:
        logger.info(f"Chat request - Session: {request.session_id}, Message length: {len(request.message)}")
        
        # Get unified COIA app
        app = await get_unified_coia_app()
        
        # Invoke chat interface
        result = await invoke_coia_chat(
            app=app,
            user_message=request.message,
            session_id=request.session_id,
            contractor_lead_id=request.contractor_lead_id,
            project_id=request.project_id
        )
        
        # Extract response message
        response_message = ""
        if result.get("messages"):
            # Get the last AI message
            for msg in reversed(result["messages"]):
                if hasattr(msg, "type") and msg.type == "ai":
                    response_message = msg.content
                    break
                elif hasattr(msg, "__class__") and "AI" in msg.__class__.__name__:
                    response_message = msg.content
                    break
        
        # Build response
        return CoIAResponse(
            success=True,
            response=response_message,
            current_mode=result.get("current_mode", "conversation"),
            interface="chat",
            session_id=request.session_id,
            contractor_profile=result.get("contractor_profile"),
            profile_completeness=result.get("profile_completeness"),
            completion_ready=result.get("completion_ready", False),
            contractor_created=result.get("contractor_created", False),
            contractor_id=result.get("contractor_id"),
            research_completed=result.get("research_completed", False),
            research_findings=result.get("research_findings"),
            intelligence_data=result.get("intelligence_data"),
            last_updated=result.get("last_updated", datetime.now().isoformat()),
            transition_reason=result.get("transition_reason"),
            error_details=result.get("error_state")
        )
    
    except Exception as e:
        logger.error(f"Error in chat conversation: {e}")
        return CoIAResponse(
            success=False,
            response="I apologize, but I'm having trouble processing your request right now. Please try again.",
            current_mode="conversation",
            interface="chat",
            session_id=request.session_id,
            error_details=str(e)
        )


@router.get("/chat/session/{session_id}")
async def get_chat_session(session_id: str) -> Dict[str, Any]:
    """Get current state of a chat session"""
    try:
        # This would load state from checkpointer
        # For now, return basic session info
        return {
            "session_id": session_id,
            "interface": "chat",
            "status": "active",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Research Interface Endpoints
@router.post("/research", response_model=CoIAResponse)
async def research_company(request: ResearchRequest) -> CoIAResponse:
    """
    Handle research portal interface requests
    Specialized interface for company research and data enrichment
    """
    try:
        logger.info(f"Research request - Session: {request.session_id}, Company: {request.company_data.get('name')}")
        
        # Get unified COIA app
        app = await get_unified_coia_app()
        
        # Invoke research interface
        result = await invoke_coia_research(
            app=app,
            company_data=request.company_data,
            session_id=request.session_id
        )
        
        # Extract response message
        response_message = "Research completed successfully."
        if result.get("messages"):
            for msg in reversed(result["messages"]):
                if hasattr(msg, "type") and msg.type == "ai":
                    response_message = msg.content
                    break
        
        return CoIAResponse(
            success=True,
            response=response_message,
            current_mode=result.get("current_mode", "research"),
            interface="research_portal",
            session_id=request.session_id,
            contractor_profile=result.get("contractor_profile"),
            profile_completeness=result.get("profile_completeness"),
            completion_ready=result.get("completion_ready", False),
            contractor_created=result.get("contractor_created", False),
            contractor_id=result.get("contractor_id"),
            research_completed=result.get("research_completed", False),
            research_findings=result.get("research_findings"),
            intelligence_data=result.get("intelligence_data"),
            last_updated=result.get("last_updated", datetime.now().isoformat()),
            transition_reason=result.get("transition_reason"),
            error_details=result.get("error_state")
        )
    
    except Exception as e:
        logger.error(f"Error in research request: {e}")
        return CoIAResponse(
            success=False,
            response="Research request failed. Please try again.",
            current_mode="research",
            interface="research_portal",
            session_id=request.session_id,
            error_details=str(e)
        )


# Intelligence Interface Endpoints
@router.post("/intelligence", response_model=CoIAResponse)
async def enhance_intelligence(request: IntelligenceRequest) -> CoIAResponse:
    """
    Handle intelligence dashboard interface requests
    Advanced interface for data enhancement and Google Places integration
    """
    try:
        logger.info(f"Intelligence request - Session: {request.session_id}, Company: {request.contractor_data.get('company_name')}")
        
        # Get unified COIA app
        app = await get_unified_coia_app()
        
        # Invoke intelligence interface
        result = await invoke_coia_intelligence(
            app=app,
            contractor_data=request.contractor_data,
            session_id=request.session_id
        )
        
        # Extract response message
        response_message = "Intelligence enhancement completed successfully."
        if result.get("messages"):
            for msg in reversed(result["messages"]):
                if hasattr(msg, "type") and msg.type == "ai":
                    response_message = msg.content
                    break
        
        return CoIAResponse(
            success=True,
            response=response_message,
            current_mode=result.get("current_mode", "intelligence"),
            interface="intelligence_dashboard",
            session_id=request.session_id,
            contractor_profile=result.get("contractor_profile"),
            profile_completeness=result.get("profile_completeness"),
            completion_ready=result.get("completion_ready", False),
            contractor_created=result.get("contractor_created", False),
            contractor_id=result.get("contractor_id"),
            research_completed=result.get("research_completed", False),
            research_findings=result.get("research_findings"),
            intelligence_data=result.get("intelligence_data"),
            last_updated=result.get("last_updated", datetime.now().isoformat()),
            transition_reason=result.get("transition_reason"),
            error_details=result.get("error_state")
        )
    
    except Exception as e:
        logger.error(f"Error in intelligence request: {e}")
        return CoIAResponse(
            success=False,
            response="Intelligence enhancement failed. Please try again.",
            current_mode="intelligence",
            interface="intelligence_dashboard",
            session_id=request.session_id,
            error_details=str(e)
        )


# System Status and Management Endpoints
@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Get unified COIA system status"""
    try:
        global _unified_coia_app
        
        # Check if system is initialized
        system_initialized = _unified_coia_app is not None
        
        # Check capabilities
        import os
        capabilities = {
            "conversation": True,  # Always available
            "research": bool(os.getenv("PLAYWRIGHT_AVAILABLE", False)),
            "intelligence": bool(os.getenv("GOOGLE_PLACES_API_KEY")),
            "memory": bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"))
        }
        
        return {
            "status": "operational" if system_initialized else "initializing",
            "system_initialized": system_initialized,
            "capabilities": capabilities,
            "interfaces": ["chat", "research_portal", "intelligence_dashboard"],
            "version": "1.0.0",
            "last_check": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }


@router.post("/restart")
async def restart_system(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Restart the unified COIA system"""
    try:
        global _unified_coia_app
        
        def restart_task():
            global _unified_coia_app
            _unified_coia_app = None
            logger.info("Unified COIA system marked for restart")
        
        background_tasks.add_task(restart_task)
        
        return {
            "status": "restart_initiated",
            "message": "System will reinitialize on next request",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error restarting system: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health Check Endpoint
@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "unified_coia",
        "timestamp": datetime.now().isoformat()
    }


# Export router
__all__ = ["router"]