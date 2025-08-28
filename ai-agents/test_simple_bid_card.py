#!/usr/bin/env python3
"""
Simple test of real-time bid card building
"""

import requests
import json
import time
import uuid

def test_bid_card_building():
    print("=" * 60)
    print("TESTING REAL-TIME BID CARD BUILDING")
    print("=" * 60)
    
    # Setup
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    print(f"Conversation ID: {conversation_id}")
    print(f"User ID: {user_id}")
    
    # Send first message about kitchen project
    payload = {
        "messages": [{"role": "user", "content": "I want to remodel my kitchen. I need new cabinets, countertops, and flooring. My budget is around $30,000."}],
        "conversation_id": conversation_id,
        "user_id": user_id
    }
    
    print("\nSending kitchen remodel message...")
    
    try:
        response = requests.post(
            "http://localhost:8008/api/cia/stream",
            json=payload,
            timeout=30,
            stream=True
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Collect response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        try:
                            data = json.loads(line_str[6:])
                            if "choices" in data and len(data["choices"]) > 0:
                                content = data["choices"][0].get("delta", {}).get("content", "")
                                full_response += content
                        except:
                            pass
            
            print(f"CIA Response: {full_response[:200]}...")
        else:
            print(f"Error: {response.text}")
            return
            
    except Exception as e:
        print(f"Error sending message: {e}")
        return
    
    # Wait for async processing
    print("\nWaiting 5 seconds for bid card creation...")
    time.sleep(5)
    
    # Check for potential bid card
    print("Checking for potential bid card...")
    
    try:
        bid_response = requests.get(
            f"http://localhost:8008/api/cia/conversation/{conversation_id}/potential-bid-card",
            timeout=10
        )
        
        print(f"Bid card check status: {bid_response.status_code}")
        
        if bid_response.status_code == 200:
            bid_card = bid_response.json()
            print("SUCCESS: Bid card was created!")
            print(f"  ID: {bid_card.get('id', 'Unknown')}")
            print(f"  Title: {bid_card.get('title', 'Unknown')}")
            print(f"  Primary Trade: {bid_card.get('primary_trade', 'Unknown')}")
            print(f"  Completion: {bid_card.get('completion_percentage', 0)}%")
            print(f"  Status: {bid_card.get('status', 'Unknown')}")
            
            # Check specific fields
            interesting_fields = ['zip_code', 'email_address', 'budget_range_min', 'budget_range_max', 'urgency_level']
            print(f"  Extracted fields:")
            for field in interesting_fields:
                value = bid_card.get(field)
                if value:
                    print(f"    {field}: {value}")
            
            return True
            
        elif bid_response.status_code == 404:
            print("No bid card found - creation may have failed")
            return False
        else:
            print(f"Error checking bid card: {bid_response.text}")
            return False
            
    except Exception as e:
        print(f"Error checking bid card: {e}")
        return False

if __name__ == "__main__":
    success = test_bid_card_building()
    print(f"\nTest Result: {'SUCCESS' if success else 'FAILED'}")