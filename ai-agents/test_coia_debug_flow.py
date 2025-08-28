#!/usr/bin/env python3
"""
Debug COIA Flow
See complete response data
"""

import requests
import json

def debug_coia_flow():
    """Debug complete flow with full response"""
    
    print("DEBUGGING COIA COMPLETE FLOW")
    print("=" * 40)
    
    test_message = "My company is JM Holiday Lighting in south florida"
    
    print(f"Message: '{test_message}'")
    print()
    
    response = requests.post(
        "http://localhost:8008/api/coia/landing",
        json={
            "message": test_message,
            "session_id": "debug-flow-001",
            "contractor_lead_id": "landing-debug-001"
        },
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Print all top-level keys
        print("TOP-LEVEL KEYS IN RESPONSE:")
        for key in sorted(result.keys()):
            value = result[key]
            if isinstance(value, dict):
                print(f"  {key}: <dict with {len(value)} keys>")
            elif isinstance(value, list):
                print(f"  {key}: <list with {len(value)} items>")
            elif isinstance(value, str) and len(str(value)) > 50:
                print(f"  {key}: '{str(value)[:50]}...'")
            else:
                print(f"  {key}: {value}")
        
        print()
        
        # Check specific fields
        print("EXTRACTION STATUS:")
        if result.get('contractor_profile'):
            profile = result['contractor_profile']
            print(f"  Company in profile: {profile.get('company_name')}")
        if result.get('company_name'):
            print(f"  Company top-level: {result['company_name']}")
        
        print()
        print("RESEARCH STATUS:")
        print(f"  research_completed: {result.get('research_completed')}")
        print(f"  business_info exists: {result.get('business_info') is not None}")
        
        if result.get('business_info'):
            print("  business_info contents:")
            biz = result['business_info']
            for k, v in biz.items():
                print(f"    {k}: {v}")
        
        print()
        print("RESEARCH FINDINGS:")
        if result.get('research_findings'):
            findings = result['research_findings']
            print(f"  Status: {findings.get('status')}")
            print(f"  Company: {findings.get('company_analyzed')}")
        
        # Print raw JSON for inspection
        print()
        print("RAW JSON (first 2000 chars):")
        print(json.dumps(result, indent=2)[:2000])
        
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text[:1000])

if __name__ == "__main__":
    debug_coia_flow()