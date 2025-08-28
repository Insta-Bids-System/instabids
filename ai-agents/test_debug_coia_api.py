#!/usr/bin/env python3
"""
Debug COIA API response to see what's failing
"""

import requests
import json
import uuid
from config.service_urls import get_backend_url

def test_debug_coia_api():
    test_company = "Premier Roofing Solutions Miami"
    user_message = f"Hi, I'm the owner of {test_company}. We specialize in residential and commercial roofing in Miami-Dade County."
    
    session_id = f"debug-{uuid.uuid4().hex[:12]}"
    contractor_lead_id = f"landing-{uuid.uuid4().hex[:12]}"
    
    payload = {
        "message": user_message,
        "session_id": session_id,
        "contractor_lead_id": contractor_lead_id
    }
    
    print(f"Testing API call...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{get_backend_url()}/api/coia/landing",
        json=payload,
        timeout=180
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nResponse keys: {list(result.keys())}")
        
        # Print all values for debugging
        for key, value in result.items():
            if key == "response":
                print(f"\n{key}: {value}")
            elif key == "error_details" and value:
                print(f"\n{key}: {value}")
            elif key == "transition_reason":
                print(f"{key}: {value}")
            elif key == "research_completed":
                print(f"{key}: {value}")
            elif key == "company_name":
                print(f"{key}: {value}")
            elif key == "contractor_profile" and value:
                print(f"{key}: {list(value.keys()) if isinstance(value, dict) else value}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_debug_coia_api()