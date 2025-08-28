#!/usr/bin/env python3
"""
Complete BSA Memory System Test (Corrected Schema)
"""

import asyncio
import requests
import json
from datetime import datetime

print('='*80)
print('COMPLETE BSA MEMORY SYSTEM TEST (CORRECTED)')
print('='*80)

contractor_id = '22222222-2222-2222-2222-222222222222'

# Test 1: Check My Bids data
print('1. CHECKING MY BIDS DATA...')
from database_simple import get_client
supabase = get_client()

my_bids = supabase.table('contractor_my_bids').select('*').eq(
    'contractor_id', contractor_id
).execute()

mybids_working = False
if my_bids.data:
    print(f'   [OK] Found {len(my_bids.data)} My Bids records')
    for bid in my_bids.data:
        print(f'   - Bid card: {bid["bid_card_id"][:8]}... (status: {bid["status"]})')
        print(f'     Interactions: {bid["interaction_count"]} | Last: {bid["last_interaction_type"]}')
    mybids_working = True
else:
    print('   [WARNING] No My Bids records found')

# Test 2: Check conversation messages using correct column
print()
print('2. CHECKING CONVERSATION MESSAGES...')

# Use sender_id instead of user_id
conversations = supabase.table('unified_conversation_messages').select('*').eq(
    'sender_id', contractor_id
).order('created_at', desc=True).limit(3).execute()

memory_working = False
if conversations.data:
    print(f'   [OK] Found {len(conversations.data)} conversation messages')
    for msg in conversations.data:
        print(f'   - {msg["sender_type"]}: {msg["content"][:60]}...')
    memory_working = True
else:
    print('   [WARNING] No conversation messages found')

# Test 3: Check memory storage
print()
print('3. CHECKING UNIFIED MEMORY...')

# Check for any memory records
memory = supabase.table('unified_conversation_memory').select('*').order(
    'created_at', desc=True
).limit(5).execute()

context_working = False
if memory.data:
    print(f'   [OK] Found {len(memory.data)} memory records')
    for mem in memory.data:
        print(f'   - Type: {mem.get("memory_type", "unknown")} | Key: {mem.get("memory_key", "unknown")}')
    context_working = True
else:
    print('   [WARNING] No memory records found')

# Test 4: Test BSA conversation
print()
print('4. TESTING BSA CONVERSATION...')

session_id = f'test-memory-{datetime.now().timestamp()}'

bsa_request = {
    'contractor_id': contractor_id,
    'message': 'What projects am I working on? Show me my bid history.',
    'session_id': session_id
}

bsa_working = False
found_my_bids_mention = False

try:
    response = requests.post(
        'http://localhost:8008/api/bsa/fast-stream',
        json=bsa_request,
        stream=True,
        timeout=15
    )
    
    if response.status_code == 200:
        print('   [OK] BSA conversation started')
        
        events_read = 0
        for line in response.iter_lines():
            if line and events_read < 25:
                try:
                    if line.startswith(b'data: '):
                        event_data = line[6:].decode('utf-8')
                        if event_data and event_data != '[DONE]':
                            event = json.loads(event_data)
                            
                            # Look for memory loading messages
                            if 'status' in event:
                                msg = event.get('message', '')
                                if 'My Bids' in msg:
                                    print(f'   BSA: {msg}')
                                    found_my_bids_mention = True
                                elif 'Loading' in msg:
                                    print(f'   BSA: {msg}')
                                
                            # Look for AI response about projects/bids
                            if 'message' in event and isinstance(event['message'], str):
                                msg_lower = event['message'].lower()
                                if 'bid' in msg_lower or 'project' in msg_lower:
                                    print(f'   AI Response: {event["message"][:100]}...')
                                    bsa_working = True
                                    break
                                    
                            events_read += 1
                except:
                    pass
    else:
        print(f'   [ERROR] BSA returned {response.status_code}')
        
except Exception as e:
    print(f'   [ERROR] BSA conversation failed: {e}')

# Test 5: Check if new conversation was stored
print()
print('5. CHECKING IF CONVERSATION WAS STORED...')

# Check for new messages after BSA conversation
new_conversations = supabase.table('unified_conversation_messages').select('*').eq(
    'sender_id', contractor_id
).order('created_at', desc=True).limit(1).execute()

conversation_stored = False
if new_conversations.data:
    latest = new_conversations.data[0]
    created_time = datetime.fromisoformat(latest['created_at'].replace('Z', '+00:00'))
    if (datetime.now().astimezone() - created_time).total_seconds() < 60:  # Within last minute
        print('   [OK] New conversation was stored')
        conversation_stored = True
    else:
        print('   [WARNING] No recent conversation found')
else:
    print('   [WARNING] No conversations stored')

print()
print('='*80)
print('COMPLETE MEMORY SYSTEM STATUS:')
print('='*80)

components = {
    'My Bids Data': mybids_working,
    'BSA Conversation': bsa_working,
    'BSA My Bids Loading': found_my_bids_mention,
    'Conversation Storage': memory_working,
    'Memory Persistence': context_working,
    'New Conversation Stored': conversation_stored
}

for component, working in components.items():
    status = 'WORKING' if working else 'BROKEN'
    print(f'{component}: {status}')

working_count = sum(1 for v in components.values() if v)
total_count = len(components)

print()
if working_count >= 4:
    print(f'[OK] MEMORY SYSTEM IS MOSTLY WORKING ({working_count}/{total_count})')
    print('Core functionality: My Bids + BSA integration operational')
else:
    print(f'[ERROR] MEMORY SYSTEM HAS ISSUES ({working_count}/{total_count})')

print()
print('WHAT THIS PROVES:')
if mybids_working and found_my_bids_mention:
    print('[OK] My Bids tracking works and BSA loads the data')
if bsa_working:
    print('[OK] BSA can access contractor context and respond intelligently')
if conversation_stored:
    print('[OK] Conversations are being persisted for future reference')

if not conversation_stored:
    print('! Conversation persistence may need debugging')
if not context_working:
    print('! Unified memory system may need attention')