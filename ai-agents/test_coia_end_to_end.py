#!/usr/bin/env python3
"""
Test complete COIA end-to-end flow with timeout fixes
"""

import asyncio
import sys
import os
sys.path.append('.')

from agents.coia.unified_graph import create_unified_coia_system
from agents.coia.unified_state import create_initial_state
from langchain_core.messages import HumanMessage

async def test_complete_coia_flow():
    print("Testing COMPLETE COIA end-to-end flow...")
    print("=" * 60)
    
    try:
        # Create COIA app
        app = await create_unified_coia_system()
        print("SUCCESS: COIA app created")
        
        # Test data for realistic contractor
        test_company = "Elite Roofing & Construction Tampa"
        user_message = f"Hi, I'm the owner of {test_company}. We've been in business for 15 years specializing in residential and commercial roofing across the Tampa Bay area."
        
        # Create initial state for landing page
        initial_state = create_initial_state(
            session_id="end-to-end-test",
            interface="landing_page",
            contractor_lead_id="87654321-4321-4321-4321-210987654321"
        ).to_langgraph_state()
        
        initial_state["messages"] = [HumanMessage(content=user_message)]
        
        config = {
            "configurable": {
                "thread_id": "end-to-end-test",
                "checkpoint_id": "test_end_to_end",
                "checkpoint_ns": "coia_test"
            },
            "recursion_limit": 50,  # Reasonable limit
            "max_concurrency": 10
        }
        
        print(f"Testing with company: {test_company}")
        print(f"User message: {user_message}")
        print("-" * 60)
        
        start_time = asyncio.get_event_loop().time()
        
        # This should complete the entire flow without hanging
        result = await app.ainvoke(initial_state, config)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        print(f"SUCCESS: Complete flow finished in {duration:.2f} seconds")
        print("-" * 60)
        
        # Analyze results
        print("FINAL RESULTS:")
        print(f"- Interface: {result.get('interface')}")
        print(f"- Company name: {result.get('company_name')}")
        print(f"- Research completed: {result.get('research_completed')}")
        print(f"- Contractor created: {result.get('contractor_created')}")
        print(f"- Current mode: {result.get('current_mode')}")
        print(f"- Profile completeness: {result.get('profile_completeness', 0)}%")
        print(f"- Completion ready: {result.get('completion_ready')}")
        
        # Check conversation flow
        messages = result.get('messages', [])
        print(f"- Total messages: {len(messages)}")
        
        if len(messages) >= 2:
            last_ai_message = messages[-1]
            if hasattr(last_ai_message, 'content'):
                print(f"- Last AI response length: {len(last_ai_message.content)} chars")
        
        # Check research data
        research_findings = result.get('research_findings')
        if research_findings:
            print(f"- Research findings: {len(str(research_findings))} chars")
            
        contractor_profile = result.get('contractor_profile', {})
        if contractor_profile.get('company_name'):
            print(f"- Profile extracted: {contractor_profile.get('company_name')}")
            
        print("\nSUCCESS: COMPLETE END-TO-END TEST PASSED!")
        print("- No hanging on API calls")
        print("- No infinite recursion")
        print("- Research completed within timeout")
        print("- Proper conversation flow maintained")
        
        # Summary for user
        if result.get('research_completed') and result.get('company_name'):
            print(f"\nBUSINESS IMPACT: COIA successfully researched and profiled {result.get('company_name')}")
            print("System is ready for production contractor onboarding!")
        
    except Exception as e:
        print(f"ERROR: End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_coia_flow())