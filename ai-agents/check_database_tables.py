#!/usr/bin/env python3
"""Check what tables exist in the database and find user data"""

from database_simple import db
import json

def list_tables():
    """List all tables in the database"""
    print("=== CHECKING DATABASE TABLES ===")
    
    # Try common table names for users
    table_names = ['users', 'profiles', 'homeowners', 'auth_users']
    
    for table_name in table_names:
        try:
            result = db.client.table(table_name).select('*').limit(1).execute()
            print(f"[OK] Table '{table_name}' exists - {len(result.data)} records found")
            
            if result.data:
                print(f"     Sample columns: {list(result.data[0].keys())}")
                
        except Exception as e:
            if "does not exist" in str(e):
                print(f"[INFO] Table '{table_name}' does not exist")
            else:
                print(f"[ERROR] Table '{table_name}' error: {str(e)[:100]}...")

def check_bid_cards_table():
    """Check the bid_cards table we know exists"""
    print(f"\n=== CHECKING BID_CARDS TABLE ===")
    
    try:
        bid_cards = db.client.table('bid_cards').select('*').limit(3).execute()
        
        if bid_cards.data:
            print(f"Found {len(bid_cards.data)} bid cards")
            
            # Look for user identification fields
            first_card = bid_cards.data[0]
            print(f"Bid card columns: {list(first_card.keys())}")
            
            # Check for user identification
            user_fields = [k for k in first_card.keys() if 'user' in k.lower() or 'homeowner' in k.lower()]
            print(f"User-related fields: {user_fields}")
            
            # Check the extracted data for user info
            if first_card.get('bid_document', {}).get('all_extracted_data'):
                extracted = first_card['bid_document']['all_extracted_data']
                user_info_fields = [k for k in extracted.keys() if 'user' in k.lower() or 'homeowner' in k.lower()]
                print(f"User info in extracted data: {user_info_fields}")
                
    except Exception as e:
        print(f"Error checking bid cards: {e}")

def check_conversations_table():
    """Check agent_conversations table"""
    print(f"\n=== CHECKING AGENT_CONVERSATIONS TABLE ===")
    
    try:
        convos = db.client.table('agent_conversations').select('*').limit(3).execute()
        
        if convos.data:
            print(f"Found {len(convos.data)} conversations")
            first_convo = convos.data[0]
            print(f"Conversation columns: {list(first_convo.keys())}")
            
            # Look for user ID
            if 'user_id' in first_convo:
                user_id = first_convo['user_id']
                print(f"Sample user_id: {user_id}")
                
                # Count conversations for this user
                user_convos = db.client.table('agent_conversations').select('*').eq('user_id', user_id).execute()
                print(f"This user has {len(user_convos.data)} conversations")
                
    except Exception as e:
        print(f"Error checking conversations: {e}")

def main():
    print("DATABASE STRUCTURE CHECK")
    print("=" * 50)
    
    list_tables()
    check_bid_cards_table()
    check_conversations_table()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print("The system appears to be using user_id directly")
    print("rather than a separate users/auth table.")
    print("User ID: e6e47a24-95ad-4af3-9ec5-f17999917bc3")
    print("This suggests the auth system may be handled")
    print("by the frontend or a separate service.")

if __name__ == "__main__":
    main()