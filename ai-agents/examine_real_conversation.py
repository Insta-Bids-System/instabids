#!/usr/bin/env python3
"""
Examine real CIA conversation to see what data is actually available
"""
import os
import json
from supabase import create_client
from dotenv import load_dotenv

# Load environment
load_dotenv(override=True)
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(supabase_url, supabase_key)

print("Examining real CIA conversations...")
print("=" * 60)

# Get recent conversations
result = supabase.table('agent_conversations').select('*').order('created_at', desc=True).limit(3).execute()

for i, conv in enumerate(result.data, 1):
    print(f"\nConversation {i}: {conv['thread_id']}")
    print(f"Created: {conv['created_at']}")
    
    # Parse state
    state = conv.get('state', {})
    if isinstance(state, str):
        state = json.loads(state)
    
    # Show collected_info
    collected_info = state.get('collected_info', {})
    print(f"\nCollected Info:")
    for key, value in collected_info.items():
        print(f"  {key}: {value}")
    
    # Show messages
    messages = state.get('messages', [])
    print(f"\nMessages ({len(messages)} total):")
    for j, msg in enumerate(messages):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        if role == 'user':
            print(f"  User: {content[:100]}..." if len(content) > 100 else f"  User: {content}")
    
    print("\n" + "-" * 40)
    
    if i >= 2:  # Just look at 2 conversations
        break
