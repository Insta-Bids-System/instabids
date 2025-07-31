#!/usr/bin/env python3
"""
Link bid cards to demo user for dashboard testing
"""
from database_simple import SupabaseDB

db = SupabaseDB()

old_user_id = 'e6e47a24-95ad-4af3-9ec5-f17999917bc3'
demo_user_id = '550e8400-e29b-41d4-a716-446655440001'

print("=== LINKING BID CARDS TO DEMO USER ===")
print(f"From: {old_user_id}")
print(f"To: {demo_user_id}")

# Update conversations to use demo user ID
conversations = db.client.table('agent_conversations').select('*').eq('user_id', old_user_id).execute()
print(f"Found {len(conversations.data) if conversations.data else 0} conversations to update")

for conv in (conversations.data or []):
    print(f"Updating conversation: {conv['thread_id']}")
    result = db.client.table('agent_conversations').update({
        'user_id': demo_user_id
    }).eq('thread_id', conv['thread_id']).execute()
    
    if result.data:
        print(f"  Updated successfully")
    else:
        print(f"  Update failed")

print()

# Verify the bid cards are now linked to demo user
target_numbers = ['BC-20250731000718', 'BC-20250731001402', 'BC-20250731001444']

# Get conversations for demo user
demo_conversations = db.client.table('agent_conversations').select('*').eq('user_id', demo_user_id).execute()
demo_thread_ids = [conv['thread_id'] for conv in (demo_conversations.data or [])]

print(f"Demo user now has {len(demo_thread_ids)} conversations")

# Check if bid cards are linked
bid_cards = db.client.table('bid_cards').select('*').execute()
linked_cards = [card for card in (bid_cards.data or []) if card['cia_thread_id'] in demo_thread_ids]

print(f"Bid cards linked to demo user: {len(linked_cards)}")
for card in linked_cards:
    if card['bid_card_number'] in target_numbers:
        print(f"  ✓ {card['bid_card_number']} - {card['project_type']} (${card['budget_min']}-${card['budget_max']})")

print(f"\nDemo login credentials:")
print(f"Just click 'Demo Homeowner Access' button")
print(f"Dashboard URL: http://localhost:5182/dashboard")