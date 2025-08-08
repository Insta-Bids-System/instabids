#!/usr/bin/env python3
"""
Test Claude API using anthropic library like the CIA agent does
"""
import os
import sys
from pathlib import Path


# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

import anthropic
from dotenv import load_dotenv


# Load .env from the instabids root directory
env_path = parent_dir / ".env"
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

def test_anthropic_library():
    """Test Claude API using anthropic library"""
    print("\n=== TESTING CLAUDE API (anthropic library) ===")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("FAIL: No Claude API key found")
        return False

    print(f"PASS: API Key loaded: {api_key[:25]}...")

    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("PASS: Anthropic client initialized")

        # Test with a simple message
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "What is 2+2? Just respond with the number."}
            ]
        )

        content = message.content[0].text
        print(f"PASS: Claude API working! Response: {content}")
        return True

    except Exception as e:
        print(f"FAIL: Anthropic library error: {e}")
        return False

if __name__ == "__main__":
    print("TESTING CLAUDE API WITH ANTHROPIC LIBRARY")
    print("=" * 60)

    works = test_anthropic_library()

    print("\n" + "=" * 60)
    print(f"Claude API (anthropic library): {'WORKING' if works else 'BROKEN'}")

    if works:
        print("\nCLAUDE API WORKING - CAN TEST CIA AGENT")
    else:
        print("\nCLAUDE API BROKEN - CANNOT TEST CIA AGENT")
