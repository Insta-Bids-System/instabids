#!/usr/bin/env python3
"""
Check what's actually in the database
"""
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

async def check_database():
    """Check agent_conversations table directly"""
    
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("Missing Supabase credentials!")
        return
    
    supabase: Client = create_client(url, key)
    
    print("="*60)
    print("CHECKING SUPABASE AGENT_CONVERSATIONS TABLE")
    print("="*60)
    
    # Get recent conversations
    result = supabase.table('agent_conversations').select("*").order('created_at', desc=True).limit(5).execute()
    
    if not result.data:
        print("No conversations found!")
        return
    
    print(f"\nFound {len(result.data)} recent conversations\n")
    
    for i, conv in enumerate(result.data, 1):
        print(f"\n{i}. Conversation:")
        print(f"   Thread ID: {conv.get('thread_id')}")
        print(f"   Agent Type: {conv.get('agent_type')}")
        print(f"   Created: {conv.get('created_at')}")
        
        # Check state field
        state = conv.get('state')
        
        if state:
            # Check if it's a string or dict
            if isinstance(state, str):
                print(f"   State Type: STRING (length: {len(state)})")
                try:
                    # Try to parse it
                    state_dict = json.loads(state)
                    print("   Successfully parsed JSON string")
                    
                    # Check collected_info
                    collected_info = state_dict.get('collected_info', {})
                    print(f"   Collected Info:")
                    print(f"     - budget_min: {collected_info.get('budget_min')}")
                    print(f"     - budget_max: {collected_info.get('budget_max')}")
                    print(f"     - project_type: {collected_info.get('project_type')}")
                    print(f"     - address: {collected_info.get('address')}")
                except Exception as e:
                    print(f"   Failed to parse state: {e}")
                    print(f"   First 200 chars: {state[:200]}")
            elif isinstance(state, dict):
                print(f"   State Type: DICT")
                
                # Check collected_info
                collected_info = state.get('collected_info', {})
                print(f"   Collected Info:")
                print(f"     - budget_min: {collected_info.get('budget_min')}")
                print(f"     - budget_max: {collected_info.get('budget_max')}")
                print(f"     - project_type: {collected_info.get('project_type')}")
                print(f"     - address: {collected_info.get('address')}")
                
                # Show messages count
                messages = state.get('messages', [])
                print(f"   Messages: {len(messages)}")
                
                # Check if budget appears anywhere in the conversation
                print("\n   Checking for budget in messages:")
                for msg in messages:
                    if isinstance(msg, dict):
                        content = msg.get('content', '')
                        if '$' in content or 'budget' in content.lower():
                            print(f"     - {msg.get('role')}: {content[:100]}...")
        else:
            print("   No state found!")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(check_database())