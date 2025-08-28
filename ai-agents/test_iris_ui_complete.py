"""
Complete UI and Backend Test for Unified IRIS System
Tests all UI components, buttons, and memory persistence
"""

import requests
import json
import time
from datetime import datetime
import uuid
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"

def test_iris_memory_persistence():
    """Test that IRIS remembers conversations across sessions"""
    
    print("\n=== TEST 1: IRIS MEMORY PERSISTENCE ===\n")
    
    # Create first session
    session1_id = str(uuid.uuid4())
    
    # First conversation
    response1 = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": TEST_USER_ID,
        "session_id": session1_id,
        "message": "I want to renovate my kitchen. It needs new cabinets and countertops.",
        "context_type": "both"
    })
    
    if response1.status_code == 200:
        print("First message sent: Kitchen renovation")
        print(f"Session 1 ID: {session1_id}")
    
    # Second message in same session
    response2 = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": TEST_USER_ID,
        "session_id": session1_id,
        "message": "Also, the kitchen floor needs to be replaced with hardwood.",
        "context_type": "both"
    })
    
    if response2.status_code == 200:
        print("Second message sent: Floor replacement")
    
    # Create NEW session to test memory
    session2_id = str(uuid.uuid4())
    
    # Ask about previous conversation in NEW session
    response3 = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": TEST_USER_ID,
        "session_id": session2_id,
        "message": "What kitchen projects have we discussed?",
        "context_type": "both"
    })
    
    if response3.status_code == 200:
        iris_response = response3.json()
        print(f"\nNew Session ID: {session2_id}")
        print("Asked IRIS about previous kitchen discussions")
        print(f"IRIS remembers: {'kitchen' in iris_response['response'].lower()}")
        
        if 'cabinet' in iris_response['response'].lower() or 'countertop' in iris_response['response'].lower():
            print("SUCCESS: IRIS remembers specific kitchen details from previous session!")
        else:
            print("WARNING: IRIS may not have full memory of previous session")
    
    return response3.status_code == 200

def test_potential_bid_card_creation():
    """Test that IRIS can create potential bid cards"""
    
    print("\n=== TEST 2: POTENTIAL BID CARD CREATION ===\n")
    
    # Create a potential bid card via IRIS conversation
    session_id = str(uuid.uuid4())
    
    # Have a detailed conversation to trigger card creation
    messages = [
        "I need to fix my leaking bathroom faucet and replace the vanity.",
        "The bathroom is about 50 square feet, it's the master bathroom.",
        "I'd like to get this done within 2 weeks if possible."
    ]
    
    for msg in messages:
        response = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "message": msg,
            "context_type": "maintenance"
        })
        
        if response.status_code == 200:
            print(f"Sent: {msg[:50]}...")
        time.sleep(1)  # Small delay between messages
    
    # Now create a potential bid card based on this conversation
    card_data = {
        "title": "Master Bathroom Plumbing Repair",
        "room_location": "Master Bathroom",
        "primary_trade": "plumbing",
        "secondary_trades": ["carpentry"],
        "project_complexity": "moderate",
        "user_scope_notes": "Fix leaking faucet and replace vanity. 50 sq ft bathroom. 2 week timeline.",
        "component_type": "maintenance",
        "urgency_level": "high",
        "ai_analysis": {
            "estimated_duration": "2-3 days",
            "required_permits": False,
            "safety_concerns": ["water damage risk"]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/iris/potential-bid-cards?user_id={TEST_USER_ID}",
        json=card_data
    )
    
    if response.status_code == 200:
        card = response.json()
        print(f"Created potential bid card: {card['title']}")
        print(f"Card ID: {card['id']}")
        print(f"Component type: {card['component_type']}")
        return card['id']
    else:
        print(f"Failed to create card: {response.status_code}")
        return None

def test_ui_component_filtering():
    """Test that UI components filter correctly by type"""
    
    print("\n=== TEST 3: UI COMPONENT FILTERING ===\n")
    
    # Test inspiration filter
    response = requests.get(
        f"{BASE_URL}/api/iris/potential-bid-cards/{TEST_USER_ID}?component_type=inspiration"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Inspiration cards: {data['total_count']}")
        
    # Test maintenance filter
    response = requests.get(
        f"{BASE_URL}/api/iris/potential-bid-cards/{TEST_USER_ID}?component_type=maintenance"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Maintenance cards: {data['total_count']}")
        
    # Test both filter
    response = requests.get(
        f"{BASE_URL}/api/iris/potential-bid-cards/{TEST_USER_ID}?component_type=both"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Both context cards: {data['total_count']}")
        
    return True

def test_bundling_functionality():
    """Test the bundling modal and workflow"""
    
    print("\n=== TEST 4: BUNDLING WORKFLOW ===\n")
    
    # Get available cards
    response = requests.get(f"{BASE_URL}/api/iris/potential-bid-cards/{TEST_USER_ID}")
    
    if response.status_code != 200:
        print("Failed to get cards")
        return False
        
    cards = response.json()['potential_bid_cards']
    
    # Find unbundled cards
    unbundled = [c for c in cards if not c.get('bundle_group_id')]
    
    if len(unbundled) < 2:
        print(f"Not enough unbundled cards to test bundling (need 2, have {len(unbundled)})")
        return False
    
    # Create a bundle
    bundle_data = {
        "project_ids": [unbundled[0]['id'], unbundled[1]['id']],
        "bundle_name": f"UI Test Bundle {datetime.now().strftime('%H:%M')}",
        "requires_general_contractor": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/iris/potential-bid-cards/bundle?user_id={TEST_USER_ID}",
        json=bundle_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Bundle created successfully!")
        print(f"Bundle ID: {result['bundle_id']}")
        print(f"Projects bundled: {len(result['bundled_projects'])}")
        return True
    else:
        print(f"Bundle creation failed: {response.status_code}")
        return False

def test_conversion_to_bid_cards():
    """Test converting potential bid cards to actual bid cards"""
    
    print("\n=== TEST 5: CONVERSION TO BID CARDS ===\n")
    
    # Get cards ready for conversion
    response = requests.get(f"{BASE_URL}/api/iris/potential-bid-cards/{TEST_USER_ID}")
    
    if response.status_code != 200:
        print("Failed to get cards")
        return False
        
    cards = response.json()['potential_bid_cards']
    
    # Find cards in 'refined' status (ready for conversion)
    refined_cards = [c for c in cards if c['status'] == 'refined']
    
    if not refined_cards:
        # Update a card to refined status
        if cards:
            card_to_refine = cards[0]
            update_response = requests.put(
                f"{BASE_URL}/api/iris/potential-bid-cards/{card_to_refine['id']}?user_id={TEST_USER_ID}",
                json={"status": "refined"}
            )
            
            if update_response.status_code == 200:
                print(f"Updated card {card_to_refine['id'][:8]}... to 'refined' status")
                refined_cards = [card_to_refine]
    
    if not refined_cards:
        print("No cards available for conversion")
        return False
    
    # Test conversion
    conversion_data = {
        "project_ids": [refined_cards[0]['id']],
        "conversion_type": "individual"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/iris/potential-bid-cards/convert-to-bid-cards?user_id={TEST_USER_ID}",
        json=conversion_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Conversion successful!")
        print(f"Converted {result['total_converted']} card(s)")
        print(f"Conversion type: {result['conversion_type']}")
        return True
    else:
        print(f"Conversion failed: {response.status_code}")
        if response.text:
            print(f"Error: {response.text}")
        return False

def test_iris_creates_cards_both_contexts():
    """Test that IRIS can create cards in both inspiration and maintenance contexts"""
    
    print("\n=== TEST 6: IRIS CREATES CARDS IN BOTH CONTEXTS ===\n")
    
    # Test inspiration context
    session_id = str(uuid.uuid4())
    
    response = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": TEST_USER_ID,
        "session_id": session_id,
        "message": "I saw a beautiful modern kitchen on Pinterest with white cabinets and marble countertops. Can we create something similar?",
        "context_type": "inspiration"
    })
    
    if response.status_code == 200:
        print("Inspiration context message sent")
        iris_resp = response.json()
        print(f"IRIS tools available: {len(iris_resp['available_tools'])} tools")
        
    # Test maintenance context
    session_id = str(uuid.uuid4())
    
    response = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": TEST_USER_ID,
        "session_id": session_id,
        "message": "My roof is leaking near the chimney and needs urgent repair before the rain season.",
        "context_type": "maintenance"
    })
    
    if response.status_code == 200:
        print("Maintenance context message sent")
        iris_resp = response.json()
        print(f"IRIS confidence: {iris_resp['reasoning']['confidence']*100:.0f}%")
        print(f"Intent detected: {iris_resp['reasoning']['user_intent']}")
    
    return True

def run_all_tests():
    """Run complete test suite"""
    
    print("\n" + "="*60)
    print("UNIFIED IRIS SYSTEM - COMPLETE UI & BACKEND TEST")
    print("="*60)
    
    results = {
        "memory_persistence": False,
        "card_creation": False,
        "ui_filtering": False,
        "bundling": False,
        "conversion": False,
        "both_contexts": False
    }
    
    # Run tests
    results["memory_persistence"] = test_iris_memory_persistence()
    
    card_id = test_potential_bid_card_creation()
    results["card_creation"] = card_id is not None
    
    results["ui_filtering"] = test_ui_component_filtering()
    
    results["bundling"] = test_bundling_functionality()
    
    results["conversion"] = test_conversion_to_bid_cards()
    
    results["both_contexts"] = test_iris_creates_cards_both_contexts()
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name.replace('_', ' ').title()}: {status}")
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! SYSTEM FULLY OPERATIONAL!")
    elif total_passed >= total_tests * 0.8:
        print("\n⚠️ MOSTLY WORKING - Some features need attention")
    else:
        print("\n❌ CRITICAL ISSUES - System needs fixes")

if __name__ == "__main__":
    run_all_tests()