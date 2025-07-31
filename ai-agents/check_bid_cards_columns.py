#!/usr/bin/env python3
"""
Check exact columns in bid_cards table
"""
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment
load_dotenv(override=True)
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(supabase_url, supabase_key)

print("Checking bid_cards table columns...")
print("=" * 50)

try:
    # Try to query with minimal field to see if table exists
    result = supabase.table('bid_cards').select('id').limit(1).execute()
    
    print("Table exists!")
    
    # Try to insert minimal record to see required fields
    from datetime import datetime
    test_record = {
        'cia_thread_id': 'column_test',
        'bid_card_number': f'TEST_{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'project_type': 'test',
        'urgency_level': 'flexible',
        'complexity_score': 5,
        'contractor_count_needed': 3,
        'budget_min': 100,
        'budget_max': 200,
        'bid_document': {},
        'requirements_extracted': {},
        'status': 'generated'
    }
    
    # Try insert
    insert_result = supabase.table('bid_cards').insert(test_record).execute()
    
    if insert_result.data:
        print("\nSuccessful insert! Available columns:")
        for key in insert_result.data[0].keys():
            print(f"  - {key}")
        
        # Clean up
        supabase.table('bid_cards').delete().eq('bid_card_number', test_record['bid_card_number']).execute()
        
except Exception as e:
    print(f"Error: {e}")
    print("\nThe bid_cards table might not have all expected columns.")
    print("You need to run the create_bid_cards_table.sql on Supabase.")
