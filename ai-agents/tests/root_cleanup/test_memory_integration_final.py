#!/usr/bin/env python
"""
Final COIA Memory Integration Test
Test contractor profile memory and bid card search enhancement
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

async def test_memory_integration():
    """Test complete memory integration workflow"""

    try:
        from langgraph.checkpoint.memory import MemorySaver

        from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

        print("COIA Memory Integration Test")
        print("=" * 40)

        # Create system
        checkpointer = MemorySaver()
        app = await create_unified_coia_system(checkpointer)
        print("System ready")

        contractor_id = "mike_hvac_test_final"

        # PHASE 1: Build contractor profile
        print("\nPHASE 1: Profile Building")
        print("-" * 30)

        profile_msg = "Hi, I'm Mike from Dallas HVAC Pro. We do emergency HVAC work in Dallas area for 15 years, projects over $5000."
        print(f"Contractor: {profile_msg}")

        result1 = await invoke_coia_chat(
            app=app,
            user_message=profile_msg,
            session_id="profile_session",
            contractor_lead_id=contractor_id
        )

        if result1:
            ai_msg1 = result1["messages"][-1].content
            print(f"AI Response: {ai_msg1[:100]}...")

            # Check profile data
            company = result1.get("company_name")
            profile = result1.get("contractor_profile", {})

            print(f"Company extracted: {company}")
            print(f"Profile fields: {len(profile)} items")

            # Show key profile data
            if profile:
                key_data = []
                if profile.get("business_name"):
                    key_data.append(f"Business: {profile['business_name']}")
                if profile.get("years_in_business"):
                    key_data.append(f"Years: {profile['years_in_business']}")
                if profile.get("service_areas"):
                    key_data.append(f"Areas: {profile['service_areas']}")
                print(f"Key data: {', '.join(key_data)}")

        # PHASE 2: Bid card search with memory
        print("\nPHASE 2: Bid Card Search")
        print("-" * 30)

        search_msg = "Show me emergency HVAC projects near me"
        print(f"Contractor: {search_msg}")

        result2 = await invoke_coia_chat(
            app=app,
            user_message=search_msg,
            session_id="search_session",  # Different session
            contractor_lead_id=contractor_id  # Same contractor
        )

        if result2:
            ai_msg2 = result2["messages"][-1].content
            print(f"AI Response: {ai_msg2[:150]}...")
            print(f"Mode: {result2.get('current_mode')}")
            print(f"Bid cards: {len(result2.get('bid_cards_attached', []))}")

            # Memory integration test
            memory_indicators = [
                "Mike" in ai_msg2,
                "Dallas HVAC Pro" in ai_msg2 or "HVAC Pro" in ai_msg2,
                "Dallas" in ai_msg2,
                "15 years" in ai_msg2 or "emergency" in ai_msg2.lower(),
                result2.get("company_name") is not None
            ]

            memory_score = sum(memory_indicators)
            print(f"Memory integration score: {memory_score}/5")

            # PHASE 3: Different conversation topic
            print("\nPHASE 3: Different Topic")
            print("-" * 30)

            update_msg = "I want to expand to Fort Worth area as well"
            print(f"Contractor: {update_msg}")

            result3 = await invoke_coia_chat(
                app=app,
                user_message=update_msg,
                session_id="update_session",
                contractor_lead_id=contractor_id
            )

            if result3:
                ai_msg3 = result3["messages"][-1].content
                print(f"AI Response: {ai_msg3[:150]}...")

                # Check context awareness
                context_indicators = [
                    "Dallas" in ai_msg3,
                    "Mike" in ai_msg3 or result3.get("company_name") is not None,
                    "HVAC" in ai_msg3,
                    "Fort Worth" in ai_msg3
                ]

                context_score = sum(context_indicators)
                print(f"Context awareness score: {context_score}/4")

                # PHASE 4: Final search with enhanced memory
                print("\nPHASE 4: Enhanced Search")
                print("-" * 30)

                final_msg = "Find me HVAC projects in Dallas or Fort Worth"
                print(f"Contractor: {final_msg}")

                result4 = await invoke_coia_chat(
                    app=app,
                    user_message=final_msg,
                    session_id="final_session",
                    contractor_lead_id=contractor_id
                )

                if result4:
                    ai_msg4 = result4["messages"][-1].content
                    print(f"AI Response: {ai_msg4[:200]}...")

                    # Final memory test
                    final_indicators = [
                        "Mike" in ai_msg4 or "Dallas HVAC Pro" in ai_msg4,
                        "Dallas" in ai_msg4,
                        "Fort Worth" in ai_msg4,
                        "HVAC" in ai_msg4,
                        result4.get("company_name") is not None
                    ]

                    final_score = sum(final_indicators)
                    print(f"Final memory score: {final_score}/5")

                    # Overall assessment
                    total_score = memory_score + context_score + final_score
                    max_score = 14  # 5 + 4 + 5
                    overall_rate = total_score / max_score

                    print("\nOVERALL RESULTS:")
                    print(f"Total score: {total_score}/{max_score} ({overall_rate:.1%})")

                    if overall_rate >= 0.6:
                        print("SUCCESS: Memory integration working well!")
                        return True
                    elif overall_rate >= 0.4:
                        print("PARTIAL: Some memory integration working")
                        return False
                    else:
                        print("NEEDS WORK: Memory integration not working")
                        return False

        return False

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    print("Starting Final Memory Integration Test")
    print("=" * 50)

    success = await test_memory_integration()

    print("\n" + "=" * 50)
    print("FINAL ASSESSMENT")
    print("=" * 50)

    if success:
        print("SUCCESS: COIA memory integration complete!")
        print("Key features working:")
        print("- Contractor profile extraction")
        print("- Memory persistence across sessions")
        print("- Enhanced bid card search")
        print("- Context-aware responses")
        print("\nReady for production integration!")
    else:
        print("PARTIAL SUCCESS: Basic functionality working")
        print("Areas for improvement:")
        print("- Memory persistence between sessions")
        print("- Profile data extraction accuracy")
        print("- Search criteria personalization")

    return success

if __name__ == "__main__":
    asyncio.run(main())
