#!/usr/bin/env python3
"""
Test the actual CIA agent with real API key - stop making excuses
"""
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

import asyncio

from agents.cia.agent import CustomerInterfaceAgent


async def test_real_cia():
    """Test the real CIA agent with actual API key"""
    print("TESTING REAL CIA AGENT")
    print("=" * 50)

    # Get the API key that's been working for days
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"Using API key: {api_key[:25]}...")

    # Initialize CIA agent
    try:
        cia = CustomerInterfaceAgent(api_key)
        print("CIA agent initialized successfully")
    except Exception as e:
        print(f"CIA initialization error: {e}")
        return False

    # Test with real conversation
    try:
        print("\nTesting CIA conversation...")
        result = await cia.handle_conversation(
            user_id="test-user-123",
            message="I need help with roof repair - there's a leak after the storm",
            session_id="test-session"
        )

        print("CIA CONVERSATION RESULT:")
        print(f"Response: {result.get('response', 'No response')}")
        print(f"Extraction Complete: {result.get('extraction_complete', False)}")

        return True

    except Exception as e:
        print(f"CIA conversation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    works = asyncio.run(test_real_cia())

    print("\n" + "=" * 50)
    print(f"CIA Agent: {'WORKING' if works else 'BROKEN'}")

    if works:
        print("CIA IS WORKING - CAN PROCEED WITH FULL SYSTEM TEST")
    else:
        print("CIA NOT WORKING - NEED TO DEBUG FURTHER")
