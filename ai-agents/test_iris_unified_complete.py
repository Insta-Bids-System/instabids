"""
Test IRIS Unified Conversation System - Complete Integration
Tests all aspects of IRIS integration with unified memory system
"""

import asyncio
import logging
from datetime import datetime
import uuid
from config.service_urls import get_backend_url

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_iris_unified_system():
    """Test complete IRIS unified conversation system integration"""
    
    print("\n" + "="*80)
    print("IRIS UNIFIED CONVERSATION SYSTEM - COMPLETE TEST")
    print("="*80)
    
    # Test parameters
    test_user_id = "550e8400-e29b-41d4-a716-446655440001"  # Test UUID
    test_session_id = f"iris_test_{int(datetime.now().timestamp())}"
    test_project_id = str(uuid.uuid4())
    
    try:
        # Import API client
        import httpx
        base_url = get_backend_url()
        
        print("\n1. Testing IRIS conversation creation with project linking...")
        
        # First message - should create new conversation
        async with httpx.AsyncClient() as client:
            response1 = await client.post(
                f"{base_url}/api/iris/chat",
                json={
                    "message": "I want to redesign my living room with a modern farmhouse style",
                    "user_id": test_user_id,
                    "session_id": test_session_id,
                    "board_id": test_project_id,  # This should link to project
                    "room_type": "living_room"
                }
            )
        
        if response1.status_code == 200:
            data1 = response1.json()
            conversation_id = data1.get("conversation_id")
            print(f"✅ Created conversation: {conversation_id}")
            print(f"   Session ID: {data1.get('session_id')}")
            print(f"   Response: {data1.get('response')[:100]}...")
        else:
            print(f"❌ Failed to create conversation: {response1.text}")
            return
        
        print("\n2. Testing conversation persistence (same session)...")
        
        # Second message - should use same conversation
        async with httpx.AsyncClient() as client:
            response2 = await client.post(
                f"{base_url}/api/iris/chat",
                json={
                    "message": "I prefer neutral colors like beige and white",
                    "user_id": test_user_id,
                    "session_id": test_session_id,
                    "board_id": test_project_id,
                    "room_type": "living_room"
                }
            )
        
        if response2.status_code == 200:
            data2 = response2.json()
            conversation_id2 = data2.get("conversation_id")
            if conversation_id2 == conversation_id:
                print(f"✅ Same conversation maintained: {conversation_id2}")
            else:
                print(f"❌ Different conversation created: {conversation_id2}")
        else:
            print(f"❌ Failed second message: {response2.text}")
        
        print("\n3. Checking unified_conversation_memory for saved preferences...")
        
        # Check database directly
        from database import SupabaseDB
        db = SupabaseDB()
        
        # Check for design preferences
        memory_result = db.client.table("unified_conversation_memory").select("*").eq(
            "conversation_id", conversation_id
        ).eq("memory_type", "design_preferences").execute()
        
        if memory_result.data:
            print(f"✅ Design preferences saved: {len(memory_result.data)} entries")
            for mem in memory_result.data:
                preferences = mem.get("memory_value", {}).get("preferences", {})
                print(f"   - Saved: {list(preferences.keys())}")
        else:
            print("❌ No design preferences saved to unified memory")
        
        print("\n4. Testing inspiration board saving...")
        
        # Import the agent directly to test board saving
        from agents.iris.agent import iris_agent
        
        board_saved = await iris_agent.save_inspiration_board_to_memory(
            conversation_id=conversation_id,
            user_id=test_user_id,
            board_data={
                "name": "Modern Farmhouse Living Room",
                "room_type": "living_room",
                "style_preferences": {
                    "primary_style": "modern_farmhouse",
                    "colors": ["neutral", "beige", "white"],
                    "materials": ["wood", "natural fibers"]
                },
                "images": []
            }
        )
        
        if board_saved:
            print("✅ Inspiration board saved to unified memory")
            
            # Verify it's in the database
            board_result = db.client.table("unified_conversation_memory").select("*").eq(
                "conversation_id", conversation_id
            ).eq("memory_type", "inspiration_board").execute()
            
            if board_result.data:
                print(f"   Verified in database: {len(board_result.data)} board(s)")
        else:
            print("❌ Failed to save inspiration board")
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        # Final verification
        all_memory = db.client.table("unified_conversation_memory").select("*").eq(
            "conversation_id", conversation_id
        ).execute()
        
        print(f"\nTotal memory entries for conversation: {len(all_memory.data) if all_memory.data else 0}")
        if all_memory.data:
            memory_types = {}
            for mem in all_memory.data:
                mem_type = mem.get("memory_type")
                memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
            
            for mem_type, count in memory_types.items():
                print(f"  - {mem_type}: {count} entries")
        
        print("\n✅ IRIS Unified System Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_iris_unified_system())
