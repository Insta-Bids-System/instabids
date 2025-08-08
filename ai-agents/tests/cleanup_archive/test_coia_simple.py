#!/usr/bin/env python
"""
Simple COIA Bid Card Test - No emojis
Test the COIA system directly to identify the source of the error
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

async def test_coia_chat_simple():
    """Test COIA chat directly"""

    try:
        # Import the unified COIA system
        from langgraph.checkpoint.memory import MemorySaver

        from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

        print("Creating COIA system...")
        checkpointer = MemorySaver()
        app = await create_unified_coia_system(checkpointer)

        print("COIA system created successfully")

        # Test bid card search query
        test_message = "Show me kitchen remodeling projects near me"
        session_id = "test_simple_session"

        print(f"Testing message: '{test_message}'")

        # Invoke COIA chat
        result = await invoke_coia_chat(
            app=app,
            user_message=test_message,
            session_id=session_id,
            contractor_lead_id=None,
            project_id=None
        )

        print("Result keys:", list(result.keys()) if result else "None")

        if result:
            print("Messages:", len(result.get("messages", [])))
            print("Current mode:", result.get("current_mode"))
            print("Bid cards attached:", len(result.get("bid_cards_attached", [])))

            # Print the actual messages
            for i, msg in enumerate(result.get("messages", [])):
                print(f"  Message {i}: {type(msg).__name__} - {msg.content[:100]}...")
        else:
            print("ERROR: Result is None - this is the source of the error!")

        return result

    except Exception as e:
        print(f"Error in direct test: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run simple test"""
    print("Starting COIA Bid Card Simple Test")
    print("=" * 50)

    result = await test_coia_chat_simple()

    print("\nSummary:")
    if result:
        print("SUCCESS: COIA chat system works")
    else:
        print("FAILED: COIA chat system failed")

if __name__ == "__main__":
    asyncio.run(main())
