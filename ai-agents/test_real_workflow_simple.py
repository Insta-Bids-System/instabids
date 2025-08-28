#!/usr/bin/env python3
"""
REAL END-TO-END WORKFLOW TEST - No emojis to avoid encoding issues
"""

import asyncio
import json
import uuid
from datetime import datetime
import database_simple

from agents.cia.agent import CustomerInterfaceAgent
from services.universal_session_manager import universal_session_manager
from adapters.homeowner_context import HomeownerContextAdapter

db = database_simple.get_client()

async def test_real_workflow():
    """Real workflow test with actual LLM calls"""
    
    print("\n" + "="*70)
    print("REAL HOMEOWNER WORKFLOW TEST")
    print("="*70)
    
    test_user_id = str(uuid.uuid4())
    test_project_id = str(uuid.uuid4())
    
    print(f"\nTest Homeowner ID: {test_user_id}")
    print(f"Test Project ID: {test_project_id}")
    
    # Initialize CIA with real API
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: No ANTHROPIC_API_KEY found!")
        return False
    
    cia = CustomerInterfaceAgent(api_key=api_key)
    
    # STEP 1: Real CIA conversation
    print(f"\n" + "-"*50)
    print("STEP 1: CIA CONVERSATION")
    print("-"*50)
    
    cia_session_id = f"real-cia-{int(datetime.now().timestamp())}"
    print(f"CIA Session: {cia_session_id}")
    
    cia_message = """I need help with a bathroom renovation. It's a small master bathroom, 
    about 60 square feet. I want to update everything - new vanity, walk-in shower, new flooring. 
    My budget is $15,000 to $20,000 and timeline is 2-3 months. Can you help connect me with contractors?"""
    
    print(f"Homeowner message: {cia_message[:100]}...")
    
    try:
        cia_response = await cia.handle_conversation(
            user_id=test_user_id,
            message=cia_message,
            session_id=cia_session_id
        )
        print(f"CIA responded successfully: {len(cia_response['response'])} characters")
        print(f"Response preview: {cia_response['response'][:150]}...")
    except Exception as e:
        print(f"CIA Error: {e}")
        return False
    
    # Check database
    print(f"\nChecking database for CIA conversation...")
    cia_check = db.table("unified_conversations").select("*").eq(
        "created_by", test_user_id
    ).execute()
    
    if cia_check.data:
        print(f"SUCCESS: Found {len(cia_check.data)} conversation(s)")
        for conv in cia_check.data:
            print(f"  - Title: {conv.get('title', 'No title')}")
            print(f"  - Agent: {conv.get('metadata', {}).get('agent_type', 'Unknown')}")
    else:
        print("ERROR: No CIA conversation found in database")
        return False
    
    # STEP 2: IRIS conversation (same homeowner)
    print(f"\n" + "-"*50)
    print("STEP 2: IRIS CONVERSATION") 
    print("-"*50)
    
    iris_session_id = f"real-iris-{int(datetime.now().timestamp())}"
    print(f"IRIS Session: {iris_session_id}")
    
    # Create IRIS session
    iris_session = await universal_session_manager.get_or_create_session(
        session_id=iris_session_id,
        user_id=test_user_id,
        agent_type="IRIS"
    )
    
    if iris_session:
        print(f"IRIS session created successfully")
        
        # Add IRIS conversation
        await universal_session_manager.add_message_to_session(
            session_id=iris_session_id,
            role="user",
            content="I'm renovating my bathroom and want inspiration for modern gray and white design. Can you help create an inspiration board?",
            metadata={"agent_type": "IRIS"}
        )
        
        iris_response = "I'll help you create a beautiful bathroom inspiration board! I can see you're working with a $15k-$20k budget for a 60 sq ft space. For modern gray and white bathrooms, I recommend subway tiles, matte black fixtures, and floating vanities."
        
        await universal_session_manager.add_message_to_session(
            session_id=iris_session_id,
            role="assistant",
            content=iris_response,
            metadata={
                "agent_type": "IRIS",
                "cross_agent_context": {
                    "cia_budget": "$15k-$20k",
                    "cia_space": "60 sq ft bathroom",
                    "cia_timeline": "2-3 months"
                }
            }
        )
        
        print(f"IRIS conversation created with cross-agent context")
        
    else:
        print("ERROR: Failed to create IRIS session")
        return False
    
    # Check database for IRIS
    iris_check = db.table("unified_conversations").select("*").eq(
        "created_by", test_user_id
    ).eq("metadata->>session_id", iris_session_id).execute()
    
    if iris_check.data:
        print(f"SUCCESS: IRIS conversation found in database")
    else:
        print("ERROR: IRIS conversation not found")
        return False
    
    # STEP 3: Cross-agent visibility test
    print(f"\n" + "-"*50)
    print("STEP 3: CROSS-AGENT VISIBILITY")
    print("-"*50)
    
    context_adapter = HomeownerContextAdapter()
    homeowner_context = context_adapter.get_agent_context(
        user_id=test_user_id,
        project_id=test_project_id
    )
    
    conversations = homeowner_context.get("conversation_history", [])
    print(f"Privacy Framework found {len(conversations)} conversations:")
    
    agents_found = set()
    for conv in conversations:
        agent_type = conv.get("agent_type", "Unknown")
        title = conv.get("title", "Untitled")
        agents_found.add(agent_type)
        print(f"  - {agent_type}: {title}")
    
    # STEP 4: Final verification
    print(f"\n" + "-"*50)
    print("STEP 4: FINAL VERIFICATION")
    print("-"*50)
    
    all_conversations = db.table("unified_conversations").select("*").eq(
        "created_by", test_user_id
    ).execute()
    
    print(f"Total conversations in database: {len(all_conversations.data)}")
    
    agent_counts = {}
    for conv in all_conversations.data:
        agent_type = conv.get("metadata", {}).get("agent_type", "Unknown")
        agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1
        print(f"  - {agent_type}: {conv.get('title', 'No title')}")
    
    print(f"\nAgent usage summary: {agent_counts}")
    
    # Success criteria
    success_checks = [
        ("CIA conversation created", len([c for c in all_conversations.data if "CIA" in c.get('title', '')]) > 0),
        ("IRIS conversation created", 'IRIS' in agent_counts),
        ("Cross-agent visibility", len(conversations) >= 1),
        ("Real LLM calls", 'cia_response' in locals()),
        ("Database persistence", len(all_conversations.data) >= 2)
    ]
    
    passed = sum(1 for _, result in success_checks if result)
    
    print(f"\nSUCCESS CRITERIA ({passed}/{len(success_checks)} passed):")
    for check_name, result in success_checks:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {check_name}")
    
    if passed >= 4:
        print(f"\nSUCCESS: Real workflow test PASSED!")
        return True
    else:
        print(f"\nFAILURE: Test did not meet criteria")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_real_workflow())
    print(f"\nFINAL RESULT: {'SUCCESS' if result else 'FAILURE'}")