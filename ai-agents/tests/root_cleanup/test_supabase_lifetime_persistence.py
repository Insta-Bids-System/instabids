#!/usr/bin/env python
"""
SUPABASE LIFETIME PERSISTENCE TEST
Uses existing Supabase checkpointer system to test true lifetime persistence
Simulates contractor conversations across days/weeks with real database storage
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

from agents.coia.supabase_checkpointer_simple import create_supabase_checkpointer
from agents.coia.unified_graph import invoke_coia_chat


CONTRACTOR_ID = "mike_lifetime_supabase"

async def simulate_day_1():
    """Day 1: Contractor introduces himself and his business"""
    print("\n============================================================")
    print("DAY 1: CONTRACTOR ONBOARDING")
    print("============================================================")

    # Conversation 1: Introduction
    print("\n[CONVERSATION 1] Introduction")
    result1 = await invoke_coia_chat(
        user_message="Hi, I'm Mike from Elite Roofing. I've been in the roofing business for 12 years and serve the Dallas metro area. I specialize in residential roofing repairs and replacements.",
        contractor_lead_id=CONTRACTOR_ID,
        interface="chat"
    )
    print(f"Response 1: {result1.get('messages', [])[-1].get('content', 'No response')[:200]}...")

    # Conversation 2: Services
    print("\n[CONVERSATION 2] Services offered")
    result2 = await invoke_coia_chat(
        user_message="My main services include roof inspections, emergency repairs, full roof replacements, and gutter work. I'm licensed and insured with $2M coverage.",
        contractor_lead_id=CONTRACTOR_ID,
        interface="chat"
    )
    print(f"Response 2: {result2.get('messages', [])[-1].get('content', 'No response')[:200]}...")

    # Check if profile was extracted
    profile = result2.get("contractor_profile", {})
    success = (
        profile.get("company_name") and
        profile.get("years_in_business") and
        profile.get("service_areas")
    )

    print("\nDAY 1 RESULTS:")
    print(f"Profile extracted: {success}")
    if success:
        print(f"Company: {profile.get('company_name')}")
        print(f"Experience: {profile.get('years_in_business')} years")
        print(f"Areas: {profile.get('service_areas')}")

    return success

async def simulate_day_7():
    """Day 7: Contractor asks about projects (should remember profile)"""
    print("\n============================================================")
    print("DAY 7: PROJECT INQUIRY (1 WEEK LATER)")
    print("============================================================")

    print("\n[CONVERSATION 3] Project inquiry")
    result3 = await invoke_coia_chat(
        user_message="Hey, I'm looking for some emergency roofing projects in Dallas. Are there any homeowners who need immediate roof repairs?",
        contractor_lead_id=CONTRACTOR_ID,
        interface="chat"
    )
    print(f"Response 3: {result3.get('messages', [])[-1].get('content', 'No response')[:200]}...")

    # Check if memory persisted
    profile = result3.get("contractor_profile", {})
    success = (
        profile.get("company_name") == "Elite Roofing" and
        profile.get("years_in_business") == 12
    )

    print("\nDAY 7 RESULTS:")
    print(f"Memory persisted: {success}")
    if profile:
        print(f"Remembered company: {profile.get('company_name')}")
        print(f"Remembered experience: {profile.get('years_in_business')}")

    return success

async def simulate_day_30():
    """Day 30: Contractor discusses bid submission (should remember everything)"""
    print("\n============================================================")
    print("DAY 30: BID SUBMISSION (1 MONTH LATER)")
    print("============================================================")

    print("\n[CONVERSATION 4] Bid discussion")
    result4 = await invoke_coia_chat(
        user_message="I want to submit a bid for that emergency roof repair project I saw. My price would be $8,500 for materials and labor, and I can start within 24 hours.",
        contractor_lead_id=CONTRACTOR_ID,
        interface="chat"
    )
    print(f"Response 4: {result4.get('messages', [])[-1].get('content', 'No response')[:200]}...")

    # Check complete memory persistence
    profile = result4.get("contractor_profile", {})
    success = (
        profile.get("company_name") == "Elite Roofing" and
        profile.get("years_in_business") == 12 and
        "Dallas" in str(profile.get("service_areas", ""))
    )

    print("\nDAY 30 RESULTS:")
    print(f"Complete memory persisted: {success}")
    if profile:
        print(f"Company: {profile.get('company_name')}")
        print(f"Experience: {profile.get('years_in_business')} years")
        print(f"Service areas: {profile.get('service_areas')}")

    return success

async def main():
    """Run complete lifetime persistence test with Supabase"""

    print("======================================================================")
    print("SUPABASE LIFETIME PERSISTENCE TEST")
    print("Using real Supabase database storage for true persistence")
    print("Testing memory across Day 1, Day 7, and Day 30 conversations")
    print("======================================================================")

    try:
        # Test Supabase checkpointer creation
        print("\n[SETUP] Creating Supabase checkpointer...")
        checkpointer = await create_supabase_checkpointer()
        print("✅ Supabase checkpointer created successfully")

        # Run simulations
        day1_success = await simulate_day_1()
        day7_success = await simulate_day_7()
        day30_success = await simulate_day_30()

        # Final results
        print("\n======================================================================")
        print("FINAL TEST RESULTS")
        print("======================================================================")
        print(f"Day 1 Profile Extraction: {'✅ PASS' if day1_success else '❌ FAIL'}")
        print(f"Day 7 Memory Persistence: {'✅ PASS' if day7_success else '❌ FAIL'}")
        print(f"Day 30 Lifetime Memory:   {'✅ PASS' if day30_success else '❌ FAIL'}")

        overall_success_rate = (day1_success + day7_success + day30_success) / 3 * 100
        print(f"\nOverall Success Rate: {overall_success_rate:.1f}%")

        if overall_success_rate >= 100:
            print("🎉 PERFECT! True lifetime persistence working across contractor's lifetime!")
        elif overall_success_rate >= 67:
            print("✅ GOOD! Most memory persisting, minor issues to fix")
        elif overall_success_rate >= 33:
            print("⚠️ PARTIAL! Some persistence working, needs improvement")
        else:
            print("❌ FAILED! Memory not persisting properly")

        return overall_success_rate

    except Exception as e:
        print(f"❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

if __name__ == "__main__":
    asyncio.run(main())
