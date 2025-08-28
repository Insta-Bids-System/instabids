#!/usr/bin/env python3
"""
TEST BASIC MESSAGING
Test the basic intelligent messaging API before trying image uploads
"""

import requests
import uuid
import json
from config.service_urls import get_backend_url

def test_basic_messaging():
    """Test basic text messaging through intelligent messaging API"""
    
    print("BASIC MESSAGING TEST")
    print("=" * 30)
    
    base_url = get_backend_url()
    url = f"{base_url}/api/intelligent-messages/send"
    
    # Test with contact information that should be blocked
    payload = {
        "content": "Hi! I love your work. My cell is 407-555-1234, please call me directly.",
        "sender_type": "homeowner",
        "sender_id": str(uuid.uuid4()),
        "bid_card_id": str(uuid.uuid4()),
        "conversation_id": None,
        "target_contractor_id": None,
        "message_type": "text",
        "metadata": {}
    }
    
    print(f"Sending to: {url}")
    print(f"Message content: {payload['content']}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            
            success = result.get('success', False)
            approved = result.get('approved', False)
            agent_decision = result.get('agent_decision', 'unknown')
            threats = result.get('threats_detected', [])
            
            print(f"\nSummary:")
            print(f"  Success: {success}")
            print(f"  Approved: {approved}")
            print(f"  Agent Decision: {agent_decision}")
            print(f"  Threats Detected: {threats}")
            
            # Check if contact info was detected and blocked
            if 'contact_info' in threats or 'contact' in str(threats).lower():
                if not approved:
                    print("\nSUCCESS: Contact info correctly detected and blocked!")
                    return True
                else:
                    print("\nISSUE: Contact info detected but not blocked")
                    return False
            else:
                print("\nISSUE: Contact info not detected")
                return False
        
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = test_basic_messaging()
    print(f"\nFinal result: {'PASS' if result else 'FAIL'}")