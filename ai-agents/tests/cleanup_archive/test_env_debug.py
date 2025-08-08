#!/usr/bin/env python3
"""
Debug environment loading
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
print(f"Loading .env from: {env_path}")
print(f"File exists: {env_path.exists()}")

load_dotenv(env_path)

key = os.getenv("ANTHROPIC_API_KEY")
print(f"Loaded key: {key}")
print(f"Key length: {len(key) if key else 'None'}")

if key:
    print(f"First 50 chars: {key[:50]}")
    print(f"Last 10 chars: {key[-10:]}")

    # Test with anthropic
    import anthropic
    try:
        client = anthropic.Anthropic(api_key=key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=20,
            messages=[
                {"role": "user", "content": "Say 'working'"}
            ]
        )
        content = message.content[0].text
        print(f"SUCCESS: Claude API working! Response: {content}")

    except Exception as e:
        print(f"FAIL: Claude API error: {e}")
else:
    print("No API key loaded")
