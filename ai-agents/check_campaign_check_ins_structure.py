#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_simple import SupabaseDB
import uuid

def check_campaign_check_ins_structure():
    """
    Check what columns exist in campaign_check_ins table
    """
    print("CHECKING CAMPAIGN_CHECK_INS TABLE STRUCTURE")
    print("=" * 50)
    
    db = SupabaseDB()
    
    # Generate proper UUID
    test_id = str(uuid.uuid4())
    
    # Try to insert with only the most basic column
    test_record = {
        'campaign_id': test_id
    }
    
    print(f"Trying to insert minimal record with campaign_id: {test_id}")
    
    try:
        result = db.client.table('campaign_check_ins').insert(test_record).execute()
        print("SUCCESS with minimal record!")
        print(f"Available columns from result: {list(result.data[0].keys()) if result.data else 'No data returned'}")
        
        # Clean up
        db.client.table('campaign_check_ins').delete().eq('campaign_id', test_id).execute()
        
    except Exception as e:
        print(f"ERROR with minimal record: {e}")
        
        # Try to see existing records to understand structure
        print("\nTrying to see existing campaign_check_ins records...")
        try:
            result = db.client.table('campaign_check_ins').select('*').limit(1).execute()
            if result.data:
                print("Found existing record!")
                print(f"Columns: {list(result.data[0].keys())}")
            else:
                print("No existing records found")
                
        except Exception as select_error:
            print(f"ERROR selecting records: {select_error}")

if __name__ == "__main__":
    check_campaign_check_ins_structure()