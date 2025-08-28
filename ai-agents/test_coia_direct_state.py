#!/usr/bin/env python3
"""
Test COIA Direct State
See what's in the LangGraph state
"""

import requests
import json

def test_direct_state():
    """Test to see complete state"""
    
    print("TESTING COIA STATE DIRECTLY")
    print("=" * 40)
    
    # Send message
    response = requests.post(
        "http://localhost:8008/api/coia/landing",
        json={
            "message": "My company is JM Holiday Lighting",
            "session_id": "state-test-001",
            "contractor_lead_id": "landing-state-001"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Save to file for inspection
        with open("coia_response.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print("Response saved to coia_response.json")
        
        # Check all state fields
        print()
        print("STATE INSPECTION:")
        print(f"  success: {result.get('success')}")
        print(f"  company_name: {result.get('company_name')}")
        print(f"  research_completed: {result.get('research_completed')}")
        print(f"  business_info: {result.get('business_info')}")
        
        # Check messages
        print()
        print("MESSAGES:")
        # Decode messages field if it exists
        messages_raw = result.get('messages')
        if messages_raw:
            print(f"  Messages field exists: {type(messages_raw)}")
            if isinstance(messages_raw, list):
                print(f"  Message count: {len(messages_raw)}")
        
        # Check contractor profile
        print()
        print("CONTRACTOR PROFILE:")
        profile = result.get('contractor_profile', {})
        if profile:
            print(f"  Company in profile: {profile.get('company_name')}")
            print(f"  Completeness: {profile.get('completeness', 0)}")
        
        # Print all keys for debugging
        print()
        print("ALL RESPONSE KEYS:")
        for key in sorted(result.keys()):
            if key not in ['response', 'messages']:  # Skip long text fields
                print(f"  {key}")
    else:
        print(f"ERROR: {response.status_code}")

if __name__ == "__main__":
    test_direct_state()