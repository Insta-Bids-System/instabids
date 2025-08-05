"""
Test WebSocket Routes - Minimal test endpoint
"""

from fastapi import APIRouter, WebSocket


# Create router
router = APIRouter()

@router.websocket("/ws/test")
async def test_websocket_endpoint(websocket: WebSocket):
    """Test WebSocket endpoint"""
    await websocket.accept()
    await websocket.send_json({"message": "Hello from test WebSocket"})

    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"echo": data})
    except Exception as e:
        print(f"WebSocket error: {e}")
