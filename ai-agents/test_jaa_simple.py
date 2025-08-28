#!/usr/bin/env python3
"""
Simple JAA Service Test
Tests JAA endpoint with minimal payload
"""

import requests
import json
from config.service_urls import get_backend_url

def test_jaa_simple():
    """Test calling JAA service directly with known bid card"""
    
    print("SIMPLE JAA SERVICE TEST")
    print("=" * 40)
    
    # Known bid card from Supabase
    bid_card_id = "93c216f1-1e3f-490a-899d-ae2a236652a4"
    
    # JAA endpoint
    jaa_endpoint = f"{get_backend_url()}/jaa/update/{bid_card_id}"
    
    # Simple payload
    payload = {
        "update_context": {
            "source_agent": "test_agent",
            "conversation_snippet": "Increase budget to $60,000",
            "detected_change_hints": ["budget"],
            "requester_info": {
                "user_id": "test-user",
                "session_id": "test-session"
            }
        },
        "update_type": "conversation_based"
    }
    
    print(f"JAA Endpoint: {jaa_endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.put(
            jaa_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nJAA Response Status: {response.status_code}")
        
        if response.status_code == 200:
            jaa_response = response.json()
            print("SUCCESS: JAA SERVICE WORKING")
            print(f"Response: {json.dumps(jaa_response, indent=2)}")
            
            # Check for expected fields
            if jaa_response.get("success"):
                print("\nJAA RESPONSE ANALYSIS:")
                print(f"- Success: {jaa_response.get('success')}")
                print(f"- Bid Card ID: {jaa_response.get('bid_card_id')}")
                print(f"- Update Summary: {jaa_response.get('update_summary', {})}")
                print(f"- Affected Contractors: {len(jaa_response.get('affected_contractors', []))}")
                print(f"- Notification Content: {bool(jaa_response.get('notification_content'))}")
                
                return True
            else:
                print("JAA responded but indicated failure")
                return False
        else:
            print(f"JAA SERVICE ERROR: {response.status_code}")
            print(f"Error Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to JAA service")
        print("Backend server may not be running on localhost:8008")
        return False
    except Exception as e:
        print(f"ERROR: JAA service call failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_jaa_simple()
    if success:
        print("\nFINAL RESULT: JAA SERVICE IS WORKING")
    else:
        print("\nFINAL RESULT: JAA SERVICE NOT WORKING")
    
    exit(0 if success else 1)