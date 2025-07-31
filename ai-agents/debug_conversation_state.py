#!/usr/bin/env python3
"""
Debug conversation state to see what CIA is saving
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import json

# Load environment variables
load_dotenv()

def debug_conversation(session_id):
    """Debug conversation state"""
    
    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    try:
        # Create Supabase client
        supabase = create_client(url, key)
        
        # Query agent_conversations table
        result = supabase.table('agent_conversations').select("*").eq('thread_id', session_id).single().execute()
        
        if result.data:
            conversation = result.data
            state = conversation.get('state', {})
            
            print(f"\n=== CONVERSATION DEBUG: {session_id} ===")
            print(f"User ID: {conversation.get('user_id')}")
            print(f"Created: {conversation.get('created_at')}")
            
            print("\n--- COLLECTED INFO ---")
            collected_info = state.get('collected_info', {})
            for key, value in collected_info.items():
                if value:  # Only show non-empty values
                    print(f"{key}: {value}")
            
            print("\n--- MESSAGES ---")
            messages = state.get('messages', [])
            for i, msg in enumerate(messages):
                if msg.get('role') == 'user':
                    print(f"\n[{i}] USER: {msg.get('content', '')[:100]}...")
            
            print("\n--- CURRENT STATE ---")
            print(f"Phase: {state.get('current_phase')}")
            print(f"Ready for JAA: {state.get('ready_for_jaa')}")
            print(f"Missing fields: {state.get('missing_fields', [])}")
            
        else:
            print(f"No conversation found for session: {session_id}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Use the session ID from the test
    session_id = input("Enter session ID (or press Enter for latest test): ").strip()
    if not session_id:
        session_id = "session_0912f528-924c-4a7c-8b70-2708b3f5f227_1753742966.065975"
    
    debug_conversation(session_id)