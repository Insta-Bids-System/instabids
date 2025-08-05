"""
Test the simplified contractor agent with single endpoint
Demonstrates pre-signup (onboarding) and post-signup (authenticated) flows
"""

import asyncio
import json
from uuid import uuid4
import requests

# Test base URL
BASE_URL = "http://localhost:8008/api/contractor"


def test_contractor_onboarding():
    """Test contractor onboarding conversation (pre-signup)"""
    print("\n" + "="*60)
    print("TESTING CONTRACTOR ONBOARDING (Pre-Signup)")
    print("="*60)
    
    session_id = str(uuid4())
    
    # Start onboarding conversation
    response = requests.post(
        f"{BASE_URL}/conversation",
        json={
            "message": "Hi, I'm interested in joining InstaBids as a contractor",
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nOnboarding Started: {data['is_onboarding']}")
        print(f"Session ID: {data['session_id']}")
        print(f"Agent Response: {data['response'][:200]}...")
        
        # Continue with company info
        response2 = requests.post(
            f"{BASE_URL}/conversation",
            json={
                "message": "I run ABC Plumbing Services. We've been in business for 10 years",
                "session_id": session_id
            }
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"\nProfile Completeness: {data2.get('profile_completeness', 0)}%")
            print(f"Current Stage: {data2.get('onboarding_stage', 'unknown')}")
            print(f"Agent Response: {data2['response'][:200]}...")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def test_authenticated_contractor():
    """Test authenticated contractor conversation (post-signup)"""
    print("\n" + "="*60)
    print("TESTING AUTHENTICATED CONTRACTOR (Post-Signup)")
    print("="*60)
    
    # Simulate an authenticated contractor
    contractor_id = "contractor_123"
    session_id = str(uuid4())
    
    response = requests.post(
        f"{BASE_URL}/conversation",
        json={
            "message": "Show me available projects in my area",
            "contractor_id": contractor_id,
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAuthenticated: {data['is_authenticated']}")
        print(f"Is Onboarding: {data['is_onboarding']}")
        print(f"Available Projects: {data.get('available_projects', 0)}")
        print(f"Active Bids: {data.get('active_bids', 0)}")
        print(f"Agent Response: {data['response'][:200]}...")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def test_agent_status():
    """Check agent capabilities and status"""
    print("\n" + "="*60)
    print("CHECKING AGENT STATUS")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/status")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nStatus: {data['status']}")
        print(f"Capabilities: {json.dumps(data['capabilities'], indent=2)}")
        print(f"Contexts Supported: {data['contexts_supported']}")
        print(f"Version: {data['version']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SIMPLIFIED CONTRACTOR AGENT TEST")
    print("Single endpoint handling all contractor interactions")
    print("="*60)
    
    # Test agent status first
    test_agent_status()
    
    # Test onboarding flow
    test_contractor_onboarding()
    
    # Test authenticated contractor flow
    test_authenticated_contractor()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nKey Benefits of Simplified System:")
    print("1. ONE endpoint (/api/contractor/conversation) for everything")
    print("2. Automatic context detection (pre vs post signup)")
    print("3. Behind-the-scenes mode switching (conversation → research → intelligence)")
    print("4. No need for frontend to choose interfaces")
    print("5. Seamless contractor experience")


if __name__ == "__main__":
    main()