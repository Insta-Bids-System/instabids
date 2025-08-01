#!/usr/bin/env python3
"""
Add missing columns using SERVICE_ROLE_KEY
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from supabase import create_client

# Get credentials
supabase_url = os.getenv("SUPABASE_URL", "https://xrhgrthdcaymxuqcgrmj.supabase.co")
service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyaGdydGhkY2F5bXh1cWNncm1qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzY1NzIwNiwiZXhwIjoyMDY5MjMzMjA2fQ.BH3hCDZUqUvCF0RL_50KXrNHWH7aWaZQKTqCTxLm8AI")

print("ADDING DATABASE COLUMNS WITH SERVICE ROLE KEY")
print("=" * 80)

# Create client with service role key
client = create_client(supabase_url, service_role_key)
print("[SUCCESS] Connected with SERVICE_ROLE_KEY")

# Try to execute DDL
try:
    # First, test if we can insert a record (this should work)
    test_data = {
        'company_name': 'DDL Test Company',
        'website': 'https://test.com',
        'discovery_source': 'test',
        'source_query': 'test',
        'project_zip_code': '12345',
        'project_type': 'test'
    }
    
    result = client.table('potential_contractors').insert(test_data).execute()
    if result.data:
        print("[SUCCESS] Can insert data")
        contractor_id = result.data[0]['id']
        
        # Clean up
        client.table('potential_contractors').delete().eq('id', contractor_id).execute()
        
    # Now try to add the new columns using postgrest
    # Unfortunately, PostgREST doesn't support DDL operations directly
    # We need to use a different approach
    
    print("\n[INFO] PostgREST (the Supabase Python client) doesn't support DDL operations")
    print("[INFO] Even with SERVICE_ROLE_KEY, we can only do DML (INSERT, UPDATE, DELETE)")
    print("[INFO] DDL operations (ALTER TABLE) must be done through:")
    print("       1. Supabase Dashboard SQL Editor")
    print("       2. Supabase CLI with migrations")
    print("       3. Direct PostgreSQL connection (not available in this environment)")
    
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "="*80)
print("SOLUTION: You must run this SQL in Supabase Dashboard:")
print("="*80)
print("""
ALTER TABLE potential_contractors 
ADD COLUMN IF NOT EXISTS ai_business_summary TEXT,
ADD COLUMN IF NOT EXISTS ai_capability_description TEXT,
ADD COLUMN IF NOT EXISTS business_size_category VARCHAR(50),
ADD COLUMN IF NOT EXISTS is_test_contractor BOOLEAN DEFAULT FALSE;
""")