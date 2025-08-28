#!/usr/bin/env python3
"""
Test CIA Streaming with Demo Homeowner
Purpose: Verify basic CIA conversation functionality with GPT-5
"""

import requests
import json
import time
from config.service_urls import get_backend_url

# Demo Homeowner Profile (from user)
DEMO_USER_ID = "550e8400-e29b-41d4-a716-446655440001"
DEMO_HOMEOWNER_ID = "1001d451-72c0-422e-afd7-1d35342d0288"

def test_cia_basic_conversation():
    """Test basic CIA conversation functionality"""
    print("Testing CIA Streaming Endpoint with Demo Homeowner")
    print("=" * 60)
    
    # Test data for demo homeowner
    test_message = "Hi! I'm thinking about renovating my kitchen. Can you help me understand the process?"
    session_id = f"test_demo_{int(time.time())}"
    
    payload = {
        "messages": [{"content": test_message}],
        "conversation_id": session_id,
        "user_id": DEMO_USER_ID,
        "max_tokens": 500,
        "model_preference": "gpt-5"
    }
    
    print(f"Demo Homeowner: {DEMO_USER_ID}")
    print(f"Message: {test_message}")
    print(f"Session: {session_id}")
    print()
    
    try:
        # Test the streaming endpoint
        print("Calling CIA streaming endpoint...")
        response = requests.post(
            f"{get_backend_url()}/api/cia/stream",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: CIA endpoint responding successfully!")
            print()
            print("Response Content (first 500 chars):")
            print("-" * 40)
            response_text = response.text[:500]
            print(response_text)
            
            # Check if it's actually streaming
            if "data:" in response_text:
                print()
                print("SUCCESS: SSE streaming format detected!")
                print("SUCCESS: GPT-5 is likely being called and responding")
            else:
                print()
                print("WARNING: Response doesn't appear to be SSE streaming format")
                
        else:
            print(f"ERROR: CIA endpoint failed with status {response.status_code}")
            print("Error details:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("TIMEOUT: Request timed out - this might indicate the endpoint is working but slow")
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection error - backend might not be running on port 8008")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")

def test_backend_health():
    """Quick backend health check"""
    print("Backend Health Check")
    print("=" * 30)
    
    try:
        response = requests.get(get_backend_url(), timeout=5)
        if response.status_code == 200:
            print("SUCCESS: Backend is running on port 8008")
            data = response.json()
            print(f"Service: {data.get('service', 'Unknown')}")
            print(f"Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print(f"WARNING: Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Backend health check failed: {e}")
        return False

if __name__ == "__main__":
    print("InstaBids CIA Agent Test")
    print("Using Demo Homeowner Profile")
    print("=" * 60)
    print()
    
    # First check if backend is running
    if test_backend_health():
        print()
        test_cia_basic_conversation()
    else:
        print()
        print("ERROR: Backend not available - cannot test CIA")
        print("Try: cd ai-agents && python main.py")