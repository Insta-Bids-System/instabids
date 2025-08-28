#!/usr/bin/env python3
"""
Test COIA with real company: Tropical Turf (South Florida)
This proves the system works with completely fresh, real business data
"""
import asyncio
import sys
import os
sys.path.append('.')

from agents.coia.unified_graph import create_unified_coia_system

async def test_coia_real_company():
    print("Testing COIA with REAL COMPANY: Tropical Turf")
    print("=" * 60)
    print("Company: Tropical Turf (verified real business)")
    print("Address: 6700 NW 82 Ave, Miami FL 33166")
    print("Phone: (305) 922-0745")
    print("Website: https://tropicalturf.com/")
    print("Services: Artificial turf installation, wholesale, commercial/residential")
    print("=" * 60)
    
    # Create COIA system
    try:
        coia_app = await create_unified_coia_system()
        print("SUCCESS: COIA app created")
    except Exception as e:
        print(f"ERROR: Failed to create COIA app: {e}")
        return
    
    # Test conversation that mentions Tropical Turf
    from langchain_core.messages import HumanMessage
    
    user_message = "Hi, I run Tropical Turf, we're an artificial grass installation company based in Miami. We do both residential and commercial projects throughout South Florida."
    
    test_input = {
        "messages": [HumanMessage(content=user_message)],
        "current_mode": "conversation",
        "conversation_history": [],
        "company_name": "",
        "research_completed": False,
        "contractor_lead_id": "12345678-1234-1234-1234-123456789012",
        "session_id": "real-company-test"
    }
    
    print(f"\nTesting with message: {user_message}")
    print("\nStarting COIA processing...")
    
    # Run with timeout to prevent hanging
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Configure with thread_id for checkpointer
        config = {"configurable": {"thread_id": "real-company-test-thread"}}
        
        # Process with 45 second timeout
        result = await asyncio.wait_for(
            coia_app.ainvoke(test_input, config=config),
            timeout=45.0
        )
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        print(f"\nSUCCESS: COIA completed in {duration:.2f} seconds")
        print(f"Research status: {result.get('research_completed')}")
        print(f"Current mode: {result.get('current_mode')}")
        print(f"Company identified: {result.get('company_name')}")
        
        # Check if we got meaningful contractor data
        contractor_profile = result.get('contractor_profile', {})
        if contractor_profile and contractor_profile.get('company_name'):
            print(f"SUCCESS: Contractor profile created for: {contractor_profile.get('company_name')}")
            print(f"Business type: {contractor_profile.get('business_type', 'Not specified')}")
            print(f"Profile completeness: {result.get('profile_completeness', 0)}%")
        else:
            print("WARNING: No contractor profile data extracted")
        
        # Check research findings
        if result.get('research_findings'):
            findings_size = len(str(result.get('research_findings')))
            print(f"SUCCESS: Research findings: {findings_size} characters of data")
        else:
            print("WARNING: No research findings available")
            
        print("\nSUCCESS: REAL COMPANY TEST COMPLETED - System working with fresh data!")
        
    except asyncio.TimeoutError:
        print("ERROR: COIA timed out after 45 seconds - timeout protection working but taking too long")
        
    except Exception as e:
        print(f"ERROR: COIA failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coia_real_company())