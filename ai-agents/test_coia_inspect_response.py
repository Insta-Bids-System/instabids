#!/usr/bin/env python3
"""
Inspect COIA Response Details
See exactly what COIA is returning
"""

import requests
import json

def inspect_coia_response():
    """Inspect full COIA response"""
    
    print("INSPECTING COIA RESPONSE DETAILS")
    print("=" * 35)
    
    test_message = "JM Holiday Lighting company, need some contractors who do work"
    
    print(f"Message: '{test_message}'")
    print()
    
    try:
        response = requests.post(
            "http://localhost:8008/api/coia/landing",
            json={
                "message": test_message,
                "session_id": "inspect-001",
                "contractor_lead_id": "landing-inspect-001"
            },
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            print("FULL RESPONSE STRUCTURE:")
            print(f"  Type: {type(result)}")
            print(f"  Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            print()
            
            print("RAW RESPONSE (first 1000 chars):")
            print(json.dumps(result, indent=2)[:1000])
            print("...")
            print()
            
            # Check specific fields
            print("KEY FIELDS:")
            print(f"  company_name: {result.get('company_name')}")
            print(f"  research_completed: {result.get('research_completed')}")
            print(f"  current_mode: {result.get('current_mode')}")
            print(f"  interface: {result.get('interface')}")
            print(f"  extraction_completed: {result.get('extraction_completed')}")
            print(f"  mode_detector_visits: {result.get('mode_detector_visits')}")
            print()
            
            # Check messages
            messages = result.get('messages', [])
            print(f"MESSAGES ({len(messages)} total):")
            for i, msg in enumerate(messages):
                if isinstance(msg, dict):
                    content = msg.get('content', '')
                    msg_type = msg.get('type', 'unknown')
                    print(f"  {i+1}. [{msg_type}] {content[:100]}...")
                else:
                    print(f"  {i+1}. [raw] {str(msg)[:100]}...")
            
            return result
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return None

if __name__ == "__main__":
    result = inspect_coia_response()
    
    if result:
        print("\nCONCLUSION:")
        if result.get('company_name'):
            print("✓ Company extraction working")
        else:
            print("✗ Company extraction not working")
            
        if result.get('research_completed'):
            print("✓ Research completed")
        else:
            print("✗ Research not completed")
            
        if len(result.get('messages', [])) > 0:
            print("✓ Messages returned")
        else:
            print("✗ No messages returned")
    else:
        print("No valid response to analyze")