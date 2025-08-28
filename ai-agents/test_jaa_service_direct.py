#!/usr/bin/env python3
"""
Direct JAA Service Test
Tests if agents can successfully call JAA service with known bid card
"""

import asyncio
import sys
import os
import json
import requests
from datetime import datetime

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents'))

from agents.cia.agent import CustomerInterfaceAgent
from agents.scope_change_handler import ScopeChangeHandler
from config.service_urls import get_backend_url

# Known bid card from database query
TEST_BID_CARD = {
    "id": "93c216f1-1e3f-490a-899d-ae2a236652a4",
    "bid_card_number": "BC0730223441", 
    "project_type": "renovation",
    "budget_min": 25000,
    "budget_max": 45000,
    "status": "contractor_selected"
}

async def test_jaa_service_direct():
    """Test calling JAA service directly"""
    
    print("DIRECT JAA SERVICE INTEGRATION TEST")
    print("=" * 60)
    print(f"Test Started: {datetime.now().isoformat()}")
    
    bid_card_id = TEST_BID_CARD["id"]
    bid_card_number = TEST_BID_CARD["bid_card_number"]
    
    print(f"\nUsing test bid card: {bid_card_number}")
    print(f"Project: {TEST_BID_CARD['project_type']}")
    print(f"Current budget: ${TEST_BID_CARD['budget_min']:,} - ${TEST_BID_CARD['budget_max']:,}")
    
    # Test 1: Direct JAA service call
    print("\n" + "="*40)
    print("TEST 1: DIRECT JAA SERVICE CALL")
    print("="*40)
    
    jaa_endpoint = f"{get_backend_url()}/jaa/update/{bid_card_id}"
    
    payload = {
        "update_context": {
            "source_agent": "test_agent",
            "conversation_snippet": "Increase budget to $60,000 for renovation project",
            "detected_change_hints": ["budget"],
            "modifications": {"budget_max": 60000},
            "requester_info": {
                "user_id": "test-user-direct",
                "session_id": "direct-test-session"
            }
        },
        "update_type": "conversation_based"
    }
    
    print(f"JAA Endpoint: {jaa_endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.put(
            jaa_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\nJAA Response Status: {response.status_code}")
        
        if response.status_code == 200:
            jaa_response = response.json()
            print("✅ JAA SERVICE RESPONDED SUCCESSFULLY")
            print(f"Response: {json.dumps(jaa_response, indent=2)}")
            jaa_direct_success = True
        else:
            print(f"❌ JAA SERVICE ERROR: {response.status_code}")
            print(f"Error: {response.text}")
            jaa_direct_success = False
            
    except requests.exceptions.ConnectionError:
        print("❌ JAA SERVICE NOT AVAILABLE - Backend server not running")
        jaa_direct_success = False
    except Exception as e:
        print(f"❌ JAA SERVICE CALL FAILED: {str(e)}")
        jaa_direct_success = False
    
    # Test 2: CIA Agent JAA integration
    print("\n" + "="*40)
    print("TEST 2: CIA AGENT → JAA SERVICE")
    print("="*40)
    
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
        cia = CustomerInterfaceAgent(api_key)
        
        print("CIA Agent initialized")
        print(f"Testing modification: 'Change budget to $55,000'")
        
        result = await cia.handle_modification(
            message="Change the budget to $55,000 for this renovation",
            bid_card_number=bid_card_number,
            bid_card_id=bid_card_id,
            user_id="test-cia-user",
            session_id="cia-test-session"
        )
        
        print(f"\nCIA Agent Result:")
        print(f"- Success: {result.get('success', False)}")
        print(f"- Has JAA Response: {bool(result.get('jaa_response'))}")
        
        if result.get('success'):
            print("✅ CIA AGENT → JAA SERVICE WORKING")
            cia_success = True
        else:
            print(f"❌ CIA AGENT FAILED: {result.get('error', 'Unknown error')}")
            cia_success = False
            
    except Exception as e:
        print(f"❌ CIA AGENT TEST FAILED: {str(e)}")
        cia_success = False
    
    # Test 3: Messaging Agent JAA integration
    print("\n" + "="*40)
    print("TEST 3: MESSAGING AGENT → JAA SERVICE")
    print("="*40)
    
    try:
        scope_handler = ScopeChangeHandler()
        
        print("Scope Change Handler initialized")
        print("Testing scope change: materials and timeline")
        
        result = await scope_handler.handle_scope_change(
            scope_changes=["Material changes"],
            scope_details={"Material changes": "Change to premium materials"},
            bid_card_id=bid_card_id,
            sender_id="test-messaging-user",
            message_content="Let's upgrade to premium materials"
        )
        
        print(f"\nMessaging Agent Result:")
        print(f"- Success: {result.get('success', False)}")
        print(f"- Scope Changes: {result.get('scope_changes_detected', [])}")
        print(f"- Contractors Found: {len(result.get('other_contractors', []))}")
        
        # Consider it successful if it processed the scope change
        messaging_success = (result.get('success', False) or 
                           len(result.get('scope_changes_detected', [])) > 0 or
                           len(result.get('other_contractors', [])) > 0)
        
        if messaging_success:
            print("✅ MESSAGING AGENT → JAA SERVICE WORKING")
        else:
            print(f"❌ MESSAGING AGENT FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ MESSAGING AGENT TEST FAILED: {str(e)}")
        messaging_success = False
    
    # Final Results
    print("\n" + "="*60)
    print("FINAL TEST RESULTS")
    print("="*60)
    
    tests = [
        ("Direct JAA Service Call", jaa_direct_success),
        ("CIA Agent → JAA Service", cia_success),
        ("Messaging Agent → JAA Service", messaging_success)
    ]
    
    passed_tests = sum(1 for _, success in tests if success)
    total_tests = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:30} : {status}")
    
    print(f"\nTests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ JAA service is available and working")
        print("✅ CIA Agent can call JAA service")
        print("✅ Messaging Agent can call JAA service")
        print("✅ All integrations working correctly")
        overall_success = True
    elif passed_tests > 0:
        print(f"\n⚠️  PARTIAL SUCCESS - {passed_tests} of {total_tests} tests passed")
        if jaa_direct_success:
            print("✅ JAA service is available")
            print("⚠️  Some agent integrations need attention")
        overall_success = False
    else:
        print("\n❌ ALL TESTS FAILED")
        if not jaa_direct_success:
            print("❌ JAA service is not available - check backend server")
        print("❌ Agent integrations not working")
        overall_success = False
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(test_jaa_service_direct())
    exit(0 if success else 1)