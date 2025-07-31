#!/usr/bin/env python3
"""
Debug thread ID linkage between conversations and bid cards
"""
from database_simple import SupabaseDB

db = SupabaseDB()

user_id = 'e6e47a24-95ad-4af3-9ec5-f17999917bc3'

# Get all conversations for our test user
conversations = db.client.table('agent_conversations').select('*').eq('user_id', user_id).execute()
print(f'User conversations ({len(conversations.data) if conversations.data else 0}):')
for conv in (conversations.data or []):
    print(f'  - {conv["thread_id"]} (Created: {conv["created_at"]})')

print()

# Get recent bid cards (last 10)
bid_cards = db.client.table('bid_cards').select('*').order('created_at', desc=True).limit(10).execute()
print(f'Recent bid cards ({len(bid_cards.data) if bid_cards.data else 0}):')
for card in (bid_cards.data or []):
    print(f'  - {card["bid_card_number"]} -> {card["cia_thread_id"]} ({card["project_type"]})')

print()

# Check for our specific bid cards
target_numbers = ['BC-20250731000718', 'BC-20250731001402', 'BC-20250731001444']
for number in target_numbers:
    result = db.client.table('bid_cards').select('*').eq('bid_card_number', number).execute()
    if result.data:
        card = result.data[0]
        print(f'{number}: cia_thread_id = {card["cia_thread_id"]}')
    else:
        print(f'{number}: NOT FOUND')