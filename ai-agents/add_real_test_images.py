"""
Add REAL test images to Supabase database for testing dream generation
"""
import os
import sys
from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not service_key:
    print("ERROR: Missing Supabase credentials in .env file")
    sys.exit(1)

supabase = create_client(supabase_url, service_key)

# Server base URL (update this when deployed)
BASE_URL = "http://localhost:8008"

# Test images data
TEST_IMAGES = [
    {
        "filename": "kitchen-outdated-2.webp",
        "category": "current_state",
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
        "category": "inspiration",
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
    },
    {
        "filename": "bathroom-outdated-1.webp",
        "category": "current_state",
        "room_type": "bathroom",
        "description": "Basic bathroom with dated fixtures and tile",
        "tags": ["bathroom", "current-state", "outdated", "needs-update"],
        "ai_analysis": {
            "style": "builder-grade",
            "condition": "functional but dated",
            "key_elements": ["basic vanity", "standard fixtures", "older tile"],
            "renovation_potential": "high",
            "estimated_budget": "$8,000-$15,000"
        }
    },
    {
        "filename": "bathroom-modern-1.webp",
        "category": "inspiration",
        "room_type": "bathroom",
        "description": "Luxurious spa-like bathroom with modern fixtures",
        "tags": ["bathroom", "inspiration", "modern", "luxury"],
        "ai_analysis": {
            "style": "modern spa",
            "condition": "excellent",
            "key_elements": ["freestanding tub", "glass shower", "double vanity", "natural light"],
            "design_features": ["spa-inspired", "minimalist", "high-end fixtures"],
            "estimated_cost": "$20,000-$35,000"
        }
    }
]

def add_test_images():
    """Add test images to the database"""
    print("Adding REAL test images to Supabase...")
    
    # Get the most recent kitchen board
    board_result = supabase.table('inspiration_boards').select('id, title').eq('room_type', 'kitchen').order('created_at.desc').limit(1).execute()
    
    if not board_result.data:
        print("No kitchen boards found. Creating one...")
        # Create a test board
        board_data = {
            "id": str(uuid4()),
            "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",  # Demo user
            "title": "Test Kitchen with REAL Images",
            "description": "Testing dream generation with actual high-quality photos",
            "room_type": "kitchen",
            "status": "collecting"
        }
        board_result = supabase.table('inspiration_boards').insert(board_data).execute()
        board_id = board_result.data[0]['id']
    else:
        board_id = board_result.data[0]['id']
        print(f"Using existing board: {board_result.data[0]['title']}")
    
    # Add images
    added_images = []
    for idx, img_data in enumerate(TEST_IMAGES):
        # Only add kitchen images to the kitchen board
        if img_data['room_type'] != 'kitchen':
            continue
            
        image_url = f"{BASE_URL}/test-images/current-state/{img_data['filename']}" if img_data['category'] == 'current_state' else f"{BASE_URL}/test-images/inspiration/{img_data['filename']}"
        
        image_record = {
            "id": str(uuid4()),
            "board_id": board_id,
            "homeowner_id": "550e8400-e29b-41d4-a716-446655440001",
            "image_url": image_url,
            "thumbnail_url": image_url,  # Same as full image for now
            "source": "pexels",
            "source_url": "https://www.pexels.com",
            "tags": img_data['tags'],
            "ai_analysis": img_data['ai_analysis'],
            "user_notes": img_data['description'],
            "liked_elements": [],
            "position": idx,
            "category": img_data['category']
        }
        
        result = supabase.table('inspiration_images').insert(image_record).execute()
        if result.data:
            added_images.append(result.data[0])
            print(f"✅ Added {img_data['filename']} - ID: {result.data[0]['id']}")
        else:
            print(f"❌ Failed to add {img_data['filename']}")
    
    print(f"\n✅ Successfully added {len(added_images)} REAL images to board {board_id}")
    
    # Return the IDs for testing
    current_image_id = None
    inspiration_image_id = None
    
    for img in added_images:
        if img['category'] == 'current_state':
            current_image_id = img['id']
        elif img['category'] == 'inspiration':
            inspiration_image_id = img['id']
    
    if current_image_id and inspiration_image_id:
        print("\n🎯 Use these IDs for dream generation testing:")
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
    
    return board_id, current_image_id, inspiration_image_id

if __name__ == "__main__":
    board_id, current_id, inspiration_id = add_test_images()