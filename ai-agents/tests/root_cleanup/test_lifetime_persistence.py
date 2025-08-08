#!/usr/bin/env python
"""
TRUE LIFETIME PERSISTENCE TEST
Simulates a contractor's journey over time with COIA
Tests that ALL context is remembered across days/weeks/months
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

# Use a consistent contractor ID for ALL tests
CONTRACTOR_ID = "mike_lifetime_test_123"

async def day_1_onboarding():
    """Day 1: Contractor signs up and has initial conversation"""
    print("\n" + "="*60)
    print("DAY 1: INITIAL ONBOARDING")
    print("="*60)

    from langgraph.checkpoint.memory import MemorySaver

    from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

    checkpointer = MemorySaver()
    app = await create_unified_coia_system(checkpointer)

    # Conversation 1: Introduction
    print("\nConversation 1: Introduction")
    print("-"*30)
    result1 = await invoke_coia_chat(
        app=app,
        user_message="Hi, I'm Mike from Dallas HVAC Pro. We've been in business for 15 years, specializing in emergency HVAC repairs in the Dallas area.",
        session_id="day1_conv1",
        contractor_lead_id=CONTRACTOR_ID
    )

    profile1 = result1.get("contractor_profile", {})
    print(f"Profile captured: Company={profile1.get('company_name')}, Years={profile1.get('years_in_business')}")

    # Conversation 2: More details
    print("\nConversation 2: Adding details")
    print("-"*30)
    result2 = await invoke_coia_chat(
        app=app,
        user_message="We handle projects from $5,000 to $50,000. Our team has 8 technicians. We're licensed and insured.",
        session_id="day1_conv2",
        contractor_lead_id=CONTRACTOR_ID
    )

    profile2 = result2.get("contractor_profile", {})
    print(f"Profile updated: Team size={profile2.get('team_size')}, Min project=${profile2.get('minimum_project_size')}")

    # Conversation 3: First bid search
    print("\nConversation 3: First bid search")
    print("-"*30)
    result3 = await invoke_coia_chat(
        app=app,
        user_message="Show me emergency HVAC projects in Dallas",
        session_id="day1_conv3",
        contractor_lead_id=CONTRACTOR_ID
    )

    mode3 = result3.get("current_mode")
    bid_cards3 = result3.get("bid_cards_attached", [])
    print(f"Mode: {mode3}, Bid cards found: {len(bid_cards3)}")

    # Check what was remembered
    final_profile = result3.get("contractor_profile", {})
    remembered_fields = [k for k, v in final_profile.items() if v]
    print(f"\nDay 1 Summary - Profile fields remembered: {len(remembered_fields)}")
    print(f"Key data: {final_profile.get('company_name')}, {final_profile.get('years_in_business')} years, {final_profile.get('team_size')} team members")

    return app, checkpointer, len(remembered_fields)

async def day_7_return():
    """Day 7: Contractor returns after a week"""
    print("\n" + "="*60)
    print("DAY 7: CONTRACTOR RETURNS")
    print("="*60)

    from langgraph.checkpoint.memory import MemorySaver

    from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

    # CRITICAL: Use same checkpointer type to test persistence
    checkpointer = MemorySaver()
    app = await create_unified_coia_system(checkpointer)

    # Test if system remembers the contractor
    print("\nConversation 4: Testing memory")
    print("-"*30)
    result4 = await invoke_coia_chat(
        app=app,
        user_message="Do you remember me? What's my company name?",
        session_id="day7_conv1",
        contractor_lead_id=CONTRACTOR_ID
    )

    response4 = result4["messages"][-1].content
    profile4 = result4.get("contractor_profile", {})

    # Check if Dallas HVAC Pro is mentioned
    remembers_company = "Dallas HVAC Pro" in response4 or "dallas hvac" in response4.lower()
    print(f"Remembers company name: {remembers_company}")
    print(f"Profile has company: {profile4.get('company_name')}")

    # Add new preference
    print("\nConversation 5: Adding preferences")
    print("-"*30)
    result5 = await invoke_coia_chat(
        app=app,
        user_message="I prefer commercial projects over residential. Also expanding to Fort Worth now.",
        session_id="day7_conv2",
        contractor_lead_id=CONTRACTOR_ID
    )

    profile5 = result5.get("contractor_profile", {})
    print(f"Service areas: {profile5.get('service_areas')}")

    # Search with new criteria
    print("\nConversation 6: Search with memory")
    print("-"*30)
    result6 = await invoke_coia_chat(
        app=app,
        user_message="Find me commercial HVAC projects in Dallas or Fort Worth",
        session_id="day7_conv3",
        contractor_lead_id=CONTRACTOR_ID
    )

    mode6 = result6.get("current_mode")
    response6 = result6["messages"][-1].content

    # Check personalization
    personalized = (
        ("Dallas" in response6 or "Fort Worth" in response6) and
        ("commercial" in response6.lower() or "HVAC" in response6)
    )
    print(f"Search personalized: {personalized}")

    profile_final = result6.get("contractor_profile", {})
    remembered_fields = [k for k, v in profile_final.items() if v]
    print(f"\nDay 7 Summary - Profile fields remembered: {len(remembered_fields)}")

    return len(remembered_fields), remembers_company, personalized

async def day_30_bidding():
    """Day 30: Full bidding workflow with history"""
    print("\n" + "="*60)
    print("DAY 30: BIDDING WITH FULL CONTEXT")
    print("="*60)

    from langgraph.checkpoint.memory import MemorySaver

    from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

    checkpointer = MemorySaver()
    app = await create_unified_coia_system(checkpointer)

    # Test complete context
    print("\nConversation 7: Contextual greeting")
    print("-"*30)
    result7 = await invoke_coia_chat(
        app=app,
        user_message="Hey, how's business been? Any new emergency HVAC projects?",
        session_id="day30_conv1",
        contractor_lead_id=CONTRACTOR_ID
    )

    response7 = result7["messages"][-1].content
    profile7 = result7.get("contractor_profile", {})

    # Should remember: company, specialization, service areas
    context_check = {
        "company": "Dallas HVAC" in response7 or profile7.get("company_name") == "Dallas Hvac Pro",
        "emergency": "emergency" in response7.lower() or "emergency" in profile7.get("specializations", []),
        "areas": any(area in response7 for area in ["Dallas", "Fort Worth"]) or len(profile7.get("service_areas", [])) > 0
    }

    print(f"Context remembered: {sum(context_check.values())}/3")
    for key, remembered in context_check.items():
        print(f"  - {key}: {remembered}")

    # Simulate bid submission
    print("\nConversation 8: Bid submission with context")
    print("-"*30)
    result8 = await invoke_coia_chat(
        app=app,
        user_message="I want to bid $15,000 on that emergency HVAC project. We can start immediately.",
        session_id="day30_conv2",
        contractor_lead_id=CONTRACTOR_ID
    )

    response8 = result8["messages"][-1].content

    # Check if bid context includes profile info
    bid_context = (
        "$15,000" in response8 and
        ("emergency" in response8.lower() or "immediately" in response8.lower())
    )
    print(f"Bid context maintained: {bid_context}")

    # Final comprehensive check
    print("\nConversation 9: Comprehensive memory test")
    print("-"*30)
    result9 = await invoke_coia_chat(
        app=app,
        user_message="Can you summarize everything you know about my business?",
        session_id="day30_conv3",
        contractor_lead_id=CONTRACTOR_ID
    )

    response9 = result9["messages"][-1].content
    profile9 = result9.get("contractor_profile", {})

    # Count what's remembered
    memory_points = {
        "Company name": profile9.get("company_name") is not None,
        "Years in business": profile9.get("years_in_business") is not None,
        "Team size": profile9.get("team_size") is not None,
        "Service areas": len(profile9.get("service_areas", [])) > 0,
        "Specializations": len(profile9.get("specializations", [])) > 0,
        "Min project size": profile9.get("minimum_project_size") is not None,
        "Preferences": profile9.get("preferred_project_types") is not None
    }

    print("\nDay 30 Final Memory Check:")
    for item, remembered in memory_points.items():
        print(f"  {item}: {'YES' if remembered else 'NO'}")

    total_remembered = sum(memory_points.values())
    print(f"\nTotal memory points: {total_remembered}/7")

    return total_remembered, context_check, bid_context

async def main():
    """Run the complete lifetime persistence test"""
    print("\n" + "="*70)
    print("CONTRACTOR LIFETIME PERSISTENCE TEST")
    print("Testing that COIA remembers EVERYTHING across the contractor's lifetime")
    print("="*70)

    # Day 1: Onboarding
    app, checkpointer, day1_fields = await day_1_onboarding()

    # Day 7: Return visit
    day7_fields, remembers_company, personalized = await day_7_return()

    # Day 30: Full context
    day30_memory, context_check, bid_context = await day_30_bidding()

    # FINAL ASSESSMENT
    print("\n" + "="*70)
    print("LIFETIME PERSISTENCE TEST RESULTS")
    print("="*70)

    print("\nMemory Progression:")
    print(f"  Day 1: {day1_fields} fields captured")
    print(f"  Day 7: {day7_fields} fields retained")
    print(f"  Day 30: {day30_memory}/7 memory points")

    print("\nKey Capabilities:")
    print(f"  Remembers company after a week: {remembers_company}")
    print(f"  Personalizes searches: {personalized}")
    print(f"  Maintains bid context: {bid_context}")
    print(f"  Full context awareness: {sum(context_check.values())}/3")

    # Success criteria
    success_criteria = [
        day1_fields >= 3,  # Captures initial profile
        remembers_company,  # Remembers after time gap
        personalized,  # Uses memory for personalization
        day30_memory >= 5,  # Retains most information
        sum(context_check.values()) >= 2  # Context aware
    ]

    success_rate = sum(success_criteria) / len(success_criteria)

    print(f"\n{'='*70}")
    if success_rate >= 0.8:
        print("SUCCESS: TRUE LIFETIME PERSISTENCE VERIFIED!")
        print("COIA maintains contractor context across entire lifetime")
    elif success_rate >= 0.6:
        print("PARTIAL SUCCESS: Some persistence working")
        print("Memory partially maintained but not fully persistent")
    else:
        print("FAILURE: Lifetime persistence NOT working")
        print("Memory is not persisting across contractor lifetime")

    print(f"Success rate: {success_rate:.0%}")

    return success_rate

if __name__ == "__main__":
    asyncio.run(main())
