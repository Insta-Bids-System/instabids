"""
Force trigger research mode by calling research node directly
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.unified_graph import create_unified_coia_system
from agents.coia.unified_state import create_initial_state
from langgraph.checkpoint.memory import MemorySaver

async def test_force_research():
    """Force trigger research mode"""
    
    print("TESTING FORCED RESEARCH MODE")
    print("=" * 50)
    
    try:
        # Initialize COIA system
        memory_checkpointer = MemorySaver()
        coia_app = await create_unified_coia_system(memory_checkpointer)
        print("SUCCESS: COIA system initialized")
        
        # Create state with company name already set
        initial_state = create_initial_state(
            session_id="force_research_test",
            interface="landing_page",
            contractor_lead_id="force_research_123"
        ).to_langgraph_state()
        
        # Set company name to trigger research
        initial_state["company_name"] = "Turf Grass Artificial Solutions"
        initial_state["current_mode"] = "research"  # Force research mode
        
        print(f"\nState setup:")
        print(f"Company Name: {initial_state.get('company_name')}")
        print(f"Current Mode: {initial_state.get('current_mode')}")
        print(f"Interface: {initial_state.get('interface')}")
        
        # Add user message
        from langchain_core.messages import HumanMessage
        initial_state["messages"] = [HumanMessage(content="Research company: Turf Grass Artificial Solutions")]
        
        # Configure for memory storage
        config = {
            "configurable": {
                "thread_id": "force_research_test"
            }
        }
        
        print("\nInvoking COIA with forced research state...")
        
        # Invoke COIA
        result = await coia_app.ainvoke(initial_state, config)
        
        print(f"\nRESULT:")
        print(f"Current Mode: {result.get('current_mode')}")
        print(f"Company Name: {result.get('company_name')}")
        print(f"Research Completed: {result.get('research_completed')}")
        print(f"Website Research Status: {result.get('website_research_status')}")
        print(f"Research Findings: {bool(result.get('research_findings'))}")
        
        # Check contractor profile
        profile = result.get("contractor_profile", {})
        if profile:
            print(f"\nENRICHED PROFILE:")
            for key, value in profile.items():
                if value:  # Only show non-empty fields
                    print(f"  {key}: {value}")
        
        # Check for extracted data
        phone = profile.get("phone") or result.get("phone")
        if phone:
            print(f"\nSUCCESS: Phone extracted: {phone}")
        else:
            print(f"\nISSUE: No phone number found")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_force_research())