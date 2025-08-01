"""
Create a real test user with full access to test the complete Iris dream generation flow
"""
import os
import sys
from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv
from supabase import create_client
import bcrypt

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize Supabase client with service role
supabase_url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not service_key:
    print("ERROR: Missing Supabase credentials in .env file")
    sys.exit(1)

supabase = create_client(supabase_url, service_key)

def create_test_user():
    """Create a real test user for end-to-end testing"""
    
    # User credentials
    email = "iristest@instabids.com"
    password = "IrisTest2025!"
    
    print(f"Creating test user: {email}")
    
    try:
        # First check if user already exists
        existing = supabase.table('users').select('*').eq('email', email).execute()
        
        if existing.data:
            print(f"User {email} already exists")
            user_id = existing.data[0]['id']
        else:
            # Create new user
            user_id = str(uuid4())
            user_data = {
                "id": user_id,
                "email": email,
                "password_hash": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = supabase.table('users').insert(user_data).execute()
            if result.data:
                print(f"[OK] Created user with ID: {user_id}")
            else:
                print("[ERROR] Failed to create user")
                return None, None
        
        # Check/create homeowner record
        homeowner_result = supabase.table('homeowners').select('*').eq('user_id', user_id).execute()
        
        if homeowner_result.data:
            homeowner_id = homeowner_result.data[0]['id']
            print(f"[OK] Homeowner record exists: {homeowner_id}")
        else:
            # Create homeowner record
            homeowner_id = str(uuid4())
            homeowner_data = {
                "id": homeowner_id,
                "user_id": user_id,
                "first_name": "Iris",
                "last_name": "Tester",
                "email": email,
                "phone": "555-0123",
                "address": "123 Dream Lane",
                "city": "Vision City",
                "state": "CA",
                "zip": "90210",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            homeowner_result = supabase.table('homeowners').insert(homeowner_data).execute()
            if homeowner_result.data:
                print(f"[OK] Created homeowner with ID: {homeowner_id}")
            else:
                print("[ERROR] Failed to create homeowner")
                return None, None
        
        # Create an inspiration board with REAL images
        board_id = str(uuid4())
        board_data = {
            "id": board_id,
            "homeowner_id": homeowner_id,
            "title": "My Dream Kitchen Transformation",
            "description": "Transform my compact kitchen into a modern industrial space",
            "room_type": "kitchen",
            "status": "collecting",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        board_result = supabase.table('inspiration_boards').insert(board_data).execute()
        if board_result.data:
            print(f"[OK] Created inspiration board: {board_id}")
        else:
            print("[ERROR] Failed to create board")
            return email, password
        
        # Add REAL images to the board
        base_url = "http://localhost:8008"
        
        # Current state image
        current_image = {
            "id": str(uuid4()),
            "board_id": board_id,
            "homeowner_id": homeowner_id,
            "image_url": f"{base_url}/test-images/current-state/kitchen-outdated-2.webp",
            "thumbnail_url": f"{base_url}/test-images/current-state/kitchen-outdated-2.webp",
            "source": "upload",
            "tags": ["kitchen", "current", "compact", "needs-update"],
            "ai_analysis": {
                "description": "Compact kitchen with white cabinets and limited counter space",
                "style": "Traditional builder-grade",
                "condition": "Functional but dated",
                "key_elements": ["white cabinets", "limited counter", "basic appliances"],
                "renovation_potential": "High - great bones for transformation"
            },
            "user_notes": "My current kitchen - functional but needs modernization",
            "category": "current",
            "position": 0,
            "created_at": datetime.now().isoformat()
        }
        
        current_result = supabase.table('inspiration_images').insert(current_image).execute()
        if current_result.data:
            print(f"[OK] Added current state image: {current_result.data[0]['id']}")
        
        # Inspiration image
        inspiration_image = {
            "id": str(uuid4()),
            "board_id": board_id,
            "homeowner_id": homeowner_id,
            "image_url": f"{base_url}/test-images/inspiration/kitchen-modern-1.webp",
            "thumbnail_url": f"{base_url}/test-images/inspiration/kitchen-modern-1.webp",
            "source": "url",
            "tags": ["kitchen", "inspiration", "modern", "industrial"],
            "ai_analysis": {
                "description": "Modern industrial kitchen with exposed brick and pendant lighting",
                "style": "Modern Industrial",
                "key_features": ["exposed brick wall", "pendant lights", "open shelving"],
                "materials": ["brick", "wood", "metal accents"],
                "estimated_cost": "$30,000-$45,000"
            },
            "user_notes": "Love the exposed brick and industrial pendant lights!",
            "liked_elements": ["exposed brick", "pendant lighting", "warm wood tones"],
            "category": "ideal",
            "position": 1,
            "created_at": datetime.now().isoformat()
        }
        
        ideal_result = supabase.table('inspiration_images').insert(inspiration_image).execute()
        if ideal_result.data:
            print(f"[OK] Added inspiration image: {ideal_result.data[0]['id']}")
        
        print("\n" + "="*50)
        print("TEST USER CREATED SUCCESSFULLY!")
        print("="*50)
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"User ID: {user_id}")
        print(f"Homeowner ID: {homeowner_id}")
        print(f"Board ID: {board_id}")
        print("\nThis user has:")
        print("- A complete profile")
        print("- An inspiration board for kitchen renovation")
        print("- REAL current state image (compact dated kitchen)")
        print("- REAL inspiration image (modern industrial style)")
        print("\nLogin at: http://localhost:5173")
        print("="*50)
        
        return email, password
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    email, password = create_test_user()