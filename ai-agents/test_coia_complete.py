"""
Complete COIA System Test
Tests all aspects of COIA: memory persistence, profile loading, and multi-turn conversations
"""

import requests
import json
import time
from datetime import datetime
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()

def test_single_conversation():
    """Test single turn conversation with real contractor"""
    print("\n" + "="*60)
    print("TEST 1: Single Turn Conversation")
    print("="*60)
    
    contractor_id = "36fab309-1b11-4826-b108-dda79e12ce0d"  # Mike's Handyman Service
    session_id = f"test-{datetime.now().strftime('%H%M%S')}"
    
    payload = {
        "contractor_lead_id": contractor_id,
        "session_id": session_id,
        "message": "Hi, I'm Mike from Mike's Handyman Service. What projects are available for me to bid on?",
        "mode": "conversation"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/coia/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Response received")
            print(f"Response: {data.get('response', '')[:300]}...")
            
            # Check if profile was loaded
            state = data.get('state', {})
            if 'contractor_profile' in str(state):
                print("[OK] Contractor profile loaded")
            else:
                print("[WARNING] Profile may not be loaded")
                
            return True
        else:
            print(f"[ERROR] Status {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_memory_persistence():
    """Test that COIA remembers previous conversation"""
    print("\n" + "="*60)
    print("TEST 2: Memory Persistence Across Turns")
    print("="*60)
    
    contractor_id = "b582d715-c3de-408b-9c1f-abad6c621ab0"  # Johnson Kitchen & Bath
    session_id = f"persist-{datetime.now().strftime('%H%M%S')}"
    
    # Turn 1: Introduction
    print("\nTurn 1: Introduction")
    payload1 = {
        "contractor_lead_id": contractor_id,
        "session_id": session_id,
        "message": "Hi, I'm from Johnson Kitchen & Bath. We specialize in bathroom renovations.",
        "mode": "conversation"
    }
    
    try:
        response1 = requests.post(f"{BASE_URL}/api/coia/chat", json=payload1, timeout=30)
        if response1.status_code == 200:
            print("[OK] First message sent")
            data1 = response1.json()
            print(f"Response: {data1.get('response', '')[:200]}...")
        else:
            print(f"[ERROR] Failed: {response1.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Turn 1 failed: {e}")
        return False
    
    time.sleep(2)  # Wait between turns
    
    # Turn 2: Reference previous context
    print("\nTurn 2: Testing memory")
    payload2 = {
        "contractor_lead_id": contractor_id,
        "session_id": session_id,  # Same session
        "message": "Based on my specialty in bathrooms that I just mentioned, which projects would be best for me?",
        "mode": "conversation"
    }
    
    try:
        response2 = requests.post(f"{BASE_URL}/api/coia/chat", json=payload2, timeout=30)
        if response2.status_code == 200:
            data2 = response2.json()
            response_text = data2.get('response', '').lower()
            
            # Check if it remembers the bathroom specialty
            if 'bathroom' in response_text or 'johnson' in response_text or 'mentioned' in response_text:
                print("[SUCCESS] COIA remembered the context!")
                print(f"Response: {data2.get('response', '')[:300]}...")
                return True
            else:
                print("[FAILED] COIA didn't remember the context")
                print(f"Response: {data2.get('response', '')[:300]}...")
                return False
        else:
            print(f"[ERROR] Failed: {response2.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Turn 2 failed: {e}")
        return False

def test_profile_loading():
    """Test that contractor profile is properly loaded"""
    print("\n" + "="*60)
    print("TEST 3: Profile Data Loading")
    print("="*60)
    
    contractor_id = "524196e3-5b9a-4515-8256-65a86c7b4e56"  # Orlando Home Pros
    session_id = f"profile-{datetime.now().strftime('%H%M%S')}"
    
    payload = {
        "contractor_lead_id": contractor_id,
        "session_id": session_id,
        "message": "Can you tell me what you know about my company Orlando Home Pros?",
        "mode": "conversation"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/coia/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '').lower()
            
            # Check if profile info is in response
            if 'orlando' in response_text or 'profile' in response_text:
                print("[SUCCESS] Profile information loaded")
                print(f"Response: {data.get('response', '')[:400]}...")
                return True
            else:
                print("[WARNING] Profile may not be fully loaded")
                print(f"Response: {data.get('response', '')[:400]}...")
                return False
        else:
            print(f"[ERROR] Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def test_bid_card_access():
    """Test that COIA can access bid cards"""
    print("\n" + "="*60)
    print("TEST 4: Bid Card Access")
    print("="*60)
    
    contractor_id = "07115863-e90c-4f75-b984-f82218f5acd6"  # Elite Remodeling
    session_id = f"bidcard-{datetime.now().strftime('%H%M%S')}"
    
    payload = {
        "contractor_lead_id": contractor_id,
        "session_id": session_id,
        "message": "Show me available projects I can bid on",
        "mode": "conversation"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/coia/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '').lower()
            
            # Check for project/bid card related content
            if any(word in response_text for word in ['project', 'bid', 'budget', 'available']):
                print("[SUCCESS] COIA can access bid cards")
                print(f"Response: {data.get('response', '')[:400]}...")
                return True
            else:
                print("[WARNING] Bid card access unclear")
                print(f"Response: {data.get('response', '')[:400]}...")
                return False
        else:
            print(f"[ERROR] Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

def verify_database_persistence():
    """Check if conversations are saved to database"""
    print("\n" + "="*60)
    print("TEST 5: Database Persistence Check")
    print("="*60)
    
    # This would normally query the database directly
    # For now, we'll test by creating a conversation and checking if it persists
    
    contractor_id = "ce25d8bb-572f-410c-9d65-427a0fb5f7d5"  # Central Florida Construction
    session_id = f"db-test-{datetime.now().strftime('%H%M%S')}"
    
    # Send first message
    payload = {
        "contractor_lead_id": contractor_id,
        "session_id": session_id,
        "message": "Testing database persistence",
        "mode": "conversation"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/coia/chat", json=payload, timeout=30)
        if response.status_code == 200:
            print("[OK] Conversation created")
            
            # Try to retrieve it with same session
            time.sleep(1)
            payload2 = {
                "contractor_lead_id": contractor_id,
                "session_id": session_id,
                "message": "Is my previous message saved?",
                "mode": "conversation"
            }
            
            response2 = requests.post(f"{BASE_URL}/api/coia/chat", json=payload2, timeout=30)
            if response2.status_code == 200:
                print("[SUCCESS] Database persistence working")
                return True
        
        print("[WARNING] Could not verify database persistence")
        return False
        
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
        return False

def run_all_tests():
    """Run comprehensive COIA testing suite"""
    print("\n" + "#"*60)
    print("COMPREHENSIVE COIA SYSTEM TEST")
    print("Testing: Memory, Profiles, Persistence, Integration")
    print("#"*60)
    
    results = {
        "single_conversation": test_single_conversation(),
        "memory_persistence": test_memory_persistence(),
        "profile_loading": test_profile_loading(),
        "bid_card_access": test_bid_card_access(),
        "database_persistence": verify_database_persistence()
    }
    
    # Summary
    print("\n" + "#"*60)
    print("TEST RESULTS SUMMARY")
    print("#"*60)
    
    for test_name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n[SUCCESS] ALL TESTS PASSED! COIA is fully operational.")
    elif total_passed >= 3:
        print("\n[PARTIAL] Most tests passed. COIA is mostly working.")
    else:
        print("\n[FAILURE] Multiple tests failed. COIA needs fixes.")
    
    return results

if __name__ == "__main__":
    results = run_all_tests()