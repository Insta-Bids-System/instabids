#!/usr/bin/env python3
"""
Test COIA with fresh state - no cached checkpoints
"""
import asyncio
import sys
import uuid
sys.path.append('.')

from agents.coia.unified_graph import create_unified_coia_system
from langchain_core.messages import HumanMessage

async def test_coia_fresh():
    print("Testing COIA with FRESH STATE - Tropical Turf")
    print("=" * 60)
    
    # Generate unique thread ID to avoid cached state
    unique_thread = f"fresh-test-{uuid.uuid4().hex[:8]}"
    print(f"Using fresh thread ID: {unique_thread}")
    
    # Create COIA system
    try:
        coia_app = await create_unified_coia_system()
        print("SUCCESS: COIA app created")
    except Exception as e:
        print(f"ERROR: Failed to create COIA app: {e}")
        return
    
    # Test conversation with Tropical Turf
    user_message = "Hi, I run Tropical Turf, we're an artificial grass installation company based in Miami. We do both residential and commercial projects throughout South Florida."
    
    # Create fresh initial state
    test_input = {
        "messages": [HumanMessage(content=user_message)],
        "current_mode": "conversation",
        "company_name": "",
        "research_completed": False,
        "completion_ready": False,  # Explicitly set to False
        "contractor_lead_id": f"test-{uuid.uuid4().hex[:12]}",
        "session_id": f"session-{uuid.uuid4().hex[:8]}"
    }
    
    print(f"\nTesting with message: {user_message[:80]}...")
    print("\nStarting COIA processing with 60 second timeout...")
    
    # Run with longer timeout for research
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Use unique thread ID to avoid cached state
        config = {"configurable": {"thread_id": unique_thread}}
        
        # Process with 60 second timeout for research
        result = await asyncio.wait_for(
            coia_app.ainvoke(test_input, config=config),
            timeout=60.0
        )
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        print(f"\n✅ COIA completed in {duration:.2f} seconds")
        print(f"Company identified: {result.get('company_name')}")
        print(f"Research completed: {result.get('research_completed')}")
        print(f"Current mode: {result.get('current_mode')}")
        
        # Check contractor profile
        contractor_profile = result.get('contractor_profile', {})
        if contractor_profile:
            print(f"\n📋 Contractor Profile:")
            print(f"  Company: {contractor_profile.get('company_name')}")
            print(f"  Phone: {contractor_profile.get('phone', 'Not found')}")
            print(f"  Email: {contractor_profile.get('email', 'Not found')}")
            print(f"  Website: {contractor_profile.get('website', 'Not found')}")
            print(f"  Profile completeness: {result.get('profile_completeness', 0)}%")
            
        # Check research findings
        research_findings = result.get('research_findings', {})
        if research_findings:
            print(f"\n🔬 Research Findings:")
            print(f"  Status: {research_findings.get('status')}")
            print(f"  Data sources: {research_findings.get('data_sources', [])}")
            print(f"  Profile saved to DB: {research_findings.get('auto_generated_profile', {}).get('database_saved', False)}")
            
            # Check if saved to database
            auto_profile = research_findings.get('auto_generated_profile', {})
            if auto_profile.get('database_saved'):
                print(f"  ✅ DATABASE SAVE SUCCESSFUL")
                print(f"  Contractor Lead ID: {auto_profile.get('contractor_lead_id')}")
            else:
                print(f"  ❌ DATABASE SAVE FAILED")
                
        print(f"\n{'✅' if result.get('research_completed') else '❌'} Test completed")
        
    except asyncio.TimeoutError:
        print("\n⏱️ TIMEOUT: Research took longer than 60 seconds")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coia_fresh())