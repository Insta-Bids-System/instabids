#!/usr/bin/env python3
"""Test the bid cards API endpoint directly"""

from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Create Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

def test_bid_cards_endpoint():
    homeowner_id = '550e8400-e29b-41d4-a716-446655440001'
    
    print(f"Testing bid cards endpoint for homeowner: {homeowner_id}")
    
    # Get conversations for this user
    conversations_result = supabase.table('agent_conversations').select('thread_id').eq('user_id', homeowner_id).execute()
    
    print(f"\nFound {len(conversations_result.data)} conversations")
    
    if not conversations_result.data:
        print("No conversations found for this user")
        return
    
    # Get thread IDs
    thread_ids = [conv['thread_id'] for conv in conversations_result.data]
    print(f"Thread IDs: {thread_ids}")
    
    # Get bid cards linked to these conversations
    result = supabase.table('bid_cards').select("*").in_('cia_thread_id', thread_ids).order('created_at', desc=True).execute()
    
    print(f"\nFound {len(result.data)} bid cards")
    
    if result.data:
        for card in result.data:
            print(f"\nBid Card ID: {card['id']}")
            print(f"Project Type: {card['project_type']}")
            print(f"Title: {card['title']}")
            print(f"Created: {card['created_at']}")

if __name__ == "__main__":
    test_bid_cards_endpoint()