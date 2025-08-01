#!/usr/bin/env python3
"""
Check actual columns in potential_contractors table
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database_simple import SupabaseDB

db = SupabaseDB()

# Get one record to see structure
print("Checking potential_contractors table structure...")
result = db.client.table('potential_contractors').select("*").limit(1).execute()

if result.data:
    record = result.data[0]
    print(f"\nFound {len(record)} columns:")
    for i, (key, value) in enumerate(record.items()):
        print(f"{i+1:2d}. {key}: {type(value).__name__}")
        
    # Check for text columns we can use
    print("\nText/JSON columns we might use for AI data:")
    for key, value in record.items():
        if value is None or isinstance(value, str):
            if key not in ['id', 'created_at', 'updated_at', 'phone', 'email', 'website']:
                print(f"  - {key}")
else:
    print("No records found")

# Try to get column info from information schema
try:
    print("\n\nTrying to get column info from system tables...")
    # This might work if we have access
    query = """
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'potential_contractors'
    ORDER BY ordinal_position
    """
    # Can't execute raw SQL, but worth documenting what we need
    print("Need to check information_schema.columns for full structure")
except:
    pass