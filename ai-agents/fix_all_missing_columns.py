#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_simple import SupabaseDB
import uuid
from datetime import datetime

def fix_missing_columns():
    """
    Add all missing columns to campaign_check_ins table
    Since we can't alter the table directly, we'll identify exactly what columns 
    the system expects vs what exists by analyzing the error messages
    """
    print("ANALYZING MISSING COLUMNS IN CAMPAIGN_CHECK_INS")
    print("=" * 55)
    
    db = SupabaseDB()
    
    # The code is trying to insert these columns based on check_in_manager.py line 104:
    expected_columns = [
        'campaign_id',
        'check_in_number', 
        'check_in_percentage',
        'scheduled_time',
        'expected_responses'  # This is definitely missing from schema
    ]
    
    print("Expected columns from code analysis:")
    for col in expected_columns:
        print(f"  - {col}")
    
    # Based on the database error, it has these columns (from the failing row):
    # Failing row contains (id, campaign_id, check_in_time, ?, 0, 0, f, null, created_at, 1, pending, 25, scheduled_time, 0, 0, 0, t, 0, f, null, 0, 0)
    
    print("\nFrom error analysis, the table appears to have different column names.")
    print("The system is trying to insert 'expected_responses' but the table doesn't have it.")
    print("\nLet me check what the orchestrator is actually trying to insert...")
    
    # Look at the exact insert that's failing in the orchestrator
    print("\nBased on enhanced_campaign_orchestrator.py line 104:")
    print("The system inserts: expected_responses")
    print("But the table schema doesn't have this column.")
    
    print("\nSince I cannot alter the table structure directly through Supabase client,")
    print("I need to modify the code to use existing columns or ask user to add the column via SQL.")
    
    print("\nRECOMMENDATION:")
    print("Run this SQL command in Supabase SQL Editor:")
    print("ALTER TABLE campaign_check_ins ADD COLUMN expected_responses INTEGER;")
    
    return False

if __name__ == "__main__":
    fix_missing_columns()
    print("\nPlease run the SQL command above in Supabase SQL Editor, then retry the campaign.")