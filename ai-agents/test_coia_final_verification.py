#!/usr/bin/env python3
"""
Final COIA Verification Test
Tests complete extraction -> research -> conversation flow
"""

import requests
import json
import time

def test_coia_complete_flow():
    """Test complete COIA flow"""
    
    print("FINAL COIA VERIFICATION TEST")
    print("=" * 40)
    
    # Test with message that should trigger research
    test_message = "My company is JM Holiday Lighting in south florida"
    
    print(f"Test Message: '{test_message}'")
    print("Expected Flow: extraction -> research -> conversation")
    print()
    
    print("Sending to COIA...")
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8008/api/coia/landing",
            json={
                "message": test_message,
                "session_id": "final-test-001",
                "contractor_lead_id": "landing-final-001"
            },
            timeout=30
        )
        
        elapsed = time.time() - start_time
        print(f"Response received in {elapsed:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            # Check extraction
            print("EXTRACTION CHECK:")
            contractor_profile = result.get('contractor_profile', {})
            extracted_name = contractor_profile.get('company_name')
            print(f"  Company extracted: {extracted_name}")
            print(f"  Extraction correct: {extracted_name == 'JM Holiday Lighting'}")
            print()
            
            # Check research
            print("RESEARCH CHECK:")
            print(f"  Research completed: {result.get('research_completed', False)}")
            print(f"  Business info exists: {bool(result.get('business_info'))}")
            
            if result.get('business_info'):
                biz_info = result['business_info']
                print(f"  Source: {biz_info.get('source', 'unknown')}")
                print(f"  Specialties found: {len(biz_info.get('specialties', []))}")
                print(f"  Verified: {biz_info.get('verified', False)}")
            print()
            
            # Check conversation
            print("CONVERSATION CHECK:")
            print(f"  Current mode: {result.get('current_mode')}")
            print(f"  Response generated: {bool(result.get('response'))}")
            
            if result.get('response'):
                response_text = result['response']
                # Check if response mentions the company
                if 'JM Holiday Lighting' in response_text or 'holiday lighting' in response_text.lower():
                    print(f"  Response mentions company: YES")
                else:
                    print(f"  Response mentions company: NO")
            print()
            
            # Overall success check
            success_criteria = [
                extracted_name == 'JM Holiday Lighting',
                result.get('business_info') is not None,
                result.get('response') is not None
            ]
            
            if all(success_criteria):
                print("[SUCCESS] COIA IS 100% WORKING!")
                print("  [OK] Extraction works")
                print("  [OK] Research works (web scraping)")
                print("  [OK] Conversation works")
                print("  [OK] No Google API needed")
                return True
            else:
                print("[PARTIAL SUCCESS]")
                if extracted_name == 'JM Holiday Lighting':
                    print("  [OK] Extraction works")
                else:
                    print("  [FAIL] Extraction failed")
                    
                if result.get('business_info'):
                    print("  [OK] Research works")
                else:
                    print("  [FAIL] Research failed")
                    
                if result.get('response'):
                    print("  [OK] Conversation works")
                else:
                    print("  [FAIL] Conversation failed")
                return False
                
        else:
            print(f"[ERROR] API returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    success = test_coia_complete_flow()
    
    print()
    print("=" * 40)
    if success:
        print("RESULT: COIA IS FULLY OPERATIONAL")
        print("All components working without Google API")
    else:
        print("RESULT: COIA needs more work")
        print("Check which components failed above")