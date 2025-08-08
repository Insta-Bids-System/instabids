"""
Simple COIA Research Test - Without Database
Test if research mode triggers and works
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_landing_page
from langgraph.checkpoint.memory import MemorySaver

async def test_coia_research_simple():
    """Test COIA research without database connection"""
    
    print("TESTING COIA RESEARCH SYSTEM")
    print("=" * 50)
    
    try:
        # Initialize with in-memory checkpointer (no database)
        print("\n1. Initializing COIA system...")
        memory_checkpointer = MemorySaver()
        coia_app = await create_unified_coia_system(memory_checkpointer)
        print("SUCCESS: COIA system initialized")
        
        # Test message
        message = "Hi, I'm from Turf Grass Artificial Solutions in South Florida. We do artificial turf installation."
        session_id = "test_123"
        
        print(f"\n2. Processing contractor message...")
        print(f"Message: {message}")
        
        # Process message
        result = await invoke_coia_landing_page(
            app=coia_app,
            user_message=message,
            session_id=session_id,
            contractor_lead_id=session_id
        )
        
        print(f"\n3. RESULTS:")
        print(f"Current Mode: {result.get('current_mode')}")
        print(f"Interface: {result.get('interface')}")
        print(f"Response: {result.get('response', 'No response')[:150]}...")
        
        # Check profile data
        profile = result.get("contractor_profile", {})
        print(f"\n4. PROFILE DATA:")
        if profile:
            for key, value in profile.items():
                print(f"  {key}: {value}")
        else:
            print("  No profile data found")
        
        # Check if research was attempted
        research_status = result.get("website_research_status")
        research_completed = result.get("research_completed")
        
        print(f"\n5. RESEARCH STATUS:")
        print(f"  Research Completed: {research_completed}")
        print(f"  Website Research Status: {research_status}")
        
        if result.get('current_mode') == 'research':
            print("SUCCESS: Research mode triggered!")
        elif profile.get('company_name'):
            print("SUCCESS: Profile extraction working!")
        else:
            print("ISSUE: No research or extraction detected")
            
        return result
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coia_research_simple())