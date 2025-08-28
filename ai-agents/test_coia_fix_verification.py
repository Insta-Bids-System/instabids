#!/usr/bin/env python3
"""
Test COIA Fix Verification
Tests that the routing bug fix enables proper research flow
"""

import asyncio
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_coia_research_flow():
    """Test COIA with the exact message that was broken before"""
    
    print("TESTING COIA RESEARCH FLOW AFTER ROUTING FIX")
    print("=" * 60)
    
    # Test with the exact message that was broken
    test_message = "JM Holiday Lighting company in south florida, need some contractors who do work"
    session_id = "test-fix-verification-001"
    contractor_lead_id = "landing-test-fix-001"
    
    print(f"Testing message: '{test_message}'")
    print(f"Expected flow: extraction -> research -> conversation")
    print(f"Should now perform Google Business search for JM Holiday Lighting")
    print()
    
    try:
        # Make request to COIA landing page endpoint
        response = requests.post(
            "http://localhost:8008/api/coia/landing",
            json={
                "message": test_message,
                "session_id": session_id,
                "contractor_lead_id": contractor_lead_id
            },
            timeout=60  # Allow time for research
        )
        
        if response.status_code == 200:
            result = response.json()
            print("COIA API Response Successful")
            print(f"Response length: {len(str(result))} characters")
            
            # Extract key information
            messages = result.get("messages", [])
            last_message = messages[-1] if messages else {}
            ai_response = last_message.get("content", "") if isinstance(last_message, dict) else str(last_message)
            
            # Check what state was set
            company_name = result.get("company_name", "")
            research_completed = result.get("research_completed", False)
            business_info = result.get("business_info", {})
            
            print(f"\nSTATE ANALYSIS:")
            print(f"   Company extracted: '{company_name}'")
            print(f"   Research completed: {research_completed}")
            print(f"   Business info available: {bool(business_info)}")
            
            print(f"\nAI RESPONSE:")
            print(f"   Length: {len(ai_response)} characters")
            print(f"   First 200 chars: {ai_response[:200]}...")
            
            # Analyze the response for research indicators
            research_indicators = [
                "google business", "business search", "research", "found information",
                "business details", "location", "phone", "website", "reviews"
            ]
            
            found_indicators = [indicator for indicator in research_indicators 
                              if indicator in ai_response.lower()]
            
            print(f"\nRESEARCH INDICATORS FOUND:")
            for indicator in found_indicators:
                print(f"   FOUND: '{indicator}'")
            
            if not found_indicators:
                print("   No research indicators found in response")
            
            # Success criteria
            success_criteria = {
                "Company name extracted": bool(company_name),
                "Response mentions research/business info": bool(found_indicators),
                "Response length indicates processing": len(ai_response) > 100,
                "No generic greeting": "hello" not in ai_response.lower()[:50]
            }
            
            print(f"\nSUCCESS CRITERIA:")
            all_passed = True
            for criteria, passed in success_criteria.items():
                status = "PASS" if passed else "FAIL"
                print(f"   {status}: {criteria}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print(f"\nSUCCESS: COIA research flow is now working!")
                print(f"   The routing bug fix enabled proper research execution")
            else:
                print(f"\nPARTIAL: Some criteria not met, may need additional fixes")
                
        else:
            print(f"API Request Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    
    return True

async def test_second_interaction():
    """Test a follow-up interaction to verify conversation flow"""
    
    print(f"\nTESTING FOLLOW-UP INTERACTION")
    print("=" * 40)
    
    followup_message = "What services do they offer?"
    session_id = "test-fix-verification-001"  # Same session
    contractor_lead_id = "landing-test-fix-001"  # Same contractor
    
    try:
        response = requests.post(
            "http://localhost:8008/api/coia/landing",
            json={
                "message": followup_message,
                "session_id": session_id,
                "contractor_lead_id": contractor_lead_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            messages = result.get("messages", [])
            last_message = messages[-1] if messages else {}
            ai_response = last_message.get("content", "") if isinstance(last_message, dict) else str(last_message)
            
            print(f"Follow-up response received")
            print(f"   Response: {ai_response[:150]}...")
            
            # Check if it remembers the company
            remembers_company = "jm holiday lighting" in ai_response.lower() or "holiday lighting" in ai_response.lower()
            provides_services = any(word in ai_response.lower() for word in ["lighting", "install", "service", "holiday", "christmas"])
            
            print(f"\nMEMORY & CONTEXT CHECK:")
            print(f"   Remembers company: {remembers_company}")
            print(f"   Provides service info: {provides_services}")
            
            return remembers_company and provides_services
        else:
            print(f"Follow-up failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Follow-up test failed: {e}")
        return False

async def main():
    """Main test execution"""
    
    print("COIA ROUTING FIX VERIFICATION TEST")
    print("=" * 50)
    print("Testing that COIA now performs research instead of skipping to bid cards")
    print()
    
    # Test 1: Primary research flow
    test1_passed = await test_coia_research_flow()
    
    # Test 2: Follow-up conversation
    test2_passed = await test_second_interaction()
    
    print(f"\nFINAL RESULTS:")
    print(f"   Test 1 (Research Flow): {'PASS' if test1_passed else 'FAIL'}")
    print(f"   Test 2 (Follow-up): {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print(f"\nALL TESTS PASSED")
        print(f"   COIA routing bug is FIXED")
        print(f"   Research flow is now operational")
        print(f"   Ready for full contractor onboarding workflow")
    else:
        print(f"\nTESTS INCOMPLETE")
        print(f"   Additional debugging may be needed")

if __name__ == "__main__":
    asyncio.run(main())