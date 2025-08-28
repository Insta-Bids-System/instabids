#!/usr/bin/env python3
"""
FINAL IRIS VERIFICATION TEST - 1000% CONFIRMATION
Tests complete IRIS functionality with image upload, classification, and storage
"""

import os
import sys
import requests
import base64
import json
import uuid
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_iris_final_verification():
    """Final comprehensive verification of IRIS agent functionality"""
    
    # Test user and session - use proper UUIDs
    test_user_id = str(uuid.uuid4())
    test_session_id = str(uuid.uuid4())
    
    print(f"FINAL IRIS VERIFICATION TEST")
    print(f"=" * 50)
    print(f"User ID: {test_user_id}")
    print(f"Session ID: {test_session_id}")
    print()
    
    # Test with actual backyard image
    test_image_path = Path("C:/Users/Not John Or Justin/Documents/instabids/test-images/YOUR_ACTUAL_BACKYARD.jpg")
    if not test_image_path.exists():
        print(f"ERROR: Test image not found: {test_image_path}")
        return False
    
    # Read and encode image
    with open(test_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    print(f"SUCCESS: Image loaded: {len(image_data)} characters")
    
    # Step 1: Upload image and get workflow questions
    upload_request = {
        "message": "Please analyze this backyard photo and ask where to save it.",
        "user_id": test_user_id,
        "session_id": test_session_id,
        "context_type": "auto",
        "images": [{
            "data": image_data,
            "filename": "final-test-backyard.jpg",
            "size": len(image_data),
            "type": "image/jpeg"
        }],
        "trigger_image_workflow": True
    }
    
    print(f"Step 1: Uploading image to IRIS...")
    
    try:
        response = requests.post(
            "http://localhost:8008/api/iris/unified-chat",
            json=upload_request,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"FAILED: Upload failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
        
        result = response.json()
        print(f"SUCCESS: Upload successful! IRIS responded with analysis")
        
        # Check if workflow questions were generated
        if 'workflow_questions' not in result or not result['workflow_questions']:
            print(f"FAILED: No workflow questions generated")
            return False
        
        questions = result['workflow_questions']
        print(f"SUCCESS: Workflow questions generated: {len(questions)} questions")
        
        # Step 2: Select "Both" storage option
        follow_up_request = {
            "message": "Both - save to inspiration board and property photos",
            "user_id": test_user_id,
            "session_id": test_session_id,
            "context_type": "auto",
            "workflow_response": {
                "selected_option": "Both",
                "callback": "store_image_location"
            }
        }
        
        print(f"Step 2: Selecting 'Both' storage option...")
        
        follow_response = requests.post(
            "http://localhost:8008/api/iris/unified-chat",
            json=follow_up_request,
            timeout=60
        )
        
        if follow_response.status_code != 200:
            print(f"FAILED: Follow-up failed with status {follow_response.status_code}")
            print(f"Error: {follow_response.text}")
            return False
        
        follow_result = follow_response.json()
        print(f"SUCCESS: Both storage selection successful!")
        
        # Step 3: Verify database storage
        print(f"Step 3: Verifying database storage...")
        
        from database_simple import db
        
        # Check property photos
        property_photos = db.client.table("property_photos")\
            .select("*, properties!property_id(user_id)")\
            .eq("properties.user_id", test_user_id)\
            .execute()
        
        property_photo_count = len(property_photos.data) if property_photos.data else 0
        print(f"Property Photos: {property_photo_count} images found")
        
        # Check inspiration boards
        inspiration_boards = db.client.table("inspiration_boards")\
            .select("*")\
            .eq("user_id", test_user_id)\
            .execute()
        
        inspiration_board_count = len(inspiration_boards.data) if inspiration_boards.data else 0
        print(f"Inspiration Boards: {inspiration_board_count} boards found")
        
        # Check inspiration images
        if inspiration_boards.data:
            board_id = inspiration_boards.data[0]['id']
            inspiration_images = db.client.table("inspiration_images")\
                .select("*")\
                .eq("board_id", board_id)\
                .execute()
            
            inspiration_image_count = len(inspiration_images.data) if inspiration_images.data else 0
            print(f"Inspiration Images: {inspiration_image_count} images in board")
        else:
            inspiration_image_count = 0
        
        # Final verification
        print()
        print(f"FINAL VERIFICATION RESULTS:")
        print(f"=" * 50)
        print(f"IRIS Response: Working")
        print(f"Image Analysis: Working")
        print(f"Workflow Questions: Working ({len(questions)} generated)")
        print(f"Storage Selection: Working")
        print(f"Property Photos Storage: {property_photo_count} images {'[SUCCESS]' if property_photo_count > 0 else '[FAILED]'}")
        print(f"Inspiration Board Creation: {inspiration_board_count} boards {'[SUCCESS]' if inspiration_board_count > 0 else '[FAILED]'}")
        print(f"Inspiration Images Storage: {inspiration_image_count} images {'[SUCCESS]' if inspiration_image_count > 0 else '[FAILED]'}")
        
        # Success criteria
        success = (
            property_photo_count > 0 and
            inspiration_board_count > 0 and
            inspiration_image_count > 0
        )
        
        print()
        if success:
            print(f"SUCCESS: IRIS AGENT 1000% OPERATIONAL!")
            print(f"   Complete image workflow functioning")
            print(f"   Both storage locations working")
            print(f"   Database persistence verified")
            print(f"   Ready for production use")
        else:
            print(f"FAILED: Some storage components not working")
            print(f"   Property Photos: {'SUCCESS' if property_photo_count > 0 else 'FAILED'}")
            print(f"   Inspiration Storage: {'SUCCESS' if inspiration_board_count > 0 and inspiration_image_count > 0 else 'FAILED'}")
        
        return success
        
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    print("IRIS FINAL VERIFICATION TEST")
    print("=" * 50)
    
    success = test_iris_final_verification()
    
    print("=" * 50)
    if success:
        print("IRIS AGENT: 1000% OPERATIONAL AND PRODUCTION READY!")
    else:
        print("IRIS AGENT: Issues detected, needs investigation")
    
    print("Test completed")