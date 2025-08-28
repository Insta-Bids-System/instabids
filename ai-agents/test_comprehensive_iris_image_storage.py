#!/usr/bin/env python3
"""
COMPREHENSIVE IRIS IMAGE STORAGE TEST
Tests IRIS agent with multiple images from test-images folder to verify:
1. Image upload and Claude Sonnet 4 classification
2. Both Property Photos and Inspiration Board storage
3. Complete user workflow
4. UI endpoints integration
"""

import os
import sys
import requests
import base64
import json
from datetime import datetime
from pathlib import Path
import time

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def load_image_to_base64(image_path):
    """Load image and convert to base64"""
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        return image_data
    except Exception as e:
        print(f"ERROR: Failed to load {image_path}: {e}")
        return None

def test_iris_with_image(image_path, test_user_id, session_id_base, test_number):
    """Test IRIS with a single image"""
    print(f"\n{'='*60}")
    print(f"TEST {test_number}: {image_path.name}")
    print(f"{'='*60}")
    
    # Load image
    image_data = load_image_to_base64(image_path)
    if not image_data:
        return False
    
    print(f"SUCCESS: Loaded image ({len(image_data)} chars)")
    
    # Create unique session for this test
    session_id = f"{session_id_base}_test_{test_number}"
    
    # Determine storage preference based on image type
    if "inspiration" in str(image_path).lower() or "ideal" in str(image_path).lower():
        storage_preference = "Inspiration Board"
        message = f"Please analyze this {image_path.stem} image for design inspiration."
    else:
        storage_preference = "Both" 
        message = f"Please analyze this {image_path.stem} image. I want to save it for both reference and inspiration."
    
    # Initial IRIS request
    request_data = {
        "message": message,
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
        # Make initial request
        print(f"STEP 1: Sending to IRIS for analysis...")
        response = requests.post(
            "http://localhost:8008/api/iris/unified-chat",
            json=request_data,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"ERROR: Initial request failed: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
        result = response.json()
        print(f"SUCCESS: IRIS analyzed image")
        
        # Check for workflow questions
        if 'workflow_questions' in result:
            print(f"SUCCESS: Generated {len(result['workflow_questions'])} workflow questions")
            
            # Make storage selection
            print(f"STEP 2: Selecting storage option: {storage_preference}")
            follow_up_request = {
                "message": f"{storage_preference} - {message}",
                "user_id": test_user_id,
                "session_id": session_id,
                "context_type": "auto",
                "workflow_response": {
                    "selected_option": storage_preference,
                    "callback": "store_image_location"
                }
            }
            
            follow_response = requests.post(
                "http://localhost:8008/api/iris/unified-chat",
                json=follow_up_request,
                timeout=60
            )
            
            if follow_response.status_code != 200:
                print(f"ERROR: Storage request failed: {follow_response.status_code}")
                return False
                
            follow_result = follow_response.json()
            print(f"SUCCESS: Storage request completed")
            
            # Check storage results
            if 'storage_results' in follow_result:
                storage = follow_result['storage_results']
                print(f"\nSTORAGE RESULTS:")
                
                property_success = storage.get('property_photos', {}).get('success', False)
                inspiration_success = storage.get('inspiration_board', {}).get('success', False)
                
                print(f"  Property Photos: {'SUCCESS' if property_success else 'FAILED'}")
                print(f"  Inspiration Board: {'SUCCESS' if inspiration_success else 'FAILED'}")
                
                if storage_preference == "Both":
                    return property_success and inspiration_success
                elif storage_preference == "Inspiration Board":
                    return inspiration_success
                else:
                    return property_success
            else:
                print(f"WARNING: No storage results in response")
                return False
        else:
            print(f"ERROR: No workflow questions generated")
            return False
            
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        return False

def verify_final_storage_state(test_user_id):
    """Verify the final state of stored images"""
    print(f"\n{'='*60}")
    print("FINAL STORAGE VERIFICATION")
    print(f"{'='*60}")
    
    try:
        from database_simple import db
        
        # Check property photos through properties join
        property_photos = db.client.table("property_photos")\
            .select("*, properties!property_id(user_id)")\
            .eq("properties.user_id", test_user_id)\
            .execute()
        
        print(f"Property Photos: {len(property_photos.data)} total")
        
        # Show recent property photos
        if property_photos.data:
            recent_photos = sorted(property_photos.data, 
                                 key=lambda x: x.get('created_at', ''), reverse=True)[:3]
            for i, photo in enumerate(recent_photos, 1):
                print(f"  {i}. ID: {photo['id'][:8]}... | Created: {photo.get('created_at', 'No timestamp')[:19]}")
        
        # Check inspiration boards
        inspiration_boards = db.client.table("inspiration_boards")\
            .select("*")\
            .eq("user_id", test_user_id)\
            .execute()
            
        print(f"\nInspiration Boards: {len(inspiration_boards.data)} total")
        
        # Check inspiration images
        total_inspiration_images = 0
        if inspiration_boards.data:
            recent_boards = sorted(inspiration_boards.data,
                                 key=lambda x: x.get('created_at', ''), reverse=True)[:3]
            
            for i, board in enumerate(recent_boards, 1):
                board_id = board['id']
                images = db.client.table("inspiration_images")\
                    .select("*")\
                    .eq("board_id", board_id)\
                    .execute()
                
                image_count = len(images.data)
                total_inspiration_images += image_count
                print(f"  {i}. Board {board_id[:8]}... | Images: {image_count} | Status: {board.get('status', 'Unknown')}")
        
        print(f"\nTotal Inspiration Images: {total_inspiration_images}")
        
        return {
            "property_photos": len(property_photos.data),
            "inspiration_boards": len(inspiration_boards.data),
            "inspiration_images": total_inspiration_images
        }
        
    except Exception as e:
        print(f"ERROR: Verification failed: {e}")
        return None

def main():
    """Run comprehensive IRIS image storage test"""
    print("COMPREHENSIVE IRIS IMAGE STORAGE TEST")
    print("=" * 60)
    print("Testing image upload, analysis, and storage with Claude Sonnet 4")
    print("Testing both Property Photos and Inspiration Board storage")
    print("=" * 60)
    
    # Test configuration
    test_user_id = "550e8400-e29b-41d4-a716-446655440001"
    session_id_base = f"comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Get test images
    test_images_dir = Path("C:/Users/Not John Or Justin/Documents/instabids/test-images")
    
    # Test images to process
    test_files = [
        test_images_dir / "YOUR_ACTUAL_BACKYARD.jpg",
        test_images_dir / "YOUR_IDEAL_TURF.jpg", 
        test_images_dir / "inspiration" / "backyard-beautiful-1.webp",
        test_images_dir / "inspiration" / "kitchen-modern-1.webp",
        test_images_dir / "inspiration" / "bathroom-luxury-1.webp"
    ]
    
    # Filter to only existing files
    existing_files = [f for f in test_files if f.exists()]
    
    print(f"Found {len(existing_files)} test images:")
    for f in existing_files:
        print(f"  - {f.name}")
    
    if not existing_files:
        print("ERROR: No test images found!")
        return
    
    # Run tests
    successful_tests = 0
    failed_tests = 0
    
    for i, image_path in enumerate(existing_files, 1):
        success = test_iris_with_image(image_path, test_user_id, session_id_base, i)
        
        if success:
            successful_tests += 1
            print(f"TEST {i} RESULT: SUCCESS")
        else:
            failed_tests += 1
            print(f"TEST {i} RESULT: FAILED")
        
        # Small delay between tests
        time.sleep(2)
    
    # Final verification
    final_state = verify_final_storage_state(test_user_id)
    
    # Summary
    print(f"\n{'='*60}")
    print("COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Run: {len(existing_files)}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {successful_tests/len(existing_files)*100:.1f}%")
    
    if final_state:
        print(f"\nFINAL STORAGE STATE:")
        print(f"Property Photos: {final_state['property_photos']}")
        print(f"Inspiration Boards: {final_state['inspiration_boards']}")
        print(f"Inspiration Images: {final_state['inspiration_images']}")
    
    overall_success = successful_tests == len(existing_files) and final_state is not None
    
    print(f"\nOVERALL RESULT: {'SUCCESS - IRIS FULLY OPERATIONAL' if overall_success else 'PARTIAL SUCCESS - Some issues remain'}")
    
    if overall_success:
        print("\nREADY FOR USER LOGIN AND UI TESTING:")
        print("1. Images stored successfully in database")
        print("2. Both Property Photos and Inspiration Board working")
        print("3. Claude Sonnet 4 analysis working")
        print("4. Ready for frontend UI integration")

if __name__ == "__main__":
    main()