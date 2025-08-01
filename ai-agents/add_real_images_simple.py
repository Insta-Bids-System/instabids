"""
Add REAL test images to Supabase database for testing dream generation
"""
import os
import sys
from datetime import datetime
from uuid import uuid4
from database_simple import db

# Server base URL (update this when deployed)
BASE_URL = "http://localhost:8008"

# Test images data - focusing on kitchen for now
TEST_IMAGES = [
    {
        "filename": "kitchen-outdated-2.webp",
        "category": "current",
        "room_type": "kitchen",
        "description": "Compact functional kitchen with dated cabinets and appliances",
        "tags": ["kitchen", "current-state", "outdated", "needs-renovation"],
        "ai_analysis": {
            "style": "traditional",
            "condition": "outdated",
            "key_elements": ["white cabinets", "limited counter space", "basic appliances"],
            "renovation_potential": "high",
            "estimated_budget": "$15,000-$25,000"
        }
    },
    {
        "filename": "kitchen-modern-1.webp",
        "category": "ideal",
        "room_type": "kitchen",
        "description": "Modern dining area with exposed brick wall and pendant lighting",
        "tags": ["kitchen", "inspiration", "modern", "industrial"],
        "ai_analysis": {
            "style": "modern industrial",
            "condition": "excellent",
            "key_elements": ["exposed brick", "pendant lights", "open layout", "wood accents"],
            "design_features": ["industrial chic", "warm lighting", "mixed materials"],
            "estimated_cost": "$30,000-$45,000"
        }
    }
]

def add_test_images():
    """Add test images to the database"""
    print("Adding REAL test images to Supabase...")
    
    try:
        # Use the first kitchen board we find
        board_id = "50a2cc3b-a502-4294-b45c-9a644c4c56aa"  # From our earlier query
        print(f"Using board ID: {board_id}")
        
        # Add images
        added_images = []
        for idx, img_data in enumerate(TEST_IMAGES):
            # Build the image URL based on category
            if img_data['category'] == 'current':
                image_url = f"{BASE_URL}/test-images/current-state/{img_data['filename']}"
            else:
                image_url = f"{BASE_URL}/test-images/inspiration/{img_data['filename']}"
            
            image_record = {
                "board_id": board_id,
                "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",  # Demo user
                "image_url": image_url,
                "thumbnail_url": image_url,  # Same as full image for now
                "source": "url",
                "source_url": "https://www.pexels.com",
                "tags": img_data['tags'],
                "ai_analysis": img_data['ai_analysis'],
                "user_notes": img_data['description'],
                "liked_elements": [],
                "position": idx,
                "category": img_data['category']
            }
            
            result = db.client.table('inspiration_images').insert(image_record).execute()
            if result.data:
                added_images.append(result.data[0])
                print(f"[OK] Added {img_data['filename']} - ID: {result.data[0]['id']}")
            else:
                print(f"[ERROR] Failed to add {img_data['filename']}")
        
        print(f"\n[SUCCESS] Successfully added {len(added_images)} REAL images to board {board_id}")
        
        # Return the IDs for testing
        current_image_id = None
        inspiration_image_id = None
        
        for img in added_images:
            if img['category'] == 'current':
                current_image_id = img['id']
            elif img['category'] == 'ideal':
                inspiration_image_id = img['id']
        
        if current_image_id and inspiration_image_id:
            print("\n>>> Use these IDs for dream generation testing:")
            print(f"Current State Image ID: {current_image_id}")
            print(f"Inspiration Image ID: {inspiration_image_id}")
            print(f"\nTest API call:")
            print(f"POST http://localhost:8008/api/dream/generate")
            print(f"{{")
            print(f'  "current_image_id": "{current_image_id}",')
            print(f'  "ideal_image_id": "{inspiration_image_id}",')
            print(f'  "room_type": "kitchen",')
            print(f'  "preferences": {{')
            print(f'    "style": "modern industrial with warmth",')
            print(f'    "must_have": ["exposed brick accent", "pendant lighting", "more counter space"],')
            print(f'    "budget_range": "$20,000-$30,000"')
            print(f'  }}')
            print(f"}}")
            
            # Also test with the demo endpoint
            print(f"\n\nOr use the demo endpoint:")
            print(f"POST http://localhost:8008/api/dream/demo")
            print(f"{{")
            print(f'  "current_image_url": "{BASE_URL}/test-images/current-state/kitchen-outdated-2.webp",')
            print(f'  "ideal_image_url": "{BASE_URL}/test-images/inspiration/kitchen-modern-1.webp",')
            print(f'  "room_type": "kitchen",')
            print(f'  "preferences": {{')
            print(f'    "style": "modern industrial with warmth",')
            print(f'    "must_have": ["exposed brick accent", "pendant lighting", "more counter space"],')
            print(f'    "budget_range": "$20,000-$30,000"')
            print(f'  }}')
            print(f"}}")
        
        return board_id, current_image_id, inspiration_image_id
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    board_id, current_id, inspiration_id = add_test_images()