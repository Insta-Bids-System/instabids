#!/usr/bin/env python3
"""
Show the enriched contractor details
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database_simple import SupabaseDB

db = SupabaseDB()

# Get the contractor we just enriched
contractor_id = "1e649f49-fba4-451c-be9d-3b19d3c774e1"

result = db.client.table('potential_contractors')\
    .select("*")\
    .eq('id', contractor_id)\
    .execute()

if result.data:
    contractor = result.data[0]
    
    print("ENRICHED CONTRACTOR IN DATABASE")
    print("=" * 80)
    print(f"\nCompany: {contractor['company_name']}")
    print(f"ID: {contractor['id']}")
    print(f"Website: {contractor['website']}")
    print(f"Phone: {contractor.get('phone', 'Not provided')}")
    print(f"Location: {contractor.get('city', '')}, {contractor.get('state', '')}")
    print(f"Google Rating: {contractor.get('google_rating', 0)} ({contractor.get('google_review_count', 0)} reviews)")
    
    print(f"\n[ENRICHMENT DATA]")
    print(f"Email: {contractor.get('email', 'Not found')}")
    print(f"Business Size Category: {contractor.get('business_size_category', 'Not classified')}")
    print(f"Years in Business: {contractor.get('years_in_business', 'Unknown')}")
    print(f"Specialties: {contractor.get('specialties', [])}")
    
    print(f"\n[AI-GENERATED CONTENT]")
    if contractor.get('ai_business_summary'):
        print(f"AI Business Summary:")
        print(f"  {contractor['ai_business_summary']}")
    
    if contractor.get('ai_capability_description'):
        print(f"\nAI Capability Description:")
        print(f"  {contractor['ai_capability_description']}")
    
    print(f"\n[FLAGS]")
    print(f"Is Test Contractor: {contractor.get('is_test_contractor', False)}")
    print(f"Insurance Verified: {contractor.get('insurance_verified', False)}")
    print(f"Bonded: {contractor.get('bonded', False)}")
    print(f"Contact Attempted: {contractor.get('contact_attempted', False)}")
    print(f"Contact Successful: {contractor.get('contact_successful', False)}")
    print(f"Onboarded: {contractor.get('onboarded', False)}")
else:
    print("Contractor not found")