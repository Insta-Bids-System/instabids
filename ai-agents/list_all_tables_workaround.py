#!/usr/bin/env python3
"""
Workaround to list ALL tables in Supabase using direct SQL
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import psycopg2
from urllib.parse import urlparse

# Load environment
parent_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(parent_dir, '.env'), override=True)

def list_all_tables_direct():
    """List all tables using direct PostgreSQL connection"""
    
    # Get Supabase URL and parse it
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY")
        return
        
    # Extract project ID from URL
    project_id = supabase_url.split('.')[0].split('//')[1]
    
    # Construct database URL (standard Supabase pattern)
    db_host = f"db.{project_id}.supabase.co"
    db_name = "postgres"
    db_user = "postgres"
    
    print(f"Project ID: {project_id}")
    print(f"Database Host: {db_host}")
    print("\nNote: Direct database connection requires database password.")
    print("Trying alternative approach using Supabase REST API...\n")
    
    # Alternative: Use Supabase client to check known patterns
    supabase = create_client(supabase_url, supabase_key)
    
    # Common Instabids table patterns
    table_patterns = [
        # Core tables
        'profiles', 'projects', 'bid_cards', 'agent_conversations',
        
        # Contractor tables
        'contractor_leads', 'contractor_outreach_attempts', 
        'contractor_engagement_summary', 'potential_contractors',
        
        # Campaign tables
        'outreach_campaigns', 'campaign_contractors', 'message_templates',
        
        # Distribution tables
        'bid_card_distributions', 'bid_card_views', 'bid_card_engagement_events',
        
        # Response tables
        'contractor_responses', 'email_tracking_events', 'response_events',
        
        # Follow-up tables
        'followup_attempts', 'followup_logs', 'notifications',
        'manual_followup_tasks',
        
        # Auth tables (usually exist)
        'auth.users', 'auth.sessions',
        
        # Other possible Instabids tables
        'homeowners', 'contractors', 'bids', 'messages', 'reviews',
        'payments', 'invoices', 'estimates', 'leads', 'conversations',
        'chat_messages', 'chat_sessions', 'user_sessions',
        'contractor_profiles', 'homeowner_profiles',
        'project_images', 'project_documents', 'project_bids',
        'contractor_ratings', 'contractor_reviews',
        'notification_settings', 'user_preferences',
        'api_logs', 'audit_logs', 'error_logs'
    ]
    
    print("Checking possible Instabids tables:")
    print("=" * 60)
    
    found_tables = []
    
    for table in table_patterns:
        try:
            # For auth schema tables
            if table.startswith('auth.'):
                # Skip auth tables for now
                continue
                
            # Try to query the table
            result = supabase.table(table).select('*').limit(0).execute()
            print(f"[FOUND] {table}")
            found_tables.append(table)
            
        except Exception as e:
            # Table doesn't exist - silent fail
            pass
    
    print("\n" + "=" * 60)
    print(f"\nFound {len(found_tables)} tables in your Instabids project:")
    for table in sorted(found_tables):
        print(f"  - {table}")
        
    print("\nNote: This may not be ALL tables. To see ALL tables:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to Table Editor")
    print("3. Or run this SQL in SQL Editor:")
    print("\n   SELECT schemaname, tablename")
    print("   FROM pg_tables")
    print("   WHERE schemaname NOT IN ('pg_catalog', 'information_schema')")
    print("   ORDER BY schemaname, tablename;")

if __name__ == "__main__":
    list_all_tables_direct()