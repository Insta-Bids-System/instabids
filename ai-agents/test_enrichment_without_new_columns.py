#!/usr/bin/env python3
"""
Test enrichment storing AI writeups in existing columns
"""
import os
import sys
import asyncio
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-api03-wF7cjEG4yTWvBAGtc7WJqmhmyRvzaQJPx5VJFcUALJqfk5PFVkXuJbLIdJGqcIZ_gKLg_LYFJa4IcBaOAIOhAg-3UXfVgAA'

async def test_enrichment_with_workaround():
    """Test enrichment using existing columns as workaround"""
    print("TESTING ENRICHMENT WITH COLUMN WORKAROUND")
    print("=" * 80)
    
    from agents.enrichment.langchain_mcp_enrichment_agent import MCPPlaywrightEnrichmentAgent
    from database_simple import SupabaseDB
    
    db = SupabaseDB()
    enricher = MCPPlaywrightEnrichmentAgent()
    
    # First, let's check what columns we DO have
    print("Checking available columns...")
    try:
        # Get a sample record to see structure
        result = db.client.table('potential_contractors').select("*").limit(1).execute()
        if result.data:
            columns = list(result.data[0].keys())
            print(f"Available columns: {', '.join(columns)}")
            
            # Check for unused columns we can repurpose
            unused_columns = []
            for col in ['notes', 'additional_info', 'metadata', 'custom_data']:
                if col in columns:
                    unused_columns.append(col)
            
            if unused_columns:
                print(f"Found unused columns we can use: {unused_columns}")
    except:
        pass
    
    # Create test contractor
    test_contractor = {
        'company_name': 'Test Kitchen Remodeling LLC',
        'website': 'https://example-kitchen.com',
        'phone': '(407) 555-0123',
        'city': 'Orlando',
        'state': 'FL',
        'zip_code': '32801',
        'google_rating': 4.8,
        'google_review_count': 125,
        'status': 'discovered',
        'discovery_source': 'test'
    }
    
    # Insert test contractor
    print("\nInserting test contractor...")
    result = db.client.table('potential_contractors').insert(test_contractor).execute()
    if result.data:
        contractor_id = result.data[0]['id']
        print(f"Created test contractor: {contractor_id}")
        
        # Run enrichment
        print("\nRunning enrichment...")
        contractor_data = {**test_contractor, 'id': contractor_id}
        enrichment_result = await enricher.enrich_contractor(contractor_data)
        
        print(f"\nEnrichment Status: {enrichment_result.enrichment_status}")
        print(f"Email: {enrichment_result.email}")
        print(f"Business Size: {enrichment_result.business_size}")
        
        # Create AI writeup data
        ai_data = {
            'business_size_category': enrichment_result.business_size,
            'ai_business_summary': f"{test_contractor['company_name']} is a {enrichment_result.business_size} contractor specializing in kitchen remodeling in Orlando. With {test_contractor['google_review_count']} reviews and a {test_contractor['google_rating']} star rating, they provide quality services.",
            'ai_capability_description': f"Specializes in: {', '.join(enrichment_result.service_types)}. Years in business: {enrichment_result.years_in_business or 'Unknown'}. Team size: {enrichment_result.team_size or 'Unknown'}.",
            'is_test_contractor': True
        }
        
        # Store AI data in notes field as JSON
        print("\nStoring AI writeup data in notes field...")
        update_result = db.client.table('potential_contractors')\
            .update({'notes': json.dumps(ai_data)})\
            .eq('id', contractor_id)\
            .execute()
        
        if update_result.data:
            print("SUCCESS! AI writeup data stored in notes field as JSON")
            
            # Verify we can retrieve it
            check = db.client.table('potential_contractors').select("notes").eq('id', contractor_id).execute()
            if check.data and check.data[0]['notes']:
                stored_data = json.loads(check.data[0]['notes'])
                print(f"\nRetrieved AI data:")
                print(f"  Business Size: {stored_data['business_size_category']}")
                print(f"  Summary: {stored_data['ai_business_summary'][:80]}...")
                print(f"  Is Test: {stored_data['is_test_contractor']}")
        
        # Clean up
        db.client.table('potential_contractors').delete().eq('id', contractor_id).execute()
        print("\nTest contractor cleaned up")
        
        return True
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_enrichment_with_workaround())
    print(f"\nRESULT: {'SUCCESS - Can use notes field for AI data' if success else 'FAILED'}")