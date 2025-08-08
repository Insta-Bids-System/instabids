#!/usr/bin/env python3
"""
Test all APIs with proper .env loading - NO UNICODE
"""
import os
import sys
from pathlib import Path

import requests


# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from dotenv import load_dotenv


# Load .env from the instabids root directory
env_path = parent_dir / ".env"
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

def test_claude_api():
    """Test Claude API"""
    print("\n=== TESTING CLAUDE API ===")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("FAIL: No Claude API key found")
        return False

    print(f"PASS: API Key loaded: {api_key[:25]}...")

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "What is 2+2? Just the number."}]
    }

    try:
        response = requests.post("https://api.anthropic.com/v1/messages",
                               headers=headers, json=payload, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result["content"][0]["text"]
            print(f"PASS: Claude API working! Response: {content}")
            return True
        else:
            print(f"FAIL: Claude API failed: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: Claude API error: {e}")
        return False

def test_google_maps():
    """Test Google Maps API"""
    print("\n=== TESTING GOOGLE MAPS API ===")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("FAIL: No Google Maps API key found")
        return False

    print(f"PASS: API Key loaded: {api_key[:25]}...")

    # Test with new Places API
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": "contractors Florida",
        "key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            results = len(data.get("results", []))

            if status == "OK":
                print(f"PASS: Google Maps API working! Found {results} results")
                return True
            else:
                print(f"FAIL: Google Maps API status: {status}")
                error_msg = data.get("error_message", "No error message")
                print(f"Error: {error_msg}")
                return False
        else:
            print(f"FAIL: Google Maps API failed: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: Google Maps API error: {e}")
        return False

if __name__ == "__main__":
    print("TESTING ALL APIs WITH PROPER .ENV LOADING")
    print("=" * 60)

    # Test each component
    claude_works = test_claude_api()
    google_works = test_google_maps()

    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"Claude API: {'WORKING' if claude_works else 'BROKEN'}")
    print(f"Google Maps API: {'WORKING' if google_works else 'BROKEN'}")

    if all([claude_works, google_works]):
        print("\nALL SYSTEMS WORKING - READY TO RUN END-TO-END TEST")
    else:
        print("\nSOME SYSTEMS BROKEN - FIX BEFORE PROCEEDING")
