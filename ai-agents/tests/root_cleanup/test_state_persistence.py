#!/usr/bin/env python
"""
Test state persistence with same checkpointer
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

async def test_state_persistence():
    """Test if state actually persists with the same app instance"""

    from langchain_core.messages import HumanMessage
    from langgraph.checkpoint.memory import MemorySaver

    from agents.coia.unified_graph import create_unified_coia_system

    print("STATE PERSISTENCE TEST")
    print("=" * 50)

    # Create ONE checkpointer and app instance
    checkpointer = MemorySaver()
    app = await create_unified_coia_system(checkpointer)

    contractor_id = "persistence_test"
    thread_id = f"chat_{contractor_id}"

    # Config for persistence
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # FIRST CALL - Set profile data
    print("\nFIRST CALL - Setting Profile")
    print("-" * 30)

    initial_state = {
        "messages": [HumanMessage(content="Hi, I'm Mike from Dallas HVAC Pro")],
        "contractor_profile": {
            "company_name": "Dallas HVAC Pro",
            "years_in_business": 15,
            "service_areas": ["Dallas"],
            "specializations": ["emergency"]
        },
        "company_name": "Dallas HVAC Pro",
        "contractor_lead_id": contractor_id,
        "session_id": "test1",
        "interface": "chat",
        "current_mode": "conversation"
    }

    result1 = await app.ainvoke(initial_state, config)

    profile1 = result1.get("contractor_profile", {})
    print(f"Profile after first call: {profile1.get('company_name')}")

    # Check if state was saved
    print("\nCHECKING SAVED STATE")
    print("-" * 30)

    saved_state = await app.aget_state(config)
    if saved_state and saved_state.values:
        print("State saved: YES")
        saved_profile = saved_state.values.get("contractor_profile", {})
        print(f"Saved profile company: {saved_profile.get('company_name')}")
    else:
        print("State saved: NO")

    # SECOND CALL - Check if profile persists
    print("\nSECOND CALL - Checking Persistence")
    print("-" * 30)

    # Just send a new message, don't recreate state
    input2 = {
        "messages": [HumanMessage(content="Show me HVAC projects")]
    }

    result2 = await app.ainvoke(input2, config)

    profile2 = result2.get("contractor_profile", {})
    print(f"Profile after second call: {profile2.get('company_name')}")

    # Check persistence
    if profile2.get("company_name") == "Dallas HVAC Pro":
        print("\nSUCCESS: Profile persisted!")
        return True
    else:
        print("\nFAILED: Profile did not persist")
        return False

if __name__ == "__main__":
    asyncio.run(test_state_persistence())
