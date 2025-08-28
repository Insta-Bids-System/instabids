#!/usr/bin/env python3
"""
Debug COIA Extraction
See if extraction node is working
"""

import requests
import json

def test_extraction():
    """Test if extraction is working"""
    
    print("TESTING COIA EXTRACTION NODE")
    print("=" * 30)
    
    # Simple test message
    test_message = "I need help with JM Holiday Lighting"
    
    print(f"Message: '{test_message}'")
    print()
    
    response = requests.post(
        "http://localhost:8008/api/coia/landing",
        json={
            "message": test_message,
            "session_id": "extract-test-001",
            "contractor_lead_id": "landing-extract-001"
        },
        timeout=20
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("EXTRACTION RESULTS:")
        print(f"  company_name: {result.get('company_name')}")
        print(f"  extraction_completed: {result.get('extraction_completed')}")
        print(f"  current_mode: {result.get('current_mode')}")
        print(f"  interface: {result.get('interface')}")
        print()
        
        # Print state fields
        print("STATE FIELDS:")
        for key in ['company_name', 'company_website', 'company_phone', 
                   'company_location', 'service_type', 'urgency_level']:
            value = result.get(key)
            if value:
                print(f"  {key}: {value}")
        
        print()
        
        # Check messages
        messages = result.get('messages', [])
        print(f"Messages count: {len(messages)}")
        
        if result.get('company_name'):
            print()
            print("[SUCCESS] Extraction is working!")
            print(f"  Extracted: {result.get('company_name')}")
        else:
            print()
            print("[FAILED] No company name extracted")
            
            # Print full response for debugging
            print()
            print("Full response (first 1000 chars):")
            print(json.dumps(result, indent=2)[:1000])
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text[:500])

if __name__ == "__main__":
    test_extraction()