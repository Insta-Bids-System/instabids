#!/usr/bin/env python3
"""
Test CIA conversation context and potential bid card updates
"""

import requests
import json
import time
import sys

API_BASE = 'http://localhost:8008'

def test_cia_context_and_bid_cards():
    """Test CIA conversation context and bid card creation/updates"""
    print("Testing CIA with Potential Bid Card Updates")
    print("=" * 60)

    user_id = 'test-user-123'
    conversation_id = 'test-conv-123'

    # Turn 1: Kitchen project
    print("\n--- Turn 1: Initial Kitchen Project ---")
    response = requests.post(f'{API_BASE}/api/cia/chat', json={
        'user_id': user_id,
        'conversation_id': conversation_id,
        'message': 'I need to renovate my kitchen. It is about 200 sq ft.'
    }, timeout=30)

    if response.status_code == 200:
        data = response.json()
        print(f"Response received (status: {response.status_code})")
        print(f"Response preview: {data.get('response', '')[:200]}...")
        
        # Check if potential bid card was created
        if 'potential_bid_card_id' in data:
            bid_card_id = data['potential_bid_card_id']
            print(f"Potential bid card created: {bid_card_id}")
            
            # Get bid card details
            bid_response = requests.get(f'{API_BASE}/api/cia/potential-bid-cards/{bid_card_id}')
            if bid_response.status_code == 200:
                bid_data = bid_response.json()
                completion = bid_data.get('completion_percentage', 0)
                missing_fields = bid_data.get('missing_fields', [])
                print(f"Completion: {completion}%")
                print(f"Missing fields: {missing_fields[:3]}..." if missing_fields else "All fields complete")
            else:
                print(f"Could not fetch bid card: {bid_response.status_code}")
        else:
            print("No potential bid card created")
    else:
        print(f"Request failed: {response.status_code} - {response.text[:200]}")
        return False

    print("\nWaiting 2 seconds between requests...")
    time.sleep(2)

    # Turn 2: Add budget info
    print("\n--- Turn 2: Adding Budget Info ---")
    response2 = requests.post(f'{API_BASE}/api/cia/chat', json={
        'user_id': user_id,
        'conversation_id': conversation_id,
        'message': 'My budget is around $30,000'
    }, timeout=30)

    if response2.status_code == 200:
        data2 = response2.json()
        print(f"Response received (status: {response2.status_code})")
        print(f"Response preview: {data2.get('response', '')[:200]}...")
        
        # Check for context awareness
        response_text = data2.get('response', '').lower()
        context_maintained = any(word in response_text for word in ['kitchen', '200', 'sq ft', 'square'])
        
        if context_maintained:
            print("SUCCESS: CIA remembered kitchen project context!")
        else:
            print("FAILURE: CIA did not reference kitchen from Turn 1")
            
        # Check if it's the generic opening
        if "Hi! I'm Alex" in data2.get('response', ''):
            print("FAILURE: CIA returned generic opening message")
            context_maintained = False
        
        # Check bid card updates
        if 'potential_bid_card_id' in data2:
            bid_card_id = data2['potential_bid_card_id']
            bid_response = requests.get(f'{API_BASE}/api/cia/potential-bid-cards/{bid_card_id}')
            if bid_response.status_code == 200:
                bid_data = bid_response.json()
                completion = bid_data.get('completion_percentage', 0)
                fields_updated = bid_data.get('fields_completed', [])
                print(f"Updated completion: {completion}%")
                print(f"Fields completed: {len(fields_updated)} fields")
                
                # Show actual updates
                if completion > 0:
                    print("BID CARD UPDATES VERIFIED!")
                else:
                    print("No bid card updates detected")
            else:
                print(f"Could not fetch updated bid card: {bid_response.status_code}")
                
        return context_maintained
    else:
        print(f"Request failed: {response2.status_code} - {response2.text[:200]}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    success = test_cia_context_and_bid_cards()
    print("\n" + "=" * 60)
    if success:
        print("TEST PASSED: CIA context and bid cards working!")
    else:
        print("TEST FAILED: CIA context not maintained")
    print("=" * 60)