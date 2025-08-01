#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_simple import SupabaseDB

def add_expected_responses_column():
    """
    Add expected_responses column to campaign_check_ins table
    """
    print("ADDING EXPECTED_RESPONSES COLUMN TO CAMPAIGN_CHECK_INS")
    print("=" * 60)
    
    db = SupabaseDB()
    
    # Add expected_responses column using direct SQL execution
    try:
        # First check if column already exists
        check_sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'campaign_check_ins' 
        AND column_name = 'expected_responses';
        """
        
        # Use raw SQL query execution
        import psycopg2
        from urllib.parse import urlparse
        import os
        
        # Parse Supabase URL to get connection details
        supabase_url = os.getenv("SUPABASE_URL")
        if not supabase_url:
            raise ValueError("SUPABASE_URL not found")
            
        # Convert to PostgreSQL connection string
        # Supabase format: https://xxx.supabase.co
        # We need: postgresql://postgres:password@xxx.supabase.co:5432/postgres
        
        project_id = supabase_url.replace('https://', '').replace('.supabase.co', '')
        password = os.getenv("SUPABASE_DB_PASSWORD", "your_password_here")
        
        conn_string = f"postgresql://postgres:{password}@{project_id}.supabase.co:5432/postgres"
        
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        
        # Check if column exists
        cur.execute(check_sql)
        result = cur.fetchone()
        
        if result:
            print("Column 'expected_responses' already exists")
        else:
            # Add the column
            alter_sql = "ALTER TABLE campaign_check_ins ADD COLUMN expected_responses INTEGER;"
            cur.execute(alter_sql)
            conn.commit()
            print("SUCCESS: Added expected_responses column")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR with SQL approach: {e}")
        print("Trying alternative approach with table structure inspection...")
        
        # Alternative: Try to insert a test record to see what columns are missing
        try:
            test_record = {
                'campaign_id': 'test-campaign-id',
                'check_in_number': 1,
                'check_in_percentage': 25.0,
                'scheduled_time': '2025-07-31T15:00:00Z',
                'expected_responses': 5
            }
            
            result = db.client.table('campaign_check_ins').insert(test_record).execute()
            print("SUCCESS: Column exists and test insert worked")
            
            # Clean up test record
            db.client.table('campaign_check_ins').delete().eq('campaign_id', 'test-campaign-id').execute()
            
        except Exception as insert_error:
            print(f"Column missing - insert error: {insert_error}")
            return False
    
    print("\nCOLUMN ADDITION COMPLETE!")
    return True

if __name__ == "__main__":
    success = add_expected_responses_column()
    if success:
        print("Ready to test campaign flow!")
    else:
        print("Fix errors before retrying")