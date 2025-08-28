"""
Test the COIA API exactly as the frontend calls it
"""
import requests
import json
from datetime import datetime

def test_frontend_api_call():
    """Test API with exact frontend payload structure"""
    
    print("=" * 60)
    print("TESTING COIA API AS FRONTEND CALLS IT")
    print("=" * 60)
    
    # Test 1: Simple message (what works with curl)
    print("\nTest 1: Simple message (like curl)")
    print("-" * 40)
    
    response = requests.post(
        "http://localhost:8008/api/coia/landing",
        json={
            "message": "I am a General Contractor looking for projects in Austin 78701",
            "session_id": f"test-simple-{datetime.now().timestamp()}"
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        bid_cards = data.get('bidCards', [])
        print(f"Success! Found {len(bid_cards)} bid cards")
        if bid_cards:
            print(f"First card: {bid_cards[0].get('title')}")
    else:
        print(f"Error: {response.text[:200]}")
    
    # Test 2: With context (what frontend sends)
    print("\nTest 2: With context object (like frontend)")
    print("-" * 40)
    
    response = requests.post(
        "http://localhost:8008/api/coia/landing",
        json={
            "message": "I am a General Contractor looking for projects in Austin 78701",
            "session_id": f"test-context-{datetime.now().timestamp()}",
            "context": {
                "current_stage": "initial",
                "profile_data": {}
            }
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        bid_cards = data.get('bidCards', [])
        print(f"Success! Found {len(bid_cards)} bid cards")
        if bid_cards:
            print(f"First card: {bid_cards[0].get('title')}")
    else:
        print(f"Error: {response.text[:200]}")
    
    # Test 3: Persistent session (multiple messages)
    print("\nTest 3: Persistent session (conversation flow)")
    print("-" * 40)
    
    session_id = f"test-persistent-{datetime.now().timestamp()}"
    
    # First message
    response1 = requests.post(
        "http://localhost:8008/api/coia/landing",
        json={
            "message": "I am a General Contractor",
            "session_id": session_id
        }
    )
    print(f"Message 1 status: {response1.status_code}")
    
    # Second message asking for projects
    response2 = requests.post(
        "http://localhost:8008/api/coia/landing",
        json={
            "message": "Show me available projects in Austin 78701",
            "session_id": session_id
        }
    )
    print(f"Message 2 status: {response2.status_code}")
    
    if response2.status_code == 200:
        data = response2.json()
        bid_cards = data.get('bidCards', [])
        print(f"Found {len(bid_cards)} bid cards in conversation")
        if bid_cards:
            for i, card in enumerate(bid_cards[:3], 1):
                print(f"  {i}. {card.get('title')}")
    else:
        print(f"Error: {response2.text[:200]}")
    
    print()
    print("=" * 60)
    print("VERDICT:")
    print("-" * 40)
    
    if all(r.status_code == 200 for r in [response, response2]):
        if any(r.json().get('bidCards') for r in [response, response2]):
            print("SUCCESS - Bid cards API is working!")
            print("The issue must be in the frontend React component")
        else:
            print("PARTIAL - API responds but no bid cards returned")
    else:
        print("FAILURE - API is returning errors")
        print("Check Docker logs for backend errors")

if __name__ == "__main__":
    test_frontend_api_call()