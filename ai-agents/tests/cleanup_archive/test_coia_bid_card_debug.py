#!/usr/bin/env python
"""
Debug COIA Bid Card Integration
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

async def test_coia_chat_direct():
    """Test COIA chat directly"""

    try:
        # Import the unified COIA system
        from langgraph.checkpoint.memory import MemorySaver

        from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

        print("🔧 Creating COIA system...")
        checkpointer = MemorySaver()
        app = await create_unified_coia_system(checkpointer)

        print("✅ COIA system created successfully")

        # Test bid card search query
        test_message = "Show me kitchen remodeling projects near me"
        session_id = "test_debug_session"

        print(f"🧪 Testing message: '{test_message}'")

        # Invoke COIA chat
        result = await invoke_coia_chat(
            app=app,
            user_message=test_message,
            session_id=session_id,
            contractor_lead_id=None,
            project_id=None
        )

        print("📋 Result keys:", list(result.keys()) if result else "None")

        if result:
            print("💬 Messages:", len(result.get("messages", [])))
            print("🎯 Current mode:", result.get("current_mode"))
            print("🔍 Bid cards attached:", len(result.get("bid_cards_attached", [])))
            print("🤖 AI recommendation:", result.get("tool_results", {}).get("bid_card_search", {}).get("ai_recommendation"))

            # Print the actual messages
            for i, msg in enumerate(result.get("messages", [])):
                print(f"  Message {i}: {type(msg).__name__} - {msg.content[:100]}...")
        else:
            print("❌ Result is None - this is the source of the error!")

        return result

    except Exception as e:
        print(f"❌ Error in direct test: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_bid_card_search_node():
    """Test bid card search node directly"""

    try:
        from langchain_core.messages import HumanMessage

        from agents.coia.bid_card_search_node import bid_card_search_node
        from agents.coia.unified_state import UnifiedCoIAState

        print("🔧 Testing bid card search node directly...")

        # Create test state
        state = UnifiedCoIAState(
            messages=[HumanMessage(content="Show me kitchen remodeling projects near me")],
            session_id="test_node_session",
            user_id=None,
            contractor_lead_id=None,
            contractor_id=None,
            interface="chat",
            current_mode="bid_card_search",
            previous_mode=None,
            mode_confidence=0.8,
            transition_reason="Test",
            last_updated="2025-08-05T23:30:00Z",
            contractor_profile={},
            profile_completeness=0.0,
            company_name=None,
            company_website=None,
            business_info=None,
            research_completed=False,
            research_confirmed=False,
            research_findings=None,
            website_research_status=None,
            intelligence_data=None,
            google_places_data=None,
            returning_contractor_id=None,
            persistent_memory_loaded=False,
            available_capabilities=["web_research", "google_places", "memory"],
            active_tools=[],
            tool_results=None,
            next_action=None,
            completion_ready=False,
            contractor_created=False,
            conversion_successful=False,
            error_state=None,
            original_project_id=None,
            source_channel=None,
            matching_projects_count=0,
            bid_cards_attached=[],
            marketplace_links=[],
            bid_search_criteria=None,
            last_bid_search=None
        )

        print("✅ Test state created")

        # Call the bid card search node
        node_result = await bid_card_search_node(state)

        print("📋 Node result keys:", list(node_result.keys()) if node_result else "None")

        if node_result:
            print("💬 Messages:", len(node_result.get("messages", [])))
            print("🎯 Current mode:", node_result.get("current_mode"))
            print("🔍 Bid cards attached:", len(node_result.get("bid_cards_attached", [])))
        else:
            print("❌ Node result is None!")

        return node_result

    except Exception as e:
        print(f"❌ Error in node test: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run all debug tests"""
    print("🚀 Starting COIA Bid Card Debug Tests")
    print("=" * 50)

    print("\n1️⃣ Testing bid card search node directly...")
    node_result = await test_bid_card_search_node()

    print("\n2️⃣ Testing full COIA chat system...")
    chat_result = await test_coia_chat_direct()

    print("\n📊 Summary:")
    if node_result:
        print("✅ Bid card search node works")
    else:
        print("❌ Bid card search node failed")

    if chat_result:
        print("✅ COIA chat system works")
    else:
        print("❌ COIA chat system failed")

if __name__ == "__main__":
    asyncio.run(main())
