#!/usr/bin/env python
"""
COIA Supabase Memory Test
Test contractor memory persistence with Supabase checkpointer
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

async def test_supabase_memory():
    """Test memory persistence with Supabase checkpointer"""

    try:
        from agents.coia.supabase_checkpointer_simple import create_supabase_checkpointer
        from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

        print("Testing COIA with Supabase Memory Persistence")
        print("=" * 55)

        # Create COIA system with Supabase checkpointer
        checkpointer = await create_supabase_checkpointer()
        app = await create_unified_coia_system(checkpointer)
        print("COIA system created with Supabase checkpointer")

        # Test contractor
        contractor_id = "test_mike_hvac_456"

        # SESSION 1: Profile building
        print("\nSESSION 1: Profile Building")
        print("-" * 30)

        profile_msg = "Hi, I'm Mike from Dallas HVAC Pro. We do emergency HVAC repairs in Dallas area for 12 years."
        print(f"User: {profile_msg}")

        result1 = await invoke_coia_chat(
            app=app,
            user_message=profile_msg,
            session_id="session1",
            contractor_lead_id=contractor_id
        )

        if result1:
            print(f"AI: {result1['messages'][-1].content[:120]}...")
            print(f"Company: {result1.get('company_name', 'None')}")
            print(f"Profile: {result1.get('contractor_profile', {}).get('company_name', 'None')}")

        # SESSION 2: Bid search with memory
        print("\nSESSION 2: Bid Search (Different Session)")
        print("-" * 40)

        search_msg = "Show me emergency HVAC projects"
        print(f"User: {search_msg}")

        result2 = await invoke_coia_chat(
            app=app,
            user_message=search_msg,
            session_id="session2",  # Different session ID
            contractor_lead_id=contractor_id  # Same contractor
        )

        if result2:
            ai_response = result2["messages"][-1].content
            print(f"AI: {ai_response[:150]}...")
            print(f"Company: {result2.get('company_name', 'None')}")
            print(f"Mode: {result2.get('current_mode')}")

            # Check if memory was used
            memory_indicators = [
                "Mike" in ai_response,
                "Dallas HVAC Pro" in ai_response,
                "12 years" in ai_response,
                result2.get("company_name") is not None
            ]

            memory_score = sum(memory_indicators)
            print(f"Memory Score: {memory_score}/4")

            if memory_score >= 2:
                print("SUCCESS: Good memory integration!")
                return True
            elif memory_score == 1:
                print("PARTIAL: Some memory integration")
                return False
            else:
                print("FAILED: No memory integration")
                return False

        return False

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run test"""
    success = await test_supabase_memory()

    print("\n" + "=" * 55)
    if success:
        print("SUCCESS: Supabase memory persistence working!")
    else:
        print("FAILED: Memory persistence needs improvement")

if __name__ == "__main__":
    asyncio.run(main())
