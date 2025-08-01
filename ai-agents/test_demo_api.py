#!/usr/bin/env python3
"""
Direct test of demo boards API to debug vision image issue
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.demo_boards import router
import asyncio

async def test_demo_api():
    """Test the demo API directly"""
    print("Testing demo boards API directly...")
    
    # Import the function
    from api.demo_boards import get_board_images
    
    # Test with the specific board ID
    board_id = "26cf972b-83e4-484c-98b6-a5d1a4affee3"
    print(f"Calling get_board_images with board_id: {board_id}")
    
    result = await get_board_images(board_id)
    
    print(f"Result: {len(result)} images returned")
    for i, img in enumerate(result):
        print(f"Image {i+1}: ID={img['id']}, Category={img.get('category', 'unknown')}, Tags={img.get('tags', [])}")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_demo_api())
    print(f"Total images returned: {len(result)}")