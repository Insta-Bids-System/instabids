#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_simple import SupabaseDB
import uuid
from datetime import datetime, timedelta

def create_test_check_in():
    """
    Try to create a test check-in record with all required fields
    """
    print("CREATING TEST CHECK-IN RECORD")
    print("=" * 40)
    
    db = SupabaseDB()
    
    test_campaign_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + 'Z'
    
    # Try with all the fields I can see from the error message
    test_record = {
        'campaign_id': test_campaign_id,
        'check_in_time': now,  # This was the NOT NULL constraint that failed
        'check_in_number': 1,
        'check_in_percentage': 25.0,
        'scheduled_time': now,
        'expected_responses': 5  # This is the column we need to add
    }
    
    print(f"Attempting to insert check-in record with expected_responses column...")
    
    try:
        result = db.client.table('campaign_check_ins').insert(test_record).execute()
        print("SUCCESS! The expected_responses column exists!")
        print(f"Record created: {result.data[0] if result.data else 'No data returned'}")
        
        # Clean up
        db.client.table('campaign_check_ins').delete().eq('campaign_id', test_campaign_id).execute()
        print("Test record cleaned up")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        
        # Try without expected_responses to see if that's the missing column
        test_record_no_expected = {
            'campaign_id': test_campaign_id,
            'check_in_time': now,
            'check_in_number': 1,
            'check_in_percentage': 25.0,
            'scheduled_time': now
        }
        
        print("\nTrying without expected_responses column...")
        
        try:
            result = db.client.table('campaign_check_ins').insert(test_record_no_expected).execute()
            print("SUCCESS without expected_responses! This column is missing.")
            print(f"Record created: {result.data[0] if result.data else 'No data returned'}")
            
            # Show all columns that exist
            if result.data:
                print(f"\nExisting columns in campaign_check_ins:")
                for key in result.data[0].keys():
                    print(f"  - {key}")
            
            # Clean up
            db.client.table('campaign_check_ins').delete().eq('campaign_id', test_campaign_id).execute()
            print("\nTest record cleaned up")
            
        except Exception as no_expected_error:
            print(f"ERROR even without expected_responses: {no_expected_error}")
            
        return False

if __name__ == "__main__":
    success = create_test_check_in()
    if not success:
        print("\nThe expected_responses column needs to be added to campaign_check_ins table")