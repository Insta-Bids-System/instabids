#!/usr/bin/env python3
"""
Fix Claude API and test it works
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

def test_both_claude_keys():
    """Test both Claude API keys to see which one works"""
    print("TESTING CLAUDE API KEYS")
    print("=" * 50)

    # Get both keys
    key1 = os.getenv("ANTHROPIC_API_KEY")

    print(f"Key 1: {key1[:25]}...")

    # Test key 1
    print("\n=== TESTING KEY 1 ===")
    try:
        client = anthropic.Anthropic(api_key=key1)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "What is 2+2? Just respond with the number."}
            ]
        )
        content = message.content[0].text
        print(f"SUCCESS: Key 1 works! Response: {content}")
        return True, key1

    except Exception as e:
        print(f"FAIL: Key 1 error: {e}")

    print("Neither key worked")
    return False, None

if __name__ == "__main__":
    works, working_key = test_both_claude_keys()

    print("\n" + "=" * 50)
    if works:
        print(f"CLAUDE API WORKING with key: {working_key[:25]}...")
        print("Ready to test CIA agent")
    else:
        print("CLAUDE API NOT WORKING")
        print("Need to check API keys")
