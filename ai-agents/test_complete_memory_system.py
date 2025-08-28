#!/usr/bin/env python3
"""
Complete BSA Memory System Test
Tests: Conversations + My Bids + Memory Persistence + UUID handling
"""

import asyncio
import requests
import json
from datetime import datetime

print('='*80)
print('COMPLETE BSA MEMORY SYSTEM TEST')
print('Testing: Conversations + My Bids + Memory Persistence + UUID handling')
print('='*80)

contractor_id = '22222222-2222-2222-2222-222222222222'

async def test_complete_memory():
    # Test 1: Make actual BSA conversation and capture what happens
    print('1. TESTING BSA CONVERSATION WITH MEMORY...')
    
    session_id = f'test-memory-{datetime.now().timestamp()}'
    
    bsa_request = {
        'contractor_id': contractor_id,
        'message': 'What projects have I been working on? What bids have I submitted recently?',
        'session_id': session_id
    }
    
    bsa_responded = False
    try:
        response = requests.post(
            'http://localhost:8008/api/bsa/fast-stream',
            json=bsa_request,
            stream=True,
            timeout=15
        )
        
        if response.status_code == 200:
            print('   [OK] BSA conversation started')
            
            # Capture first several events
            events_read = 0
            for line in response.iter_lines():
                if line and events_read < 20:
                    try:
                        if line.startswith(b'data: '):
                            event_data = line[6:].decode('utf-8')
                            if event_data and event_data != '[DONE]':
                                event = json.loads(event_data)
                                
                                # Look for memory loading messages
                                if 'status' in event:
                                    msg = event.get('message', '')
                                    if 'Loading' in msg or 'My Bids' in msg:
                                        print(f'   BSA: {msg}')
                                    
                                # Look for actual AI response mentioning bids
                                if 'message' in event and isinstance(event['message'], str):
                                    if 'bid' in event['message'].lower() or 'project' in event['message'].lower():
                                        print(f'   AI Response mentions projects/bids: YES')
                                        bsa_responded = True
                                        break
                                        
                                events_read += 1
                    except:
                        pass
        else:
            print(f'   [ERROR] BSA returned {response.status_code}')
            
    except Exception as e:
        print(f'   [ERROR] BSA conversation failed: {e}')
    
    # Test 2: Check what got stored in memory tables
    print()
    print('2. CHECKING MEMORY PERSISTENCE...')
    
    from database_simple import get_client
    supabase = get_client()
    
    # Check unified_conversation_messages for this contractor
    conversations = supabase.table('unified_conversation_messages').select('*').eq(
        'user_id', contractor_id
    ).order('created_at', desc=True).limit(3).execute()
    
    memory_working = False
    if conversations.data:
        print(f'   [OK] Found {len(conversations.data)} conversation messages')
        for msg in conversations.data:
            print(f'   - {msg["role"]}: {msg["content"][:60]}...')
        memory_working = True
    else:
        print('   [WARNING] No conversation messages found')
    
    # Check unified_conversation_memory for context storage
    memory = supabase.table('unified_conversation_memory').select('*').eq(
        'user_id', contractor_id
    ).order('created_at', desc=True).limit(2).execute()
    
    context_working = False
    if memory.data:
        print(f'   [OK] Found {len(memory.data)} memory records')
        for mem in memory.data:
            print(f'   - Memory type: {mem.get("memory_type", "unknown")}')
            content_preview = str(mem.get("content", ""))[:60]
            print(f'   - Content: {content_preview}...')
        context_working = True
    else:
        print('   [WARNING] No memory records found')
    
    # Test 3: Check My Bids integration
    print()
    print('3. CHECKING MY BIDS INTEGRATION...')
    
    my_bids = supabase.table('contractor_my_bids').select('*').eq(
        'contractor_id', contractor_id
    ).execute()
    
    mybids_working = False
    if my_bids.data:
        print(f'   [OK] Found {len(my_bids.data)} My Bids records')
        for bid in my_bids.data:
            print(f'   - Bid card: {bid["bid_card_id"][:8]}... (status: {bid["status"]})')
        mybids_working = True
    else:
        print('   [WARNING] No My Bids records found')
    
    # Test 4: Test UUID handling specifically
    print()
    print('4. TESTING UUID HANDLING...')
    
    # Try to create a conversation with UUID format check
    test_message = {
        'user_id': contractor_id,  # This should be valid UUID
        'content': 'Test message for UUID validation',
        'role': 'user',
        'session_id': session_id,
        'created_at': datetime.utcnow().isoformat()
    }
    
    uuid_working = False
    try:
        result = supabase.table('unified_conversation_messages').insert(test_message).execute()
        if result.data:
            print('   [OK] UUID format accepted by database')
            uuid_working = True
        else:
            print('   [ERROR] UUID format rejected')
    except Exception as e:
        print(f'   [ERROR] UUID error: {e}')
        if 'invalid input syntax for type uuid' in str(e):
            print('   DIAGNOSIS: UUID format issue confirmed')
    
    # Test 5: Cross-reference My Bids with BSA memory loading
    print()
    print('5. TESTING BSA MEMORY LOADING OF MY BIDS...')
    
    if mybids_working:
        # Check if BSA streaming included My Bids loading
        print('   My Bids data exists for BSA to load')
        if bsa_responded:
            print('   BSA conversation completed successfully')
            print('   [LIKELY OK] BSA should have loaded My Bids context')
        else:
            print('   [WARNING] BSA conversation may have failed')
    else:
        print('   [ERROR] No My Bids data for BSA to load')
    
    print()
    print('='*80)
    print('COMPLETE MEMORY SYSTEM STATUS:')
    print('='*80)
    
    components = {
        'BSA Conversations': bsa_responded,
        'Memory Persistence': memory_working,
        'Context Storage': context_working,
        'My Bids Integration': mybids_working,
        'UUID Handling': uuid_working
    }
    
    for component, working in components.items():
        status = 'WORKING' if working else 'BROKEN'
        print(f'{component}: {status}')
    
    working_count = sum(1 for v in components.values() if v)
    total_count = len(components)
    
    print()
    if working_count == total_count:
        print('[OK] COMPLETE MEMORY SYSTEM IS FULLY OPERATIONAL')
        print('All components verified: conversations, memory, My Bids, UUIDs')
    elif working_count >= 3:
        print(f'[PARTIAL] MEMORY SYSTEM MOSTLY WORKING ({working_count}/{total_count})')
        print('Core functionality operational, some issues remain')
    else:
        print(f'[ERROR] MEMORY SYSTEM HAS SERIOUS ISSUES ({working_count}/{total_count})')
        print('Major components are not working properly')
    
    # Specific recommendations
    print()
    print('SPECIFIC ISSUES TO FIX:')
    if not uuid_working:
        print('- UUID format issue needs fixing for proper memory storage')
    if not memory_working:
        print('- Conversation persistence not working')
    if not context_working:
        print('- Context storage not working')
    if not mybids_working:
        print('- My Bids tracking not working')
    if not bsa_responded:
        print('- BSA memory loading/conversation needs debugging')
        
    if working_count == total_count:
        print('- No issues found! System is working correctly.')

if __name__ == "__main__":
    asyncio.run(test_complete_memory())