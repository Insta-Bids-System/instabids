#!/usr/bin/env python3
"""
Check all bid cards for test user
"""

import os
from database_simple import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def check_all_bid_cards():
    """Check all bid cards for test user"""
    print("Checking all bid cards...")
    
    # Get all bid cards for test user
    test_user_id = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"
    
    # First get conversations for this user
    conversations = db.client.table('agent_conversations').select('thread_id').eq('user_id', test_user_id).execute()
    
    if not conversations.data:
        print("No conversations found for test user!")
        return
        
    thread_ids = [conv['thread_id'] for conv in conversations.data]
    
    # Now get bid cards linked to these conversations
    result = db.client.table('bid_cards').select('*').in_('cia_thread_id', thread_ids).execute()
    
    if result.data:
        print(f"\nFound {len(result.data)} bid cards for test user:")
        print("-" * 80)
        
        for card in result.data:
            print(f"\nBid Card: {card['bid_card_number']}")
            print(f"Project Type: {card['project_type']}")
            print(f"Budget: ${card['budget_min']:,} - ${card['budget_max']:,}")
            print(f"Urgency: {card['urgency_level']}")
            print(f"Status: {card['status']}")
            print(f"Created: {card['created_at']}")
            print(f"Thread ID: {card.get('cia_thread_id', 'N/A')}")
            
            # Check for photos
            if card.get('bid_document'):
                photos = card['bid_document'].get('all_extracted_data', {}).get('photo_urls', [])
                print(f"Photos: {len(photos)}")
            else:
                print("Photos: 0")
    else:
        print("No bid cards found for test user!")
    
    # Also check conversations
    print("\n" + "="*80)
    print("Checking conversations...")
    
    conv_result = db.client.table('agent_conversations').select('*').eq('user_id', test_user_id).execute()
    
    if conv_result.data:
        print(f"\nFound {len(conv_result.data)} conversations:")
        for conv in conv_result.data:
            print(f"\n- Thread: {conv['thread_id']}")
            print(f"  State: {conv['state']}")
            print(f"  Ready for JAA: {conv.get('ready_for_jaa', False)}")

if __name__ == "__main__":
    check_all_bid_cards()