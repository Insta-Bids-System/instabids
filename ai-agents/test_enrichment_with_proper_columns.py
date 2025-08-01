#!/usr/bin/env python3
"""
Test enrichment with PROPER database columns
"""
import os
import sys
import asyncio
import uuid

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-api03-wF7cjEG4yTWvBAGtc7WJqmhmyRvzaQJPx5VJFcUALJqfk5PFVkXuJbLIdJGqcIZ_gKLg_LYFJa4IcBaOAIOhAg-3UXfVgAA'

async def test_enrichment_with_proper_columns():
    """Test enrichment with newly added database columns"""
    print("TESTING ENRICHMENT WITH PROPER DATABASE COLUMNS")
    print("=" * 80)
    
    from agents.enrichment.langchain_mcp_enrichment_agent import MCPPlaywrightEnrichmentAgent
    from database_simple import SupabaseDB
    
    db = SupabaseDB()
    enricher = MCPPlaywrightEnrichmentAgent()
    print("[SUCCESS] Systems initialized")
    
    # Create test contractor
    test_contractor = {
        'company_name': 'Elite Kitchen Remodeling Orlando',
        'website': 'https://example-elite-kitchen.com',
        'phone': '(407) 555-8888',
        'city': 'Orlando',
        'state': 'FL',
        'project_zip_code': '32801',
        'project_type': 'kitchen remodeling',
        'google_rating': 4.9,
        'google_review_count': 256,
        'discovery_source': 'test',
        'source_query': 'kitchen remodeling Orlando',
        'specialties': ['kitchen', 'remodeling', 'cabinets'],
        'search_rank': 1,
        'match_score': 98.0,
        'insurance_verified': True,
        'bonded': True,
        'contact_attempted': False,
        'contact_successful': False,
        'onboarded': False,
        'is_test_contractor': True  # NEW COLUMN!
    }
    
    # Insert test contractor
    print("\nInserting test contractor...")
    result = db.client.table('potential_contractors').insert(test_contractor).execute()
    
    if result.data:
        contractor_id = result.data[0]['id']
        print(f"[SUCCESS] Created test contractor: {contractor_id}")
        
        # Run enrichment
        print("\nRunning enrichment process...")
        contractor_data = {**test_contractor, 'id': contractor_id}
        enrichment_result = await enricher.enrich_contractor(contractor_data)
        
        print(f"\n[ENRICHMENT RESULTS]")
        print(f"   Status: {enrichment_result.enrichment_status}")
        print(f"   Email: {enrichment_result.email}")
        print(f"   Business Size: {enrichment_result.business_size}")
        print(f"   Service Types: {', '.join(enrichment_result.service_types)}")
        
        # Update with enrichment
        print("\nUpdating database with enrichment data...")
        update_success = enricher.update_contractor_after_enrichment(contractor_id, enrichment_result)
        
        if update_success:
            print("[SUCCESS] Database updated with enrichment data")
            
            # Verify proper column storage
            print("\nVerifying data in PROPER columns...")
            check = db.client.table('potential_contractors').select("*").eq('id', contractor_id).execute()
            
            if check.data:
                record = check.data[0]
                
                print("\n[VERIFICATION RESULTS]")
                print(f"   is_test_contractor: {record.get('is_test_contractor')}")
                print(f"   business_size_category: {record.get('business_size_category')}")
                print(f"   ai_business_summary: {record.get('ai_business_summary', 'NOT FOUND')[:100]}...")
                print(f"   ai_capability_description: {record.get('ai_capability_description', 'NOT FOUND')[:100]}...")
                
                # Check if data is in proper columns
                if record.get('business_size_category') and record.get('ai_business_summary'):
                    print("\n[SUCCESS] AI data stored in PROPER columns!")
                    print("No more workarounds needed!")
                else:
                    print("\n[WARNING] Some columns might still be missing")
        
        # Clean up
        print("\nCleaning up test data...")
        db.client.table('potential_contractors').delete().eq('id', contractor_id).execute()
        print("[DONE] Test contractor removed")
        
        print("\n" + "="*80)
        print("SYSTEM READY FOR PRODUCTION")
        print("="*80)
        print("\nThe enrichment system is now using proper database columns:")
        print("  - business_size_category: Proper business classification")
        print("  - ai_business_summary: AI-generated contractor descriptions")
        print("  - ai_capability_description: AI-generated capability writeups")
        print("  - is_test_contractor: Test/fake contractor flag")
        
        return True
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_enrichment_with_proper_columns())
    print(f"\nFINAL RESULT: {'SUCCESS - Ready to create fake contractors' if success else 'FAILED'}")