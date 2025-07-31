"""
Create missing Supabase tables programmatically
This will create the conversations and bid_cards tables
"""
import os
from dotenv import load_dotenv

# Load with override
load_dotenv(override=True)

print("=== CREATING SUPABASE TABLES ===")

try:
    from supabase import create_client
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"Connecting to: {url}")
    
    supabase = create_client(url, key)
    
    # Create conversations table
    print("\n1. Creating conversations table...")
    
    conversations_sql = """
    CREATE TABLE IF NOT EXISTS conversations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id VARCHAR(255) UNIQUE NOT NULL,
        state JSONB NOT NULL DEFAULT '{}',
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )
    """
    
    try:
        # Try using a stored procedure or direct SQL execution
        result = supabase.rpc('exec_sql', {'sql': conversations_sql}).execute()
        print(f"   [OK] Conversations table created: {result}")
    except Exception as e:
        print(f"   [ERROR] Failed to create conversations table: {e}")
        
        # Alternative: Try creating via REST API call (this might not work)
        print("   Trying alternative method...")
        
        # For now, let's just test if we can insert a dummy record
        # This will fail but might give us info about the table structure
        try:
            dummy_insert = supabase.table('conversations').insert({
                'session_id': 'test_session',
                'state': {'test': True}
            }).execute()
            print(f"   [UNEXPECTED] Table exists and insert worked")
        except Exception as e2:
            if "does not exist" in str(e2):
                print(f"   [CONFIRMED] Table doesn't exist: {e2}")
            else:
                print(f"   [INFO] Different error: {e2}")
    
    # Create bid_cards table
    print("\n2. Creating bid_cards table...")
    
    bid_cards_sql = """
    CREATE TABLE IF NOT EXISTS bid_cards (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        cia_session_id VARCHAR(255),
        bid_card_number VARCHAR(50) UNIQUE NOT NULL,
        project_type VARCHAR(100),
        urgency_level VARCHAR(20),
        complexity_score INTEGER,
        contractor_count_needed INTEGER DEFAULT 3,
        budget_min INTEGER,
        budget_max INTEGER,
        bid_document JSONB,
        requirements_extracted JSONB,
        status VARCHAR(20) DEFAULT 'generated',
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )
    """
    
    try:
        result = supabase.rpc('exec_sql', {'sql': bid_cards_sql}).execute()
        print(f"   [OK] Bid cards table created: {result}")
    except Exception as e:
        print(f"   [ERROR] Failed to create bid_cards table: {e}")
    
    print(f"\n=== SOLUTION ===")
    print(f"Since we can't create tables programmatically with the anon key,")
    print(f"you need to run the SQL manually in Supabase dashboard:")
    print(f"")
    print(f"1. Go to https://supabase.com/dashboard")
    print(f"2. Open your project: xrhgrthdcaymxuqcgrmj")
    print(f"3. Go to SQL Editor")
    print(f"4. Run the contents of 'setup_supabase_schema.sql'")
    print(f"")
    print(f"OR you need the service key (not anon key) to create tables.")
    
    # Test current permissions
    print(f"\n=== TESTING CURRENT PERMISSIONS ===")
    try:
        # Try to insert into a non-existent table to see the error
        result = supabase.table('test_table').select('*').limit(1).execute()
        print(f"Unexpected success")
    except Exception as e:
        print(f"Expected error (confirms no tables): {e}")
        
except Exception as e:
    print(f"Connection failed: {e}")
    import traceback
    traceback.print_exc()