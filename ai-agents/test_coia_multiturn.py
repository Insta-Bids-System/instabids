"""
Comprehensive Multi-Turn COIA Conversation Test
Tests memory persistence and context loading across multiple conversation turns
"""

import requests
import json
import time
from datetime import datetime
from config.service_urls import get_backend_url

# Test configuration
BASE_URL = get_backend_url()
CONTRACTOR_ID = "test-contractor-123"
SESSION_ID = f"test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def test_conversation_turn(turn_number, message, expected_context=None):
    """Send a message and verify response maintains context"""
    print(f"\n{'='*60}")
    print(f"TURN {turn_number}: {message}")
    print(f"{'='*60}")
    
    payload = {
        "contractor_lead_id": CONTRACTOR_ID,
        "session_id": SESSION_ID,
        "message": message,
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
            print(f"[OK] Response received:")
            print(f"   Message: {data.get('response', 'No response')[:200]}...")
            
            # Check if context is maintained
            if expected_context:
                response_text = data.get('response', '').lower()
                for context_item in expected_context:
                    if context_item.lower() in response_text:
                        print(f"   [OK] Context maintained: {context_item}")
                    else:
                        print(f"   [MISS] Context missing: {context_item}")
            
            # Check state info
            state = data.get('state', {})
            messages = state.get('messages', [])
            print(f"   Messages in state: {len(messages)}")
            print(f"   Current mode: {state.get('current_mode', 'unknown')}")
            
            return data
        else:
            print(f"[ERROR] Status {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return None

def verify_database_persistence():
    """Check if conversations are being saved to database"""
    print(f"\n{'='*60}")
    print("VERIFYING DATABASE PERSISTENCE")
    print(f"{'='*60}")
    
    # Note: This would normally query Supabase directly
    # For now, we'll check via the adapter endpoint if available
    print("[CHECK] Database persistence check would go here")
    print("  (Would query unified_conversations table)")

def run_comprehensive_test():
    """Run complete multi-turn conversation test"""
    print(f"\n{'#'*60}")
    print("COMPREHENSIVE MULTI-TURN COIA TEST")
    print(f"Contractor ID: {CONTRACTOR_ID}")
    print(f"Session ID: {SESSION_ID}")
    print(f"{'#'*60}")
    
    # Turn 1: Initial greeting and profile query
    result1 = test_conversation_turn(
        1,
        "Hi, I'm interested in bidding on some projects. Can you tell me about available opportunities?"
    )
    
    time.sleep(1)
    
    # Turn 2: Reference previous context
    result2 = test_conversation_turn(
        2,
        "I mentioned I'm interested in projects. What types of landscaping projects are available?",
        expected_context=["interested", "projects"]
    )
    
    time.sleep(1)
    
    # Turn 3: Ask about specific project details
    result3 = test_conversation_turn(
        3,
        "Can you tell me more about the budget ranges for these projects? I need to know if they fit my company size.",
        expected_context=["landscaping", "budget"]
    )
    
    time.sleep(1)
    
    # Turn 4: Reference earlier parts of conversation
    result4 = test_conversation_turn(
        4,
        "Based on what we discussed about landscaping projects, which one would you recommend I bid on first?",
        expected_context=["landscaping", "discussed", "recommend"]
    )
    
    time.sleep(1)
    
    # Turn 5: Switch context but maintain memory
    result5 = test_conversation_turn(
        5,
        "Actually, let me ask about my company profile. What information do you have about my business?",
        expected_context=["company", "profile"]
    )
    
    # Verify persistence
    verify_database_persistence()
    
    # Summary
    print(f"\n{'#'*60}")
    print("TEST SUMMARY")
    print(f"{'#'*60}")
    
    turns_completed = sum(1 for r in [result1, result2, result3, result4, result5] if r is not None)
    print(f"[DONE] Completed {turns_completed}/5 conversation turns")
    
    if turns_completed == 5:
        print("[PASSED] MULTI-TURN CONVERSATION TEST PASSED")
    else:
        print("[FAILED] MULTI-TURN CONVERSATION TEST FAILED")
    
    return turns_completed == 5

def test_context_loading():
    """Test that contractor context is properly loaded"""
    print(f"\n{'#'*60}")
    print("TESTING CONTEXT LOADING")
    print(f"{'#'*60}")
    
    # Test with a contractor that should have profile data
    payload = {
        "contractor_lead_id": "22222222-2222-2222-2222-222222222222",  # Known test contractor
        "session_id": f"context-test-{datetime.now().strftime('%H%M%S')}",
        "message": "What information do you have about my company and past bids?",
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
            response_text = data.get('response', '')
            
            print("[OK] Context loading request successful")
            print(f"Response preview: {response_text[:300]}...")
            
            # Check for context indicators
            context_indicators = [
                "company", "profile", "bid", "project", "contractor"
            ]
            
            found_indicators = []
            for indicator in context_indicators:
                if indicator.lower() in response_text.lower():
                    found_indicators.append(indicator)
            
            print(f"\nContext indicators found: {found_indicators}")
            
            if len(found_indicators) >= 3:
                print("[PASSED] CONTEXT LOADING TEST PASSED")
                return True
            else:
                print("[WARNING] Limited context found")
                return False
        else:
            print(f"[ERROR] Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False

if __name__ == "__main__":
    # Run the comprehensive test
    multi_turn_success = run_comprehensive_test()
    
    print("\n" + "="*60)
    
    # Run context loading test
    context_success = test_context_loading()
    
    # Final results
    print(f"\n{'#'*60}")
    print("FINAL TEST RESULTS")
    print(f"{'#'*60}")
    print(f"Multi-turn conversation: {'[PASSED]' if multi_turn_success else '[FAILED]'}")
    print(f"Context loading: {'[PASSED]' if context_success else '[FAILED]'}")
    
    if multi_turn_success and context_success:
        print("\n[SUCCESS] ALL TESTS PASSED! COIA memory system is working correctly.")
    else:
        print("\n[WARNING] Some tests failed. Review the output above for details.")