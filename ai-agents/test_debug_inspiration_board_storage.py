#!/usr/bin/env python3
"""
DEBUG: Inspiration Board Storage Issue
Test to identify why inspiration board storage is failing despite service role authentication fix
"""

import os
import sys
import requests
import base64
import json
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_inspiration_board_storage_debug():
    """Debug inspiration board storage issue with detailed logging"""
    
    # Test user and session
    test_user_id = "550e8400-e29b-41d4-a716-446655440001"
    test_session_id = f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Load test image
    test_image_path = Path("C:/Users/Not John Or Justin/Documents/instabids/test-images/modern-backyard-1.jpg")
    if not test_image_path.exists():
        print(f"❌ Test image not found: {test_image_path}")
        return False
    
    # Read and encode image
    with open(test_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    print(f"✅ Test image loaded: {len(image_data)} characters")
    
    # Test request with debugging intent
    request_data = {
        "message": "Please analyze this backyard photo. I want to store this in my inspiration board for design ideas.",
        "user_id": test_user_id,
        "session_id": test_session_id,
        "context_type": "auto",
        "images": [{
            "data": image_data,
            "filename": "debug-modern-backyard.jpg",
            "size": len(image_data),
            "type": "image/jpeg"
        }],
        "trigger_image_workflow": True,
        "debug_inspiration_storage": True  # Special flag for debugging
    }
    
    print(f"\n🧪 DEBUGGING: Inspiration Board Storage")
    print(f"User ID: {test_user_id}")
    print(f"Session ID: {test_session_id}")
    print(f"Image size: {len(image_data)} chars")
    
    try:
        # Make request to IRIS unified chat
        response = requests.post(
            "http://localhost:8008/api/iris/unified-chat",
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ IRIS Response Status: 200")
            print(f"Response: {json.dumps(result, indent=2)[:500]}...")
            
            # Check if workflow questions were generated
            if 'workflow_questions' in result:
                questions = result['workflow_questions']
                print(f"✅ Workflow questions generated: {len(questions)} questions")
                
                # Now test selecting "inspiration board" option
                follow_up_request = {
                    "message": "Both - save to inspiration board and property photos",
                    "user_id": test_user_id,
                    "session_id": test_session_id,
                    "context_type": "auto",
                    "workflow_response": True,
                    "selected_option": "Both",  
                    "debug_inspiration_storage": True
                }
                
                print(f"\n🧪 TESTING: Selection Response (Both)")
                
                # Make follow-up request
                follow_response = requests.post(
                    "http://localhost:8008/api/iris/unified-chat",
                    json=follow_up_request,
                    timeout=60
                )
                
                if follow_response.status_code == 200:
                    follow_result = follow_response.json()
                    print(f"✅ Follow-up Response Status: 200")
                    print(f"Follow-up Response: {json.dumps(follow_result, indent=2)[:500]}...")
                    
                    # Check storage results
                    if 'storage_results' in follow_result:
                        storage = follow_result['storage_results']
                        print(f"\n📊 STORAGE RESULTS:")
                        print(f"Property Photos: {storage.get('property_photos', {}).get('success', 'Not attempted')}")
                        print(f"Inspiration Board: {storage.get('inspiration_board', {}).get('success', 'Not attempted')}")
                        
                        # Debug inspiration board specifically
                        if 'inspiration_board' in storage:
                            inspiration_result = storage['inspiration_board']
                            if not inspiration_result.get('success'):
                                print(f"❌ INSPIRATION BOARD FAILED:")
                                print(f"Error: {inspiration_result.get('error', 'Unknown error')}")
                                print(f"Details: {inspiration_result.get('details', 'No details')}")
                    
                    # Now verify what actually got stored
                    print(f"\n🔍 VERIFICATION: Checking database for stored images")
                    
                    # Use Supabase MCP to check what was actually saved
                    return verify_storage_results(test_user_id, test_session_id)
                    
                else:
                    print(f"❌ Follow-up request failed: {follow_response.status_code}")
                    print(f"Error: {follow_response.text}")
                    return False
            else:
                print(f"❌ No workflow questions in response")
                return False
        else:
            print(f"❌ IRIS request failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in debug test: {e}")
        return False

def verify_storage_results(user_id, session_id):
    """Verify what was actually stored in the database"""
    print(f"\n🔍 VERIFYING STORAGE RESULTS")
    
    try:
        # Check property photos
        from database_simple import db
        
        # Query property photos
        property_photos = db.client.table("property_photos").select("*").eq("user_id", user_id).execute()
        print(f"📷 Property photos found: {len(property_photos.data)}")
        
        if property_photos.data:
            latest_photo = property_photos.data[-1]
            print(f"   Latest photo ID: {latest_photo['id']}")
            print(f"   Image URL: {latest_photo.get('image_url', 'No URL')[:50]}...")
            print(f"   Created: {latest_photo.get('created_at', 'No timestamp')}")
        
        # Query inspiration boards  
        inspiration_boards = db.client.table("inspiration_boards").select("*").eq("user_id", user_id).execute()
        print(f"🎨 Inspiration boards found: {len(inspiration_boards.data)}")
        
        if inspiration_boards.data:
            latest_board = inspiration_boards.data[-1]
            print(f"   Latest board ID: {latest_board['id']}")
            print(f"   Board status: {latest_board.get('status', 'No status')}")
            print(f"   Created: {latest_board.get('created_at', 'No timestamp')}")
            
            # Check inspiration images
            board_id = latest_board['id']
            inspiration_images = db.client.table("inspiration_images").select("*").eq("inspiration_board_id", board_id).execute()
            print(f"🖼️  Images in board: {len(inspiration_images.data)}")
            
            if inspiration_images.data:
                for img in inspiration_images.data:
                    print(f"   Image ID: {img['id']}")
                    print(f"   Image URL: {img.get('image_url', 'No URL')[:50]}...")
            else:
                print(f"   ❌ No images found in inspiration board {board_id}")
        else:
            print(f"   ❌ No inspiration boards found for user {user_id}")
        
        # Summary
        property_count = len(property_photos.data)
        inspiration_count = len(inspiration_boards.data)
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"Property Photos: {property_count} (Expected: 1+)")
        print(f"Inspiration Boards: {inspiration_count} (Expected: 1+)")
        
        success = property_count > 0 and inspiration_count > 0
        print(f"Overall Success: {success}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error verifying storage: {e}")
        return False

if __name__ == "__main__":
    print("🧪 IRIS Inspiration Board Storage Debug Test")
    print("=" * 50)
    
    success = test_inspiration_board_storage_debug()
    
    print("=" * 50)
    if success:
        print("✅ INSPIRATION BOARD STORAGE: WORKING")
    else:
        print("❌ INSPIRATION BOARD STORAGE: STILL BROKEN")
    
    print("Debug test completed")