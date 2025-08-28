#!/usr/bin/env python3
"""
Test COIA with clean state - fresh session to test the conversation node fix
"""
import asyncio
import sys
import os
sys.path.append('.')

from agents.coia.unified_graph import create_unified_coia_system

async def test_coia_clean():
    print("Testing COIA with CLEAN STATE - Fixed Conversation Node")
    print("=" * 60)
    print("Company: Tropical Turf (verified real business)")
    print("Testing conversation node processing of explicit company mention")
    print("=" * 60)
    
    # Create COIA system
    coia_app = await create_unified_coia_system()
    
    # Configure with fresh thread_id
    config = {"configurable": {"thread_id": "tropical-turf-clean-test"}}
    
    # Fresh conversation with explicit company information
    from langchain_core.messages import HumanMessage
    
    user_message = "Hi, our company is called Tropical Turf and we specialize in artificial grass installation. We're based at 6700 NW 82 Ave, Miami FL 33166."
    
    test_input = {
        "messages": [HumanMessage(content=user_message)],
        "current_mode": "conversation",
        "conversation_history": [],
        "company_name": "",
        "research_completed": False,
        "contractor_lead_id": "12345678-1234-1234-1234-123456789012", 
        "session_id": "tropical-turf-clean"
    }
    
    print(f"\nTesting fresh conversation with: {user_message}")
    print("\nStarting COIA processing (should extract company name now)...")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        result = await asyncio.wait_for(
            coia_app.ainvoke(test_input, config=config),
            timeout=60.0
        )
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        print(f"\nProcessing completed in {duration:.2f} seconds")
        print(f"Research status: {result.get('research_completed')}")
        print(f"Current mode: {result.get('current_mode')}")
        print(f"Company identified: '{result.get('company_name')}'")
        
        # Check if company name was extracted (THIS IS THE KEY TEST)
        if result.get('company_name'):
            print(f"SUCCESS: Company name extracted: '{result.get('company_name')}'")
            if result.get('company_name').lower() == 'tropical turf':
                print("SUCCESS: Exact company name match!")
            else:
                print(f"WARNING: Company name extracted but different: '{result.get('company_name')}'")
        else:
            print("FAILURE: Company name NOT extracted from explicit mention")
        
        # Check if research was triggered
        if result.get('current_mode') == 'research':
            print("SUCCESS: Research mode was triggered")
        elif result.get('research_completed'):
            print("SUCCESS: Research was completed")
        else:
            print("ISSUE: Research was not triggered")
            
        # Show final AI response to verify it's responding to actual input
        messages = result.get('messages', [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                response_content = last_message.content
            else:
                response_content = last_message.get('content', 'No content')
            print(f"\nAI Response: {response_content}")
            
            # Check if response is generic or contextual
            if "what's your company name" in response_content.lower():
                print("ISSUE: AI still asking for company name that was already provided")
            elif "tropical turf" in response_content.lower():
                print("SUCCESS: AI acknowledging the company name provided")
            else:
                print("INFO: AI response is contextual (not generic greeting)")
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coia_clean())