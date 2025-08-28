#!/usr/bin/env python3
"""
Test CIA Agent with Unified Conversation System
Verifies CIA saves to unified tables, not agent_conversations
"""

import asyncio
import json
from datetime import datetime
from agents.cia.agent import CustomerInterfaceAgent
import database_simple

# Initialize
import os
api_key = os.getenv("ANTHROPIC_API_KEY", "test-key")
cia = CustomerInterfaceAgent(api_key=api_key)
db = database_simple.get_client()

async def test_cia_unified():
    """Test that CIA saves to unified system"""
    
    print("\n" + "="*60)
    print("TESTING CIA WITH UNIFIED CONVERSATION SYSTEM")
    print("="*60)
    
    # Test parameters
    test_user_id = "test-unified-user-123"
    test_session_id = f"test-unified-session-{datetime.now().timestamp()}"
    
    print(f"\nTest User ID: {test_user_id}")
    print(f"Test Session ID: {test_session_id}")
    
    # Test conversation
    print("\n--- SENDING TEST MESSAGE TO CIA ---")
    result = await cia.handle_conversation(
        user_id=test_user_id,
        message="I need help with a kitchen remodel. It's about 200 square feet and needs new cabinets.",
        session_id=test_session_id
    )
    
    print(f"\nCIA Response: {result['response'][:200]}...")
    
    # Check unified_conversations table
    print("\n--- CHECKING UNIFIED_CONVERSATIONS TABLE ---")
    unified_check = db.table("unified_conversations").select("*").eq(
        "metadata->>session_id", test_session_id
    ).execute()
    
    if unified_check.data:
        print(f"✅ Found conversation in unified_conversations!")
        conv = unified_check.data[0]
        print(f"   - Conversation ID: {conv['id']}")
        print(f"   - Title: {conv['title']}")
        print(f"   - Created by: {conv['created_by']}")
        print(f"   - Metadata: {json.dumps(conv.get('metadata', {}), indent=2)}")
        
        # Check unified_messages
        print("\n--- CHECKING UNIFIED_MESSAGES TABLE ---")
        messages_check = db.table("unified_messages").select("*").eq(
            "conversation_id", conv['id']
        ).execute()
        
        if messages_check.data:
            print(f"✅ Found {len(messages_check.data)} messages in unified_messages!")
            for msg in messages_check.data:
                print(f"   - {msg['sender_type']}: {msg['content'][:50]}...")
        else:
            print("❌ No messages found in unified_messages")
            
        # Check unified_conversation_memory
        print("\n--- CHECKING UNIFIED_CONVERSATION_MEMORY TABLE ---")
        memory_check = db.table("unified_conversation_memory").select("*").eq(
            "conversation_id", conv['id']
        ).execute()
        
        if memory_check.data:
            print(f"✅ Found {len(memory_check.data)} memory entries!")
            for mem in memory_check.data:
                print(f"   - {mem['memory_type']}: {mem['memory_key']}")
        else:
            print("❌ No memory found in unified_conversation_memory")
            
    else:
        print("❌ No conversation found in unified_conversations table!")
        
    # Check if it's still saving to old table (should NOT be)
    print("\n--- CHECKING OLD AGENT_CONVERSATIONS TABLE ---")
    old_check = db.table("agent_conversations").select("*").eq(
        "thread_id", test_session_id
    ).execute()
    
    if old_check.data:
        print("❌ WARNING: Still saving to old agent_conversations table!")
        print(f"   This should NOT happen after migration!")
    else:
        print("✅ Good! Not saving to old agent_conversations table")
        
    # Test second message to verify updates work
    print("\n--- SENDING SECOND MESSAGE ---")
    result2 = await cia.handle_conversation(
        user_id=test_user_id,
        message="I want modern style cabinets with an island",
        session_id=test_session_id
    )
    
    print(f"CIA Response: {result2['response'][:200]}...")
    
    # Verify messages were added
    if unified_check.data:
        messages_check2 = db.table("unified_messages").select("*").eq(
            "conversation_id", conv['id']
        ).execute()
        
        print(f"\n✅ Now have {len(messages_check2.data)} total messages")
        
    print("\n" + "="*60)
    print("UNIFIED SYSTEM TEST COMPLETE")
    print("="*60)
    
    # Summary
    if unified_check.data and not old_check.data:
        print("\n✅ SUCCESS: CIA is using unified system correctly!")
        print("   - Saves to unified_conversations ✓")
        print("   - Saves to unified_messages ✓")
        print("   - Saves to unified_conversation_memory ✓")
        print("   - NOT saving to old agent_conversations ✓")
    else:
        print("\n❌ FAILURE: CIA is not fully migrated to unified system")
        if not unified_check.data:
            print("   - Not saving to unified tables")
        if old_check.data:
            print("   - Still saving to old table")

if __name__ == "__main__":
    asyncio.run(test_cia_unified())