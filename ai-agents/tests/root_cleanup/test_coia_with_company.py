"""
Test COIA with company name already set to trigger research
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_landing_page
from langgraph.checkpoint.memory import MemorySaver

async def test_coia_with_company():
    """Test COIA with company name pre-set"""
    
    print("TESTING COIA WITH COMPANY NAME SET")
    print("=" * 50)
    
    try:
        # Initialize COIA system
        memory_checkpointer = MemorySaver()
        coia_app = await create_unified_coia_system(memory_checkpointer)
        print("SUCCESS: COIA system initialized")
        
        # Test message - simple follow up that shouldn't change company name
        message = "Can you help me get more bids?"
        session_id = "test_with_company"
        
        print(f"\nProcessing message: {message}")
        
        # First, send initial message to establish company name
        result1 = await invoke_coia_landing_page(
            app=coia_app,
            user_message="Hi, I'm from Turf Grass Artificial Solutions. We do artificial turf installation.",
            session_id=session_id,
            contractor_lead_id=session_id + "_1"
        )
        
        print(f"\nFIRST MESSAGE RESULT:")
        print(f"Current Mode: {result1.get('current_mode')}")
        print(f"Company Name: {result1.get('company_name')}")
        print(f"Research Completed: {result1.get('research_completed')}")
        print(f"Website Research Status: {result1.get('website_research_status')}")
        
        # Check if research was triggered
        if result1.get('current_mode') == 'research':
            print("SUCCESS: Research mode triggered on first message!")
        elif result1.get('company_name'):
            print(f"PARTIAL: Company name extracted: {result1['company_name']}")
            
            # Send follow-up message to same session
            result2 = await invoke_coia_landing_page(
                app=coia_app,
                user_message=message,
                session_id=session_id,
                contractor_lead_id=session_id + "_1"  # Same contractor_lead_id
            )
            
            print(f"\nSECOND MESSAGE RESULT:")
            print(f"Current Mode: {result2.get('current_mode')}")
            print(f"Research Completed: {result2.get('research_completed')}")
            print(f"Website Research Status: {result2.get('website_research_status')}")
            
            if result2.get('current_mode') == 'research':
                print("SUCCESS: Research mode triggered on second message!")
            else:
                print("ISSUE: Research mode not triggered on follow-up")
        else:
            print("ISSUE: No company name extracted")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coia_with_company())