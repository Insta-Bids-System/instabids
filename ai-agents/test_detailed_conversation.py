#!/usr/bin/env python3
"""
Test detailed conversation for better field extraction
"""

import requests
import json
import time
import uuid

def send_cia_message(conversation_id, user_id, message):
    payload = {
        "messages": [{"role": "user", "content": message}],
        "conversation_id": conversation_id,
        "user_id": user_id
    }
    
    print(f"Message: {message[:80]}...")
    
    response = requests.post(
        "http://localhost:8008/api/cia/stream",
        json=payload,
        timeout=30,
        stream=True
    )
    
    if response.status_code == 200:
        # Just consume the stream, we don't need the response text
        for line in response.iter_lines():
            pass
        print("  -> Sent successfully")
        return True
    else:
        print(f"  -> Error: {response.status_code}")
        return False

def check_bid_card_progress(conversation_id):
    response = requests.get(
        f"http://localhost:8008/api/cia/conversation/{conversation_id}/potential-bid-card",
        timeout=10
    )
    
    if response.status_code == 200:
        bid_card = response.json()
        
        # Show key extracted fields
        extracted = []
        if bid_card.get('title') and bid_card.get('title') != 'New Project':
            extracted.append(f"title: {bid_card.get('title')}")
        if bid_card.get('primary_trade') != 'general':
            extracted.append(f"trade: {bid_card.get('primary_trade')}")
        if bid_card.get('zip_code'):
            extracted.append(f"location: {bid_card.get('zip_code')}")
        if bid_card.get('budget_range_min') or bid_card.get('budget_range_max'):
            min_b = bid_card.get('budget_range_min', 0)
            max_b = bid_card.get('budget_range_max', 0)
            extracted.append(f"budget: ${min_b}-${max_b}")
        if bid_card.get('urgency_level') != 'medium':
            extracted.append(f"urgency: {bid_card.get('urgency_level')}")
        
        completion = bid_card.get('completion_percentage', 0)
        print(f"  Completion: {completion}% | Extracted: {', '.join(extracted) if extracted else 'basic fields only'}")
        
        return bid_card
    else:
        print(f"  No bid card found")
        return None

def test_detailed_conversation():
    print("TESTING DETAILED CONVERSATION FOR FIELD EXTRACTION")
    print("=" * 60)
    
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    print(f"Conversation: {conversation_id[:8]}...")
    
    # Progressive conversation with specific details
    messages = [
        "Hi! I need help with renovating my master bathroom.",
        "The bathroom is about 8x10 feet. I want to replace the shower, vanity, and flooring.",
        "I live in Chicago, Illinois, zip code 60614. My email is test@example.com.",
        "My budget is between $15,000 and $25,000 for this project.",
        "This is somewhat urgent - I'd like to complete it within the next 2 months."
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        
        # Send message
        if send_cia_message(conversation_id, user_id, message):
            # Wait for processing
            time.sleep(3)
            
            # Check bid card progress
            bid_card = check_bid_card_progress(conversation_id)
    
    # Final check
    print(f"\n=== FINAL RESULT ===")
    final_bid_card = check_bid_card_progress(conversation_id)
    
    if final_bid_card:
        print(f"SUCCESS: Bid card built with {final_bid_card.get('completion_percentage', 0)}% completion")
        
        # Show all non-empty fields
        print("All extracted data:")
        important_fields = [
            'title', 'primary_trade', 'zip_code', 'email_address', 
            'budget_range_min', 'budget_range_max', 'urgency_level',
            'user_scope_notes', 'project_complexity'
        ]
        
        for field in important_fields:
            value = final_bid_card.get(field)
            if value and value not in ['New Project', 'general', 'medium', '', None]:
                print(f"  {field}: {value}")
        
        return True
    else:
        print("FAILED: No bid card created")
        return False

if __name__ == "__main__":
    success = test_detailed_conversation()
    print(f"\nOverall Result: {'SUCCESS' if success else 'FAILED'}")