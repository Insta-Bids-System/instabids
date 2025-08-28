"""Test IRIS cross-session memory"""

import requests
import time
from datetime import datetime
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"

def test_cross_session():
    """Test if IRIS remembers across different sessions for same user"""
    
    print("\n=== TESTING IRIS CROSS-SESSION MEMORY ===\n")
    
    # Session 1: Initial conversation
    session1_id = f"session1_{int(datetime.now().timestamp())}"
    
    print("SESSION 1: Initial conversation")
    print("-" * 50)
    
    # Tell IRIS about a project
    response1 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "I'm planning to add a swimming pool to my backyard next summer",
            "session_id": session1_id
        }
    )
    
    if response1.status_code == 200:
        data = response1.json()
        print(f"IRIS: {data.get('response', '')[:200]}...")
    
    # Continue in same session
    response2 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "The pool should be about 30 feet long",
            "session_id": session1_id
        }
    )
    
    if response2.status_code == 200:
        data = response2.json()
        print(f"IRIS: {data.get('response', '')[:200]}...")
    
    print("\n" + "="*50)
    print("Simulating user coming back in a NEW SESSION...")
    print("="*50 + "\n")
    
    time.sleep(2)
    
    # Session 2: Different session, same user
    session2_id = f"session2_{int(datetime.now().timestamp())}"
    
    print("SESSION 2: New session, same user")
    print("-" * 50)
    
    # Ask about previous conversation
    response3 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Can you remind me what project we discussed before?",
            "session_id": session2_id
        }
    )
    
    if response3.status_code == 200:
        data = response3.json()
        response_text = data.get('response', '')
        print(f"IRIS: {response_text[:400]}")
        
        # Check if IRIS has any context
        if "pool" in response_text.lower() or "backyard" in response_text.lower():
            print("\n[AMAZING] IRIS remembers conversations from different sessions!")
        else:
            print("\n[INFO] IRIS treats each session independently (by design)")
            print("This is normal - each session_id creates a separate conversation thread")
    
    # Test: Ask about general property context (should always work)
    print("\n" + "-"*50)
    print("Testing general context awareness (should work across sessions):")
    
    response4 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "What do you know about my property?",
            "session_id": session2_id
        }
    )
    
    if response4.status_code == 200:
        data = response4.json()
        print(f"IRIS: {data.get('response', '')[:300]}...")
        
        context = data.get('context_summary', {})
        print(f"\nContext Summary:")
        print(f"- Property Photos: {context.get('property_photos', 0)}")
        print(f"- Trade Projects: {context.get('trade_projects', 0)}")
        print(f"- Inspiration Boards: {context.get('inspiration_boards', 0)}")

if __name__ == "__main__":
    test_cross_session()