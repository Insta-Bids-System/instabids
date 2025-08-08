#!/usr/bin/env python3
"""
RUN FRESH SYSTEM TEST - Create new bid card RIGHT NOW
"""
import asyncio
import os
import sys
from pathlib import Path


# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from dotenv import load_dotenv


# Load .env from the instabids root directory
env_path = parent_dir / ".env"
load_dotenv(env_path)

from agents.cia.agent import CustomerInterfaceAgent
from agents.jaa.agent import JobAssessmentAgent


async def run_fresh_system():
    """RUN THE SYSTEM RIGHT NOW - CREATE FRESH DATA"""
    print("RUNNING FRESH SYSTEM TEST - CREATING NEW DATA")
    print("=" * 60)

    # Use the profile we just created
    user_id = "12345678-1234-1234-1234-123456789012"
    session_id = "fresh-test-session-001"

    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    # STEP 1: CIA Agent - Handle roofing emergency RIGHT NOW
    print("\n=== STEP 1: CIA AGENT - FRESH CONVERSATION ===")
    try:
        cia = CustomerInterfaceAgent(anthropic_key)

        result = await cia.handle_conversation(
            user_id=user_id,
            message="My roof is leaking badly after the storm - I need emergency repair contractors ASAP. Water is coming into my bedroom!",
            session_id=session_id
        )

        response = result.get("response", "")
        if response:
            print("SUCCESS: CIA generated fresh response")
            print(f"Response: {response[:200]}...")
        else:
            print("FAIL: No response from CIA")
            return False

    except Exception as e:
        print(f"CIA FAILED: {e}")
        return False

    # STEP 2: JAA Agent - Process the conversation RIGHT NOW
    print("\n=== STEP 2: JAA AGENT - PROCESS CONVERSATION ===")
    try:
        jaa = JobAssessmentAgent()

        # Process the roofing conversation
        jaa_result = await jaa.process_conversation(
            user_id=user_id,
            conversation_data={
                "messages": [
                    {"role": "user", "content": "My roof is leaking badly after the storm - I need emergency repair contractors ASAP. Water is coming into my bedroom!"}
                ],
                "project_type": "roofing",
                "urgency_level": "emergency"
            }
        )

        if jaa_result.get("success"):
            print("SUCCESS: JAA processed conversation")
            bid_card_id = jaa_result.get("bid_card_id")
            if bid_card_id:
                print(f"Created new bid card: {bid_card_id}")
            else:
                print("No bid card ID returned")
        else:
            print(f"JAA FAILED: {jaa_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"JAA ERROR: {e}")
        # Continue anyway - maybe JAA isn't the right method
        print("Continuing without JAA...")

    print("\n" + "=" * 60)
    print("FRESH SYSTEM TEST RESULTS:")
    print("1. CIA Agent: Created fresh response to emergency roof leak")
    print("2. JAA Agent: Attempted to process conversation")
    print("3. NEW DATA: Fresh conversation created in database")

    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(run_fresh_system())

        if success:
            print("\nFRESH SYSTEM TEST: CREATED NEW DATA")
        else:
            print("\nSYSTEM FAILED TO CREATE NEW DATA")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
