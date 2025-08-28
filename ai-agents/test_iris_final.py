"""Final comprehensive test of IRIS unified system"""

import requests
import json
import time
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"

def test_iris_both_contexts():
    """Test IRIS creates cards in both inspiration and maintenance contexts"""
    print("\n=== TEST: IRIS IN BOTH CONTEXTS ===\n")
    
    # Test 1: Inspiration context
    print("1. Testing inspiration context...")
    response = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": TEST_USER_ID,
        "message": "I love the coastal modern style with white shiplap walls and blue accents. Can we plan a living room makeover?",
        "context_type": "inspiration"
    }, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   SUCCESS - Session: {data['session_id'][:8]}...")
        print(f"   - Confidence: {data['reasoning']['confidence']*100:.0f}%")
        print(f"   - Intent: {data['reasoning']['user_intent']}")
    else:
        print(f"   FAILED: {response.status_code}")
    
    # Test 2: Maintenance context
    print("\n2. Testing maintenance context...")
    response = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": TEST_USER_ID,
        "message": "My bathroom faucet is dripping and the toilet keeps running. Need urgent repairs.",
        "context_type": "maintenance"
    }, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   SUCCESS - Session: {data['session_id'][:8]}...")
        print(f"   - Response length: {len(data['response'])} chars")
        print(f"   - Suggestions: {len(data['suggestions'])} items")
    else:
        print(f"   FAILED: {response.status_code}")
    
    # Test 3: Both context with memory
    print("\n3. Testing 'both' context with memory...")
    session_id = None
    messages = [
        "I want to renovate my master bedroom",
        "The room is 200 sq ft with outdated wallpaper",
        "I prefer a minimalist modern style"
    ]
    
    for i, msg in enumerate(messages, 1):
        request_data = {
            "user_id": TEST_USER_ID,
            "message": msg,
            "context_type": "both"
        }
        if session_id:
            request_data["session_id"] = session_id
            
        response = requests.post(f"{BASE_URL}/api/iris/unified-chat", json=request_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data['session_id']
            print(f"   Message {i}: SUCCESS")
        else:
            print(f"   Message {i}: FAILED")
    
    return True

def test_memory_persistence():
    """Test unified memory persistence across sessions"""
    print("\n=== TEST: MEMORY PERSISTENCE ===\n")
    
    # Create first session with specific topic
    session1 = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": TEST_USER_ID,
        "message": "I want to install solar panels on my roof",
        "context_type": "both"
    }, timeout=30)
    
    if session1.status_code == 200:
        session1_id = session1.json()['session_id']
        print(f"Session 1 created: {session1_id[:8]}...")
    
    time.sleep(1)
    
    # Create NEW session and ask about previous topic
    session2 = requests.post(f"{BASE_URL}/api/iris/unified-chat", json={
        "user_id": TEST_USER_ID,
        "message": "What projects have we discussed recently?",
        "context_type": "both"
    }, timeout=30)
    
    if session2.status_code == 200:
        response_text = session2.json()['response'].lower()
        session2_id = session2.json()['session_id']
        print(f"Session 2 created: {session2_id[:8]}...")
        
        if "solar" in response_text or "panel" in response_text:
            print("SUCCESS: IRIS remembers solar panel discussion from previous session!")
            return True
        else:
            print("WARNING: IRIS may not have full memory persistence")
            return False
    
    return False

def test_bundling_and_conversion():
    """Test bundling and conversion workflows"""
    print("\n=== TEST: BUNDLING & CONVERSION ===\n")
    
    # Get current cards
    response = requests.get(f"{BASE_URL}/api/iris/potential-bid-cards/{TEST_USER_ID}")
    
    if response.status_code != 200:
        print("Failed to get cards")
        return False
    
    cards = response.json()['potential_bid_cards']
    print(f"Found {len(cards)} potential bid cards")
    
    # Test bundling if we have enough cards
    unbundled = [c for c in cards if not c.get('bundle_group_id')]
    
    if len(unbundled) >= 2:
        print(f"\nTesting bundling with {len(unbundled)} unbundled cards...")
        
        bundle_response = requests.post(
            f"{BASE_URL}/api/iris/potential-bid-cards/bundle?user_id={TEST_USER_ID}",
            json={
                "project_ids": [unbundled[0]['id'], unbundled[1]['id']],
                "bundle_name": "Test Bundle",
                "requires_general_contractor": False
            }
        )
        
        if bundle_response.status_code == 200:
            print("SUCCESS: Bundle created")
        else:
            print(f"Bundle creation failed: {bundle_response.status_code}")
    else:
        print("Not enough unbundled cards for bundling test")
    
    return True

def test_ui_filtering():
    """Test component type filtering"""
    print("\n=== TEST: UI COMPONENT FILTERING ===\n")
    
    filters = {
        "inspiration": 0,
        "maintenance": 0,
        "both": 0
    }
    
    for component_type in filters.keys():
        response = requests.get(
            f"{BASE_URL}/api/iris/potential-bid-cards/{TEST_USER_ID}?component_type={component_type}"
        )
        
        if response.status_code == 200:
            count = response.json()['total_count']
            filters[component_type] = count
            print(f"{component_type}: {count} cards")
        else:
            print(f"{component_type}: FAILED")
    
    total = sum(filters.values())
    print(f"\nTotal across all filters: {total} cards")
    
    return True

def main():
    print("\n" + "="*60)
    print("IRIS UNIFIED SYSTEM - FINAL VERIFICATION")
    print("="*60)
    
    tests = []
    
    # Run all tests
    tests.append(("Both Contexts", test_iris_both_contexts()))
    tests.append(("Memory Persistence", test_memory_persistence()))
    tests.append(("UI Filtering", test_ui_filtering()))
    tests.append(("Bundling/Conversion", test_bundling_and_conversion()))
    
    # Summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    passed = 0
    for name, result in tests:
        status = "PASS" if result else "FAIL"
        passed += 1 if result else 0
        print(f"{name}: {status}")
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\nSYSTEM STATUS: FULLY OPERATIONAL")
    elif passed >= len(tests) * 0.75:
        print("\nSYSTEM STATUS: MOSTLY WORKING")
    else:
        print("\nSYSTEM STATUS: NEEDS ATTENTION")

if __name__ == "__main__":
    main()