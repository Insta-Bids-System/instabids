#!/usr/bin/env python3
"""
Test all APIs with proper .env loading from parent directory
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
        print("No Claude API key found")
        return False

    print(f"API Key loaded: {api_key[:25]}...")

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
            print(f"✅ Claude API working! Response: {content}")
            return True
        else:
            print(f"❌ Claude API failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return False

def test_google_maps():
    """Test Google Maps API"""
    print("\n=== TESTING GOOGLE MAPS API ===")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ No Google Maps API key found")
        return False

    print(f"✅ API Key loaded: {api_key[:25]}...")

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
                print(f"✅ Google Maps API working! Found {results} results")
                return True
            else:
                print(f"❌ Google Maps API status: {status}")
                error_msg = data.get("error_message", "No error message")
                print(f"Error: {error_msg}")
                return False
        else:
            print(f"❌ Google Maps API failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Google Maps API error: {e}")
        return False

def test_backend_endpoints():
    """Test backend endpoints that should exist"""
    print("\n=== TESTING BACKEND ENDPOINTS ===")

    base_url = "http://localhost:8008"

    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend running: {response.json()}")
        else:
            print("❌ Backend not responding properly")
            return False
    except Exception as e:
        print(f"❌ Backend not running: {e}")
        return False

    # Test some actual endpoints
    test_endpoints = [
        "/api/cia/chat",
        "/demo/chat",
        "/api/admin/dashboard"
    ]

    working_endpoints = []
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=3)
            if response.status_code != 404:
                working_endpoints.append(endpoint)
                print(f"✅ {endpoint} exists (status: {response.status_code})")
            else:
                print(f"❌ {endpoint} not found")
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")

    return len(working_endpoints) > 0

if __name__ == "__main__":
    print("TESTING ALL APIs WITH PROPER .ENV LOADING")
    print("=" * 60)

    # Test each component
    claude_works = test_claude_api()
    google_works = test_google_maps()
    backend_works = test_backend_endpoints()

    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"Claude API: {'✅ WORKING' if claude_works else '❌ BROKEN'}")
    print(f"Google Maps API: {'✅ WORKING' if google_works else '❌ BROKEN'}")
    print(f"Backend: {'✅ WORKING' if backend_works else '❌ BROKEN'}")

    if all([claude_works, google_works, backend_works]):
        print("\n🎉 ALL SYSTEMS WORKING - READY TO RUN END-TO-END TEST")
    else:
        print("\n🚨 SOME SYSTEMS BROKEN - FIX BEFORE PROCEEDING")
