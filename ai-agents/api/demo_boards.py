"""
Demo Inspiration Boards API - Simple hardcoded responses for testing
"""

from fastapi import APIRouter
from typing import List

router = APIRouter()

# Hardcoded demo boards to get the frontend working
demo_boards = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "title": "Backyard Transformation",
        "description": "Modern backyard renovation with artificial turf",
        "room_type": "backyard",
        "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
        "status": "collecting",
        "created_at": "2025-07-30T02:00:00.000Z",
        "updated_at": "2025-07-30T02:00:00.000Z",
        "image_count": 0
    },
    {
        "id": "44da2df2-c5f8-428b-a89f-a3f384834f66",
        "title": "Kitchen Inspiration",
        "description": "Modern farmhouse kitchen ideas",
        "room_type": "kitchen",
        "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
        "status": "organizing",
        "created_at": "2025-07-29T17:00:00.000Z",
        "updated_at": "2025-07-29T17:00:00.000Z",
        "image_count": 3
    }
]

@router.get("/api/demo/inspiration/boards")
async def get_demo_boards(homeowner_id: str):
    """
    Get demo inspiration boards for testing
    """
    return [board for board in demo_boards if board["homeowner_id"] == homeowner_id]

@router.post("/api/demo/inspiration/boards")
async def create_demo_board(board_data: dict):
    """
    Create a demo board (just returns success)
    """
    new_board = {
        "id": f"demo_board_{len(demo_boards) + 1}",
        "title": board_data.get("title", "New Board"),
        "description": board_data.get("description"),
        "room_type": board_data.get("room_type"),
        "homeowner_id": board_data.get("homeowner_id"),
        "status": "collecting",
        "created_at": "2025-07-30T02:00:00.000Z",
        "updated_at": "2025-07-30T02:00:00.000Z",
        "image_count": 0
    }
    demo_boards.append(new_board)
    return new_board