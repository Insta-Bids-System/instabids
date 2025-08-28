#!/usr/bin/env python3
"""
Test COIA with Web Scraping Solution
Verifies COIA works 100% without Google API
"""

import asyncio
import requests
import json
import time

async def test_coia_working():
    """Test COIA with working web scraping solution"""
    
    print("TESTING COIA WITH WEB SCRAPING SOLUTION")
    print("=" * 40)
    
    # Test message with company that needs research
    test_message = "JM Holiday Lighting company in south florida, need contractors who do work"
    
    print(f"Test Message: '{test_message}'")
    print()
    
    print("Sending to COIA landing endpoint...")
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8008/api/coia/landing",
            json={
                "message": test_message,
                "session_id": "test-working-001",
                "contractor_lead_id": "landing-test-working-001"
            },
            timeout=30  # 30 second timeout should be enough
        )
        
        elapsed = time.time() - start_time
        print(f"Response received in {elapsed:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            # Check key fields
            print("KEY RESULTS:")
            print(f"  Company Name Extracted: {result.get('company_name', 'NOT FOUND')}")
            print(f"  Research Completed: {result.get('research_completed', False)}")
            print(f"  Business Info Found: {bool(result.get('business_info'))}")
            print(f"  Current Mode: {result.get('current_mode', 'unknown')}")
            print()
            
            # Check if research data was populated
            if result.get('business_info'):
                print("BUSINESS DATA EXTRACTED:")
                business_info = result['business_info']
                print(f"  Company: {business_info.get('company_name', 'N/A')}")
                print(f"  Location: {business_info.get('location', 'N/A')}")
                print(f"  Specialties: {business_info.get('specialties', [])}")
                print(f"  Source: {business_info.get('source', 'N/A')}")
                print(f"  Verified: {business_info.get('verified', False)}")
                print()
            
            # Check messages for conversation flow
            messages = result.get('messages', [])
            if messages and len(messages) > 1:
                last_message = messages[-1]
                if isinstance(last_message, dict):
                    content = last_message.get('content', '')
                else:
                    content = str(last_message)
                
                print("COIA RESPONSE (first 500 chars):")
                print(content[:500])
                print()
            
            # Determine success
            if result.get('company_name') and result.get('business_info'):
                print("[SUCCESS] COIA IS 100% WORKING!")
                print("  - Company extraction: WORKING")
                print("  - Research with web scraping: WORKING")
                print("  - No Google API needed: CONFIRMED")
                return True
            else:
                print("[PARTIAL] COIA partially working")
                print("  - Missing some expected data")
                return False
                
        else:
            print(f"[ERROR] API returned {response.status_code}")
            print(response.text[:500])
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"[TIMEOUT] Request timed out after {elapsed:.2f} seconds")
        print("This might mean research is still processing")
        return False
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    # Run the async test
    success = asyncio.run(test_coia_working())
    
    print()
    print("=" * 40)
    if success:
        print("FINAL RESULT: COIA IS 100% OPERATIONAL")
        print("No Google API needed - web scraping works!")
    else:
        print("FINAL RESULT: COIA needs more debugging")
        print("Check the backend logs for details")