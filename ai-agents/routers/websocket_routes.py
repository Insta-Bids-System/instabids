"""
WebSocket Routes - Real-time Communication Endpoints
Owner: Shared (Used by multiple agents)
"""

from fastapi import APIRouter, WebSocket


# Create router
router = APIRouter()

@router.websocket("/ws/realtime")
async def websocket_realtime_proxy(websocket: WebSocket):
    """Proxy WebSocket connection to OpenAI Realtime API with authentication"""
    from routes.realtime_proxy import websocket_endpoint
    await websocket_endpoint(websocket)
