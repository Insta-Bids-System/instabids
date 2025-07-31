#!/usr/bin/env python3
"""
Verify bid cards for test user
"""
from database_simple import SupabaseDB

db = SupabaseDB()

# Get all conversations for our test user
user_id = 'e6e47a24-95ad-4af3-9ec5-f17999917bc3'
conversations = db.client.table('agent_conversations').select('*').eq('user_id', user_id).execute()
print(f'Conversations for user: {len(conversations.data) if conversations.data else 0}')

# Get all bid cards
bid_cards = db.client.table('bid_cards').select('*').execute()
print(f'Total bid cards in database: {len(bid_cards.data) if bid_cards.data else 0}')

# Find bid cards linked to our user
user_thread_ids = [conv['thread_id'] for conv in (conversations.data or [])]
user_bid_cards = [card for card in (bid_cards.data or []) if card['cia_thread_id'] in user_thread_ids]

print(f'Bid cards for our test user: {len(user_bid_cards)}')
for i, card in enumerate(user_bid_cards):
    print(f'  {i+1}. {card["bid_card_number"]} - {card["project_type"]} (Status: {card["status"]})')
    print(f'      Budget: ${card["budget_min"]}-${card["budget_max"]}')
    print(f'      Created: {card["created_at"]}')

print(f'\nLogin credentials for testing:')
print(f'Email: test.homeowner@instabids.com')
print(f'Password: testpass123')
print(f'Dashboard URL: http://localhost:5182/dashboard')