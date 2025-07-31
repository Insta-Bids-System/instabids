#!/usr/bin/env python3
"""
Check the actual schema of agent_conversations table
"""
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment
load_dotenv(override=True)
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

print("Checking agent_conversations table schema...")
print("=" * 50)

try:
    supabase = create_client(supabase_url, supabase_key)
    
    # Try to query with minimal fields
    result = supabase.table('agent_conversations').select('thread_id').limit(1).execute()
    
    print("Table exists and is accessible")
    
    # Get one record to see structure
    if result.data:
        print("\nSample record structure:")
        for key in result.data[0].keys():
            print(f"  - {key}")
    else:
        print("No records found, trying to insert minimal record...")
        # Try minimal insert
        test_result = supabase.table('agent_conversations').insert({
            'thread_id': 'schema_test',
            'user_id': 'test_user',
            'state': {}
        }).execute()
        
        if test_result.data:
            print("\nSuccessful insert! Table columns:")
            for key in test_result.data[0].keys():
                print(f"  - {key}")
            
            # Clean up
            supabase.table('agent_conversations').delete().eq('thread_id', 'schema_test').execute()
            
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying to create the table if it doesn't exist...")
