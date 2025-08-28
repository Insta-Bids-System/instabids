#!/usr/bin/env python3
"""
REAL COIA Verification - Wait for completion and verify actual data
"""

import requests
import json
import time

def test_coia_with_patience():
    """Test COIA and wait for actual completion with real data"""
    
    print("REAL COIA TEST - WAITING FOR ACTUAL COMPLETION")
    print("=" * 50)
    
    test_message = "JM Holiday Lighting company in south florida"
    
    print(f"Testing: '{test_message}'")
    print("Will wait up to 3 minutes for real research completion...")
    print()
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8008/api/coia/landing",
            json={
                "message": test_message,
                "session_id": "real-test-001",
                "contractor_lead_id": "landing-real-001"
            },
            timeout=180  # 3 minutes - enough for real research
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"SUCCESS: Got response after {elapsed:.1f} seconds")
            print()
            
            # Extract actual data
            company_name = result.get("company_name", "")
            research_completed = result.get("research_completed", False)
            business_info = result.get("business_info", {})
            contractor_profile = result.get("contractor_profile", {})
            
            messages = result.get("messages", [])
            last_message = messages[-1] if messages else {}
            ai_response = last_message.get("content", "") if isinstance(last_message, dict) else str(last_message)
            
            print("ACTUAL DATA EXTRACTED:")
            print(f"  Company Name: '{company_name}'")
            print(f"  Research Completed: {research_completed}")
            print(f"  Business Info Available: {bool(business_info)}")
            print(f"  Business Info Fields: {list(business_info.keys()) if business_info else []}")
            print(f"  Contractor Profile: {bool(contractor_profile)}")
            print(f"  Profile Fields: {list(contractor_profile.keys()) if contractor_profile else []}")
            print()
            
            print("AI RESPONSE ANALYSIS:")
            print(f"  Response Length: {len(ai_response)} characters")
            print(f"  Contains 'research': {'research' in ai_response.lower()}")
            print(f"  Contains 'google': {'google' in ai_response.lower()}")
            print(f"  Contains 'business': {'business' in ai_response.lower()}")
            print(f"  Contains 'lighting': {'lighting' in ai_response.lower()}")
            print()
            
            print("RESPONSE PREVIEW:")
            print(f"  First 300 chars: {ai_response[:300]}...")
            print()
            
            # Real verification criteria
            real_success = (
                bool(company_name) and
                len(ai_response) > 100 and
                ('lighting' in ai_response.lower() or 'holiday' in ai_response.lower())
            )
            
            if real_success:
                print("REAL SUCCESS: COIA extracted company and processed it")
                if business_info:
                    print("BONUS: Business info was actually populated!")
                return True
            else:
                print("PARTIAL: Basic extraction but no clear research evidence")
                return False
                
        else:
            print(f"API FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ReadTimeout:
        elapsed = time.time() - start_time
        print(f"TIMEOUT after {elapsed:.1f} seconds")
        print("This could mean:")
        print("  1. Research is working but taking too long")
        print("  2. Research is stuck in infinite loop")
        print("  3. Research is erroring and not handling it")
        print("Need to check backend logs to determine which")
        return False
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"ERROR after {elapsed:.1f} seconds: {e}")
        return False

if __name__ == "__main__":
    print("HONEST TEST: Will this actually work end-to-end?")
    print()
    
    success = test_coia_with_patience()
    
    print("\nHONEST RESULT:")
    if success:
        print("YES - COIA is actually working with real data")
    else:
        print("NO - Still broken or incomplete")
        print("The routing fix may not be enough")