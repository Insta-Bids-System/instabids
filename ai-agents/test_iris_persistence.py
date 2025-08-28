"""Test IRIS conversation persistence"""

import requests
import time
from datetime import datetime
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"

def test_persistence():
    """Test if IRIS remembers conversation history"""
    
    print("\n=== TESTING IRIS CONVERSATION PERSISTENCE ===\n")
    
    session_id = f"persist_test_{int(datetime.now().timestamp())}"
    
    # Message 1: Introduce ourselves
    print("Message 1: Tell IRIS our name and project")
    response1 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Hi IRIS, my name is Bob and I want to renovate my kitchen",
            "session_id": session_id
        }
    )
    
    if response1.status_code == 200:
        data = response1.json()
        print(f"IRIS: {data.get('response', '')[:200]}...")
    else:
        print(f"Error: {response1.status_code}")
        return
    
    # Wait a moment
    time.sleep(2)
    
    # Message 2: Ask if IRIS remembers
    print("\nMessage 2: Check if IRIS remembers")
    response2 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "What did I tell you my name was and what room am I renovating?",
            "session_id": session_id
        }
    )
    
    if response2.status_code == 200:
        data = response2.json()
        response_text = data.get('response', '')
        
        print(f"IRIS: {response_text[:400]}")
        
        # Check if IRIS remembers
        if "Bob" in response_text and "kitchen" in response_text:
            print("\n[SUCCESS] IRIS remembers the conversation!")
            print("- Remembered name: Bob")
            print("- Remembered project: kitchen renovation")
        else:
            print("\n[WARNING] IRIS might not be remembering correctly")
            print(f"- 'Bob' found: {'Bob' in response_text}")
            print(f"- 'kitchen' found: {'kitchen' in response_text}")
    else:
        print(f"Error: {response2.status_code}")

if __name__ == "__main__":
    test_persistence()