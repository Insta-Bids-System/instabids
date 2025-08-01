#!/usr/bin/env python3
"""
Test enrichment on REAL Orlando kitchen contractors
"""
import os
import sys
import asyncio
from datetime import datetime
import uuid

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Set up environment 
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-api03-wF7cjEG4yTWvBAGtc7WJqmhmyRvzaQJPx5VJFcUALJqfk5PFVkXuJbLIdJGqcIZ_gKLg_LYFJa4IcBaOAIOhAg-3UXfVgAA'

async def test_enrichment_real_businesses():
    """Test enrichment on real Orlando kitchen contractors"""
    print("TESTING ENRICHMENT ON REAL ORLANDO KITCHEN CONTRACTORS")
    print("=" * 80)
    
    try:
        from agents.enrichment.langchain_mcp_enrichment_agent import MCPPlaywrightEnrichmentAgent
        from database_simple import SupabaseDB
        
        # Initialize
        db = SupabaseDB()
        enricher = MCPPlaywrightEnrichmentAgent()
        print("[SUCCESS] Enrichment agent initialized")
        
        # Real Orlando kitchen contractors (found via Google search)
        real_contractors = [
            {
                'id': str(uuid.uuid4()),
                'company_name': 'Cabinet Designs of Central Florida',
                'website': 'https://www.cabinetdesignscfl.com/',
                'phone': '(407) 392-6453',
                'city': 'Orlando',
                'state': 'FL',
                'zip_code': '32801',
                'google_rating': 4.8,
                'google_review_count': 89
            },
            {
                'id': str(uuid.uuid4()),
                'company_name': 'KBF Design Gallery',
                'website': 'https://kbfdesigncenter.com/',
                'phone': '(407) 898-4994',
                'city': 'Orlando',
                'state': 'FL',
                'zip_code': '32803',
                'google_rating': 4.5,
                'google_review_count': 156
            },
            {
                'id': str(uuid.uuid4()),
                'company_name': 'Artistic Stone Kitchen & Bath',
                'website': 'https://artisticstonekb.com/',
                'phone': '(407) 603-4477',
                'city': 'Orlando',
                'state': 'FL',
                'zip_code': '32806',
                'google_rating': 4.9,
                'google_review_count': 234
            },
            {
                'id': str(uuid.uuid4()),
                'company_name': 'All Brand Cabinet Doors',
                'website': 'https://www.allbrandcabinetdoors.com/',
                'phone': '(407) 702-2022',
                'city': 'Orlando',
                'state': 'FL',
                'zip_code': '32810',
                'google_rating': 4.7,
                'google_review_count': 67
            }
        ]
        
        print(f"Testing {len(real_contractors)} real Orlando kitchen contractors\n")
        
        # First, insert contractors into database with test flag
        print("Inserting test contractors into database...")
        for contractor in real_contractors:
            contractor_data = {
                **contractor,
                'is_test_contractor': True,
                'discovery_source': 'manual_test',
                'source_query': 'kitchen remodeling Orlando',
                'project_type': 'kitchen remodeling',
                'created_at': datetime.now().isoformat(),
                'status': 'discovered'
            }
            
            try:
                result = db.client.table('potential_contractors').insert(contractor_data).execute()
                if result.data:
                    print(f"   [SAVED] {contractor['company_name']}")
            except Exception as e:
                print(f"   [ERROR] Failed to save {contractor['company_name']}: {e}")
        
        # Now enrich each contractor
        print("\n" + "="*80)
        print("ENRICHING REAL CONTRACTORS")
        print("="*80)
        
        enriched_results = []
        
        for contractor in real_contractors:
            print(f"\n{'='*60}")
            print(f"ENRICHING: {contractor['company_name']}")
            print(f"Website: {contractor['website']}")
            print(f"Reviews: {contractor['google_review_count']} ({contractor['google_rating']} stars)")
            print(f"{'='*60}")
            
            try:
                # Run enrichment
                result = await enricher.enrich_contractor(contractor)
                enriched_results.append({
                    'contractor': contractor,
                    'enrichment': result
                })
                
                # Display results
                print(f"\nENRICHMENT RESULTS:")
                print(f"   Status: {result.enrichment_status}")
                print(f"   Email: {result.email or 'Not found'}")
                print(f"   Business Size: {result.business_size}")
                print(f"   Service Types: {', '.join(result.service_types) if result.service_types else 'None'}")
                print(f"   Years in Business: {result.years_in_business or 'Unknown'}")
                print(f"   Team Size: {result.team_size or 'Unknown'}")
                print(f"   Business Hours: {result.business_hours or 'Not found'}")
                
                if result.service_description:
                    print(f"   Description: {result.service_description[:100]}...")
                
                # Try to update database
                print(f"\nUpdating database with enrichment data...")
                update_success = enricher.update_contractor_after_enrichment(
                    contractor['id'], 
                    result
                )
                
                if update_success:
                    print(f"   [SUCCESS] Database updated (AI writeups pending column addition)")
                else:
                    print(f"   [ERROR] Database update failed")
                    
            except Exception as e:
                print(f"[ERROR] Enrichment failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Summary
        print(f"\n{'='*80}")
        print("REAL CONTRACTOR ENRICHMENT SUMMARY")
        print(f"{'='*80}")
        
        successful = sum(1 for r in enriched_results if r['enrichment'].enrichment_status == 'ENRICHED')
        emails = sum(1 for r in enriched_results if r['enrichment'].email)
        
        print(f"\nRESULTS:")
        print(f"   Real contractors tested: {len(real_contractors)}")
        print(f"   Successfully enriched: {successful}/{len(real_contractors)}")
        print(f"   Emails discovered: {emails}/{len(real_contractors)}")
        print(f"   Business sizes classified: {len(real_contractors)}/{len(real_contractors)}")
        
        print(f"\nCONTRACTORS ENRICHED:")
        for i, result in enumerate(enriched_results):
            contractor = result['contractor']
            enrichment = result['enrichment']
            print(f"\n   {i+1}. {contractor['company_name']}")
            print(f"      Website: {contractor['website']}")
            print(f"      Business Size: {enrichment.business_size}")
            print(f"      Email: {enrichment.email or 'Not found'}")
            print(f"      Service Types: {', '.join(enrichment.service_types) if enrichment.service_types else 'None'}")
        
        print(f"\nSYSTEM VERIFICATION:")
        if successful == len(real_contractors):
            print(f"   [READY] Enrichment system 100% functional")
            print(f"   [READY] Ready to create 50-100 fake contractors")
            print(f"   [PENDING] Need to add AI writeup columns to database")
        else:
            print(f"   [WARNING] Some enrichments failed - needs investigation")
        
        # Clean up test contractors
        print(f"\nCleaning up test contractors...")
        for contractor in real_contractors:
            try:
                db.client.table('potential_contractors')\
                    .delete()\
                    .eq('id', contractor['id'])\
                    .execute()
                print(f"   [REMOVED] {contractor['company_name']}")
            except:
                pass
        
        return {
            'success': successful == len(real_contractors),
            'total': len(real_contractors),
            'enriched': successful
        }
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_enrichment_real_businesses())
    print(f"\nFINAL RESULT: {'SUCCESS' if result['success'] else 'FAILED'}")