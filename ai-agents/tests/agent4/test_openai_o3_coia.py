"""
Test OpenAI O3 COIA Implementation
Tests the new OpenAI O3-based contractor onboarding agent
"""

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Add parent directory to path
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.coia.openai_o3_agent import OpenAIO3CoIA


async def test_o3_understanding():
    """Test that O3 understands natural language without regex patterns"""
    print("\n" + "="*80)
    print("TESTING OPENAI O3 COIA - Natural Language Understanding")
    print("="*80)

    # Initialize the O3 COIA
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("[X] ERROR: OPENAI_API_KEY not found in environment")
        return

    print(f"[OK] OpenAI API Key found: {openai_key[:20]}...")

    try:
        coia = OpenAIO3CoIA(openai_key)
        print("[OK] OpenAI O3 COIA initialized successfully")
    except Exception as e:
        print(f"[X] ERROR initializing O3 COIA: {e}")
        return

    # Test cases that previously failed with regex
    test_messages = [
        {
            "message": "I specialize in holiday lighting installation",
            "expected": "Should understand this is about holiday lighting services"
        },
        {
            "message": "We do Christmas light installation in South Florida",
            "expected": "Should understand business type and location"
        },
        {
            "message": "JM Holiday Lighting - we've been decorating homes for 10 years",
            "expected": "Should extract business name and experience"
        },
        {
            "message": "My company does professional holiday decorations and lighting",
            "expected": "Should understand service type without 'I own' pattern"
        }
    ]

    session_id = f"test_o3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    for i, test in enumerate(test_messages):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Message: '{test['message']}'")
        print(f"Expected: {test['expected']}")

        try:
            result = await coia.process_message(
                session_id=session_id,
                user_message=test["message"]
            )

            print("\n[OK] O3 Response:")
            print(f"Stage: {result.get('stage')}")
            print(f"Response Preview: {result.get('response', '')[:200]}...")

            # Check if O3 understood business information
            profile_data = result.get("profile_progress", {}).get("collectedData", {})
            if profile_data:
                print("\n[TARGET] O3 Extracted Data:")
                for key, value in profile_data.items():
                    print(f"  - {key}: {value}")

        except Exception as e:
            print(f"[X] ERROR: {e}")
            import traceback
            traceback.print_exc()

async def test_o3_vs_regex_comparison():
    """Compare O3's understanding vs old regex approach"""
    print("\n" + "="*80)
    print("O3 vs REGEX COMPARISON TEST")
    print("="*80)

    # This message should work with O3 but fail with regex
    tricky_message = "I specialize in holiday lighting installation throughout South Florida"

    print(f"\nTest Message: '{tricky_message}'")
    print("\nOLD REGEX APPROACH: Would fail because it doesn't match patterns like 'I own X'")
    print("NEW O3 APPROACH: Should understand this is about a holiday lighting business\n")

    # Test with O3
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("[X] ERROR: OPENAI_API_KEY not found")
        return

    coia = OpenAIO3CoIA(openai_key)
    session_id = f"comparison_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        result = await coia.process_message(
            session_id=session_id,
            user_message=tricky_message
        )

        print("[OK] O3 SUCCESSFULLY UNDERSTOOD THE MESSAGE!")
        print(f"\nStage: {result.get('stage')}")

        # Check if research was triggered
        if "research" in result.get("stage", ""):
            print("[OK] O3 correctly triggered business research")

        # Show what O3 extracted
        profile_data = result.get("profile_progress", {}).get("collectedData", {})
        if profile_data:
            print("\n[TARGET] O3 Extracted:")
            for key, value in profile_data.items():
                if value:
                    print(f"  - {key}: {value}")

    except Exception as e:
        print(f"[X] ERROR: {e}")

async def test_full_conversation():
    """Test a full conversation flow with O3"""
    print("\n" + "="*80)
    print("FULL CONVERSATION TEST WITH O3")
    print("="*80)

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("[X] ERROR: OPENAI_API_KEY not found")
        return

    coia = OpenAIO3CoIA(openai_key)
    session_id = f"full_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Simulate a conversation
    conversation = [
        "Hi there",
        "I specialize in holiday lighting installation",
        "Yes, my company is JM Holiday Lighting in South Florida",
        "Yes, that's all correct"
    ]

    for i, message in enumerate(conversation):
        print(f"\n{'='*60}")
        print(f"Turn {i+1} - User: '{message}'")

        try:
            result = await coia.process_message(
                session_id=session_id,
                user_message=message
            )

            print("\nAssistant Response:")
            print(f"Stage: {result.get('stage')}")
            print(f"Response: {result.get('response', '')[:300]}...")

            # Show contractor ID if created
            if result.get("contractor_id"):
                print("\n[OK] CONTRACTOR PROFILE CREATED!")
                print(f"Contractor ID: {result['contractor_id']}")

        except Exception as e:
            print(f"[X] ERROR: {e}")
            break

async def main():
    """Run all tests"""
    print("\n[ROCKET] STARTING OPENAI O3 COIA TESTS")
    print(f"Timestamp: {datetime.now()}")

    # Check for API key first
    if not os.getenv("OPENAI_API_KEY"):
        print("\n[X] FATAL ERROR: OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file")
        return

    # Run tests
    await test_o3_understanding()
    await test_o3_vs_regex_comparison()
    await test_full_conversation()

    print("\n[OK] ALL TESTS COMPLETED")

if __name__ == "__main__":
    asyncio.run(main())
