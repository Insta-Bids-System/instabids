#!/usr/bin/env python3
"""
Fix the thread ID mismatch between bid cards and conversations
"""
from database_simple import SupabaseDB

db = SupabaseDB()
user_id = 'e6e47a24-95ad-4af3-9ec5-f17999917bc3'

# Get all conversations for our test user
conversations = db.client.table('agent_conversations').select('*').eq('user_id', user_id).execute()
print(f'User conversations: {len(conversations.data) if conversations.data else 0}')

# Map of truncated thread IDs back to full ones
thread_id_map = {}
for conv in (conversations.data or []):
    full_id = conv['thread_id']
    truncated_id = full_id[-20:]  # What JAA stores
    thread_id_map[truncated_id] = full_id
    print(f'  {full_id} -> {truncated_id}')

print()

# Get our specific bid cards
target_numbers = ['BC-20250731000718', 'BC-20250731001402', 'BC-20250731001444']
for number in target_numbers:
    result = db.client.table('bid_cards').select('*').eq('bid_card_number', number).execute()
    if result.data:
        card = result.data[0]
        stored_thread_id = card['cia_thread_id']
        
        # Find the full thread ID
        full_thread_id = None
        for conv in (conversations.data or []):
            if conv['thread_id'].endswith(stored_thread_id):
                full_thread_id = conv['thread_id']
                break
        
        if full_thread_id:
            print(f'Updating {number}: {stored_thread_id} -> {full_thread_id}')
            
            # Update the bid card
            update_result = db.client.table('bid_cards').update({
                'cia_thread_id': full_thread_id
            }).eq('bid_card_number', number).execute()
            
            if update_result.data:
                print(f'  ✅ Updated successfully')
            else:
                print(f'  ❌ Update failed')
        else:
            print(f'{number}: Could not find matching conversation for {stored_thread_id}')
    else:
        print(f'{number}: NOT FOUND')

print('\n=== VERIFICATION ===')
# Verify the fix worked
for number in target_numbers:
    result = db.client.table('bid_cards').select('*').eq('bid_card_number', number).execute()
    if result.data:
        card = result.data[0]
        print(f'{number}: cia_thread_id = {card["cia_thread_id"]}')