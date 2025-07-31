#!/usr/bin/env python3
"""
Create memory tables for multi-project system using Supabase client
"""
import sys
sys.path.append('.')
from database_simple import db

def create_memory_tables():
    """Create the memory system tables"""
    
    print("Creating memory system tables...")
    
    # Since we can't execute DDL directly, we'll create these tables by using the 
    # Supabase client's table creation approach through data insertion
    
    # Method: Create dummy records that will force table creation with proper schema
    
    # For user_memories table
    try:
        print("Creating user_memories structure...")
        # Create a comprehensive test record that establishes the schema
        user_memory_record = {
            'id': '00000000-0000-0000-0000-000000000001',  # Will be overridden by gen_random_uuid()
            'user_id': '00000000-0000-0000-0000-000000000001',
            'memory_type': 'setup_test',
            'memory_data': {
                'table_creation': True,
                'created_by': 'migration_script',
                'structure_test': {
                    'nested_data': True,
                    'arrays': ['test1', 'test2'],
                    'numbers': 123,
                    'booleans': True
                }
            },
            'created_at': '2025-07-29T19:00:00.000Z',
            'updated_at': '2025-07-29T19:00:00.000Z'
        }
        
        # This should work if table exists, or give us specific error about table structure
        result = db.client.table('user_memories').insert(user_memory_record).execute()
        
        if result.data:
            # Success - clean up
            record_id = result.data[0]['id']
            db.client.table('user_memories').delete().eq('id', record_id).execute()
            print("[OK] user_memories table ready")
        else:
            print("[ERROR] user_memories table creation failed")
            
    except Exception as e:
        print(f"[INFO] user_memories table issue: {e}")
        
        # If table doesn't exist, we need to create it differently
        # Let's try using the raw SQL approach through rpc if available
        try:
            create_user_memories_sql = '''
            CREATE TABLE IF NOT EXISTS user_memories (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL,
                memory_type VARCHAR(100) NOT NULL,
                memory_data JSONB NOT NULL DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id, memory_type)
            );
            '''
            
            # Try RPC call for SQL execution
            rpc_result = db.client.rpc('create_table', {'sql': create_user_memories_sql}).execute()
            print("[OK] user_memories table created via RPC")
            
        except Exception as rpc_e:
            print(f"[ERROR] Could not create user_memories table: {rpc_e}")
    
    # For project_summaries table  
    try:
        print("Creating project_summaries structure...")
        summary_record = {
            'id': '00000000-0000-0000-0000-000000000002',
            'user_id': '00000000-0000-0000-0000-000000000001',
            'project_id': '12345678-1234-1234-1234-123456789012',
            'summary_data': {
                'project_type': 'test',
                'status': 'setup',
                'key_info': ['item1', 'item2']
            },
            'last_updated': '2025-07-29T19:00:00.000Z'
        }
        
        result = db.client.table('project_summaries').insert(summary_record).execute()
        
        if result.data:
            record_id = result.data[0]['id'] 
            db.client.table('project_summaries').delete().eq('id', record_id).execute()
            print("[OK] project_summaries table ready")
        else:
            print("[ERROR] project_summaries table creation failed")
            
    except Exception as e:
        print(f"[INFO] project_summaries table issue: {e}")
    
    # For project_contexts table
    try:
        print("Creating project_contexts structure...")
        context_record = {
            'id': '00000000-0000-0000-0000-000000000003',
            'user_id': '00000000-0000-0000-0000-000000000001',
            'project_id': '12345678-1234-1234-1234-123456789012', 
            'context_data': {
                'conversation_stage': 'test',
                'collected_info': {},
                'agent_insights': {}
            },
            'last_accessed': '2025-07-29T19:00:00.000Z'
        }
        
        result = db.client.table('project_contexts').insert(context_record).execute()
        
        if result.data:
            record_id = result.data[0]['id']
            db.client.table('project_contexts').delete().eq('id', record_id).execute() 
            print("[OK] project_contexts table ready")
        else:
            print("[ERROR] project_contexts table creation failed")
            
    except Exception as e:
        print(f"[INFO] project_contexts table issue: {e}")
    
    print("\nMemory tables creation completed!")
    print("Testing table access...")
    
    # Test final access
    test_tables = ['user_memories', 'project_summaries', 'project_contexts']
    
    for table in test_tables:
        try:
            result = db.client.table(table).select('*').limit(1).execute()
            print(f"[OK] {table} accessible")
        except Exception as e:
            print(f"[ERROR] {table} not accessible: {e}")

if __name__ == "__main__":
    create_memory_tables()