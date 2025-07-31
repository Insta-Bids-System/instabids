#!/usr/bin/env python3
"""
Check if bid_cards table exists in Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def check_bid_cards_table():
    """Check if bid_cards table exists"""
    
    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY")
        return False
    
    try:
        # Create Supabase client
        supabase = create_client(url, key)
        
        print(f"Checking Supabase: {url}")
        
        # Try to query the bid_cards table
        result = supabase.table('bid_cards').select("id").limit(1).execute()
        
        print("✅ bid_cards table EXISTS!")
        print(f"   Table has {len(result.data)} rows (checked limit 1)")
        return True
        
    except Exception as e:
        error_str = str(e)
        if "relation" in error_str and "does not exist" in error_str:
            print("❌ bid_cards table does NOT exist")
            print("\nTo create it:")
            print("1. Go to https://supabase.com/dashboard/project/xrhgrthdcaymxuqcgrmj/sql/new")
            print("2. Copy and paste the contents of create_bid_cards_table.sql")
            print("3. Click 'Run'")
            return False
        else:
            print(f"ERROR checking table: {e}")
            return False

if __name__ == "__main__":
    exists = check_bid_cards_table()
    
    if not exists:
        print("\n" + "="*60)
        print("SQL to create table is in: create_bid_cards_table.sql")
        print("="*60)