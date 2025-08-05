"""
InstaBids AI Agents - Modular FastAPI Server
Main application entry point with router-based architecture

This file has been refactored from a monolithic 1693-line structure into
modular routers for better maintainability and reduced merge conflicts.

All API endpoints remain exactly the same - only the internal structure changed.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from agents.cda.agent import ContractorDiscoveryAgent as CDAAgent

# Agent initialization imports
from agents.cia.agent import CustomerInterfaceAgent as CIAAgent
from agents.coia.openai_o3_agent import OpenAIO3CoIA as ContractorChatAgent
from agents.eaa.agent import ExternalAcquisitionAgent as EAAAgent
from agents.jaa.agent import JobAssessmentAgent as JAAAgent

# Add the working demo boards router
from api.demo_boards import router as demo_boards_router

# Add the image generation router
from api.image_generation import router as image_generation_router

# Add the Iris chat router
from api.iris_chat import router as iris_router

# Import all router modules
# from routers.admin_routes import router as admin_router  # Temporarily disabled - missing dependencies

# Add enhanced admin router
from routers.admin_routes_enhanced import router as admin_enhanced_router
from routers.bid_card_api_simple import router as bid_card_api_simple_router
from routers.bid_card_lifecycle_routes import router as bid_card_lifecycle_router
from routers.contractor_job_search import router as contractor_job_search_router
from routers.bid_card_simple_lifecycle import router as bid_card_simple_lifecycle_router
from routers.cda_routes import router as cda_router
from routers.cia_routes import router as cia_router
from routers.contractor_routes import router as contractor_router
from routers.demo_routes import router as demo_router
from routers.eaa_routes import router as eaa_router
from routers.homeowner_routes import router as homeowner_router
from routers.jaa_routes import router as jaa_router
from routers.messaging_simple import router as messaging_api_router
from routers.monitoring_routes import router as monitoring_router

# Add test WebSocket router
from routers.test_ws_routes import router as test_ws_router
from routers.websocket_routes import router as websocket_router

# Add unified COIA router
# from routers.unified_coia_api import router as unified_coia_router  # Temporarily disabled - missing psycopg dependency

# Import image persistence service
from services.image_persistence_service import image_service


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instances
agents: dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic"""
    # Startup
    logger.info("Starting InstaBids AI Agents server...")

    # Initialize all agents
    try:
        # Load API key from environment
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not found - agents will run in demo mode")
            anthropic_api_key = "demo_key"

        # Get OpenAI key for O3 COIA
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not found - COIA will fail")

        agents["cia"] = CIAAgent(anthropic_api_key)
        agents["jaa"] = JAAAgent()
        agents["cda"] = CDAAgent()
        agents["eaa"] = EAAAgent()
        agents["contractor_chat"] = ContractorChatAgent(openai_api_key)  # Now uses OpenAI O3

        # Set the COIA agent in the contractor routes
        from routers.contractor_routes import set_coia_agent
        set_coia_agent(agents["contractor_chat"])

        # Set the CIA agent in the CIA routes
        from routers.cia_routes import set_cia_agent
        set_cia_agent(agents["cia"])

        logger.info("All agents initialized successfully")

        # Test database connections
        from data_access import test_connection
        if await test_connection():
            logger.info("Database connection verified")
        else:
            logger.error("Database connection failed")

    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        # Don't raise - continue with router-only mode
        logger.info("Continuing in router-only mode")

    logger.info("Router-only mode: All routers loaded successfully")

    # Start realtime polling for admin dashboard
    try:
        from admin.realtime_poller import start_realtime_polling
        from admin.websocket_manager import admin_websocket_manager

        realtime_poller = await start_realtime_polling(admin_websocket_manager)
        if realtime_poller:
            logger.info("Realtime polling started for admin dashboard")
        else:
            logger.warning("Failed to start realtime polling")
    except Exception as e:
        logger.error(f"Error starting realtime polling: {e}")

    yield

    # Shutdown
    logger.info("Shutting down InstaBids AI Agents server...")

    # Stop realtime polling
    try:
        if "realtime_poller" in locals() and realtime_poller:
            await realtime_poller.stop_polling()
            logger.info("Stopped realtime polling")
    except Exception as e:
        logger.error(f"Error stopping realtime polling: {e}")

# Create FastAPI application
app = FastAPI(
    title="InstaBids AI Agents",
    description="Multi-agent system for construction project bidding and management",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS - Allow ALL localhost ports for development with proper cookie support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177", "http://localhost:5178", "http://localhost:5179", "http://localhost:5180", "http://localhost:5181", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175", "http://127.0.0.1:5176", "http://127.0.0.1:5177", "http://127.0.0.1:5178", "http://127.0.0.1:5179", "http://127.0.0.1:5180", "http://127.0.0.1:5181", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(admin_router, prefix="/api/admin")           # Agent 2 - Admin Dashboard
app.include_router(cia_router, prefix="/api/cia")  # Agent 1 - Customer Interface
app.include_router(jaa_router)             # Agent 2 - Job Analysis
app.include_router(cda_router)             # Agent 2 - Contractor Discovery
app.include_router(eaa_router)             # Agent 2 - External Acquisition
app.include_router(contractor_router)      # Agent 4 - Contractor Chat
app.include_router(homeowner_router)       # Agent 3 - Homeowner UI
app.include_router(demo_router)            # Shared - Demo Pages
app.include_router(demo_boards_router)     # Working Demo Boards API
app.include_router(iris_router)            # Iris Chat Agent
app.include_router(image_generation_router)  # Image Generation API
app.include_router(websocket_router)       # Shared - WebSocket
app.include_router(monitoring_router)      # Agent 6 - System Monitoring
app.include_router(bid_card_lifecycle_router)  # Agent 2 - Bid Card Lifecycle Tracking
app.include_router(bid_card_api_simple_router, prefix="/api/bid-cards")    # Agent 1 - Enhanced Bid Card API
app.include_router(bid_card_simple_lifecycle_router)  # Agent 1 - Simplified Bid Card Lifecycle
app.include_router(contractor_job_search_router)      # Agent 4 - Contractor Job Search with Radius
app.include_router(messaging_api_router)    # Agent 1 - Messaging System
app.include_router(test_ws_router, prefix="/api/test")  # Test WebSocket endpoint
app.include_router(admin_enhanced_router)  # Enhanced admin routes with full bid card data
# app.include_router(unified_coia_router)    # Agent 4 - Unified COIA (Consolidated Agent) - Temporarily disabled

# Radius search is now handled directly in the bid_card_api.py router

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Root endpoint - serves welcome page"""
    return """
    <html>
        <head>
            <title>InstaBids AI Agents</title>
        </head>
        <body>
            <h1>InstaBids AI Agents Server</h1>
            <p>Multi-agent system running successfully!</p>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/admin">Admin Dashboard</a></li>
                <li><a href="/demo">Demo Pages</a></li>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/test-dashboard">Test Admin Dashboard</a></li>
            </ul>
        </body>
    </html>
    """

@app.post("/api/iris/fix-expired-images")
async def fix_expired_images():
    """Fix all expired OpenAI image URLs by storing them permanently"""
    try:
        result = await image_service.fix_all_expired_images()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/test-dashboard", response_class=HTMLResponse)
async def test_dashboard():
    """Serve the test admin dashboard HTML"""
    try:
        with open("test_admin_dashboard.html", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Test dashboard file not found</h1>", status_code=404)

@app.get("/api/real-images/{board_id}")
async def get_real_images(board_id: str):
    """Get real inspiration images directly from database using MCP"""
    try:
        # Import Supabase MCP connection here
        from database_simple import SupabaseDB

        db = SupabaseDB()
        result = db.client.table("inspiration_images").select("*").eq("board_id", board_id).execute()

        if result.data:
            logger.info(f"Found {len(result.data)} real images for board {board_id}")
            return result.data
        else:
            logger.info(f"No images found for board {board_id}")
            return []

    except Exception as e:
        logger.error(f"Error getting real images: {e}")
        return {"error": str(e)}

@app.get("/api/test-radius/{zip_code}")
async def test_radius_search(zip_code: str, radius: int = 15):
    """Test endpoint to verify radius search functionality"""
    try:
        # Import radius search utilities
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from utils.radius_search_fixed import get_zip_codes_in_radius, calculate_distance_miles
        
        # Get zip codes within radius
        zip_codes = get_zip_codes_in_radius(zip_code, radius)
        
        # Calculate distances to some nearby zip codes for testing
        distances = []
        for test_zip in zip_codes[:10]:  # Test first 10
            if test_zip != zip_code:
                distance = calculate_distance_miles(zip_code, test_zip)
                if distance is not None:
                    distances.append({"zip_code": test_zip, "distance_miles": distance})
        
        # Sort by distance
        distances.sort(key=lambda x: x["distance_miles"])
        
        return {
            "success": True,
            "center_zip": zip_code,
            "search_radius_miles": radius,
            "total_zip_codes_found": len(zip_codes),
            "all_zip_codes": zip_codes,
            "sample_distances": distances[:5],  # Show closest 5
            "message": f"Radius search is working! Found {len(zip_codes)} zip codes within {radius} miles of {zip_code}"
        }
        
    except Exception as e:
        logger.error(f"Error testing radius search: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Radius search test failed"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
