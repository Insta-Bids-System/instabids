"""
Instabids API Server
FastAPI backend that serves the LangGraph AI agents
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
from datetime import datetime
import base64
import io
import asyncio
from PIL import Image
import asyncio
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add the agents directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cia.agent import CustomerInterfaceAgent
from agents.cia.state import ConversationState
from agents.jaa.agent import JobAssessmentAgent
from agents.cda.agent_v2 import IntelligentContractorDiscoveryAgent  # Opus 4 powered CDA
from agents.eaa.agent import ExternalAcquisitionAgent
from agents.iris.agent import iris_agent, IrisRequest, IrisResponse
from agents.coia.intelligent_research_agent import initialize_intelligent_coia, get_intelligent_coia
from agents.orchestration.timing_probability_engine import ContractorOutreachCalculator, UrgencyLevel
from agents.orchestration.enhanced_campaign_orchestrator import EnhancedCampaignOrchestrator, CampaignRequest
from agents.orchestration.check_in_manager import CampaignCheckInManager
from database_simple import db
from api.bid_cards_simple import router as bid_cards_router
from api.projects import router as projects_router
# from api.iris_chat import router as iris_chat_router  # Removed - causing internal errors
from api.tracking import router as tracking_router

# Global agent instances
cia_agent = None
jaa_agent = None
cda_agent = None
eaa_agent = None
coia_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agents on startup and cleanup on shutdown"""
    global cia_agent, jaa_agent, cda_agent, eaa_agent, coia_agent
    
    print("\n[STARTUP] Beginning agent initialization...")
    print(f"[STARTUP] Working directory: {os.getcwd()}")
    print(f"[STARTUP] Looking for .env in: {os.path.join(os.path.dirname(__file__), '..', '.env')}")
    
    # Get API key from environment
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"[STARTUP] ANTHROPIC_API_KEY from env: {anthropic_key[:20] if anthropic_key else 'NOT FOUND'}...")
    
    if not anthropic_key:
        print("[WARNING] ANTHROPIC_API_KEY not set. Using demo mode.")
        print("[WARNING] This means AI will give generic responses and not use Claude Opus 4!")
        anthropic_key = "demo_key"
    else:
        print(f"[OK] Anthropic API key loaded successfully: {anthropic_key[:10]}...")
    
    try:
        cia_agent = CustomerInterfaceAgent(anthropic_key)
        print("[OK] CIA Agent initialized successfully with Claude Opus 4 + NEW InstaBids structure")
        
        jaa_agent = JobAssessmentAgent()
        print("[OK] Intelligent JAA Agent initialized successfully with Claude Opus 4 + LangGraph")
        
        cda_agent = IntelligentContractorDiscoveryAgent()
        print("[OK] CDA Agent (Opus 4) initialized successfully with intelligent matching")
        
        eaa_agent = ExternalAcquisitionAgent()
        print("[OK] EAA Agent initialized successfully")
        
        coia_agent = initialize_intelligent_coia(anthropic_key)
        print("[OK] Intelligent Research-Based CoIA Agent initialized successfully with Claude Opus 4")
        
        print("\n[READY] INSTABIDS NEW SYSTEM READY!")
        print("[OK] All agents powered by Claude Opus 4")
        print("[OK] Ready for production testing!\n")
    except Exception as e:
        print(f"[ERROR] Failed to initialize agents: {e}")
    
    yield
    
    # Cleanup on shutdown
    print("[SHUTDOWN] Cleaning up agents...")

# Initialize FastAPI app with lifespan
app = FastAPI(title="Instabids AI Agents API", version="1.0.0", lifespan=lifespan)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development - agents can use any port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bid_cards_router)
app.include_router(projects_router, prefix="/api")
# app.include_router(iris_chat_router)  # Removed - causing internal errors
app.include_router(tracking_router, prefix="/api")

# Add inspiration boards router
from api.inspiration_boards import router as inspiration_boards_router
app.include_router(inspiration_boards_router)

# Add demo boards router for testing
from api.demo_boards import router as demo_boards_router
app.include_router(demo_boards_router)

# Add demo iris router for testing
from api.demo_iris import router as demo_iris_router
app.include_router(demo_iris_router)

# Add image generation router
from api.image_generation import router as image_generation_router
app.include_router(image_generation_router)

# Add vision analysis router
from api.vision import router as vision_router
app.include_router(vision_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount test images for demo purposes
test_images_path = os.path.join(os.path.dirname(__file__), '..', 'test-images')
if os.path.exists(test_images_path):
    app.mount("/test-images", StaticFiles(directory=test_images_path), name="test-images")
    print(f"[OK] Test images mounted from: {test_images_path}")

# Mount static uploads directory for local image storage fallback
static_path = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(static_path):
    os.makedirs(static_path, exist_ok=True)
    os.makedirs(os.path.join(static_path, 'uploads'), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")
print(f"[OK] Static uploads mounted from: {static_path}")

@app.get("/demo/wfa-rich-preview", response_class=HTMLResponse)
async def get_wfa_demo():
    """WFA Demo page showing form filling with rich preview links"""
    try:
        demo_path = os.path.join(os.path.dirname(__file__), "templates", "demo_page.html")
        with open(demo_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Demo page not found</h1>", status_code=404)

@app.get("/api/bid-cards/homeowner/{homeowner_id}")
async def get_homeowner_bid_cards_direct(homeowner_id: str):
    """Get all bid cards for a specific homeowner - Direct implementation"""
    try:
        from asyncio import timeout as async_timeout
        
        # Add timeout to prevent hanging
        async with async_timeout(10):  # 10 second timeout
            # Get conversations for this user
            conversations_result = db.client.table('agent_conversations').select('thread_id').eq('user_id', homeowner_id).execute()
            
            if not conversations_result.data:
                return []
            
            # Get thread IDs
            thread_ids = [conv['thread_id'] for conv in conversations_result.data]
            
            # Get bid cards linked to these conversations
            result = db.client.table('bid_cards').select("*").in_('cia_thread_id', thread_ids).order('created_at', desc=True).execute()
        
        if not result.data:
            return []
            
        # Process bid cards to ensure photo_urls field exists
        bid_cards = []
        for card in result.data:
            # Map images to photo_urls for frontend compatibility
            if card.get('bid_document') and card['bid_document'].get('all_extracted_data'):
                extracted = card['bid_document']['all_extracted_data']
                if 'images' in extracted and 'photo_urls' not in extracted:
                    extracted['photo_urls'] = extracted['images']
            bid_cards.append(card)
            
        return bid_cards
        
    except asyncio.TimeoutError:
        print(f"[API ERROR] Timeout getting bid cards for {homeowner_id}")
        raise HTTPException(status_code=504, detail="Database query timeout")
    except Exception as e:
        print(f"[API ERROR] Failed to get homeowner bid cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/real-preview", response_class=HTMLResponse)
async def get_real_preview_test():
    """Real inline preview test page with JavaScript"""
    try:
        test_path = os.path.join(os.path.dirname(__file__), "test_real_preview.html")
        with open(test_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Test page not found</h1>", status_code=404)

# Pydantic models

class ChatMessage(BaseModel):
    message: str
    images: Optional[List[str]] = None  # Base64 encoded images
    session_id: Optional[str] = None
    user_id: Optional[str] = None  # Authenticated user ID
    project_id: Optional[str] = None  # Project ID for multi-project support

class ChatResponse(BaseModel):
    response: str
    session_id: str
    current_phase: str
    ready_for_jaa: bool
    missing_fields: List[str]

class ContractorChatMessage(BaseModel):
    session_id: str
    message: str
    current_stage: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None

class ContractorChatResponse(BaseModel):
    response: str
    stage: str
    profile_progress: Dict[str, Any]
    contractor_id: Optional[str] = None
    session_data: Dict[str, Any]

# Health check endpoint

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Instabids AI Agents API",
        "agents": {
            "cia": "active" if cia_agent else "inactive",
            "jaa": "active" if jaa_agent else "inactive",
            "cda": "active" if cda_agent else "inactive",
            "eaa": "active" if eaa_agent else "inactive",
            "coia": "active" if coia_agent else "inactive"
        },
        "instabids_features": {
            "service_type_classification": True,
            "group_bidding_assessment": True,
            "intention_scoring": True,
            "value_propositions": True,
            "12_data_points": True
        },
        "environment": {
            "anthropic_key_loaded": bool(os.getenv("ANTHROPIC_API_KEY")),
            "model": "claude-opus-4-20250514"
        }
    }

@app.post("/api/cia/chat", response_model=ChatResponse)
async def cia_chat(chat_data: ChatMessage):
    """Handle chat messages for the CIA agent with Supabase persistence"""
    if not cia_agent:
        # If agent not initialized (no API key), provide intelligent fallback
        return ChatResponse(
            response=generate_intelligent_response(chat_data.message, chat_data.images),
            session_id=chat_data.session_id or f"demo_{datetime.now().timestamp()}",
            current_phase="discovery",
            ready_for_jaa=False,
            missing_fields=["project_type", "budget", "timeline"]
        )
    
    try:
        # Use authenticated user ID if provided, otherwise use anonymous UUID
        user_id = chat_data.user_id or "00000000-0000-0000-0000-000000000000"
        if chat_data.user_id:
            print(f"[CIA] Using authenticated user ID: {user_id}")
        else:
            print(f"[CIA] Using anonymous user ID: {user_id}")
        
        # Handle project awareness
        project_id = chat_data.project_id
        bid_card_context = None
        if project_id:
            print(f"[CIA] Using project ID: {project_id}")
            # Load bid card data
            try:
                # Try to load bid card data
                bid_card_result = db.client.table('bid_cards').select('*').eq('id', project_id).execute()
                if bid_card_result.data:
                    bid_card_context = bid_card_result.data[0]
                    print(f"[CIA] Loaded bid card: {bid_card_context.get('bid_card_number')}")
                else:
                    print(f"[CIA] No bid card found for project ID: {project_id}")
                
                # Verify user access if authenticated
                if user_id != "00000000-0000-0000-0000-000000000000" and bid_card_context:
                    # For authenticated users, check homeowner relationship
                    homeowner_result = db.client.table('homeowners').select('id').eq('user_id', user_id).execute()
                    if homeowner_result.data:
                        homeowner_id = homeowner_result.data[0]['id']
                        if bid_card_context.get('homeowner_id') != homeowner_id:
                            raise HTTPException(status_code=403, detail="Bid card access denied")
                        print(f"[CIA] Verified bid card access for homeowner {homeowner_id}")
            except HTTPException:
                raise
            except Exception as e:
                print(f"[CIA] Bid card loading warning: {e}")
        
        # Generate session ID - include project if specified
        if not chat_data.session_id:
            if project_id:
                session_id = f"project_{project_id}_{datetime.now().timestamp()}"
            else:
                session_id = f"cia_anonymous_{datetime.now().timestamp()}"
        else:
            session_id = chat_data.session_id
        
        # Load existing conversation state from Supabase
        existing_conversation = await db.load_conversation_state(session_id)
        
        # Extract state if conversation exists
        if existing_conversation:
            print(f"[CIA] Loaded existing conversation for session {session_id}")
            existing_state = existing_conversation.get('state', {})
        else:
            print(f"[CIA] Starting new conversation for session {session_id}")
            existing_state = None
        
        # Process images if provided
        image_urls = []
        if chat_data.images:
            for img_data in chat_data.images:
                # In production, save to Supabase storage
                # For now, we'll just pass the base64 data
                image_urls.append(img_data)
        
        # Enhance existing state with bid card context if available
        if existing_state and bid_card_context:
            existing_state['bid_card_context'] = bid_card_context
            existing_state['project_id'] = project_id
        elif bid_card_context:
            existing_state = {
                'bid_card_context': bid_card_context,
                'project_id': project_id
            }
        
        # Call the actual CIA agent with existing state
        result = await cia_agent.handle_conversation(
            user_id=user_id,
            message=chat_data.message,
            images=image_urls,
            session_id=session_id,
            existing_state=existing_state,
            project_id=project_id
        )
        
        # Save conversation state to Supabase
        if 'state' in result:
            # Add project information to state if available
            enhanced_state = result['state'].copy()
            if project_id:
                enhanced_state['project_id'] = project_id
                enhanced_state['project_context'] = True
            
            await db.save_conversation_state(
                user_id=user_id,
                thread_id=session_id,
                agent_type='CIA',
                state=enhanced_state
            )
            print(f"[CIA] Saved conversation state for session {session_id}")
            
            # If project is specified and conversation is ready for JAA, link them
            if project_id and result.get('ready_for_jaa', False):
                try:
                    db.client.table('projects').update({
                        'cia_conversation_id': session_id,
                        'status': 'in_progress'
                    }).eq('id', project_id).execute()
                    print(f"[CIA] Linked conversation {session_id} to project {project_id}")
                except Exception as e:
                    print(f"[CIA] Warning: Could not link conversation to project: {e}")
        
        return ChatResponse(**result)
        
    except Exception as e:
        import traceback
        print(f"Error in CIA chat: {e}")
        print(traceback.format_exc())
        # Fallback to intelligent response
        return ChatResponse(
            response=generate_intelligent_response(chat_data.message, chat_data.images),
            session_id=chat_data.session_id or f"demo_{datetime.now().timestamp()}",
            current_phase="discovery",
            ready_for_jaa=False,
            missing_fields=["project_type", "budget", "timeline"]
        )

def generate_intelligent_response(message: str, images: Optional[List[str]] = None) -> str:
    """Generate contextually appropriate responses without LLM"""
    message_lower = message.lower()
    
    # Image handling
    if images and len(images) > 0:
        image_count = len(images)
        image_response = f"I can see you've uploaded {image_count} {'photo' if image_count == 1 else 'photos'}. "
        
        # Analyze based on context
        if "kitchen" in message_lower:
            return image_response + "From what I can see, this kitchen space has great potential! Can you tell me what specific changes you're envisioning? Are you thinking about updating the cabinets, countertops, appliances, or going for a complete transformation?"
        elif "bathroom" in message_lower:
            return image_response + "Thanks for sharing these bathroom photos. I can see the current setup. What's your main goal with this renovation - are you looking to update fixtures, retile, or do a complete remodel?"
        else:
            return image_response + "These photos really help me understand your space. What specific improvements are you hoping to make?"
    
    # Project type responses
    if "kitchen" in message_lower:
        if "complete" in message_lower or "full" in message_lower:
            return "A complete kitchen renovation is an exciting project! This typically includes new cabinets, countertops, appliances, flooring, and sometimes layout changes. What's your approximate budget range for this project? Most full kitchen remodels in your area range from $25,000 to $60,000."
        elif "cabinet" in message_lower:
            return "Cabinet updates can dramatically transform your kitchen! Are you thinking about refacing the existing cabinets, painting them, or installing completely new ones? Also, what style appeals to you - modern, traditional, or transitional?"
        else:
            return "Great! Kitchen projects are very popular and can really transform your home. To help match you with the right contractors, could you tell me more about what you'd like to change? For example, are you updating cabinets, countertops, appliances, or planning a complete remodel?"
    
    elif "bathroom" in message_lower:
        if "master" in message_lower or "primary" in message_lower:
            return "A master bathroom renovation - excellent choice! These typically include updating fixtures, tile work, vanities, and sometimes expanding the space. What's the size of your current bathroom, and what are your must-have features?"
        elif "guest" in message_lower or "powder" in message_lower:
            return "Guest bathroom updates are great for both functionality and home value. Are you thinking about a simple refresh with new fixtures and paint, or a more comprehensive update with new tile and vanity?"
        else:
            return "Bathroom renovations are fantastic for both daily enjoyment and home value. What's motivating this project - is it style updates, fixing problems, or adding functionality? And which bathroom are we talking about - master, guest, or another?"
    
    elif "roof" in message_lower:
        if "leak" in message_lower or "damage" in message_lower:
            return "I understand - roof leaks need immediate attention. How severe is the damage? Are you seeing water stains inside, missing shingles, or active leaking? This will help determine if you need emergency repairs or can plan for a full replacement."
        else:
            return "Roof work is crucial for protecting your home. Are you dealing with damage that needs repair, or is it time for a full replacement? Also, do you know approximately how old your current roof is?"
    
    elif "budget" in message_lower:
        return "Budget planning is smart! For reference, here are typical ranges in your area:\n• Kitchen remodels: $15,000-$60,000\n• Bathroom remodels: $8,000-$25,000\n• Roofing: $8,000-$20,000\n• Flooring: $3-12 per sq ft\n\nWhat's your comfortable investment range for this project?"
    
    elif "timeline" in message_lower or "when" in message_lower or "how long" in message_lower:
        return "Timing is definitely important to plan for. Are you looking to start as soon as possible, or do you have a specific timeframe in mind? Also, is there a particular deadline you need the project completed by? This helps contractors plan their schedules and give you accurate timelines."
    
    elif "contractor" in message_lower or "how" in message_lower and "work" in message_lower:
        return "Great question! Here's how Instabids works: I'll help you describe your project in detail, including photos if you have them. Then our system matches you with qualified contractors who will submit competitive bids. You only pay a connection fee when you choose a contractor. No more endless sales meetings! What project would you like to start with?"
    
    # General fallback
    else:
        return "I'd be happy to help with your home improvement project! Could you tell me what type of work you're considering? Common projects include kitchen remodels, bathroom updates, roofing, flooring, painting, or outdoor improvements. Feel free to share photos if you have them - they really help me understand your vision."

@app.post("/api/contractor-chat/message", response_model=ContractorChatResponse)
async def contractor_chat(chat_data: ContractorChatMessage):
    """Handle contractor onboarding chat messages with CoIA agent"""
    if not coia_agent:
        # Fallback response if CoIA not initialized
        return ContractorChatResponse(
            response="I'm having trouble connecting right now. Please try again in a moment.",
            stage=chat_data.current_stage or "welcome",
            profile_progress={
                "completeness": 0,
                "stage": chat_data.current_stage or "welcome",
                "collectedData": {},
                "matchingProjects": 0
            },
            contractor_id=None,
            session_data={}
        )
    
    try:
        # Process message with CoIA agent
        result = await coia_agent.process_message(
            session_id=chat_data.session_id,
            user_message=chat_data.message,
            context={
                "current_stage": chat_data.current_stage,
                "profile_data": chat_data.profile_data or {}
            }
        )
        
        return ContractorChatResponse(**result)
        
    except Exception as e:
        import traceback
        print(f"Error in contractor chat: {e}")
        print(traceback.format_exc())
        
        # Fallback response
        return ContractorChatResponse(
            response="I apologize, but I'm having trouble processing that right now. Could you please try rephrasing your response?",
            stage=chat_data.current_stage or "welcome",
            profile_progress={
                "completeness": 0,
                "stage": chat_data.current_stage or "welcome", 
                "collectedData": chat_data.profile_data or {},
                "matchingProjects": 0
            },
            contractor_id=None,
            session_data={}
        )

@app.post("/api/jaa/process/{thread_id}")
async def process_with_jaa(thread_id: str):
    """Process CIA conversation with JAA to generate bid card"""
    if not jaa_agent:
        raise HTTPException(500, "JAA agent not initialized")
    
    try:
        result = jaa_agent.process_conversation(thread_id)
        
        if result['success']:
            return {
                "success": True,
                "bid_card_number": result['bid_card_number'],
                "bid_card_data": result['bid_card_data'],
                "cia_thread_id": result['cia_thread_id'],
                "database_id": result['database_id']
            }
        else:
            raise HTTPException(500, result.get('error', 'Unknown error processing conversation'))
    
    except Exception as e:
        print(f"[JAA API ERROR] {e}")
        raise HTTPException(500, f"JAA processing failed: {str(e)}")


@app.post("/api/cda/discover/{bid_card_id}")
async def discover_contractors(bid_card_id: str, contractors_needed: int = 5):
    """Discover contractors for a bid card using Opus 4 intelligent matching"""
    if not cda_agent:
        raise HTTPException(500, "CDA agent not initialized")
    
    try:
        result = cda_agent.discover_contractors_for_bid(bid_card_id, contractors_needed)
        
        if result['success']:
            return {
                "success": True,
                "bid_card_id": result['bid_card_id'],
                "contractors_found": len(result.get('selected_contractors', [])),
                "selected_contractors": result['selected_contractors'],
                "tier_breakdown": result['tier_breakdown'],
                "processing_time_ms": result['processing_time_ms'],
                "opus4_analysis": result.get('bid_analysis'),
                "cache_id": result.get('cache_id')
            }
        else:
            raise HTTPException(500, result.get('error', 'Unknown error discovering contractors'))
    
    except Exception as e:
        print(f"[CDA API ERROR] {e}")
        raise HTTPException(500, f"CDA discovery failed: {str(e)}")

@app.get("/api/cda/cache/{bid_card_id}")
async def get_discovery_cache(bid_card_id: str):
    """Get cached contractor discovery results for a bid card"""
    if not cda_agent:
        raise HTTPException(500, "CDA agent not initialized")
    
    try:
        cache_data = cda_agent.get_discovery_cache(bid_card_id)
        
        if cache_data:
            return {
                "success": True,
                "cache_data": cache_data
            }
        else:
            raise HTTPException(404, "No discovery cache found for this bid card")
    
    except Exception as e:
        print(f"[CDA CACHE ERROR] {e}")
        raise HTTPException(500, f"Failed to get discovery cache: {str(e)}")

# EAA API Endpoints
@app.post("/api/eaa/campaign/start")
async def start_eaa_campaign(campaign_data: dict):
    """Start EAA outreach campaign for discovered contractors"""
    if not eaa_agent:
        raise HTTPException(500, "EAA agent not initialized")
    
    try:
        bid_card_id = campaign_data.get('bid_card_id')
        contractors = campaign_data.get('contractors', [])
        channels = campaign_data.get('channels', ['email', 'sms'])
        urgency = campaign_data.get('urgency', 'week')
        
        if not bid_card_id or not contractors:
            raise HTTPException(400, "bid_card_id and contractors are required")
        
        result = eaa_agent.start_campaign(
            bid_card_id=bid_card_id,
            contractors=contractors,
            channels=channels,
            urgency=urgency
        )
        
        if result['success']:
            return {
                "success": True,
                "campaign_id": result['campaign_id'],
                "messages_sent": result['messages_sent'],
                "tier_breakdown": result['tier_breakdown'],
                "tracking_url": result['tracking_url']
            }
        else:
            raise HTTPException(500, result.get('error', 'Unknown error starting campaign'))
    
    except Exception as e:
        print(f"[EAA API ERROR] {e}")
        raise HTTPException(500, f"EAA campaign failed: {str(e)}")

@app.get("/api/eaa/campaign/{campaign_id}/status")
async def get_eaa_campaign_status(campaign_id: str):
    """Get EAA campaign status and metrics"""
    if not eaa_agent:
        raise HTTPException(500, "EAA agent not initialized")
    
    try:
        result = eaa_agent.get_campaign_status(campaign_id)
        
        if result['success']:
            return {
                "success": True,
                "campaign_id": result['campaign_id'],
                "status": result['status'],
                "metrics": result['metrics'],
                "recent_responses": result['recent_responses'],
                "tier_breakdown": result['tier_breakdown']
            }
        else:
            raise HTTPException(404, result.get('error', 'Campaign not found'))
    
    except Exception as e:
        print(f"[EAA STATUS ERROR] {e}")
        raise HTTPException(500, f"Failed to get campaign status: {str(e)}")

@app.post("/api/eaa/response/process")
async def process_eaa_response(response_data: dict):
    """Process incoming contractor response"""
    if not eaa_agent:
        raise HTTPException(500, "EAA agent not initialized")
    
    try:
        message_id = response_data.get('message_id')
        response_content = response_data.get('response_content')
        channel = response_data.get('channel')
        
        if not all([message_id, response_content, channel]):
            raise HTTPException(400, "message_id, response_content, and channel are required")
        
        result = eaa_agent.process_response(message_id, response_content, channel)
        
        if result['success']:
            return {
                "success": True,
                "response_id": result['response_id'],
                "intent": result['intent'],
                "interest_level": result['interest_level'],
                "action_taken": result['action_taken'],
                "follow_up_scheduled": result['follow_up_scheduled']
            }
        else:
            raise HTTPException(500, result.get('error', 'Unknown error processing response'))
    
    except Exception as e:
        print(f"[EAA RESPONSE ERROR] {e}")
        raise HTTPException(500, f"Failed to process response: {str(e)}")

@app.post("/api/eaa/onboarding/start")
async def start_eaa_onboarding(onboarding_data: dict):
    """Start contractor onboarding process"""
    if not eaa_agent:
        raise HTTPException(500, "EAA agent not initialized")
    
    try:
        contractor_email = onboarding_data.get('contractor_email')
        source_campaign = onboarding_data.get('source_campaign')
        
        if not contractor_email:
            raise HTTPException(400, "contractor_email is required")
        
        result = eaa_agent.start_onboarding(contractor_email, source_campaign)
        
        if result['success']:
            return {
                "success": True,
                "onboarding_id": result['onboarding_id'],
                "next_step": result['next_step'],
                "estimated_completion": result['estimated_completion']
            }
        else:
            raise HTTPException(500, result.get('error', 'Unknown error starting onboarding'))
    
    except Exception as e:
        print(f"[EAA ONBOARDING ERROR] {e}")
        raise HTTPException(500, f"Failed to start onboarding: {str(e)}")

@app.get("/api/eaa/analytics")
async def get_eaa_analytics(date_range: int = 30):
    """Get EAA performance analytics"""
    if not eaa_agent:
        raise HTTPException(500, "EAA agent not initialized")
    
    try:
        result = eaa_agent.get_analytics(date_range)
        
        if result['success']:
            return {
                "success": True,
                "period_days": result['period_days'],
                "campaigns_launched": result['campaigns_launched'],
                "total_contractors_contacted": result['total_contractors_contacted'],
                "overall_metrics": result['overall_metrics'],
                "channel_performance": result['channel_performance'],
                "top_performing_templates": result['top_performing_templates']
            }
        else:
            raise HTTPException(500, result.get('error', 'Unknown error getting analytics'))
    
    except Exception as e:
        print(f"[EAA ANALYTICS ERROR] {e}")
        raise HTTPException(500, f"Failed to get analytics: {str(e)}")

# Webhook endpoints for external services
@app.post("/api/eaa/webhook/email-response")
async def handle_email_webhook(webhook_data: dict):
    """Handle SendGrid email webhook"""
    if not eaa_agent:
        raise HTTPException(500, "EAA agent not initialized")
    
    try:
        # Process email webhook
        result = eaa_agent.email_channel.handle_webhook(webhook_data)
        return {"success": result['success'], "processed": True}
    
    except Exception as e:
        print(f"[EMAIL WEBHOOK ERROR] {e}")
        raise HTTPException(500, f"Failed to process email webhook: {str(e)}")

@app.post("/api/eaa/webhook/sms-response")
async def handle_sms_webhook(webhook_data: dict):
    """Handle Twilio SMS webhook"""
    if not eaa_agent:
        raise HTTPException(500, "EAA agent not initialized")
    
    try:
        # Process SMS webhook
        result = eaa_agent.sms_channel.handle_incoming_sms(webhook_data)
        return {"success": result['success'], "processed": True}
    
    except Exception as e:
        print(f"[SMS WEBHOOK ERROR] {e}")
        raise HTTPException(500, f"Failed to process SMS webhook: {str(e)}")

# Orchestration & Timing Endpoints
@app.post("/api/timing/calculate")
async def calculate_timing_strategy(request: dict):
    """Calculate how many contractors to contact based on timeline"""
    try:
        calculator = ContractorOutreachCalculator()
        strategy = calculator.calculate_outreach_strategy(
            bids_needed=request.get('bids_needed', 4),
            timeline_hours=request.get('timeline_hours', 24),
            tier1_available=request.get('tier1_available', 10),
            tier2_available=request.get('tier2_available', 30),
            tier3_available=request.get('tier3_available', 100),
            project_type=request.get('project_type'),
            location=request.get('location')
        )
        
        return {
            "success": True,
            "total_contractors": strategy.total_to_contact,
            "expected_responses": strategy.expected_total_responses,
            "confidence": strategy.confidence_score,
            "urgency": strategy.urgency_level.value,
            "tier_breakdown": {
                "tier1": {
                    "to_contact": strategy.tier1_strategy.to_contact,
                    "expected_responses": strategy.tier1_strategy.expected_responses,
                    "response_rate": strategy.tier1_strategy.response_rate
                },
                "tier2": {
                    "to_contact": strategy.tier2_strategy.to_contact,
                    "expected_responses": strategy.tier2_strategy.expected_responses,
                    "response_rate": strategy.tier2_strategy.response_rate
                },
                "tier3": {
                    "to_contact": strategy.tier3_strategy.to_contact,
                    "expected_responses": strategy.tier3_strategy.expected_responses,
                    "response_rate": strategy.tier3_strategy.response_rate
                }
            },
            "check_in_times": [t.isoformat() for t in strategy.check_in_times],
            "recommendations": strategy.recommendations
        }
    except Exception as e:
        print(f"[TIMING API ERROR] {e}")
        raise HTTPException(500, f"Failed to calculate timing strategy: {str(e)}")

@app.post("/api/campaigns/create-intelligent")
async def create_intelligent_campaign(campaign_data: dict):
    """Create campaign with timing and orchestration"""
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Create campaign request
        request = CampaignRequest(
            bid_card_id=campaign_data['bid_card_id'],
            project_type=campaign_data['project_type'],
            timeline_hours=campaign_data.get('timeline_hours', 24),
            urgency_level=campaign_data.get('urgency_level', 'standard'),
            bids_needed=campaign_data.get('bids_needed', 4),
            location=campaign_data.get('location', {})
        )
        
        # Create intelligent campaign
        result = await orchestrator.create_intelligent_campaign(request)
        
        return {
            "success": result.get('success', False),
            "campaign_id": result.get('campaign_id'),
            "total_contractors": result.get('total_contractors'),
            "strategy": result.get('strategy'),
            "error": result.get('error')
        }
        
    except Exception as e:
        print(f"[CAMPAIGN CREATE ERROR] {e}")
        raise HTTPException(500, f"Failed to create intelligent campaign: {str(e)}")

@app.get("/api/campaigns/{campaign_id}/check-in")
async def check_campaign_status(campaign_id: str):
    """Check if campaign needs escalation"""
    try:
        manager = CampaignCheckInManager()
        # Use perform_check_in instead of check_campaign_status
        status = await manager.perform_check_in(campaign_id)
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "bids_received": status.bids_received,
            "bids_expected": status.bids_expected,
            "on_track": status.on_track,
            "escalation_needed": status.escalation_needed,
            "escalation_level": status.escalation_level.value if status.escalation_level else None,
            "additional_contractors_needed": status.additional_contractors_needed
        }
        
    except Exception as e:
        print(f"[CAMPAIGN CHECK-IN ERROR] {e}")
        raise HTTPException(500, f"Failed to check campaign status: {str(e)}")

@app.get("/api/campaigns/{campaign_id}/metrics")
async def get_campaign_metrics(campaign_id: str):
    """Get detailed campaign performance metrics"""
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Get campaign from database
        campaign = db.client.table('outreach_campaigns').select('*').eq('id', campaign_id).execute()
        
        if not campaign.data:
            raise HTTPException(404, "Campaign not found")
        
        # Get outreach attempts
        attempts = db.client.table('contractor_outreach_attempts').select('*').eq('campaign_id', campaign_id).execute()
        
        # Calculate metrics
        total_sent = len([a for a in attempts.data if a['status'] in ['sent', 'delivered', 'opened', 'clicked', 'responded']])
        total_opened = len([a for a in attempts.data if a['status'] in ['opened', 'clicked', 'responded']])
        total_responded = len([a for a in attempts.data if a['status'] == 'responded'])
        
        # Get check-ins
        check_ins = db.client.table('campaign_check_ins').select('*').eq('campaign_id', campaign_id).order('check_in_time', desc=False).execute()
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "status": campaign.data[0]['status'],
            "created_at": campaign.data[0]['created_at'],
            "metrics": {
                "total_contractors": len(attempts.data),
                "messages_sent": total_sent,
                "open_rate": (total_opened / total_sent * 100) if total_sent > 0 else 0,
                "response_rate": (total_responded / total_sent * 100) if total_sent > 0 else 0,
                "bids_received": total_responded
            },
            "check_ins": [
                {
                    "time": ci['check_in_time'],
                    "bids_at_time": ci['bids_received'],
                    "on_track": ci['on_track'],
                    "action_taken": ci['action_taken']
                }
                for ci in check_ins.data
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[CAMPAIGN METRICS ERROR] {e}")
        raise HTTPException(500, f"Failed to get campaign metrics: {str(e)}")

@app.post("/api/campaigns/{campaign_id}/escalate")
async def escalate_campaign(campaign_id: str, escalation_data: dict):
    """Manually escalate a campaign by adding more contractors"""
    try:
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Get campaign
        campaign = db.client.table('outreach_campaigns').select('*').eq('id', campaign_id).execute()
        
        if not campaign.data:
            raise HTTPException(404, "Campaign not found")
        
        # Add more contractors based on escalation level
        additional_contractors = escalation_data.get('additional_contractors', 5)
        tier_preference = escalation_data.get('tier_preference', 'tier2')
        
        # Get available contractors
        existing_attempts = db.client.table('contractor_outreach_attempts').select('contractor_lead_id').eq('campaign_id', campaign_id).execute()
        existing_ids = [a['contractor_lead_id'] for a in existing_attempts.data]
        
        # Find new contractors
        new_contractors = db.client.table('potential_contractors').select('*').not_.in_('id', existing_ids).limit(additional_contractors).execute()
        
        if new_contractors.data:
            # Create new outreach attempts
            new_attempts = []
            for contractor in new_contractors.data:
                for channel in ['email', 'website_form']:
                    new_attempts.append({
                        'contractor_lead_id': contractor['id'],
                        'bid_card_id': campaign.data[0]['bid_card_id'],
                        'campaign_id': campaign_id,
                        'channel': channel,
                        'status': 'queued',
                        'message_content': f"Escalation outreach to {contractor.get('business_name', 'Contractor')}",
                        'created_at': datetime.now().isoformat()
                    })
            
            db.client.table('contractor_outreach_attempts').insert(new_attempts).execute()
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "contractors_added": len(new_contractors.data),
                "new_total": len(existing_ids) + len(new_contractors.data)
            }
        else:
            return {
                "success": False,
                "error": "No additional contractors available"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[CAMPAIGN ESCALATE ERROR] {e}")
        raise HTTPException(500, f"Failed to escalate campaign: {str(e)}")

# Inspiration Board Endpoints
@app.get("/api/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    return {
        "supabase_url": os.getenv("SUPABASE_URL", "NOT_SET"),
        "service_key_exists": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY")),
        "service_key_first_20": os.getenv("SUPABASE_SERVICE_ROLE_KEY", "NOT_SET")[:20],
        "anthropic_key_exists": bool(os.getenv("ANTHROPIC_API_KEY")),
        "working_dir": os.getcwd(),
        "env_file_path": os.path.join(os.path.dirname(__file__), '..', '.env'),
        "env_file_exists": os.path.exists(os.path.join(os.path.dirname(__file__), '..', '.env'))
    }

@app.post("/api/inspiration/boards")
async def create_inspiration_board(board_data: dict):
    """Create inspiration board with service-level permissions for demo users"""
    try:
        from supabase import create_client
        
        # Use service role key for demo operations
        supabase_url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        print(f"[DEBUG] SUPABASE_URL: {supabase_url}")
        print(f"[DEBUG] SERVICE_KEY: {service_key[:20] if service_key else 'None'}...")
        print(f"[DEBUG] SERVICE_KEY equals placeholder: {service_key == 'your_supabase_service_key'}")
        print(f"[DEBUG] SERVICE_KEY is None: {service_key is None}")
        print(f"[DEBUG] SERVICE_KEY bool: {bool(service_key)}")
        
        # Check if we have the real service key from .env
        if not service_key or service_key == "your_supabase_service_key":
            print("[DEBUG] No service key found - using demo mode")
            # For development, we'll skip RLS by creating via raw SQL
            # This is a temporary workaround for demo functionality
            return {
                "id": f"demo_board_{datetime.now().timestamp()}",
                "title": board_data.get("title", "Demo Board"),
                "description": board_data.get("description"),
                "room_type": board_data.get("room_type"),
                "homeowner_id": board_data.get("homeowner_id"),
                "status": "collecting",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "image_count": 0
            }
        
        print("[DEBUG] Service key found - attempting real database call")
        
        supabase = create_client(supabase_url, service_key)
        
        # Handle homeowner_id - use valid UUID or default test user
        homeowner_id = board_data.get("homeowner_id")
        if not homeowner_id or homeowner_id.startswith("test-user-"):
            # For demo/test users, use the default test user
            homeowner_id = "4442e0a3-2fea-4f88-82d5-c8e77a531844"  # test@instabids.com
            print(f"[DEBUG] Using default test user UUID: {homeowner_id}")
        
        # Insert board using service role (bypasses RLS)
        print(f"[DEBUG] Inserting board with homeowner_id: {homeowner_id}")
        response = supabase.table("inspiration_boards").insert({
            "title": board_data.get("title"),
            "description": board_data.get("description"),
            "room_type": board_data.get("room_type"),
            "homeowner_id": homeowner_id,
            "status": board_data.get("status", "collecting")
        }).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(500, "Failed to create board")
            
    except Exception as e:
        import traceback
        print(f"[BOARD CREATION ERROR] {e}")
        print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
        # Fallback to demo response
        return {
            "id": f"demo_board_{datetime.now().timestamp()}",
            "title": board_data.get("title", "Demo Board"),
            "description": board_data.get("description"),
            "room_type": board_data.get("room_type"),
            "homeowner_id": board_data.get("homeowner_id"),
            "status": "collecting",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "image_count": 0
        }

# OLD Iris endpoint removed - using new iris_chat_router instead

@app.get("/api/iris/status")
async def get_iris_status():
    """Get Iris agent status"""
    return {
        "status": "active",
        "description": "Design Inspiration Assistant",
        "model": "Claude Opus 4 (claude-3-opus-20240229)",
        "capabilities": [
            "Analyze design styles",
            "Organize inspiration images",
            "Provide budget estimates",
            "Create vision summaries",
            "Guide to project creation"
        ]
    }

@app.post("/api/conversations/transfer")
async def transfer_conversation(data: dict):
    """Transfer anonymous conversation to authenticated user after signup"""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    
    if not session_id or not user_id:
        raise HTTPException(400, "session_id and user_id are required")
    
    try:
        success = await db.transfer_anonymous_conversation(session_id, user_id)
        if success:
            return {"success": True, "message": "Conversation transferred successfully"}
        else:
            return {"success": False, "message": "No conversations to transfer"}
    except Exception as e:
        print(f"[TRANSFER ERROR] {e}")
        raise HTTPException(500, f"Failed to transfer conversation: {str(e)}")

@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all AI agents"""
    return {
        "cia": {
            "status": "active" if cia_agent else "offline",
            "description": "Customer Interface Agent",
            "model": "Claude Opus 4 (claude-opus-4-20250514)"
        },
        "coia": {
            "status": "active" if coia_agent else "offline",
            "description": "Contractor Interface Agent",
            "model": "Claude Opus 4 (claude-opus-4-20250514)"
        },
        "jaa": {
            "status": "active" if jaa_agent else "offline",
            "description": "Intelligent Job Assessment Agent with LangGraph + Claude Opus 4",
            "model": "Claude Opus 4 + LangGraph Workflow"
        },
        "cda": {
            "status": "active" if cda_agent else "offline",
            "description": "Contractor Discovery Agent with Opus 4 Intelligence",
            "model": "Claude Opus 4 + 3-Tier Sourcing + Google Maps API"
        },
        "eaa": {
            "status": "active" if eaa_agent else "offline",
            "description": "External Acquisition Agent",
            "model": "Multi-Channel Outreach System"
        },
        "iris": {
            "status": "active",
            "description": "Design Inspiration Assistant",
            "model": "Claude Opus 4 (claude-3-opus-20240229)"
        }
    }

# WebSocket endpoint for OpenAI Realtime API proxy
@app.websocket("/ws/realtime")
async def websocket_realtime_proxy(websocket: WebSocket):
    """Proxy WebSocket connection to OpenAI Realtime API with authentication"""
    from routes.realtime_proxy import websocket_endpoint
    await websocket_endpoint(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)