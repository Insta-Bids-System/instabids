#!/usr/bin/env python3
"""Debug the conversation -> bid card linking"""

from database_simple import db

def debug_conversations():
    print("=== DEBUGGING CONVERSATION -> BID CARD LINKING ===")
    
    test_user_id = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"
    
    try:
        # Step 1: Check if test user has any conversations
        print(f"1. Checking conversations for user: {test_user_id}")
        conversations = db.client.table('agent_conversations').select('*').eq('user_id', test_user_id).execute()
        
        print(f"   Found {len(conversations.data)} conversations")
        
        if conversations.data:
            for conv in conversations.data:
                print(f"   - Thread ID: {conv['thread_id']}")
                print(f"     Created: {conv.get('created_at', 'N/A')}")
                print(f"     Status: {conv.get('status', 'N/A')}")
        
        # Step 2: Get thread IDs and check bid cards
        if conversations.data:
            thread_ids = [conv['thread_id'] for conv in conversations.data]
            print(f"\n2. Checking bid cards for thread IDs: {thread_ids}")
            
            bid_cards = db.client.table('bid_cards').select('*').in_('cia_thread_id', thread_ids).execute()
            print(f"   Found {len(bid_cards.data)} bid cards linked to these threads")
            
            for card in bid_cards.data:
                print(f"   - {card['bid_card_number']}: {card['project_type']} (Thread: {card['cia_thread_id']})")
        
        # Step 3: Check what thread IDs exist in bid_cards table
        print(f"\n3. Checking all bid cards and their thread IDs:")
        all_cards = db.client.table('bid_cards').select('bid_card_number, project_type, cia_thread_id').execute()
        
        for card in all_cards.data:
            print(f"   - {card['bid_card_number']}: Thread {card['cia_thread_id']}")
        
        # Step 4: Check if any conversation thread IDs match bid card thread IDs
        print(f"\n4. Checking for thread ID matches:")
        if conversations.data and all_cards.data:
            conv_threads = set(conv['thread_id'] for conv in conversations.data)
            card_threads = set(card['cia_thread_id'] for card in all_cards.data)
            
            matches = conv_threads.intersection(card_threads)
            print(f"   Conversation threads: {len(conv_threads)}")
            print(f"   Bid card threads: {len(card_threads)}")
            print(f"   Matches: {len(matches)}")
            
            if matches:
                print(f"   Matching threads: {matches}")
            else:
                print("   [PROBLEM] No matching thread IDs - this breaks the link!")
                print("   This is why the frontend shows no bid cards!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_conversations()