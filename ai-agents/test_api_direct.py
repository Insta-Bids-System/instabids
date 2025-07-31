#!/usr/bin/env python3
"""
Test the bid cards API logic directly
"""
from database_simple import SupabaseDB

# Initialize database
db = SupabaseDB()
demo_user_id = '550e8400-e29b-41d4-a716-446655440001'

print(f"=== TESTING BID CARDS API LOGIC ===")
print(f"Demo user ID: {demo_user_id}")

# Step 1: Get conversations for demo user
print("\n1. Getting conversations for demo user...")
conversations_result = db.client.table('agent_conversations').select('thread_id').eq('user_id', demo_user_id).execute()

print(f"Found {len(conversations_result.data) if conversations_result.data else 0} conversations")
if conversations_result.data:
    thread_ids = [conv['thread_id'] for conv in conversations_result.data]
    for i, thread_id in enumerate(thread_ids[:5]):  # Show first 5
        print(f"  {i+1}. {thread_id}")
    if len(thread_ids) > 5:
        print(f"  ... and {len(thread_ids) - 5} more")
else:
    print("  ERROR: No conversations found!")
    exit(1)

# Step 2: Get bid cards linked to these conversations
print(f"\n2. Getting bid cards for {len(thread_ids)} thread IDs...")
result = db.client.table('bid_cards').select("*").in_('cia_thread_id', thread_ids).order('created_at', desc=True).execute()

print(f"Found {len(result.data) if result.data else 0} matching bid cards")
if result.data:
    for i, card in enumerate(result.data):
        print(f"  {i+1}. {card['bid_card_number']} - {card['project_type']} (${card['budget_min']}-${card['budget_max']})")
        print(f"      Thread ID: {card['cia_thread_id']}")
        print(f"      Created: {card['created_at']}")
        print()

print("=== API LOGIC TEST COMPLETE ===")
if result.data and len(result.data) > 0:
    print("✓ The API logic should work - bid cards found!")
    print(f"API should return {len(result.data)} bid cards")
else:
    print("✗ API logic failed - no bid cards found")