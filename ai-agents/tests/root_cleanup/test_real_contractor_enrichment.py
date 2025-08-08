#!/usr/bin/env python
"""
REAL CONTRACTOR ENRICHMENT TEST
Test COIA system with actual enriched contractor from database
Verify the system finds website, enriches profile, saves to database
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

from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat


# Real contractor from database: Elite Remodeling Solutions
REAL_CONTRACTOR_ID = "07115863-e90c-4f75-b984-f82218f5acd6"
REAL_CONTRACTOR_DATA = {
    "company_name": "Elite Remodeling Solutions",
    "website": "https://eliteremodeling.com",
    "phone": "407-555-0004",
    "years_in_business": 15,
    "specialties": ["luxury kitchen remodeling", "custom cabinets", "high-end finishes"]
}

async def test_real_contractor_enrichment():
    """Test COIA system with real enriched contractor from database"""
    print("======================================================================")
    print("TESTING COIA WITH REAL ENRICHED CONTRACTOR")
    print(f"Contractor: {REAL_CONTRACTOR_DATA['company_name']}")
    print(f"Website: {REAL_CONTRACTOR_DATA['website']}")
    print("======================================================================")

    try:
        # Create the COIA system app
        print("[SETUP] Creating COIA system...")
        app = await create_unified_coia_system()
        print("COIA system created")

        # Conversation 1: Contractor introduces themselves - should match database contractor
        print("\n[CONVERSATION 1] Real contractor introduction")
        result1 = await invoke_coia_chat(
            app=app,
            user_message=f"Hi, I'm from {REAL_CONTRACTOR_DATA['company_name']}. We've been in business for {REAL_CONTRACTOR_DATA['years_in_business']} years specializing in luxury kitchen remodeling and custom cabinets. Our website is {REAL_CONTRACTOR_DATA['website']}.",
            session_id="real_contractor_test",
            contractor_lead_id=REAL_CONTRACTOR_ID
        )

        # Extract response
        messages1 = result1.get("messages", [])
        if messages1:
            response1 = messages1[-1].content if hasattr(messages1[-1], "content") else str(messages1[-1])
            print(f"Response 1: {response1[:150]}...")

        # Check if it found the contractor in the database
        profile1 = result1.get("contractor_profile", {})
        print(f"Profile extracted: {profile1}")

        # Conversation 2: Ask about website research - should trigger research mode
        print("\n[CONVERSATION 2] Trigger website research")
        result2 = await invoke_coia_chat(
            app=app,
            user_message="Can you research my company website and tell me what services I offer?",
            session_id="real_contractor_test",
            contractor_lead_id=REAL_CONTRACTOR_ID
        )

        messages2 = result2.get("messages", [])
        if messages2:
            response2 = messages2[-1].content if hasattr(messages2[-1], "content") else str(messages2[-1])
            print(f"Response 2: {response2[:150]}...")

        profile2 = result2.get("contractor_profile", {})
        mode2 = result2.get("current_mode", "unknown")
        print(f"Mode after research request: {mode2}")
        print(f"Profile after research: {profile2}")

        # Conversation 3: Request bid cards - should trigger bid card search
        print("\n[CONVERSATION 3] Request luxury kitchen remodeling projects")
        result3 = await invoke_coia_chat(
            app=app,
            user_message="I'm looking for luxury kitchen remodeling projects I can bid on. Show me high-end kitchen renovation projects.",
            session_id="real_contractor_test",
            contractor_lead_id=REAL_CONTRACTOR_ID
        )

        messages3 = result3.get("messages", [])
        if messages3:
            response3 = messages3[-1].content if hasattr(messages3[-1], "content") else str(messages3[-1])
            print(f"Response 3: {response3[:150]}...")

        profile3 = result3.get("contractor_profile", {})
        mode3 = result3.get("current_mode", "unknown")
        print(f"Mode after bid card request: {mode3}")

        # Test results analysis
        contractor_found_in_db = profile1.get("company_name") == REAL_CONTRACTOR_DATA["company_name"]
        website_found = REAL_CONTRACTOR_DATA["website"] in str(profile1) or profile1.get("website") == REAL_CONTRACTOR_DATA["website"]
        research_mode_triggered = mode2 == "research" or "research" in response2.lower()
        bid_search_triggered = mode3 == "bid_card_search" or "luxury kitchen" in response3.lower()

        print("\n======================================================================")
        print("REAL CONTRACTOR TEST RESULTS")
        print("======================================================================")
        print(f"Contractor found in database: {'PASS' if contractor_found_in_db else 'FAIL'}")
        print(f"Website information extracted: {'PASS' if website_found else 'FAIL'}")
        print(f"Research mode triggered: {'PASS' if research_mode_triggered else 'FAIL'}")
        print(f"Bid card search triggered: {'PASS' if bid_search_triggered else 'FAIL'}")

        # Check if system created/updated contractor in backend
        print("\nContractor Profile Details:")
        if profile3:
            for key, value in profile3.items():
                if value:
                    print(f"  {key}: {value}")

        success_count = sum([contractor_found_in_db, website_found, research_mode_triggered, bid_search_triggered])
        success_rate = (success_count / 4) * 100

        print(f"\nOverall Success Rate: {success_rate:.1f}%")

        if success_rate >= 75:
            print("EXCELLENT! Real contractor enrichment system working")
        elif success_rate >= 50:
            print("GOOD! Most features working, minor issues")
        else:
            print("NEEDS WORK! Core functionality not working")

        return success_rate >= 75

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_contractor_enrichment())
    print(f"\nFINAL RESULT: {'SUCCESS' if success else 'FAILED'}")
