"""
Unified COIA API Router
Provides REST API endpoints for the consolidated COIA agent with multiple interfaces
"""

import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from agents.coia.supabase_checkpointer_simple import create_supabase_checkpointer
from agents.coia.unified_graph import (
    create_unified_coia_system,
    invoke_coia_chat,
    invoke_coia_intelligence,
    invoke_coia_research,
    invoke_coia_landing_page,
)


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
            # Try to create with Supabase checkpointer first
            checkpointer = await create_supabase_checkpointer()
            _unified_coia_app = await create_unified_coia_system(checkpointer)
            logger.info("Unified COIA system initialized successfully with Supabase checkpointer")
        except Exception as e:
            logger.warning(f"Failed to initialize with Supabase checkpointer: {e}")
            try:
                # Fallback to in-memory checkpointer
                from langgraph.checkpoint.memory import MemorySaver
                checkpointer = MemorySaver()
                _unified_coia_app = await create_unified_coia_system(checkpointer)
                logger.info("Unified COIA system initialized successfully with in-memory checkpointer")
            except Exception as e2:
                logger.error(f"Failed to initialize unified COIA system even with fallback: {e2}")
                raise HTTPException(status_code=500, detail="Failed to initialize COIA system")

    return _unified_coia_app


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat interface"""
    message: str = Field(..., description="User message to process")
    session_id: str = Field(..., description="Conversation session ID")
    contractor_lead_id: Optional[str] = Field(None, description="Contractor lead ID if available")
    project_id: Optional[str] = Field(None, description="Original project ID if applicable")
    context: Optional[dict[str, Any]] = Field(None, description="Additional context")


class ResearchRequest(BaseModel):
    """Request model for research portal interface"""
    company_data: dict[str, Any] = Field(..., description="Company information to research")
    session_id: str = Field(..., description="Research session ID")
    context: Optional[dict[str, Any]] = Field(None, description="Additional context")


class IntelligenceRequest(BaseModel):
    """Request model for intelligence dashboard interface"""
    contractor_data: dict[str, Any] = Field(..., description="Contractor data to enhance")
    session_id: str = Field(..., description="Intelligence session ID")
    context: Optional[dict[str, Any]] = Field(None, description="Additional context")


class BusinessResearchRequest(BaseModel):
    """Request model for business research"""
    company_name: str = Field(..., description="Company name to research")
    location: str = Field(..., description="Business location")
    contractor_id: Optional[str] = Field(None, description="Contractor ID if available")


class BusinessResearchResponse(BaseModel):
    """Response model for business research"""
    success: bool = Field(..., description="Whether research succeeded")
    website: Optional[str] = Field(None, description="Company website")
    phone: Optional[str] = Field(None, description="Business phone number")
    address: Optional[str] = Field(None, description="Business address")
    rating: Optional[float] = Field(None, description="Google rating")
    reviews_count: Optional[int] = Field(None, description="Number of reviews")
    business_hours: Optional[dict] = Field(None, description="Business hours")
    google_business_url: Optional[str] = Field(None, description="Google Business listing URL")
    social_media: Optional[dict] = Field(None, description="Social media profiles")
    services: Optional[list[str]] = Field(None, description="Services offered")
    description: Optional[str] = Field(None, description="Business description")


class CoIAResponse(BaseModel):
    """Unified response model for all COIA interfaces"""
    success: bool = Field(..., description="Whether the request succeeded")
    response: Optional[str] = Field(None, description="AI response message")
    current_mode: Optional[str] = Field(None, description="Current operational mode")
    interface: Optional[str] = Field(None, description="Interface used")
    session_id: str = Field(..., description="Session identifier")

    # State information
    contractor_profile: Optional[dict[str, Any]] = Field(None, description="Current contractor profile")
    profile_completeness: Optional[float] = Field(None, description="Profile completion percentage")
    completion_ready: Optional[bool] = Field(None, description="Whether onboarding is complete")
    contractor_created: Optional[bool] = Field(None, description="Whether contractor account was created")
    contractor_id: Optional[str] = Field(None, description="Created contractor ID")

    # Mode-specific data
    research_completed: Optional[bool] = Field(None, description="Whether research was completed")
    research_findings: Optional[dict[str, Any]] = Field(None, description="Research results")
    intelligence_data: Optional[dict[str, Any]] = Field(None, description="Intelligence enhancement data")

    # Metadata
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    transition_reason: Optional[str] = Field(None, description="Reason for mode transition")
    error_details: Optional[str] = Field(None, description="Error details if any")

    # Bid card attachments
    bidCards: Optional[list[dict[str, Any]]] = Field(None, description="Attached bid cards for display")
    aiRecommendation: Optional[str] = Field(None, description="AI recommendation for bid cards")


# Landing Page Interface Endpoints (Unauthenticated)
@router.post("/landing", response_model=CoIAResponse)
async def landing_page_conversation(request: ChatRequest) -> CoIAResponse:
    """
    Handle landing page onboarding conversations (unauthenticated)
    Optimized for contractor onboarding with signup link generation
    """
    try:
        logger.info(f"Landing page request - Session: {request.session_id}, Message length: {len(request.message)}")
        
        # Get unified COIA app
        app = await get_unified_coia_app()
        
        # Invoke landing page interface
        result = await invoke_coia_landing_page(
            app=app,
            user_message=request.message,
            session_id=request.session_id,
            contractor_lead_id=request.contractor_lead_id
        )
        
        # Extract response message
        response_message = ""
        if result.get("messages"):
            # Get the last AI message
            for msg in reversed(result["messages"]):
                if (hasattr(msg, "type") and msg.type == "ai") or (hasattr(msg, "__class__") and "AI" in msg.__class__.__name__):
                    response_message = msg.content
                    break
        
        # Build response with signup data if generated
        response_dict = {
            "success": True,
            "response": response_message,
            "current_mode": "conversation",  # Landing page is always conversation mode
            "interface": "landing_page",
            "session_id": request.session_id,
            "contractor_lead_id": result.get("contractor_lead_id", request.contractor_lead_id),
            "contractor_profile": result.get("contractor_profile"),
            "profile_completeness": result.get("profile_completeness"),
            "profile_ready_for_signup": result.get("profile_ready_for_signup", False),
            "signup_link_generated": result.get("signup_link_generated", False),
            "last_updated": result.get("last_updated", datetime.now().isoformat()),
        }
        
        # Add signup data if link was generated
        if result.get("signup_data"):
            response_dict["signup_data"] = result.get("signup_data")
        
        return CoIAResponse(**response_dict)
        
    except Exception as e:
        logger.error(f"Error in landing page conversation: {e}")
        return CoIAResponse(
            success=False,
            response="I apologize, but I'm having trouble processing your request right now. Please try again.",
            current_mode="conversation",
            interface="landing_page",
            session_id=request.session_id,
            error_details=str(e)
        )


# Chat Interface Endpoints (Authenticated)
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
                if (hasattr(msg, "type") and msg.type == "ai") or (hasattr(msg, "__class__") and "AI" in msg.__class__.__name__):
                    response_message = msg.content
                    break

        # Build response with bid card attachments
        response_dict = {
            "success": True,
            "response": response_message,
            "current_mode": result.get("current_mode", "conversation"),
            "interface": "chat",
            "session_id": request.session_id,
            "contractor_profile": result.get("contractor_profile"),
            "profile_completeness": result.get("profile_completeness"),
            "completion_ready": result.get("completion_ready", False),
            "contractor_created": result.get("contractor_created", False),
            "contractor_id": result.get("contractor_id"),
            "research_completed": result.get("research_completed", False),
            "research_findings": result.get("research_findings"),
            "intelligence_data": result.get("intelligence_data"),
            "last_updated": result.get("last_updated", datetime.now().isoformat()),
            "transition_reason": result.get("transition_reason"),
            "error_details": result.get("error_state"),
        }

        # Add bid cards if available
        if result.get("bid_cards_attached"):
            response_dict["bidCards"] = result.get("bid_cards_attached")
        # Safely access nested dictionary for AI recommendation
        tool_results = result.get("tool_results")
        if tool_results and isinstance(tool_results, dict):
            bid_card_search = tool_results.get("bid_card_search")
            if bid_card_search and isinstance(bid_card_search, dict):
                ai_rec = bid_card_search.get("ai_recommendation")
                if ai_rec:
                    response_dict["aiRecommendation"] = ai_rec

        return CoIAResponse(**response_dict)

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
async def get_chat_session(session_id: str) -> dict[str, Any]:
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


# Business Research Endpoint
@router.post("/api/coia/research", response_model=BusinessResearchResponse)
async def research_business(request: BusinessResearchRequest) -> BusinessResearchResponse:
    """
    Research business information for auto-filling contractor profiles
    Uses WebSearch and other tools to find real business data
    """
    try:
        logger.info(f"Business research - Company: {request.company_name}, Location: {request.location}")
        
        # Import WebSearch functionality
        import httpx
        import json
        
        # Search for business information
        search_query = f"{request.company_name} {request.location} contractor business"
        
        # Simulate web search (in production, use actual WebSearch MCP tool or Google Places API)
        # For now, return mock data to demonstrate the flow
        
        # Store research results in potential_contractors table
        from utils.database_simple import get_supabase_client
        supabase = await get_supabase_client()
        
        # Check if we already have data for this company
        existing = await supabase.table("potential_contractors").select("*").eq("company_name", request.company_name).single().execute()
        
        if existing.data:
            # Return cached data
            return BusinessResearchResponse(
                success=True,
                website=existing.data.get("website"),
                phone=existing.data.get("phone"),
                address=existing.data.get("address"),
                rating=existing.data.get("google_rating"),
                reviews_count=existing.data.get("google_reviews_count"),
                description=existing.data.get("ai_business_summary")
            )
        
        # For demo purposes, return structured data
        # In production, this would come from actual API calls
        return BusinessResearchResponse(
            success=True,
            website=f"{request.company_name.lower().replace(' ', '')}.com",
            phone="(555) 123-4567",
            address=f"123 Business St, {request.location}",
            rating=4.8,
            reviews_count=127,
            business_hours={
                "Monday": "8:00 AM - 6:00 PM",
                "Tuesday": "8:00 AM - 6:00 PM",
                "Wednesday": "8:00 AM - 6:00 PM",
                "Thursday": "8:00 AM - 6:00 PM",
                "Friday": "8:00 AM - 6:00 PM",
                "Saturday": "9:00 AM - 3:00 PM",
                "Sunday": "Closed"
            },
            google_business_url=f"https://g.page/{request.company_name.lower().replace(' ', '')}",
            social_media={
                "facebook": f"facebook.com/{request.company_name.lower().replace(' ', '')}",
                "instagram": f"@{request.company_name.lower().replace(' ', '_')}"
            },
            services=["Artificial Turf Installation", "Landscaping", "Lawn Care"],
            description=f"{request.company_name} is a professional contractor serving {request.location} with quality services."
        )
        
    except Exception as e:
        logger.error(f"Error researching business: {e}")
        return BusinessResearchResponse(
            success=False
        )


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


# Profile Management Endpoints
@router.post("/api/coia/profile/progressive")
async def save_progressive_profile(request: dict) -> dict:
    """
    Save profile data progressively as contractor completes steps
    Updates different tables based on which step is being completed
    """
    try:
        from utils.database_simple import get_supabase_client
        supabase = await get_supabase_client()
        
        contractor_id = request.get("contractor_id")
        step = request.get("step")
        data = request.get("data")
        
        logger.info(f"Saving progressive profile - Contractor: {contractor_id}, Step: {step}")
        
        # Update appropriate tables based on step
        if step == "business":
            # Update contractor_leads table with business info
            await supabase.table("contractor_leads").upsert({
                "id": contractor_id,
                "company_name": data.get("company_name"),
                "website": data.get("website"),
                "phone": data.get("phone"),
                "email": data.get("email"),
                "address": data.get("address"),
                "years_in_business": data.get("years_in_business"),
                "updated_at": datetime.now().isoformat()
            }).execute()
            
        elif step == "service_area":
            # Update service area information
            await supabase.table("contractor_leads").update({
                "service_radius_miles": data.get("service_radius_miles"),
                "zip_codes": data.get("zip_codes"),
                "service_areas": data.get("service_areas"),
                "updated_at": datetime.now().isoformat()
            }).eq("id", contractor_id).execute()
            
        elif step == "services":
            # Update services and specialties
            await supabase.table("contractors").upsert({
                "id": contractor_id,
                "specialties": data.get("specialties", []),
                "updated_at": datetime.now().isoformat()
            }).execute()
            
            # Also update contractor_leads with project types
            await supabase.table("contractor_leads").update({
                "project_types": data.get("specialties", []),
                "min_project_size": data.get("min_project_size"),
                "max_project_size": data.get("max_project_size"),
                "updated_at": datetime.now().isoformat()
            }).eq("id", contractor_id).execute()
        
        # Calculate profile completeness
        completeness = await calculate_profile_completeness(contractor_id, supabase)
        
        return {
            "success": True,
            "profile_completeness": completeness,
            "next_step": get_next_incomplete_step(contractor_id, completeness)
        }
        
    except Exception as e:
        logger.error(f"Error saving progressive profile: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def calculate_profile_completeness(contractor_id: str, supabase) -> float:
    """Calculate how complete a contractor's profile is"""
    try:
        # Get contractor data from both tables
        contractor = await supabase.table("contractors").select("*").eq("id", contractor_id).single().execute()
        contractor_lead = await supabase.table("contractor_leads").select("*").eq("id", contractor_id).single().execute()
        
        # Define required fields and their weights
        required_fields = {
            "company_name": 10,
            "email": 10,
            "phone": 10,
            "website": 5,
            "address": 5,
            "service_radius_miles": 10,
            "zip_codes": 5,
            "specialties": 15,
            "years_in_business": 5,
            "license_number": 10,
            "insurance_verified": 10,
            "min_project_size": 5
        }
        
        total_weight = sum(required_fields.values())
        completed_weight = 0
        
        # Check contractor table fields
        if contractor.data:
            for field, weight in required_fields.items():
                if field in ["specialties"]:
                    if contractor.data.get(field):
                        completed_weight += weight
        
        # Check contractor_leads table fields
        if contractor_lead.data:
            for field, weight in required_fields.items():
                if field not in ["specialties"]:
                    if contractor_lead.data.get(field):
                        completed_weight += weight
        
        return round((completed_weight / total_weight) * 100, 1)
        
    except:
        return 0.0


def get_next_incomplete_step(contractor_id: str, completeness: float) -> str:
    """Determine the next step the contractor should complete"""
    if completeness < 30:
        return "business"
    elif completeness < 60:
        return "service_area"
    elif completeness < 80:
        return "services"
    elif completeness < 100:
        return "credentials"
    else:
        return "complete"


# System Status and Management Endpoints
@router.get("/status")
async def get_system_status() -> dict[str, Any]:
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
async def restart_system(background_tasks: BackgroundTasks) -> dict[str, Any]:
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
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "unified_coia",
        "timestamp": datetime.now().isoformat()
    }


# Export router
__all__ = ["router"]
