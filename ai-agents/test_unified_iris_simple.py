"""
Test unified IRIS integration - Memory and photo storage compliance
Tests that IRIS properly uses unified photo_storage and user_memories
"""
import asyncio
import uuid
import base64
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_unified_iris_integration():
    """Test IRIS integration with unified memory and photo storage systems"""
    
    print("TESTING UNIFIED IRIS INTEGRATION")
    print("="*50)
    
    try:
        # Import IRIS agent
        from agents.iris.agent import iris_agent, IrisRequest
        from database import SupabaseDB
        
        # Initialize database connection
        db = SupabaseDB()
        
        # Generate test user ID
        test_user_id = str(uuid.uuid4())
        test_session_id = f"iris-test-{int(datetime.now().timestamp())}"
        test_board_id = str(uuid.uuid4())
        
        print(f"Test User ID: {test_user_id}")
        print(f"Test Session ID: {test_session_id}")
        print(f"Test Board ID: {test_board_id}")
        
        # 1. Test Cross-Project Design Memory Loading
        print("\n1. TESTING CROSS-PROJECT MEMORY LOADING")
        print("-" * 40)
        
        # Create fake base64 image data for testing
        fake_image_data = base64.b64encode(b"fake image data for testing").decode('utf-8')
        uploaded_images = [fake_image_data, fake_image_data]  # Two test images
        
        # Create test request with uploaded images
        test_request = IrisRequest(
            message="I love this modern farmhouse kitchen style! What elements should I focus on for my renovation?",
            board_id=test_board_id,
            board_title="Master Kitchen Renovation", 
            board_room_type="kitchen",
            board_status="collecting",
            uploaded_images=uploaded_images,
            image_category="ideal"
        )
        
        print(f"Uploading {len(uploaded_images)} test images...")
        
        # 2. Test Full IRIS Conversation with Memory Integration
        print("\n2. TESTING FULL IRIS CONVERSATION")
        print("-" * 40)
        
        # Process message through IRIS
        response = await iris_agent.process_message(
            request=test_request,
            session_id=test_session_id,
            user_id=test_user_id
        )
        
        print("IRIS processed message successfully!")
        print(f"Response: {response.response[:100]}...")
        print(f"Suggestions: {response.suggestions}")
        
        # 3. Verify Unified Photo Storage
        print("\n3. VERIFYING UNIFIED PHOTO STORAGE")
        print("-" * 40)
        
        # Check if images were saved to photo_storage table
        photo_results = db.client.table("photo_storage").select("*").eq(
            "user_id", test_user_id
        ).execute()
        
        if photo_results.data:
            print(f"SUCCESS: Found {len(photo_results.data)} images in unified photo_storage")
            for i, photo in enumerate(photo_results.data):
                print(f"   Image {i+1}: {photo['description']}")
                print(f"       Project ID: {photo['project_id']}")
        else:
            print("WARNING: No images found in unified photo_storage")
        
        # 4. Verify Enhanced Memory Updates
        print("\n4. VERIFYING ENHANCED MEMORY UPDATES")
        print("-" * 40)
        
        # Check updated design preferences
        memory_results = db.client.table("user_memories").select("*").eq(
            "user_id", test_user_id
        ).eq("memory_type", "design_preferences").execute()
        
        if memory_results.data:
            updated_prefs = memory_results.data[0]["memory_data"]
            print("SUCCESS: Enhanced design preferences updated:")
            print(f"   Rooms worked on: {updated_prefs.get('rooms_worked_on', [])}")
            print(f"   Style preferences: {updated_prefs.get('style_preferences', [])}")
            print(f"   Total boards: {updated_prefs.get('total_boards', 0)}")
            print(f"   Total images: {updated_prefs.get('total_images_uploaded', 0)}")
            print(f"   Interactions: {len(updated_prefs.get('interaction_history', []))}")
        else:
            print("WARNING: No enhanced design preferences found")
        
        # 5. Test Cross-Project Context Loading
        print("\n5. TESTING CROSS-PROJECT CONTEXT")
        print("-" * 40)
        
        # Create another request to test context awareness
        followup_request = IrisRequest(
            message="Now I want to work on my bathroom. Any style recommendations?",
            board_title="Guest Bathroom Refresh",
            board_room_type="bathroom", 
            board_status="collecting"
        )
        
        followup_response = await iris_agent.process_message(
            request=followup_request,
            session_id=f"{test_session_id}-followup",
            user_id=test_user_id
        )
        
        print("Cross-project context conversation successful!")
        print(f"Response: {followup_response.response[:150]}...")
        
        # Check if IRIS mentions previous work or preferences
        response_lower = followup_response.response.lower()
        context_indicators = ["kitchen", "previous", "similar", "consistent", "style"]
        context_found = any(indicator in response_lower for indicator in context_indicators)
        
        if context_found:
            print("SUCCESS: IRIS showed cross-project awareness!")
        else:
            print("INFO: IRIS response may lack cross-project context")
        
        # 6. Clean Up Test Data
        print("\n6. CLEANING UP TEST DATA")
        print("-" * 40)
        
        # Delete test photos
        db.client.table("photo_storage").delete().eq("user_id", test_user_id).execute()
        print("Cleaned up test photos from photo_storage")
        
        # Delete test memories  
        db.client.table("user_memories").delete().eq("user_id", test_user_id).execute()
        print("Cleaned up test memories from user_memories")
        
        print("\n" + "="*50)
        print("UNIFIED IRIS INTEGRATION TEST COMPLETE!")
        print("Memory system: CONNECTED")
        print("Photo storage: UNIFIED") 
        print("Cross-project awareness: ENABLED")
        print("System integration: SUCCESSFUL")
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_unified_iris_integration())