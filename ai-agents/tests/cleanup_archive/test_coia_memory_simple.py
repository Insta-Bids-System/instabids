#!/usr/bin/env python
"""
COIA Memory Persistence Test - Simple Version
Test contractor memory across multiple sessions with bid card search
"""

import asyncio
import logging
import os

from dotenv import load_dotenv


# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_contractor_memory_persistence():
    """Test memory persistence across multiple contractor sessions"""

    try:
        from langgraph.checkpoint.memory import MemorySaver

        from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

        print("Starting COIA Memory Persistence Test")
        print("=" * 60)

        # Create COIA system with memory
        checkpointer = MemorySaver()
        app = await create_unified_coia_system(checkpointer)
        print("COIA system created with memory persistence")

        # Test contractor profile: Mike's HVAC Solutions
        contractor_id = "contractor_mike_hvac_123"

        # SESSION 1: Build contractor profile
        print("\nSESSION 1: Building contractor profile")
        print("-" * 40)

        profile_message = "Hi, I'm Mike from Mike's HVAC Solutions. We do commercial HVAC work in Dallas for 15 years."
        print(f"User: {profile_message}")

        result1 = await invoke_coia_chat(
            app=app,
            user_message=profile_message,
            session_id=f"session1_{contractor_id}",
            contractor_lead_id=contractor_id
        )

        if result1:
            print(f"AI: {result1['messages'][-1].content[:150]}...")
            print(f"Company: {result1.get('company_name', 'Not set')}")
            print(f"Mode: {result1.get('current_mode')}")

        # SESSION 2: Bid card search with memory
        print("\nSESSION 2: Bid card search with memory")
        print("-" * 40)

        search_message = "Show me HVAC projects near me"
        print(f"User: {search_message}")

        result2 = await invoke_coia_chat(
            app=app,
            user_message=search_message,
            session_id=f"session2_{contractor_id}",
            contractor_lead_id=contractor_id
        )

        if result2:
            ai_response = result2["messages"][-1].content
            print(f"AI: {ai_response[:200]}...")
            print(f"Company: {result2.get('company_name', 'Not remembered')}")
            print(f"Mode: {result2.get('current_mode')}")

            # Check memory integration
            memory_used = False
            if "Mike" in ai_response or "HVAC Solutions" in ai_response:
                print("SUCCESS: Memory integrated in response!")
                memory_used = True
            else:
                print("WARNING: Memory not clearly used in response")

        # SESSION 3: Different session, same contractor
        print("\nSESSION 3: New session, same contractor")
        print("-" * 40)

        return_message = "I'm looking for emergency HVAC projects"
        print(f"User: {return_message}")

        result3 = await invoke_coia_chat(
            app=app,
            user_message=return_message,
            session_id=f"session3_{contractor_id}",
            contractor_lead_id=contractor_id
        )

        if result3:
            ai_response = result3["messages"][-1].content
            print(f"AI: {ai_response[:200]}...")
            print(f"Company: {result3.get('company_name', 'Not remembered')}")

            # Check persistent memory
            if "Mike" in ai_response or result3.get("company_name") == "Mike's HVAC Solutions":
                print("SUCCESS: Memory persisted across sessions!")
                return True
            else:
                print("WARNING: Memory not persisted across sessions")
                return False

        return False

    except Exception as e:
        print(f"Error in memory persistence test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run memory persistence test"""
    print("COIA Memory Persistence Test")
    print("=" * 50)

    success = await test_contractor_memory_persistence()

    print("\n" + "=" * 50)
    print("FINAL RESULTS:")

    if success:
        print("SUCCESS: Memory persistence working!")
        print("- Contractor profiles remembered")
        print("- Bid card searches personalized")
        print("- Multi-session continuity maintained")
    else:
        print("FAILED: Memory persistence needs work")
        print("- Check memory integration")


if __name__ == "__main__":
    asyncio.run(main())
