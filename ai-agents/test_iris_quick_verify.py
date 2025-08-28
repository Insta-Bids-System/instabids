#!/usr/bin/env python3
"""
QUICK IRIS VERIFICATION TEST
Quickly test 2 different image types to verify IRIS is fully operational
"""

import requests
import base64
import json
from datetime import datetime
from pathlib import Path
import sys

# Add project root to Python path  
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def load_and_test_image(image_path, storage_type, test_name):
    """Test single image with IRIS"""
    print(f"\n=== {test_name} ===")
    
    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return False
        
    # Load image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    print(f"SUCCESS: Loaded {image_path.name} ({len(image_data)} chars)")
    
    # Test configuration
    test_user_id = "550e8400-e29b-41d4-a716-446655440001"
    session_id = f"quick_test_{datetime.now().strftime('%H%M%S')}_{test_name.lower()}"
    
    # Initial request
    request_data = {
        "message": f"Analyze this {image_path.stem} image and help me store it properly.",
        "user_id": test_user_id,
        "session_id": session_id,
        "context_type": "auto",
        "images": [{
            "data": image_data,
            "filename": image_path.name,
            "size": len(image_data),
            "type": "image/jpeg" if image_path.suffix.lower() in ['.jpg', '.jpeg'] else "image/webp"
        }],
        "trigger_image_workflow": True
    }
    
    try:
        # Step 1: Initial analysis
        print("STEP 1: Sending to IRIS...")
        response = requests.post(
            "http://localhost:8008/api/iris/unified-chat",
            json=request_data,
            timeout=45
        )
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: IRIS responded with analysis")
            
            if 'workflow_questions' in result:
                print(f"SUCCESS: Generated {len(result['workflow_questions'])} workflow questions")
                
                # Step 2: Storage selection
                print(f"STEP 2: Selecting '{storage_type}' storage...")
                follow_up_request = {
                    "message": f"{storage_type}",
                    "user_id": test_user_id,
                    "session_id": session_id,
                    "context_type": "auto",
                    "workflow_response": {
                        "selected_option": storage_type,
                        "callback": "store_image_location"
                    }
                }
                
                follow_response = requests.post(
                    "http://localhost:8008/api/iris/unified-chat",
                    json=follow_up_request,
                    timeout=45
                )
                
                if follow_response.status_code == 200:
                    follow_result = follow_response.json()
                    print("SUCCESS: Storage completed")
                    
                    # Check results
                    if 'storage_results' in follow_result:
                        storage = follow_result['storage_results']
                        property_success = storage.get('property_photos', {}).get('success', False)
                        inspiration_success = storage.get('inspiration_board', {}).get('success', False)
                        
                        print(f"Property Photos: {'SUCCESS' if property_success else 'FAILED'}")
                        print(f"Inspiration Board: {'SUCCESS' if inspiration_success else 'FAILED'}")
                        
                        if storage_type == "Both":
                            return property_success and inspiration_success
                        elif storage_type == "Property Photos":
                            return property_success
                        elif storage_type == "Inspiration Board":
                            return inspiration_success
                        else:
                            return property_success or inspiration_success
                    else:
                        print("ERROR: No storage results")
                        return False
                else:
                    print(f"ERROR: Storage failed: {follow_response.status_code}")
                    return False
            else:
                print("ERROR: No workflow questions")
                return False
        else:
            print(f"ERROR: Initial request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def verify_database_state():
    """Quick database verification"""
    print(f"\n=== DATABASE VERIFICATION ===")
    
    try:
        from database_simple import db
        test_user_id = "550e8400-e29b-41d4-a716-446655440001"
        
        # Property photos
        property_photos = db.client.table("property_photos")\
            .select("*, properties!property_id(user_id)")\
            .eq("properties.user_id", test_user_id)\
            .execute()
        
        # Inspiration boards
        inspiration_boards = db.client.table("inspiration_boards")\
            .select("*")\
            .eq("user_id", test_user_id)\
            .execute()
        
        # Inspiration images
        total_images = 0
        for board in inspiration_boards.data or []:
            images = db.client.table("inspiration_images")\
                .select("*")\
                .eq("board_id", board['id'])\
                .execute()
            total_images += len(images.data or [])
        
        print(f"Property Photos: {len(property_photos.data or [])}")
        print(f"Inspiration Boards: {len(inspiration_boards.data or [])}")
        print(f"Inspiration Images: {total_images}")
        
        return len(property_photos.data or []) > 0 and len(inspiration_boards.data or []) > 0
        
    except Exception as e:
        print(f"ERROR: Database verification failed: {e}")
        return False

def main():
    print("QUICK IRIS VERIFICATION TEST")
    print("="*50)
    
    # Test images
    test_images_dir = Path("C:/Users/Not John Or Justin/Documents/instabids/test-images")
    
    tests = [
        (test_images_dir / "YOUR_ACTUAL_BACKYARD.jpg", "Property Photos", "Property Photo Test"),
        (test_images_dir / "inspiration" / "backyard-beautiful-1.webp", "Inspiration Board", "Inspiration Test")
    ]
    
    results = []
    for image_path, storage_type, test_name in tests:
        success = load_and_test_image(image_path, storage_type, test_name)
        results.append((test_name, success))
        print(f"RESULT: {test_name} - {'SUCCESS' if success else 'FAILED'}")
    
    # Database verification
    db_success = verify_database_state()
    
    # Summary
    print(f"\n=== FINAL SUMMARY ===")
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        print(f"{test_name}: {'SUCCESS' if success else 'FAILED'}")
    
    print(f"Database Verification: {'SUCCESS' if db_success else 'FAILED'}")
    print(f"Overall: {successful}/{total} tests passed")
    
    if successful == total and db_success:
        print("\nSUCCESS: IRIS FULLY OPERATIONAL!")
        print("- Image upload working")
        print("- Claude Sonnet 4 analysis working") 
        print("- Property Photos storage working")
        print("- Inspiration Board storage working")
        print("- Database integration working")
        print("- Ready for UI integration!")
    else:
        print("\nPARTIAL SUCCESS: Some issues remain")

if __name__ == "__main__":
    main()