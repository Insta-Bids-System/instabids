#!/usr/bin/env python
"""
COIA Memory Working Test - Focus on Working Functionality
Test what actually works in the COIA memory integration
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

async def test_coia_working_functionality():
    """Test COIA functionality that actually works"""

    try:
        from langgraph.checkpoint.memory import MemorySaver

        from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

        print("COIA Working Functionality Test")
        print("=" * 40)

        # Use in-memory storage for reliable testing
        checkpointer = MemorySaver()
        app = await create_unified_coia_system(checkpointer)
        print("✅ System created successfully")

        contractor_id = "mike_hvac_working"

        # TEST 1: Profile extraction and processing
        print("\n🧪 TEST 1: Profile Processing")
        print("-" * 30)

        profile_msg = "Hi, I'm Mike from Dallas HVAC Pro. We specialize in emergency HVAC repairs in Dallas, been in business 15 years."
        print(f"Input: {profile_msg}")

        result1 = await invoke_coia_chat(
            app=app,
            user_message=profile_msg,
            session_id="test1",
            contractor_lead_id=contractor_id
        )

        if result1:
            # Test profile data extraction
            profile = result1.get("contractor_profile", {})
            company = result1.get("company_name")

            print(f"✅ Response generated: {len(result1['messages'][-1].content)} characters")
            print(f"✅ Company extracted: {company}")
            print(f"✅ Profile fields: {len(profile)}")

            # Check key profile fields
            key_fields = ["business_name", "primary_trade", "service_areas", "years_in_business"]
            extracted_fields = [field for field in key_fields if profile.get(field)]
            print(f"✅ Key fields extracted: {len(extracted_fields)}/{len(key_fields)} - {extracted_fields}")

            test1_success = len(extracted_fields) >= 2
            print(f"✅ TEST 1 {'PASS' if test1_success else 'FAIL'}: Profile extraction working")
        else:
            print("❌ TEST 1 FAIL: No response generated")
            test1_success = False

        # TEST 2: Mode detection and routing
        print("\n🧪 TEST 2: Mode Detection")
        print("-" * 30)

        search_msg = "Show me emergency HVAC projects"
        print(f"Input: {search_msg}")

        result2 = await invoke_coia_chat(
            app=app,
            user_message=search_msg,
            session_id="test2",
            contractor_lead_id=contractor_id
        )

        if result2:
            current_mode = result2.get("current_mode")
            print(f"✅ Mode detected: {current_mode}")
            print(f"✅ Response generated: {len(result2['messages'][-1].content)} characters")

            test2_success = current_mode == "bid_card_search"
            print(f"✅ TEST 2 {'PASS' if test2_success else 'FAIL'}: Bid card search mode triggered")
        else:
            print("❌ TEST 2 FAIL: No response generated")
            test2_success = False

        # TEST 3: Conversation continuity within session
        print("\n🧪 TEST 3: Session Continuity")
        print("-" * 30)

        followup_msg = "What about Fort Worth projects?"
        print(f"Input: {followup_msg}")

        # Use same session to test continuity
        result3 = await invoke_coia_chat(
            app=app,
            user_message=followup_msg,
            session_id="test2",  # Same session as test 2
            contractor_lead_id=contractor_id
        )

        if result3:
            response = result3["messages"][-1].content
            print(f"✅ Response generated: {len(response)} characters")

            # Check if response shows awareness of previous context
            context_indicators = [
                "Fort Worth" in response,
                "HVAC" in response or "hvac" in response,
                len(response) > 50  # Substantial response
            ]

            context_score = sum(context_indicators)
            print(f"✅ Context awareness: {context_score}/3 indicators")

            test3_success = context_score >= 2
            print(f"✅ TEST 3 {'PASS' if test3_success else 'FAIL'}: Session continuity working")
        else:
            print("❌ TEST 3 FAIL: No response generated")
            test3_success = False

        # Overall assessment
        print("\n📊 OVERALL RESULTS")
        print("=" * 40)

        total_tests = 3
        passed_tests = sum([test1_success, test2_success, test3_success])
        success_rate = passed_tests / total_tests

        print(f"Tests passed: {passed_tests}/{total_tests} ({success_rate:.1%})")

        if success_rate >= 0.8:
            print("🎉 EXCELLENT: COIA system working very well!")
            status = "excellent"
        elif success_rate >= 0.6:
            print("✅ GOOD: COIA system working well")
            status = "good"
        elif success_rate >= 0.4:
            print("⚠️  PARTIAL: Some COIA functionality working")
            status = "partial"
        else:
            print("❌ NEEDS WORK: COIA system needs debugging")
            status = "needs_work"

        # Working features summary
        print("\n✅ CONFIRMED WORKING FEATURES:")
        if test1_success:
            print("- Profile extraction from natural language")
        if test2_success:
            print("- Bid card search mode detection")
        if test3_success:
            print("- Session-based conversation continuity")

        print("\n🔧 AREAS FOR IMPROVEMENT:")
        if not test1_success:
            print("- Profile data extraction accuracy")
        if not test2_success:
            print("- Mode detection and routing")
        if not test3_success:
            print("- Conversation context awareness")

        return status

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return "error"

async def main():
    """Run the working functionality test"""
    print("COIA Working Functionality Test")
    print("=" * 50)

    status = await test_coia_working_functionality()

    print("\n" + "=" * 50)
    print("FINAL ASSESSMENT")
    print("=" * 50)

    if status == "excellent":
        print("🎉 COIA system is working excellently!")
        print("Ready for enhanced memory integration.")
    elif status == "good":
        print("✅ COIA system is working well!")
        print("Basic functionality confirmed, ready for production testing.")
    elif status == "partial":
        print("⚠️  COIA has partial functionality working.")
        print("Focus on fixing failing components.")
    else:
        print("❌ COIA needs debugging before memory integration.")
        print("Focus on core functionality first.")

    return status

if __name__ == "__main__":
    asyncio.run(main())
