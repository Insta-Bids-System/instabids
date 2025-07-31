"""
Check what tables and schema exist in Supabase
"""
import os
from dotenv import load_dotenv

# Load with override
load_dotenv(override=True)

print("=== SUPABASE SCHEMA CHECK ===")

try:
    from supabase import create_client
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"Connecting to: {url}")
    
    supabase = create_client(url, key)
    
    # Try to get list of tables using information_schema
    print("\nChecking for existing tables...")
    
    # This query should work to list tables
    tables_query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    """
    
    try:
        result = supabase.rpc('query', {'query': tables_query}).execute()
        print(f"Tables query result: {result}")
    except Exception as e:
        print(f"Tables query failed: {e}")
    
    # Try some common table names that might exist
    common_tables = ['conversations', 'users', 'projects', 'messages', 'chat_sessions']
    
    for table_name in common_tables:
        try:
            result = supabase.table(table_name).select("*").limit(1).execute()
            print(f"✓ Table '{table_name}' exists - {len(result.data)} rows found")
        except Exception as e:
            print(f"✗ Table '{table_name}' - {str(e)}")
    
    # Check if we can create a conversations table
    print(f"\nChecking table creation permissions...")
    
    try:
        # This should fail gracefully if we don't have permissions
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id VARCHAR(255) UNIQUE NOT NULL,
            state JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
        """
        # Note: This might not work via the Python client, but worth trying
        print("Would need to create conversations table via SQL")
        
    except Exception as e:
        print(f"Cannot create table: {e}")
        
except Exception as e:
    print(f"Connection failed: {e}")
    import traceback
    traceback.print_exc()