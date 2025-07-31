#!/usr/bin/env python3
"""
Run foreign key migration to fix table references
"""

import os
from supabase import create_client
from dotenv import load_dotenv

def run_migration():
    # Load environment
    load_dotenv(override=True)

    # Create Supabase client
    supabase = create_client(
        os.getenv('SUPABASE_URL'), 
        os.getenv('SUPABASE_ANON_KEY')
    )

    print('Running foreign key migration...')

    # SQL commands to fix foreign keys and add test flags
    migration_steps = [
        {
            "name": "Fix contractor_outreach_attempts foreign key",
            "sql": "ALTER TABLE contractor_outreach_attempts DROP CONSTRAINT IF EXISTS contractor_outreach_attempts_contractor_lead_id_fkey"
        },
        {
            "name": "Add contractor_outreach_attempts foreign key",
            "sql": "ALTER TABLE contractor_outreach_attempts ADD CONSTRAINT contractor_outreach_attempts_contractor_lead_id_fkey FOREIGN KEY (contractor_lead_id) REFERENCES potential_contractors(id)"
        },
        {
            "name": "Fix contractor_engagement_summary foreign key",
            "sql": "ALTER TABLE contractor_engagement_summary DROP CONSTRAINT IF EXISTS contractor_engagement_summary_contractor_lead_id_fkey"
        },
        {
            "name": "Add contractor_engagement_summary foreign key", 
            "sql": "ALTER TABLE contractor_engagement_summary ADD CONSTRAINT contractor_engagement_summary_contractor_lead_id_fkey FOREIGN KEY (contractor_lead_id) REFERENCES potential_contractors(id)"
        },
        {
            "name": "Add test flag to potential_contractors",
            "sql": "ALTER TABLE potential_contractors ADD COLUMN IF NOT EXISTS is_test_contractor BOOLEAN DEFAULT FALSE"
        },
        {
            "name": "Add test flag to outreach_campaigns",
            "sql": "ALTER TABLE outreach_campaigns ADD COLUMN IF NOT EXISTS is_test_campaign BOOLEAN DEFAULT FALSE"
        },
        {
            "name": "Add test flag to contractor_outreach_attempts",
            "sql": "ALTER TABLE contractor_outreach_attempts ADD COLUMN IF NOT EXISTS is_test_outreach BOOLEAN DEFAULT FALSE"
        },
        {
            "name": "Add test flag to contractor_engagement_summary",
            "sql": "ALTER TABLE contractor_engagement_summary ADD COLUMN IF NOT EXISTS is_test_data BOOLEAN DEFAULT FALSE"
        },
        {
            "name": "Create index for potential_contractors test flag",
            "sql": "CREATE INDEX IF NOT EXISTS idx_potential_contractors_test ON potential_contractors(is_test_contractor)"
        },
        {
            "name": "Create index for outreach_attempts test flag",
            "sql": "CREATE INDEX IF NOT EXISTS idx_outreach_attempts_test ON contractor_outreach_attempts(is_test_outreach)"
        }
    ]
    
    success_count = 0
    for i, step in enumerate(migration_steps, 1):
        try:
            print(f'Executing {i}/{len(migration_steps)}: {step["name"]}')
            result = supabase.rpc('exec_sql', {'sql': step['sql']}).execute()
            print(f'  Success')
            success_count += 1
        except Exception as e:
            print(f'  Failed - {str(e)[:100]}')
    
    print(f'\nMigration Results: {success_count}/{len(migration_steps)} commands succeeded')
    
    if success_count == len(migration_steps):
        print('Migration completed successfully!')
        print('Fixed references to potential_contractors table')
        print('Added test flags to all contractor tables')
        print('Created indexes for efficient test data filtering')
    else:
        print('Some migration commands failed - check logs above')
    
    # Verify the changes
    print('\nVerifying foreign key constraints...')
    try:
        # Check if we can query with joins
        result = supabase.table('contractor_outreach_attempts')\
            .select('id, contractor_lead_id, potential_contractors(company_name)')\
            .limit(1)\
            .execute()
        print('Foreign key joins working correctly')
        return True
    except Exception as e:
        print(f'Foreign key verification failed: {e}')
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print('\nNext steps:')
        print('1. Create fake contractors with is_test_contractor=TRUE')
        print('2. Run end-to-end outreach test with fake data')
        print('3. Test campaign creation (should work now)')
    exit(0 if success else 1)