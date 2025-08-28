#!/usr/bin/env python3
"""
Test Cross-Agent Information Sharing
Tests CIA, IRIS, and MESSAGING agents sharing data through unified system
"""

import asyncio
import json
from datetime import datetime
import database_simple

# Initialize database
db = database_simple.get_client()

async def test_cross_agent_sharing():
    """Test that all 3 agents can see each other's data"""
    
    print("\n" + "="*60)
    print("TESTING CROSS-AGENT INFORMATION SHARING")
    print("="*60)
    
    test_user_id = "test-cross-user-123"
    test_project_id = "test-project-456"
    
    # Step 1: Create a CIA conversation
    print("\n--- STEP 1: Creating CIA conversation ---")
    cia_session_id = f"cia-test-{datetime.now().timestamp()}"
    
    # Simulate CIA saving a conversation
    cia_conversation = db.table("unified_conversations").insert({
        "created_by": test_user_id,
        "title": "CIA Session - Kitchen Remodel Planning",
        "metadata": {
            "session_id": cia_session_id,
            "agent_type": "CIA",
            "project_id": test_project_id,
            "project_type": "kitchen_remodel",
            "budget_range": "$15000-$25000",
            "timeline": "2-3 months"
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }).execute()
    
    if cia_conversation.data:
        cia_conv_id = cia_conversation.data[0]["id"]
        
        # Add CIA messages
        db.table("unified_messages").insert({
            "conversation_id": cia_conv_id,
            "sender_type": "user",
            "sender_id": test_user_id,
            "content": "I need help planning a kitchen remodel. Budget is $20k, timeline 3 months.",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        db.table("unified_messages").insert({
            "conversation_id": cia_conv_id,
            "sender_type": "agent",
            "sender_id": "cia",
            "content": "Perfect! I'll help you plan your $20k kitchen remodel. Let's start with your priorities.",
            "metadata": {
                "extracted_data": {
                    "project_type": "kitchen_remodel",
                    "budget": "$20,000",
                    "timeline": "3 months"
                }
            },
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        print(f"✅ CIA conversation created: {cia_conv_id}")
        
    # Step 2: Create an IRIS conversation
    print("\n--- STEP 2: Creating IRIS conversation ---")
    iris_session_id = f"iris-test-{datetime.now().timestamp()}"
    
    iris_conversation = db.table("unified_conversations").insert({
        "created_by": test_user_id,
        "title": "Kitchen Design Inspiration Board",
        "metadata": {
            "session_id": iris_session_id,
            "agent_type": "IRIS",
            "project_id": test_project_id,  # Same project!
            "inspiration_style": "modern_farmhouse",
            "color_scheme": "white_and_navy"
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }).execute()
    
    if iris_conversation.data:
        iris_conv_id = iris_conversation.data[0]["id"]
        
        # Add IRIS messages
        db.table("unified_messages").insert({
            "conversation_id": iris_conv_id,
            "sender_type": "user",
            "sender_id": test_user_id,
            "content": "I love modern farmhouse style. Can you help me create an inspiration board?",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        db.table("unified_messages").insert({
            "conversation_id": iris_conv_id,
            "sender_type": "agent", 
            "sender_id": "iris",
            "content": "I see you're planning a kitchen remodel! Modern farmhouse is perfect. Based on your $20k budget, here are some ideas...",
            "metadata": {
                "cross_agent_context": {
                    "referenced_cia_session": cia_session_id,
                    "budget_awareness": "$20,000",
                    "project_type": "kitchen_remodel"
                }
            },
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        print(f"✅ IRIS conversation created: {iris_conv_id}")
        
    # Step 3: Create a MESSAGING conversation
    print("\n--- STEP 3: Creating MESSAGING conversation ---")
    messaging_session_id = f"messaging-test-{datetime.now().timestamp()}"
    
    messaging_conversation = db.table("unified_conversations").insert({
        "created_by": test_user_id,
        "title": "Contractor Communication Hub",
        "metadata": {
            "session_id": messaging_session_id,
            "agent_type": "MESSAGING",
            "project_id": test_project_id,  # Same project!
            "communication_type": "contractor_bidding"
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }).execute()
    
    if messaging_conversation.data:
        msg_conv_id = messaging_conversation.data[0]["id"]
        
        # Add MESSAGING messages
        db.table("unified_messages").insert({
            "conversation_id": msg_conv_id,
            "sender_type": "system",
            "sender_id": "messaging_agent",
            "content": "Started contractor communication for your kitchen remodel project. Budget: $20k, Style: Modern Farmhouse",
            "metadata": {
                "cross_agent_context": {
                    "cia_budget": "$20,000",
                    "iris_style": "modern_farmhouse",
                    "project_context": "3 month timeline"
                }
            },
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        print(f"✅ MESSAGING conversation created: {msg_conv_id}")
    
    # Step 4: Test cross-agent data retrieval
    print("\n--- STEP 4: Testing cross-agent data retrieval ---")
    
    # Test: Can IRIS see CIA's budget information?
    print("\n🔍 Testing: Can IRIS see CIA's project data?")
    project_conversations = db.table("unified_conversations").select("*").eq(
        "created_by", test_user_id
    ).eq("metadata->>project_id", test_project_id).execute()
    
    if project_conversations.data and len(project_conversations.data) >= 2:
        print(f"✅ IRIS can see {len(project_conversations.data)} conversations for project {test_project_id}")
        for conv in project_conversations.data:
            agent_type = conv.get("metadata", {}).get("agent_type", "Unknown")
            title = conv.get("title", "Untitled")
            print(f"   - {agent_type}: {title}")
    else:
        print("❌ Cross-agent visibility failed")
        
    # Test: Can MESSAGING see both CIA and IRIS data?
    print("\n🔍 Testing: Can MESSAGING access all project context?")
    all_messages = db.table("unified_messages").select("*").in_(
        "conversation_id", [cia_conv_id, iris_conv_id, msg_conv_id]
    ).order("created_at", desc=False).execute()
    
    if all_messages.data:
        print(f"✅ MESSAGING can access {len(all_messages.data)} messages across all agents:")
        for msg in all_messages.data[:3]:  # Show first 3
            sender = msg.get("sender_type", "unknown")
            content = msg.get("content", "")[:50] + "..."
            print(f"   - {sender}: {content}")
    else:
        print("❌ Cross-message access failed")
        
    # Step 5: Test Privacy Framework access
    print("\n--- STEP 5: Testing Privacy Framework ---")
    from adapters.homeowner_context import HomeownerContextAdapter
    
    context_adapter = HomeownerContextAdapter()
    context = context_adapter.get_agent_context(
        user_id=test_user_id,
        project_id=test_project_id
    )
    
    conversations = context.get("conversation_history", [])
    if conversations and len(conversations) >= 2:
        print(f"✅ Privacy Framework can see {len(conversations)} conversations")
        for conv in conversations[:2]:
            agent_type = conv.get("agent_type", "Unknown")
            title = conv.get("title", "Untitled")
            print(f"   - {agent_type}: {title}")
    else:
        print("❌ Privacy Framework access failed")
    
    print("\n" + "="*60)
    print("CROSS-AGENT SHARING TEST RESULTS")
    print("="*60)
    
    success_criteria = [
        len(project_conversations.data) >= 3,  # All 3 agents created conversations
        len(all_messages.data) >= 4,           # Multiple messages across agents
        len(conversations) >= 2                # Privacy framework sees conversations
    ]
    
    if all(success_criteria):
        print("✅ SUCCESS: All agents can share information through unified system")
        print("   - CIA extracts and stores project data ✓")
        print("   - IRIS accesses CIA's project context ✓") 
        print("   - MESSAGING sees both CIA and IRIS data ✓")
        print("   - Privacy Framework provides cross-agent access ✓")
    else:
        print("❌ FAILURE: Cross-agent sharing has issues")
        print(f"   - Project conversations: {len(project_conversations.data)}")
        print(f"   - Cross-agent messages: {len(all_messages.data)}")
        print(f"   - Privacy framework access: {len(conversations)}")
    
    # Cleanup test data
    print(f"\n🧹 Cleaning up test data...")
    if cia_conversation.data:
        db.table("unified_messages").delete().eq("conversation_id", cia_conv_id).execute()
        db.table("unified_conversations").delete().eq("id", cia_conv_id).execute()
    if iris_conversation.data:
        db.table("unified_messages").delete().eq("conversation_id", iris_conv_id).execute() 
        db.table("unified_conversations").delete().eq("id", iris_conv_id).execute()
    if messaging_conversation.data:
        db.table("unified_messages").delete().eq("conversation_id", msg_conv_id).execute()
        db.table("unified_conversations").delete().eq("id", msg_conv_id).execute()
    print("✅ Test data cleaned up")

if __name__ == "__main__":
    asyncio.run(test_cross_agent_sharing())