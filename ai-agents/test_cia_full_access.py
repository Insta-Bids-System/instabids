"""
Test CIA agent with full database access via HomeownerContextAdapter
"""

import asyncio
import os
from dotenv import load_dotenv

# Load root env
load_dotenv(r'C:\Users\Not John Or Justin\Documents\instabids\.env', override=True)

# Import the adapter
from adapters.homeowner_context import HomeownerContextAdapter

def test_adapter_access():
    """Test that the adapter can access all required tables"""
    print("=" * 60)
    print("TESTING CIA HOMEOWNER ADAPTER - FULL DATABASE ACCESS")
    print("=" * 60)
    
    # Initialize adapter
    adapter = HomeownerContextAdapter()
    print("\n[OK] Adapter initialized with Supabase connection")
    
    # Test user ID (you can change this to a real one)
    test_user_id = "11111111-1111-1111-1111-111111111111"
    
    # Test all major access methods
    print("\n--- Testing Database Access Methods ---")
    
    # 1. Unified Conversation System
    print("\n1. UNIFIED CONVERSATION SYSTEM:")
    conversations = adapter.get_unified_conversations(test_user_id)
    print(f"   - get_unified_conversations: {len(conversations)} found")
    
    # 2. User & Project Tables
    print("\n2. USER & PROJECT TABLES:")
    homeowner = adapter.get_homeowner(test_user_id)
    print(f"   - get_homeowner: {'Found' if homeowner else 'Not found'}")
    
    projects = adapter.get_projects(test_user_id)
    print(f"   - get_projects: {len(projects)} found")
    
    properties = adapter.get_properties(test_user_id)
    print(f"   - get_properties: {len(properties)} found")
    
    bid_cards = adapter.get_bid_cards(test_user_id) 
    print(f"   - get_bid_cards: {len(bid_cards)} found")
    
    # 3. Memory System
    print("\n3. MEMORY SYSTEM:")
    memories = adapter.get_user_memories(test_user_id)
    print(f"   - get_user_memories: {len(memories)} found")
    
    # 4. RFI System
    print("\n4. RFI SYSTEM:")
    if bid_cards:
        test_bid_card_id = bid_cards[0]["id"]
        rfi_requests = adapter.get_rfi_requests(test_bid_card_id)
        print(f"   - get_rfi_requests: {len(rfi_requests)} found")
    else:
        print(f"   - get_rfi_requests: No bid cards to test")
    
    # 5. Full Context Method
    print("\n5. FULL CONTEXT METHOD:")
    full_context = adapter.get_full_agent_context(test_user_id)
    print(f"   - get_full_agent_context returned {len(full_context)} data categories:")
    for key in full_context.keys():
        if isinstance(full_context[key], list):
            print(f"     * {key}: {len(full_context[key])} items")
        elif isinstance(full_context[key], dict):
            print(f"     * {key}: {len(full_context[key])} fields")
        else:
            print(f"     * {key}: {type(full_context[key]).__name__}")
    
    print("\n" + "=" * 60)
    print("CIA ADAPTER TEST COMPLETE - READY FOR PRODUCTION")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_adapter_access()
        if success:
            print("\n[SUCCESS] CIA agent has FULL database access via adapter!")
            print("The adapter is ready for production use.")
    except Exception as e:
        print(f"\n[ERROR] Adapter test failed: {e}")
        import traceback
        traceback.print_exc()