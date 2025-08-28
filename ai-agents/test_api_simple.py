#!/usr/bin/env python3
"""
Simple API Test - No Unicode Issues
"""

import requests
import json
from config.service_urls import get_backend_url

def test_api_simple():
    """Simple API test"""
    
    print("INTELLIGENT MESSAGING API TEST")
    print("=" * 40)
    
    # Test contact info blocking
    payload = {
        "content": "Hi! My email is john@contractor.com and phone is 555-123-4567. Please contact me directly.",
        "sender_type": "contractor",
        "sender_id": "550e8400-e29b-41d4-a716-446655440001",
        "bid_card_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    
    try:
        response = requests.post(f"{get_backend_url()}/api/intelligent-messages/send", json=payload, timeout=30)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content: '{payload['content'][:50]}...'")
        print(f"Approved: {result.get('approved', 'unknown')}")
        print(f"Decision: {result.get('agent_decision', 'unknown')}")
        print(f"Threats: {result.get('threats_detected', [])}")
        print(f"Error: {result.get('error', 'none')}")
        
        # System should block contact info
        blocked = not result.get('approved')
        if blocked:
            print("PASS - Contact info blocked")
        else:
            print("FAIL - Contact info not blocked")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    print()
    
    # Test legitimate content  
    payload2 = {
        "content": "I can install kitchen cabinets for $15,000 in 2-3 weeks. Do you prefer oak or maple?",
        "sender_type": "contractor",
        "sender_id": "550e8400-e29b-41d4-a716-446655440002", 
        "bid_card_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    
    try:
        response = requests.post(f"{get_backend_url()}/api/intelligent-messages/send", json=payload2, timeout=30)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content: '{payload2['content'][:50]}...'")
        print(f"Approved: {result.get('approved', 'unknown')}")
        print(f"Decision: {result.get('agent_decision', 'unknown')}")
        print(f"Threats: {result.get('threats_detected', [])}")
        print(f"Error: {result.get('error', 'none')}")
        
        # System should approve legitimate content
        approved = result.get('approved')
        if approved:
            print("PASS - Legitimate content approved")
        else:
            print("FAIL - Legitimate content blocked")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_api_simple()