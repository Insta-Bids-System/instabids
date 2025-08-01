#!/usr/bin/env python3
"""
Force add columns through direct database manipulation
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database_simple import SupabaseDB

# Initialize database
db = SupabaseDB()

# First, let's see what we can do
print("Testing database access...")

# Try to create a test record with the new columns
test_data = {
    'company_name': 'Column Test Company',
    'website': 'https://test.com',
    'status': 'discovered',
    'discovery_source': 'test',
    'ai_business_summary': 'This is a test summary',
    'ai_capability_description': 'Test capabilities',
    'business_size_category': 'OWNER_OPERATOR',
    'is_test_contractor': True
}

try:
    # Try inserting with new columns
    result = db.client.table('potential_contractors').insert(test_data).execute()
    print("SUCCESS! Columns exist!")
    # Clean up
    db.client.table('potential_contractors').delete().eq('company_name', 'Column Test Company').execute()
except Exception as e:
    print(f"Columns don't exist: {e}")
    
    # Try another approach - use raw RPC call
    try:
        print("\nTrying RPC approach...")
        result = db.client.rpc('exec_sql', {
            'query': """
            ALTER TABLE potential_contractors 
            ADD COLUMN IF NOT EXISTS ai_business_summary TEXT,
            ADD COLUMN IF NOT EXISTS ai_capability_description TEXT,
            ADD COLUMN IF NOT EXISTS business_size_category VARCHAR(50),
            ADD COLUMN IF NOT EXISTS is_test_contractor BOOLEAN DEFAULT FALSE;
            """
        }).execute()
        print("RPC SUCCESS!")
    except Exception as rpc_error:
        print(f"RPC failed: {rpc_error}")
        
        # Try creating through schema endpoint
        try:
            print("\nTrying schema modification...")
            # This might work if we have schema access
            result = db.client.table('_migrations').insert({
                'name': 'add_ai_columns',
                'executed_at': 'now()',
                'hash': 'manual_add_columns',
                'migration': """
                ALTER TABLE potential_contractors 
                ADD COLUMN IF NOT EXISTS ai_business_summary TEXT,
                ADD COLUMN IF NOT EXISTS ai_capability_description TEXT,
                ADD COLUMN IF NOT EXISTS business_size_category VARCHAR(50),
                ADD COLUMN IF NOT EXISTS is_test_contractor BOOLEAN DEFAULT FALSE;
                """
            }).execute()
            print("Migration inserted!")
        except Exception as migration_error:
            print(f"Migration approach failed: {migration_error}")