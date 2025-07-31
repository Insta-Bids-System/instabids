#!/usr/bin/env python3
"""
Check Database Structure for Contractor Outreach Tracking
"""

from supabase import create_client
import os
from dotenv import load_dotenv

def check_outreach_database():
    """Check what outreach tracking infrastructure exists"""
    print("CHECKING CONTRACTOR OUTREACH TRACKING INFRASTRUCTURE")
    print("=" * 60)
    
    load_dotenv('../.env', override=True)
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))

    # Check what tables exist for outreach tracking
    tables = [
        'contractor_outreach_attempts',
        'contractor_engagement_summary', 
        'potential_contractors',
        'bid_cards'
    ]

    existing_tables = []
    
    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f'[EXISTS] Table: {table}')
            existing_tables.append(table)
            
            if result.data:
                columns = list(result.data[0].keys())
                print(f'         Columns: {", ".join(columns)}')
            else:
                print(f'         Status: Empty table')
                
        except Exception as e:
            print(f'[MISSING] Table: {table}')
            print(f'          Error: {str(e)[:80]}...')
        print()
    
    # Check if we have outreach tracking data
    if 'contractor_outreach_attempts' in existing_tables:
        try:
            attempts = supabase.table('contractor_outreach_attempts').select('*').limit(3).execute()
            print(f"OUTREACH ATTEMPTS DATA: {len(attempts.data)} records found")
            for attempt in attempts.data:
                print(f"  - {attempt.get('company_name', 'Unknown')} via {attempt.get('outreach_method', 'Unknown')}")
        except Exception as e:
            print(f"OUTREACH ATTEMPTS: Could not read data - {e}")
        print()
    
    # Check what we have in potential_contractors
    if 'potential_contractors' in existing_tables:
        try:
            contractors = supabase.table('potential_contractors').select(
                'company_name,phone,email,website,google_rating,google_review_count,match_score,discovery_source'
            ).limit(3).execute()
            
            print(f"POTENTIAL CONTRACTORS: {len(contractors.data)} records found")
            for contractor in contractors.data:
                has_email = "YES" if contractor.get('email') else "NO"
                has_website = "YES" if contractor.get('website') else "NO"
                print(f"  - {contractor.get('company_name', 'Unknown')}")
                print(f"    Email: {has_email}, Website: {has_website}, Rating: {contractor.get('google_rating', 'N/A')}")
        except Exception as e:
            print(f"POTENTIAL CONTRACTORS: Could not read data - {e}")
        print()
    
    print("ANALYSIS:")
    print("=========")
    
    # Check if we have the basic tracking infrastructure
    has_outreach_tracking = 'contractor_outreach_attempts' in existing_tables
    has_contractors = 'potential_contractors' in existing_tables
    has_engagement_tracking = 'contractor_engagement_summary' in existing_tables
    
    print(f"Outreach Tracking Table: {'EXISTS' if has_outreach_tracking else 'MISSING'}")
    print(f"Contractor Discovery: {'EXISTS' if has_contractors else 'MISSING'}")
    print(f"Engagement Tracking: {'EXISTS' if has_engagement_tracking else 'MISSING'}")
    
    if has_contractors:
        # Check email coverage
        contractors = supabase.table('potential_contractors').select('email,website').execute()
        total = len(contractors.data)
        with_emails = len([c for c in contractors.data if c.get('email')])
        with_websites = len([c for c in contractors.data if c.get('website')])
        
        print(f"\nCONTRACTOR DATA QUALITY:")
        print(f"Total Contractors: {total}")
        print(f"With Emails: {with_emails} ({(with_emails/total*100):.1f}%)" if total > 0 else "With Emails: 0")
        print(f"With Websites: {with_websites} ({(with_websites/total*100):.1f}%)" if total > 0 else "With Websites: 0")
    
    return {
        'has_outreach_tracking': has_outreach_tracking,
        'has_contractors': has_contractors,
        'has_engagement_tracking': has_engagement_tracking,
        'existing_tables': existing_tables
    }

if __name__ == "__main__":
    result = check_outreach_database()
    
    print("\nNEXT STEPS NEEDED:")
    print("==================")
    
    if not result['has_outreach_tracking']:
        print("1. CREATE outreach tracking tables")
    
    if result['has_contractors']:
        print("2. BUILD email extraction agent with Playwright")
        print("3. CREATE contractor ranking/selection system")
        print("4. SETUP automated outreach campaigns")
    else:
        print("1. SETUP contractor discovery first")
    
    print("5. IMPLEMENT bid card tracking per contractor")
    print("6. BUILD response monitoring and follow-up system")