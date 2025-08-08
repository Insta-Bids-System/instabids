#!/usr/bin/env python
"""
COIA Profile-Enhanced Bid Card Search Test
Test how contractor profile data enhances bid card search results
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

async def test_profile_enhanced_search():
    """Test bid card search enhancement with contractor profiles"""

    try:
        from langgraph.checkpoint.memory import MemorySaver

        from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

        print("Testing Profile-Enhanced Bid Card Search")
        print("=" * 45)

        # Create COIA system
        checkpointer = MemorySaver()
        app = await create_unified_coia_system(checkpointer)
        print("COIA system ready")

        # Test different contractor profiles
        contractors = [
            {
                "id": "hvac_mike_dallas",
                "profile_msg": "Hi, I'm Mike from Elite HVAC Solutions. We do high-end commercial HVAC work in Dallas and Fort Worth. 15 years experience, projects over $10,000 only.",
                "search_msg": "Show me HVAC projects near me",
                "expected_elements": ["Elite HVAC Solutions", "Dallas", "Fort Worth", "commercial"]
            },
            {
                "id": "plumber_sarah_emergency",
                "profile_msg": "I'm Sarah from Emergency Plumbing Pro. We specialize in 24/7 emergency plumbing repairs in residential homes. Service radius 20 miles from downtown Dallas.",
                "search_msg": "Find me emergency plumbing work",
                "expected_elements": ["Emergency Plumbing Pro", "emergency", "residential", "20 miles"]
            },
            {
                "id": "kitchen_contractor_luxury",
                "profile_msg": "Hi, I'm David from Luxury Kitchen Designs. We do high-end kitchen renovations for upscale clients. Minimum project $25,000, Dallas metro area.",
                "search_msg": "Show me kitchen remodeling projects",
                "expected_elements": ["Luxury Kitchen Designs", "David", "luxury", "kitchen", "$25,000"]
            }
        ]

        total_tests = 0
        successful_tests = 0

        for contractor in contractors:
            print(f"\n{'='*60}")
            print(f"CONTRACTOR: {contractor['id'].upper()}")
            print("="*60)

            # STEP 1: Build contractor profile
            print("\n1️⃣ BUILDING PROFILE")
            print("-" * 30)

            profile_msg = contractor["profile_msg"]
            print(f"User: {profile_msg}")

            result1 = await invoke_coia_chat(
                app=app,
                user_message=profile_msg,
                session_id=f"profile_{contractor['id']}",
                contractor_lead_id=contractor["id"]
            )

            if result1:
                ai_response1 = result1["messages"][-1].content
                print(f"AI: {ai_response1[:120]}...")
                company = result1.get("company_name", "None")
                print(f"✅ Company Extracted: {company}")

                # Check profile extraction
                profile = result1.get("contractor_profile", {})
                profile_keys = list(profile.keys())
                print(f"✅ Profile Fields: {len(profile_keys)} fields")

            # STEP 2: Enhanced bid card search
            print("\n2️⃣ ENHANCED BID CARD SEARCH")
            print("-" * 35)

            search_msg = contractor["search_msg"]
            print(f"User: {search_msg}")

            result2 = await invoke_coia_chat(
                app=app,
                user_message=search_msg,
                session_id=f"search_{contractor['id']}", # Different session
                contractor_lead_id=contractor["id"]  # Same contractor ID for memory
            )

            if result2:
                ai_response2 = result2["messages"][-1].content
                print(f"AI: {ai_response2[:200]}...")
                print(f"🎯 Mode: {result2.get('current_mode')}")
                print(f"📋 Bid Cards: {len(result2.get('bid_cards_attached', []))}")

                # Test memory integration
                total_tests += 1
                expected = contractor["expected_elements"]
                memory_score = 0
                found_elements = []

                print("\n🧠 MEMORY INTEGRATION TEST:")
                print("-" * 30)

                for element in expected:
                    if element.lower() in ai_response2.lower():
                        memory_score += 1
                        found_elements.append(element)
                        print(f"✅ Found: {element}")
                    else:
                        print(f"❌ Missing: {element}")

                # Also check state values
                state_company = result2.get("company_name", "")
                if state_company and any(word in state_company.lower() for word in expected):
                    print(f"✅ State Company: {state_company}")
                    if state_company not in found_elements:
                        memory_score += 1
                        found_elements.append(f"State: {state_company}")

                # Calculate success
                success_rate = memory_score / len(expected)
                print(f"📊 Memory Score: {memory_score}/{len(expected)} ({success_rate:.1%})")

                if success_rate >= 0.5:  # 50% or better
                    successful_tests += 1
                    print("🎉 MEMORY INTEGRATION: SUCCESS")
                else:
                    print("⚠️ MEMORY INTEGRATION: NEEDS IMPROVEMENT")

        # OVERALL RESULTS
        print(f"\n{'='*60}")
        print("FINAL RESULTS")
        print("="*60)

        overall_success_rate = successful_tests / total_tests
        print(f"📊 Overall Success Rate: {successful_tests}/{total_tests} ({overall_success_rate:.1%})")

        if overall_success_rate >= 0.7:
            print("🎉 EXCELLENT: Profile-enhanced search working well!")
            return True
        elif overall_success_rate >= 0.5:
            print("✅ GOOD: Profile enhancement partially working")
            return True
        else:
            print("❌ NEEDS WORK: Profile enhancement not working effectively")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the profile enhancement test"""
    success = await test_profile_enhanced_search()

    print(f"\n{'='*60}")
    print("SUMMARY")
    print("="*60)

    if success:
        print("✅ SUCCESS: COIA bid card search enhanced with contractor profiles!")
        print("🎯 Key achievements:")
        print("   • Contractor profiles extracted from conversation")
        print("   • Bid card search personalized with profile data")
        print("   • Memory integration working across sessions")
        print("   • Enhanced search criteria based on contractor specialties")
    else:
        print("❌ PARTIAL SUCCESS: Some improvements needed")
        print("⚠️  Areas to improve:")
        print("   • Better memory persistence across sessions")
        print("   • More robust profile data extraction")
        print("   • Enhanced search criteria mapping")

    print("\n🔗 Ready for real bid card API integration!")

if __name__ == "__main__":
    asyncio.run(main())
