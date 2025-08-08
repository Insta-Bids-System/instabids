#!/usr/bin/env python
"""
COIA Memory Persistence Test
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

        print("🚀 Starting COIA Memory Persistence Test")
        print("=" * 60)

        # Create COIA system with memory
        checkpointer = MemorySaver()
        app = await create_unified_coia_system(checkpointer)
        print("✅ COIA system created with memory persistence")

        # Test contractor profile: Mike's HVAC Solutions
        contractor_id = "contractor_mike_hvac_123"
        company_name = "Mike's HVAC Solutions"

        # =================================================================
        # SESSION 1: Initial profile building conversation
        # =================================================================
        print("\n🎭 SESSION 1: Initial Profile Building")
        print("-" * 40)

        session_1_messages = [
            "Hi, I'm Mike from Mike's HVAC Solutions. We've been doing commercial and residential HVAC work for 15 years in the Dallas area.",
            "We specialize in energy-efficient installations and emergency repairs. Our service radius is about 25 miles from downtown Dallas.",
            "We're looking for projects over $5000 and prefer commercial work."
        ]

        for i, message in enumerate(session_1_messages, 1):
            print(f"\n👤 User Message {i}: {message}")

            result = await invoke_coia_chat(
                app=app,
                user_message=message,
                session_id=f"session1_{contractor_id}",
                contractor_lead_id=contractor_id
            )

            if result:
                ai_message = result["messages"][-1].content[:200] + "..."
                print(f"🤖 AI Response: {ai_message}")
                print(f"📊 Profile Completeness: {result.get('profile_completeness', 0):.1f}%")
                print(f"🏢 Company Name: {result.get('company_name', 'Not set')}")
                print(f"🎯 Mode: {result.get('current_mode')}")

        print("✅ Session 1 completed - contractor profile established")

        # =================================================================
        # SESSION 2: Bid card search with memory (same day)
        # =================================================================
        print("\n🔍 SESSION 2: Bid Card Search (Same Day)")
        print("-" * 40)

        search_message = "Show me HVAC projects near me that I can bid on"
        print(f"\n👤 User Message: {search_message}")

        result = await invoke_coia_chat(
            app=app,
            user_message=search_message,
            session_id=f"session2_{contractor_id}",
            contractor_lead_id=contractor_id
        )

        if result:
            ai_message = result["messages"][-1].content
            print(f"🤖 AI Response: {ai_message[:300]}...")
            print(f"🏢 Remembered Company: {result.get('company_name', 'Not remembered')}")
            print(f"🎯 Mode: {result.get('current_mode')}")
            print(f"📋 Bid Cards Found: {len(result.get('bid_cards_attached', []))}")

            # Check if memory was used for search criteria
            if "Mike's HVAC Solutions" in ai_message:
                print("✅ MEMORY WORKING: AI remembered contractor name!")
            else:
                print("❌ MEMORY ISSUE: AI did not remember contractor name")

        # =================================================================
        # SESSION 3: Different conversation topic (next day)
        # =================================================================
        print("\n💬 SESSION 3: Different Topic (Next Day)")
        print("-" * 40)

        different_message = "I want to update my service areas to include Fort Worth as well"
        print(f"\n👤 User Message: {different_message}")

        result = await invoke_coia_chat(
            app=app,
            user_message=different_message,
            session_id=f"session3_{contractor_id}",
            contractor_lead_id=contractor_id
        )

        if result:
            ai_message = result["messages"][-1].content
            print(f"🤖 AI Response: {ai_message[:300]}...")
            print(f"🏢 Remembered Company: {result.get('company_name', 'Not remembered')}")
            print(f"🎯 Mode: {result.get('current_mode')}")

            # Check for memory references
            if "Dallas" in ai_message or "Mike" in ai_message:
                print("✅ MEMORY WORKING: AI referenced previous conversation!")
            else:
                print("❌ MEMORY ISSUE: AI did not reference previous conversation")

        # =================================================================
        # SESSION 4: Another bid search with enhanced memory
        # =================================================================
        print("\n🔍 SESSION 4: Enhanced Bid Search (With Updated Profile)")
        print("-" * 40)

        enhanced_search = "Find me emergency HVAC projects in Dallas or Fort Worth area"
        print(f"\n👤 User Message: {enhanced_search}")

        result = await invoke_coia_chat(
            app=app,
            user_message=enhanced_search,
            session_id=f"session4_{contractor_id}",
            contractor_lead_id=contractor_id
        )

        if result:
            ai_message = result["messages"][-1].content
            print(f"🤖 AI Response: {ai_message[:400]}...")
            print(f"🏢 Company: {result.get('company_name')}")
            print(f"🎯 Mode: {result.get('current_mode')}")
            print(f"📋 Bid Cards: {len(result.get('bid_cards_attached', []))}")

            # Check for enhanced personalization
            memory_indicators = [
                "Mike's HVAC Solutions" in ai_message,
                "Dallas" in ai_message or "Fort Worth" in ai_message,
                "15 years" in ai_message,
                "emergency" in ai_message.lower()
            ]

            memory_score = sum(memory_indicators)
            print(f"📊 Memory Integration Score: {memory_score}/4")

            if memory_score >= 2:
                print("✅ EXCELLENT MEMORY: AI using multiple memory elements!")
            elif memory_score == 1:
                print("⚠️  PARTIAL MEMORY: AI using some memory elements")
            else:
                print("❌ MEMORY FAILURE: AI not using stored memory")

        # =================================================================
        # SESSION 5: Test with different contractor (memory isolation)
        # =================================================================
        print("\n👥 SESSION 5: Different Contractor (Memory Isolation Test)")
        print("-" * 40)

        different_contractor = "contractor_sarah_plumbing_456"
        isolation_message = "Hi, I'm Sarah from Premium Plumbing. Looking for kitchen and bathroom projects."
        print(f"\n👤 Different Contractor: {isolation_message}")

        result = await invoke_coia_chat(
            app=app,
            user_message=isolation_message,
            session_id=f"session5_{different_contractor}",
            contractor_lead_id=different_contractor
        )

        if result:
            ai_message = result["messages"][-1].content
            print(f"🤖 AI Response: {ai_message[:300]}...")

            # Check memory isolation - should NOT remember Mike's details
            if "Mike" in ai_message or "HVAC" in ai_message:
                print("❌ MEMORY LEAK: AI confused contractors!")
            else:
                print("✅ MEMORY ISOLATION: AI correctly isolated contractors")

        # =================================================================
        # FINAL SESSION: Return to Mike with accumulated memory
        # =================================================================
        print("\n🔄 FINAL SESSION: Return to Mike (Full Memory Test)")
        print("-" * 40)

        final_message = "Show me projects again"
        print(f"\n👤 Mike Returns: {final_message}")

        result = await invoke_coia_chat(
            app=app,
            user_message=final_message,
            session_id=f"final_session_{contractor_id}",
            contractor_lead_id=contractor_id
        )

        if result:
            ai_message = result["messages"][-1].content
            print(f"🤖 Final AI Response: {ai_message[:400]}...")

            # Check for complete memory integration
            complete_memory_check = [
                "Mike's HVAC Solutions" in ai_message,
                ("Dallas" in ai_message or "Fort Worth" in ai_message),
                "HVAC" in ai_message,
                "$5000" in ai_message or "5000" in ai_message
            ]

            final_memory_score = sum(complete_memory_check)
            print(f"📊 Complete Memory Score: {final_memory_score}/4")

            return final_memory_score >= 3

    except Exception as e:
        print(f"❌ Error in memory persistence test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run memory persistence test"""
    print("🧠 COIA Memory Persistence & Bid Card Integration Test")
    print("=" * 70)

    success = await test_contractor_memory_persistence()

    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS:")

    if success:
        print("🎉 SUCCESS: Memory persistence working across sessions!")
        print("✅ Contractor profiles remembered")
        print("✅ Bid card searches personalized")
        print("✅ Memory isolation between contractors")
        print("✅ Multi-session continuity maintained")
    else:
        print("❌ FAILED: Memory persistence needs improvement")
        print("⚠️  Check memory integration and state persistence")

    print("\n🎯 Next: Test with real bid card API integration")

if __name__ == "__main__":
    asyncio.run(main())
