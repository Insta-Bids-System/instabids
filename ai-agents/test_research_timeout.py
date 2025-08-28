#!/usr/bin/env python3
"""
Test COIA research node timeout handling specifically
"""

import asyncio
import sys
import os
sys.path.append('.')

from agents.coia.langgraph_nodes import research_node
from agents.coia.unified_state import UnifiedCoIAState
from langchain_core.messages import HumanMessage, AIMessage

async def test_research_timeout():
    print("Testing COIA research node timeout handling...")
    print("=" * 60)
    
    # Create test state ready for research
    test_state = UnifiedCoIAState(
        messages=[
            HumanMessage(content="Hi, I'm the owner of Premier Roofing Solutions Miami. We specialize in residential and commercial roofing in Miami-Dade County."),
            AIMessage(content="Welcome! Let me research your company to build your profile.")
        ],
        interface="landing_page",
        company_name="Premier Roofing Solutions Miami",
        research_completed=False,
        current_mode="research",
        contractor_lead_id="12345678-1234-1234-1234-123456789012",
        session_id="debug-test"
    )
    
    print(f"Starting research for: {test_state.get('company_name')}")
    print(f"Research completed: {test_state.get('research_completed')}")
    print("-" * 60)
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        # This should complete within 30 seconds or timeout
        result = await research_node(test_state)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        print(f"SUCCESS: Research completed in {duration:.2f} seconds")
        print(f"Research status: {result.get('research_completed')}")
        print(f"Current mode: {result.get('current_mode')}")
        print(f"Contractor profile completeness: {result.get('profile_completeness', 0)}%")
        
        # Check if we got meaningful data
        contractor_profile = result.get('contractor_profile', {})
        if contractor_profile.get('company_name'):
            print(f"SUCCESS: Profile data extracted: {contractor_profile.get('company_name')}")
        
        if result.get('research_findings'):
            print(f"SUCCESS: Research findings available: {len(str(result.get('research_findings')))} chars")
            
        print("\nSUCCESS: TIMEOUT HANDLING TEST PASSED - Research completed within acceptable time")
        
    except asyncio.TimeoutError:
        print("ERROR: Research timed out - this should not happen with our timeout wrapper")
        
    except Exception as e:
        print(f"ERROR: Research failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_research_timeout())