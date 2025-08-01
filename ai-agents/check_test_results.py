#!/usr/bin/env python3
"""Check test results in database"""

from database_simple import db
import json

# Get recent bid cards
print('=== RECENT BID CARDS ===')
bid_cards = db.client.table('bid_cards').select('*').order('created_at', desc=True).limit(10).execute()

if bid_cards.data:
    for card in bid_cards.data:
        print(f"\nBid Card: {card['bid_card_number']}")
        print(f"Type: {card['project_type']}") 
        print(f"Budget: ${card['budget_min']:,} - ${card['budget_max']:,}")
        print(f"Status: {card['status']}")
        print(f"Created: {card['created_at']}")
        
        # Check for photos
        if card.get('bid_document', {}).get('all_extracted_data'):
            data = card['bid_document']['all_extracted_data']
            images = data.get('images', []) or data.get('photo_urls', [])
            print(f"Photos: {len(images)}")
            if images:
                print(f"First photo: {images[0][:80]}...")
                # Check if local storage
                if 'localhost:8008/static' in images[0]:
                    print("[OK] Using local storage (RLS bypass working!)")
else:
    print('No bid cards found')

# Check recent conversations
print('\n\n=== RECENT CONVERSATIONS ===')
convos = db.client.table('agent_conversations').select('thread_id,state,ready_for_jaa,created_at').eq('user_id', 'e6e47a24-95ad-4af3-9ec5-f17999917bc3').order('created_at', desc=True).limit(10).execute()

if convos.data:
    for conv in convos.data:
        print(f"\nThread: {conv['thread_id']}")
        print(f"State: {conv['state']}")
        print(f"Ready for JAA: {conv.get('ready_for_jaa', False)}")
        print(f"Created: {conv['created_at']}")

# Check local storage
import os
static_uploads = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'e6e47a24-95ad-4af3-9ec5-f17999917bc3')
print(f'\n\n=== LOCAL STORAGE ===')
print(f'Path: {static_uploads}')
if os.path.exists(static_uploads):
    files = os.listdir(static_uploads)
    print(f'Found {len(files)} images:')
    for f in files[:10]:  # Show first 10
        print(f'  - {f}')
else:
    print('No local storage directory found')