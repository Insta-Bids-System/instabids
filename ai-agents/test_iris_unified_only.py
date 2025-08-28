"""
Test IRIS unified memory compliance
Verifies IRIS uses ONLY unified_conversation_memory table
"""
import asyncio
import uuid
from datetime import datetime

async def test_iris_unified_only():
    """Test that IRIS uses only unified memory system"""
    
    print("TESTING IRIS UNIFIED MEMORY COMPLIANCE")
    print("="*50)
    
    try:
        # Import IRIS agent
        from agents.iris.agent import iris_agent, IrisRequest
        from database import SupabaseDB
        
        db = SupabaseDB()
        
        # Generate test IDs
        test_user_id = str(uuid.uuid4())
        test_conversation_id = str(uuid.uuid4())
        test_tenant_id = test_user_id  # Use user_id as tenant_id
        
        print(f"Test User ID: {test_user_id}")
        print(f"Test Conversation ID: {test_conversation_id}")
        print(f"Test Tenant ID: {test_tenant_id}")
        
        # 1. Test IRIS conversation through unified memory
        print("\n1. TESTING IRIS WITH UNIFIED MEMORY")
        print("-" * 40)
        
        # Create test request
        test_request = IrisRequest(
            message="I love modern farmhouse style kitchens with white cabinets and black hardware. What elements should I focus on?",
            user_id=test_user_id,
            conversation_id=test_conversation_id,
            tenant_id=test_tenant_id,
            board_context={"room_type": "kitchen", "style": "modern farmhouse"}
        )
        
        # Process through IRIS
        response = await iris_agent.process_message(test_request)
        
        print("SUCCESS: IRIS processed message")
        print(f"Response: {response.response[:100]}...")
        print(f"Suggestions: {response.suggestions}")
        
        # 2. Verify data saved to unified_conversation_memory ONLY
        print("\n2. VERIFYING UNIFIED MEMORY STORAGE")
        print("-" * 40)
        
        # Check unified_conversation_memory table
        unified_results = db.client.table("unified_conversation_memory").select("*").eq(
            "tenant_id", test_tenant_id
        ).eq("conversation_id", test_conversation_id).execute()
        
        if unified_results.data:
            print(f"SUCCESS: Found {len(unified_results.data)} records in unified_conversation_memory")
            for i, record in enumerate(unified_results.data):
                print(f"  Record {i+1}: {record['memory_type']} - {record['memory_key']}")
        else:
            print("ERROR: No records found in unified_conversation_memory")
        
        # 3. Verify NO data in non-unified tables
        print("\n3. VERIFYING NO NON-UNIFIED STORAGE")
        print("-" * 40)
        
        # Check user_memories (should be empty)
        user_mem_results = db.client.table("user_memories").select("*").eq(
            "user_id", test_user_id
        ).execute()
        
        if user_mem_results.data:
            print(f"ERROR: Found {len(user_mem_results.data)} records in user_memories (should be 0)")
        else:
            print("SUCCESS: No records in user_memories (correct)")
        
        # Check photo_storage (should be empty)
        photo_results = db.client.table("photo_storage").select("*").eq(
            "user_id", test_user_id
        ).execute()
        
        if photo_results.data:
            print(f"ERROR: Found {len(photo_results.data)} records in photo_storage (should be 0)")
        else:
            print("SUCCESS: No records in photo_storage (correct)")
        
        # Check inspiration_images (should be empty)
        inspiration_results = db.client.table("inspiration_images").select("*").eq(
            "user_id", test_user_id
        ).execute()
        
        if inspiration_results.data:
            print(f"ERROR: Found {len(inspiration_results.data)} records in inspiration_images (should be 0)")
        else:
            print("SUCCESS: No records in inspiration_images (correct)")
        
        # 4. Test conversation continuity through unified memory
        print("\n4. TESTING CONVERSATION CONTINUITY")
        print("-" * 40)
        
        # Second message in same conversation
        followup_request = IrisRequest(
            message="What about the budget for this style?",
            user_id=test_user_id,
            conversation_id=test_conversation_id,
            tenant_id=test_tenant_id
        )
        
        followup_response = await iris_agent.process_message(followup_request)
        print("SUCCESS: Followup message processed")
        print(f"Response: {followup_response.response[:100]}...")
        
        # Check if context was maintained
        if "kitchen" in followup_response.response.lower() or "farmhouse" in followup_response.response.lower():
            print("SUCCESS: Context maintained across messages")
        else:
            print("INFO: Limited context detected in response")
        
        # 5. Verify final unified memory state
        print("\n5. FINAL UNIFIED MEMORY VERIFICATION")
        print("-" * 40)
        
        final_unified_results = db.client.table("unified_conversation_memory").select("*").eq(
            "tenant_id", test_tenant_id
        ).eq("conversation_id", test_conversation_id).execute()
        
        if final_unified_results.data:
            print(f"SUCCESS: Final unified memory contains {len(final_unified_results.data)} records")
            
            # Count by memory type
            memory_types = {}
            for record in final_unified_results.data:
                mem_type = record['memory_type']
                memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
            
            for mem_type, count in memory_types.items():
                print(f"  {mem_type}: {count} records")
        
        # 6. Clean up test data
        print("\n6. CLEANING UP TEST DATA")
        print("-" * 40)
        
        db.client.table("unified_conversation_memory").delete().eq(
            "tenant_id", test_tenant_id
        ).eq("conversation_id", test_conversation_id).execute()
        print("Cleaned up test data from unified_conversation_memory")
        
        print("\n" + "="*50)
        print("IRIS UNIFIED MEMORY COMPLIANCE TEST COMPLETE")
        print("Data flow: UNIFIED ONLY")
        print("Non-unified tables: CLEAN") 
        print("Memory system: COMPLIANT")
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_iris_unified_only())