#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_simple import SupabaseDB

def test_campaign_check_ins_columns():
    """
    Test what columns exist in campaign_check_ins by trying to insert a test record
    """
    print("TESTING CAMPAIGN_CHECK_INS COLUMNS")
    print("=" * 50)
    
    db = SupabaseDB()
    
    # Try to insert a minimal test record to see what columns exist
    test_record = {
        'campaign_id': 'test-campaign-id',
        'check_in_number': 1,
        'check_in_percentage': 25.0,
        'scheduled_time': '2025-07-31T15:00:00Z',
        'expected_responses': 5
    }
    
    try:
        result = db.client.table('campaign_check_ins').insert(test_record).execute()
        print("SUCCESS: All columns exist!")
        print(f"Inserted record: {result.data}")
        
        # Clean up test record
        db.client.table('campaign_check_ins').delete().eq('campaign_id', 'test-campaign-id').execute()
        print("Cleaned up test record")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nLet me try with just basic columns...")
        
        # Try with minimal columns
        basic_record = {
            'campaign_id': 'test-campaign-id',
            'check_in_number': 1
        }
        
        try:
            result = db.client.table('campaign_check_ins').insert(basic_record).execute()
            print("SUCCESS: Basic columns work!")
            print(f"Inserted record: {result.data}")
            
            # Clean up
            db.client.table('campaign_check_ins').delete().eq('campaign_id', 'test-campaign-id').execute()
            
        except Exception as basic_error:
            print(f"ERROR even with basic columns: {basic_error}")
            
        return False

if __name__ == "__main__":
    test_campaign_check_ins_columns()