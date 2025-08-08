#!/usr/bin/env python
"""
SIMPLE TEST OF FIXED SYSTEM
Quick test to verify infinite loop is fixed and basic functionality works
"""

import asyncio
import logging
import os

from dotenv import load_dotenv


# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Set up logging to show less noise
logging.basicConfig(level=logging.WARNING)  # Reduced noise
logger = logging.getLogger(__name__)

from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat


async def test_fixed_system():
    """Test that infinite loop is fixed and basic enrichment works"""
    print("Testing fixed COIA system...")

    try:
        # Create app
        app = await create_unified_coia_system()

        # Test 1: Basic conversation with real contractor data
        print("\n[TEST 1] Basic conversation with contractor profile")
        result = await invoke_coia_chat(
            app=app,
            user_message="Hi, I'm from Elite Remodeling Solutions. We've been in business for 15 years and specialize in luxury kitchen remodeling. Our website is https://eliteremodeling.com.",
            session_id="test_session",
            contractor_lead_id="test_contractor_123"
        )

        # Check if profile was extracted
        profile = result.get("contractor_profile", {})
        company_extracted = profile.get("company_name") == "Elite Remodeling Solutions"
        website_extracted = profile.get("website") == "https://eliteremodeling.com"
        years_extracted = profile.get("years_in_business") == 15

        print(f"Company extracted: {'PASS' if company_extracted else 'FAIL'}")
        print(f"Website extracted: {'PASS' if website_extracted else 'FAIL'}")
        print(f"Years extracted: {'PASS' if years_extracted else 'FAIL'}")

        # Test 2: Follow-up conversation (memory test)
        print("\n[TEST 2] Follow-up conversation - memory test")
        result2 = await invoke_coia_chat(
            app=app,
            user_message="Can you tell me what services my company offers?",
            session_id="test_session",
            contractor_lead_id="test_contractor_123"
        )

        # Check if it remembers the company
        messages = result2.get("messages", [])
        response_text = ""
        if messages:
            response_text = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

        memory_working = "Elite Remodeling" in response_text or "luxury kitchen" in response_text.lower()
        print(f"Memory working: {'PASS' if memory_working else 'FAIL'}")
        print(f"Response: {response_text[:100]}...")

        # Overall success
        success = company_extracted and years_extracted and memory_working
        print(f"\nOVERALL TEST: {'SUCCESS' if success else 'FAILED'}")

        return success

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixed_system())
    if success:
        print("\n✓ System is working - infinite loop fixed, basic enrichment functional")
    else:
        print("\n✗ System still has issues")
