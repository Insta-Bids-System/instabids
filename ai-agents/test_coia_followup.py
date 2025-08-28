#!/usr/bin/env python3
"""
Test COIA with follow-up message to Tropical Turf conversation
"""
import asyncio
import sys
import os
sys.path.append('.')

from agents.coia.unified_graph import create_unified_coia_system

async def test_coia_followup():
    print("Testing COIA with follow-up message for Tropical Turf")
    print("=" * 60)
    
    # Create COIA system
    coia_app = await create_unified_coia_system()
    
    # Configure with thread_id
    config = {"configurable": {"thread_id": "tropical-turf-followup"}}
    
    # Simulate the conversation where user provides company name directly
    test_input = {
        "message": "Our company is called Tropical Turf and we're located at 6700 NW 82 Ave, Miami FL 33166. We install artificial grass for homes and businesses.",
        "current_mode": "conversation",
        "conversation_history": [],
        "company_name": "",
        "research_completed": False,
        "contractor_lead_id": "12345678-1234-1234-1234-123456789012", 
        "session_id": "tropical-turf-test"
    }
    
    print(f"\nTesting with explicit company message: {test_input['message']}")
    print("\nStarting COIA processing...")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        result = await asyncio.wait_for(
            coia_app.ainvoke(test_input, config=config),
            timeout=45.0
        )
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        print(f"\nProcessing completed in {duration:.2f} seconds")
        print(f"Research status: {result.get('research_completed')}")
        print(f"Current mode: {result.get('current_mode')}")
        print(f"Company identified: '{result.get('company_name')}'")
        
        # Check if company name was extracted
        if result.get('company_name'):
            print(f"SUCCESS: Company name extracted: {result.get('company_name')}")
        else:
            print("ISSUE: Company name not extracted from explicit mention")
        
        # Check if research was triggered
        if result.get('research_completed'):
            print("SUCCESS: Research was completed")
            contractor_profile = result.get('contractor_profile', {})
            if contractor_profile.get('company_name'):
                print(f"SUCCESS: Profile created for: {contractor_profile.get('company_name')}")
        else:
            print("ISSUE: Research was not triggered")
            
        # Show final AI response
        messages = result.get('messages', [])
        if messages:
            print(f"\nAI Response: {messages[-1].content}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coia_followup())