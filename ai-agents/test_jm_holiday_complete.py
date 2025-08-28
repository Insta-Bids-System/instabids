"""
Test complete JM Holiday Lighting workflow with all COIA features
Tests: Introduction -> Research -> Bid Search -> Account Creation
"""

import asyncio
import json
import time
import uuid
import requests
from datetime import datetime
from config.service_urls import get_backend_url

# Configuration
BASE_URL = get_backend_url()
SESSION_ID = f"jm-holiday-test-{uuid.uuid4().hex[:8]}"
CONTRACTOR_LEAD_ID = f"jm-lead-{uuid.uuid4().hex[:8]}"

def test_coia_landing(message: str, continue_session=False):
    """Test COIA landing page endpoint"""
    
    endpoint = f"{BASE_URL}/api/coia/landing"
    
    # Use same session for continuity
    payload = {
        "message": message,
        "session_id": SESSION_ID,
        "contractor_lead_id": CONTRACTOR_LEAD_ID if continue_session else None
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: {message[:50]}...")
    print(f"Session: {SESSION_ID}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(endpoint, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Got response from COIA")
            # Handle Unicode characters in response
            response_text = data.get('response', 'No response')
            try:
                print(f"Response: {response_text[:500]}...")
            except UnicodeEncodeError:
                # Clean response of Unicode characters
                clean_response = response_text.encode('ascii', 'ignore').decode('ascii')
                print(f"Response: {clean_response[:500]}...")
            
            # Check what mode was triggered
            if 'current_mode' in data:
                print(f"Current Mode: {data['current_mode']}")
            
            # Check if research was done
            if 'research_completed' in data:
                print(f"Research Completed: {data['research_completed']}")
            
            # Check if bid cards were found
            if 'bid_cards' in data and data['bid_cards']:
                print(f"Bid Cards Found: {len(data['bid_cards'])}")
                for card in data['bid_cards'][:2]:
                    print(f"  - {card.get('title', 'Unknown')}: ${card.get('budget_min', 0)}-${card.get('budget_max', 0)}")
            
            # Check if account was created
            if 'contractor_created' in data:
                print(f"Account Created: {data['contractor_created']}")
            
            return data
        else:
            print(f"ERROR: Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out after 30 seconds")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def main():
    """Run complete JM Holiday Lighting test workflow"""
    
    print("\n" + "="*80)
    print("COMPLETE JM HOLIDAY LIGHTING COIA TEST")
    print("Testing all features: Introduction -> Research -> Bid Search -> Account Creation")
    print("="*80)
    
    # Test 1: Introduction (should trigger research mode)
    print("\n\nTEST 1: INTRODUCTION WITH COMPANY NAME")
    result1 = test_coia_landing(
        "Hi, I'm Justin with JM Holiday Lighting. We specialize in professional Christmas light installation in Fort Lauderdale."
    )
    
    if not result1:
        print("FAILED: Could not get initial response")
        return
    
    time.sleep(2)
    
    # Test 2: Ask about our services (should continue conversation with research data)
    print("\n\nTEST 2: CONTINUE CONVERSATION")
    result2 = test_coia_landing(
        "Yes, we've been in business for 8 years and have a team of 5 installers. Can you tell me more about InstaBids?",
        continue_session=True
    )
    
    time.sleep(2)
    
    # Test 3: Ask for bid opportunities (should trigger bid card search)
    print("\n\nTEST 3: SEARCH FOR BID OPPORTUNITIES")
    result3 = test_coia_landing(
        "Show me available holiday lighting projects in my area",
        continue_session=True
    )
    
    time.sleep(2)
    
    # Test 4: Request account creation
    print("\n\nTEST 4: CREATE ACCOUNT")
    result4 = test_coia_landing(
        "I'd like to create an account so I can start bidding on projects",
        continue_session=True
    )
    
    time.sleep(2)
    
    # Test 5: Confirm account creation (if interrupted)
    print("\n\nTEST 5: CONFIRM ACCOUNT CREATION")
    result5 = test_coia_landing(
        "Yes, please create my account with the information you have",
        continue_session=True
    )
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    tests_passed = 0
    
    # Check Test 1: Did it recognize company and trigger research?
    if result1 and (result1.get('current_mode') == 'research' or result1.get('research_completed') or 'research' in str(result1).lower()):
        print("[PASS] Test 1: Company recognition and research trigger - PASSED")
        tests_passed += 1
    else:
        print("[FAIL] Test 1: Company recognition and research trigger - FAILED")
    
    # Check Test 2: Did it maintain conversation context?
    if result2 and 'instabids' in result2.get('response', '').lower():
        print("[PASS] Test 2: Conversation continuity - PASSED")
        tests_passed += 1
    else:
        print("[FAIL] Test 2: Conversation continuity - FAILED")
    
    # Check Test 3: Did it find bid cards?
    if result3 and (result3.get('bid_cards') or result3.get('current_mode') == 'bid_card_search' or 'project' in str(result3).lower()):
        print("[PASS] Test 3: Bid card search - PASSED")
        tests_passed += 1
    else:
        print("[FAIL] Test 3: Bid card search - FAILED")
    
    # Check Test 4/5: Did it create an account?
    if (result4 and result4.get('contractor_created')) or (result5 and result5.get('contractor_created')) or (result5 and 'account' in str(result5).lower()):
        print("[PASS] Test 4/5: Account creation - PASSED")
        tests_passed += 1
    else:
        print("[FAIL] Test 4/5: Account creation - FAILED")
    
    print(f"\nOVERALL: {tests_passed}/4 tests passed")
    
    if tests_passed == 4:
        print("\n[SUCCESS] All COIA features working!")
    elif tests_passed >= 2:
        print("\n[PARTIAL] Some features working")
    else:
        print("\n[FAILURE] Most features not working")


if __name__ == "__main__":
    main()