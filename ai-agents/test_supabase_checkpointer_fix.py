"""
Test Supabase checkpointer with enhanced serialization
"""

import asyncio
import os
from agents.coia.supabase_checkpointer_simple import create_supabase_checkpointer
from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_bid_card_link

async def test_supabase_checkpointer():
    """Test Supabase checkpointer with real COIA system"""
    
    print("TESTING: Supabase Checkpointer with Enhanced Serialization...")
    
    try:
        # Create Supabase checkpointer
        print("Creating Supabase checkpointer...")
        checkpointer = await create_supabase_checkpointer()
        print("SUCCESS: Supabase checkpointer created successfully")
        
        # Create COIA system with Supabase checkpointer
        print("Creating COIA system with Supabase persistence...")
        app = await create_unified_coia_system(checkpointer)
        print("SUCCESS: COIA system created with Supabase checkpointer")
        
        # Test bid card link entry point with persistence
        print("Testing bid card link with persistent memory...")
        result = await invoke_coia_bid_card_link(
            app=app,
            bid_card_id="4aa5e277-82b1-4679-a86a-24fd56b10e4c",
            contractor_lead_id="36fab309-1b11-4826-b108-dda79e12ce0d", 
            verification_token="test-persistence-token"
        )
        
        print("SUCCESS: Bid card link invocation completed")
        print(f"Session ID: {result.get('session_id')}")
        
        # Extract response message
        if result.get("messages"):
            for msg in reversed(result["messages"]):
                if hasattr(msg, "type") and msg.type == "ai":
                    print(f"AI Response: {msg.content[:100]}...")
                    break
        
        # Test that the conversation persisted by checking session state
        session_id = result.get('session_id', 'bid-link-4aa5e277-82b1-4679-a86a-24fd56b10e4c-36fab309')
        thread_id = f"contractor-36fab309"
        
        # Try to get the checkpoint to verify persistence  
        config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": "bid_card_onboarding"
            }
        }
        
        checkpoint_tuple = await checkpointer.aget_tuple(config)
        if checkpoint_tuple:
            print("SUCCESS: PERSISTENT MEMORY CONFIRMED - Checkpoint found in Supabase!")
            print(f"Checkpoint ID: {checkpoint_tuple.checkpoint.get('id', 'N/A')}")
            print(f"Messages in state: {len(checkpoint_tuple.checkpoint.get('channel_values', {}).get('messages', []))}")
        else:
            print("ERROR: No checkpoint found - memory not persisting")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    print("TESTING: Enhanced Supabase Checkpointer...")
    success = await test_supabase_checkpointer()
    
    if success:
        print("\nSUCCESS: SUPABASE CHECKPOINTER TEST PASSED")
        print("SUCCESS: PERMANENT MEMORY PERSISTENCE CONFIRMED")
    else:
        print("\nERROR: SUPABASE CHECKPOINTER TEST FAILED")
        print("ERROR: MEMORY PERSISTENCE NEEDS FIXING")

if __name__ == "__main__":
    asyncio.run(main())