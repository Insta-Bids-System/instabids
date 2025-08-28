#!/usr/bin/env python3
"""
Direct test of COIA routing to debug infinite loop
"""

import asyncio
import sys
import os
sys.path.append('.')

from agents.coia.unified_graph import create_unified_coia_system
from agents.coia.unified_state import create_initial_state
from langchain_core.messages import HumanMessage

async def test_coia_direct_debug():
    print("Testing COIA routing directly...")
    print("=" * 60)
    
    # Create COIA app
    app = await create_unified_coia_system()
    
    # Create test message
    test_company = "Premier Roofing Solutions Miami"
    user_message = f"Hi, I'm the owner of {test_company}. We specialize in residential and commercial roofing in Miami-Dade County."
    
    # Create initial state for landing page
    initial_state = create_initial_state(
        session_id="debug-123",
        interface="landing_page",
        contractor_lead_id="landing-456"
    ).to_langgraph_state()
    
    initial_state["messages"] = [HumanMessage(content=user_message)]
    
    config = {
        "configurable": {
            "thread_id": "landing-456",
            "checkpoint_id": "landing_landing-456",
            "checkpoint_ns": "coia_landing"
        },
        "recursion_limit": 100,  # Higher limit to see full error instead of recursion limit
        "max_concurrency": 10
    }
    
    print(f"Initial state interface: {initial_state.get('interface')}")
    print(f"User message: {user_message}")
    print("-" * 60)
    
    try:
        result = await app.ainvoke(initial_state, config)
        print("Success!")
        print(f"Final state keys: {list(result.keys())}")
        
    except Exception as e:
        print(f"Error: {e}")
        
        # If recursion error, let's trace the routing decisions
        if "recursion" in str(e).lower():
            print("\nRecursion error detected. This suggests routing loop.")
            print("Likely causes:")
            print("1. conversation node not setting completion_ready properly")
            print("2. mode detector not routing to research")
            print("3. research node not completing properly")
            
            # Let's check if our fix worked by testing the conversation node directly
            from agents.coia.langgraph_nodes import conversation_node
            from agents.coia.unified_state import UnifiedCoIAState
            
            print("\n" + "=" * 60)
            print("Testing conversation node directly...")
            
            test_state = UnifiedCoIAState(
                messages=[HumanMessage(content=user_message)],
                interface="landing_page",
                company_name="",
                research_completed=False
            )
            
            try:
                conv_result = await conversation_node(test_state)
                print(f"Conversation result keys: {list(conv_result.keys())}")
                print(f"Company name extracted: {conv_result.get('company_name')}")
                print(f"Completion ready: {conv_result.get('completion_ready')}")
                print(f"Research completed: {conv_result.get('research_completed')}")
                
                # This should be: company_name extracted, completion_ready=False, research_completed=False
                if conv_result.get("company_name") and not conv_result.get("completion_ready"):
                    print(">> Conversation node fix working correctly!")
                else:
                    print(">> Conversation node still has issues")
                
            except Exception as conv_e:
                print(f"Conversation node error: {conv_e}")

if __name__ == "__main__":
    asyncio.run(test_coia_direct_debug())