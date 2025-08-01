#!/usr/bin/env python3
"""
Check which contractors have been enriched with AI data
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database_simple import SupabaseDB

db = SupabaseDB()

print("CHECKING ENRICHED CONTRACTORS IN DATABASE")
print("=" * 80)

# First, check if the new columns exist by trying to select them
print("\n1. Checking for contractors with AI data in new columns...")
try:
    result = db.client.table('potential_contractors')\
        .select("id,company_name,website,business_size_category,ai_business_summary,ai_capability_description,is_test_contractor")\
        .not_.is_('ai_business_summary', 'null')\
        .limit(10)\
        .execute()
    
    if result.data:
        print(f"\nFound {len(result.data)} contractors with AI summaries:")
        for i, contractor in enumerate(result.data, 1):
            print(f"\n{i}. {contractor['company_name']}")
            print(f"   ID: {contractor['id']}")
            print(f"   Website: {contractor.get('website', 'None')}")
            print(f"   Business Size: {contractor.get('business_size_category', 'Not set')}")
            print(f"   Is Test: {contractor.get('is_test_contractor', False)}")
            if contractor.get('ai_business_summary'):
                print(f"   AI Summary: {contractor['ai_business_summary'][:100]}...")
            if contractor.get('ai_capability_description'):
                print(f"   AI Capabilities: {contractor['ai_capability_description'][:100]}...")
    else:
        print("No contractors found with AI summaries in the new columns")
        
except Exception as e:
    print(f"Error checking new columns: {e}")

# Check for any enriched contractors (might be using old method)
print("\n\n2. Checking for contractors marked as enriched...")
try:
    # Check if email field has been populated (sign of enrichment)
    result = db.client.table('potential_contractors')\
        .select("id,company_name,website,email,google_business_status,license_number")\
        .not_.is_('email', 'null')\
        .limit(10)\
        .execute()
    
    if result.data:
        print(f"\nFound {len(result.data)} contractors with emails (indicating enrichment):")
        for i, contractor in enumerate(result.data, 1):
            print(f"\n{i}. {contractor['company_name']}")
            print(f"   Email: {contractor['email']}")
            print(f"   Website: {contractor.get('website', 'None')}")
            
            # Check if using workaround columns
            if contractor.get('google_business_status') in ['INDIVIDUAL_HANDYMAN', 'OWNER_OPERATOR', 'LOCAL_BUSINESS_TEAMS', 'NATIONAL_COMPANY']:
                print(f"   [WORKAROUND] Business size in google_business_status: {contractor['google_business_status']}")
            if contractor.get('license_number') and 'AI_SUMMARY:' in str(contractor['license_number']):
                print(f"   [WORKAROUND] AI summary in license_number field")
    else:
        print("No enriched contractors found")
        
except Exception as e:
    print(f"Error checking enriched contractors: {e}")

# Check total contractor count
print("\n\n3. Overall contractor statistics...")
try:
    result = db.client.table('potential_contractors').select("id", count="exact").execute()
    print(f"Total contractors in database: {result.count}")
    
    # Check how many are from directories
    directories = ['homeadvisor', 'angies_list', 'bbb', 'yelp']
    for directory in directories:
        result = db.client.table('potential_contractors')\
            .select("id", count="exact")\
            .ilike('company_name', f'%{directory}%')\
            .execute()
        if result.count > 0:
            print(f"   From {directory}: {result.count}")
            
except Exception as e:
    print(f"Error getting statistics: {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)