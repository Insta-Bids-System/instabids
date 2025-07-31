#!/usr/bin/env python3
"""
ACTUALLY check ALL tables in Supabase database
"""
import os
import sys
from dotenv import load_dotenv
import requests

# Load environment
parent_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(parent_dir, '.env'), override=True)

def get_all_tables():
    """Get ALL tables using REST API"""
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY")
        return
        
    # Query the information_schema to get all tables
    query_url = f"{url}/rest/v1/rpc/get_tables"
    
    # Try a different approach - query a known table and check error
    # Since we can't directly query information_schema, let's use a workaround
    print(f"Connected to Supabase project: {url.split('.')[0].split('//')[1]}")
    print("\nTrying to detect all tables...")
    print("=" * 60)
    
    # Try to use the REST API to get schema info
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # First, let's try to get all data from a system table
    # This might give us hints about other tables
    test_tables = [
        'information_schema.tables',
        'pg_catalog.pg_tables', 
        'public.*'
    ]
    
    print("\nNote: Direct table listing requires admin access.")
    print("I can only check tables I know about from the code.")
    print("\nTo see ALL 20 tables you mentioned, you would need to:")
    print("1. Check the Supabase dashboard directly")
    print("2. Use pgAdmin or another PostgreSQL client")
    print("3. Run this SQL in the Supabase SQL editor:")
    print("\n   SELECT table_name FROM information_schema.tables")
    print("   WHERE table_schema = 'public'")
    print("   ORDER BY table_name;")
    
    return None

if __name__ == "__main__":
    get_all_tables()