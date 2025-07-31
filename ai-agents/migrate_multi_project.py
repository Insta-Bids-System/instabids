#!/usr/bin/env python3
"""
Run multi-project system migration using existing database connection
"""
import os
import sys
import asyncio
sys.path.append('.')
from database_simple import db

async def run_migration():
    """Execute the multi-project system migration"""
    
    print("Starting multi-project system migration...")
    print("=" * 50)
    
    # Test database connection first
    try:
        await db.load_conversation_state('test-connection')
        print("[OK] Database connection verified")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False
    
    # Individual migration steps that we can execute safely
    migration_steps = [
        {
            "name": "Create projects table",
            "action": "create_table",
            "table": "projects",
            "data": {
                'id': '00000000-0000-0000-0000-000000000000',  # Will be replaced by gen_random_uuid()
                'user_id': '00000000-0000-0000-0000-000000000001',
                'title': 'Migration Test Project',
                'description': 'Test project for migration',
                'status': 'active'
            }
        }
    ]
    
    # Try to execute each step using the existing client
    for step in migration_steps:
        try:
            print(f"Executing: {step['name']}")
            
            if step['action'] == 'create_table':
                # Try to insert test data - this will create table if it doesn't exist
                table_name = step['table']
                test_data = step['data']
                
                print(f"  Testing table creation by inserting into {table_name}...")
                
                # Use the client from database_simple
                result = db.client.table(table_name).insert(test_data).execute()
                
                if result.data:
                    # Success - clean up test data
                    test_id = result.data[0]['id']
                    db.client.table(table_name).delete().eq('id', test_id).execute()
                    print(f"  [OK] Table {table_name} exists and working")
                else:
                    print(f"  [ERROR] Could not test table {table_name}")
                    
        except Exception as e:
            error_msg = str(e).lower()
            if 'relation' in error_msg and 'does not exist' in error_msg:
                print(f"  [INFO] Table {step['table']} needs to be created")
                print(f"  [ERROR] Cannot create tables via client - need SQL DDL access")
            else:
                print(f"  [ERROR] {step['name']} failed: {e}")
    
    # Test what tables currently exist
    print("\nTesting existing table access...")
    
    existing_tables = ['agent_conversations', 'conversation_images', 'profiles']
    
    for table in existing_tables:
        try:
            result = db.client.table(table).select('*').limit(1).execute()
            print(f"  [OK] Table {table} exists and accessible")
        except Exception as e:
            print(f"  [ERROR] Table {table} error: {e}")
    
    # Since we can't create tables directly, let's update our approach
    print("\n" + "=" * 50)
    print("MIGRATION APPROACH NEEDED:")
    print("1. Tables need to be created via Supabase Dashboard SQL Editor")
    print("2. Or via service key with elevated permissions")
    print("3. Current anon key only allows data operations")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = asyncio.run(run_migration())
    sys.exit(0 if success else 1)