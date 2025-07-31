#!/usr/bin/env python3
"""
Check all tables in Supabase database
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment
parent_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(parent_dir, '.env'), override=True)

def check_tables():
    """Check which tables exist in database"""
    
    # Initialize Supabase
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY")
        return
        
    supabase = create_client(url, key)
    print(f"Connected to Supabase project: {url.split('.')[0].split('//')[1]}")
    
    # List of tables to check
    tables_to_check = [
        # Core tables (should exist)
        'bid_cards',
        'contractor_leads', 
        'agent_conversations',
        'profiles',
        'projects',
        
        # Outreach tables (from migration 005)
        'contractor_outreach_attempts',
        'contractor_engagement_summary',
        'outreach_campaigns',
        'message_templates',
        
        # Distribution tables (might be missing)
        'bid_card_distributions',
        'campaign_contractors',
        'contractor_responses',
        'email_tracking_events',
        
        # Other possible tables
        'bid_card_views',
        'bid_card_engagement_events',
        'followup_attempts',
        'followup_logs',
        'notifications',
        'manual_followup_tasks'
    ]
    
    print("\nChecking tables:")
    print("=" * 60)
    
    existing_tables = []
    missing_tables = []
    
    for table in tables_to_check:
        try:
            # Try to select one record from the table
            result = supabase.table(table).select('id').limit(1).execute()
            print(f"[EXISTS] {table:<35}")
            existing_tables.append(table)
        except Exception as e:
            error_msg = str(e)
            if 'relation' in error_msg and 'does not exist' in error_msg:
                print(f"[MISSING] {table:<35}")
                missing_tables.append(table)
            else:
                print(f"[ERROR] {table:<35} {error_msg[:50]}...")
    
    print("\n" + "=" * 60)
    print(f"\nSummary:")
    print(f"  Existing tables: {len(existing_tables)}")
    print(f"  Missing tables:  {len(missing_tables)}")
    
    if missing_tables:
        print(f"\nMissing tables that need to be created:")
        for table in missing_tables:
            print(f"  - {table}")
            
        print("\nThese tables are needed for:")
        if 'bid_card_distributions' in missing_tables:
            print("  - bid_card_distributions: Track which contractors received which bid cards")
        if 'campaign_contractors' in missing_tables:
            print("  - campaign_contractors: Link campaigns to specific contractors")
        if 'contractor_responses' in missing_tables:
            print("  - contractor_responses: Track detailed contractor responses")
        if 'email_tracking_events' in missing_tables:
            print("  - email_tracking_events: Track email opens and clicks")
            
    print("\nNote: You can create missing tables using the SQL migrations in:")
    print("  ai-agents/database/migrations/")
    print("  Or from the CREATE TABLE statements in the agent files")

if __name__ == "__main__":
    check_tables()