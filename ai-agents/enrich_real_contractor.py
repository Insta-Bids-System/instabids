#!/usr/bin/env python3
"""
Enrich a real contractor from the database
"""
import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-api03-wF7cjEG4yTWvBAGtc7WJqmhmyRvzaQJPx5VJFcUALJqfk5PFVkXuJbLIdJGqcIZ_gKLg_LYFJa4IcBaOAIOhAg-3UXfVgAA'

async def enrich_real_contractor():
    from agents.enrichment.langchain_mcp_enrichment_agent import MCPPlaywrightEnrichmentAgent
    from database_simple import SupabaseDB
    
    db = SupabaseDB()
    enricher = MCPPlaywrightEnrichmentAgent()
    
    print("ENRICHING A REAL CONTRACTOR FROM DATABASE")
    print("=" * 80)
    
    # Find a contractor that hasn't been enriched yet
    result = db.client.table('potential_contractors')\
        .select("*")\
        .is_('email', 'null')\
        .not_.eq('company_name', '')\
        .not_.ilike('website', '%homeadvisor%')\
        .not_.ilike('website', '%angies_list%')\
        .not_.ilike('website', '%bbb.%')\
        .not_.ilike('website', '%yelp.%')\
        .limit(1)\
        .execute()
    
    if not result.data:
        print("No unenriched contractors found")
        return
    
    contractor = result.data[0]
    print(f"\nSelected contractor: {contractor['company_name']}")
    print(f"ID: {contractor['id']}")
    print(f"Website: {contractor.get('website', 'None')}")
    print(f"Current email: {contractor.get('email', 'None')}")
    print(f"Current AI summary: {contractor.get('ai_business_summary', 'None')}")
    
    # Run enrichment
    print("\nRunning enrichment...")
    enrichment_result = await enricher.enrich_contractor(contractor)
    
    print(f"\nEnrichment Status: {enrichment_result.enrichment_status}")
    print(f"Email found: {enrichment_result.email}")
    print(f"Business size: {enrichment_result.business_size}")
    
    # Update database
    print("\nUpdating database...")
    update_success = enricher.update_contractor_after_enrichment(contractor['id'], enrichment_result)
    
    if update_success:
        print("[SUCCESS] Database updated")
        
        # Verify the update
        check = db.client.table('potential_contractors')\
            .select("id,company_name,email,business_size_category,ai_business_summary,ai_capability_description")\
            .eq('id', contractor['id'])\
            .execute()
        
        if check.data:
            updated = check.data[0]
            print("\n[VERIFICATION] After enrichment:")
            print(f"   Company: {updated['company_name']}")
            print(f"   Email: {updated.get('email', 'Not set')}")
            print(f"   Business Size Category: {updated.get('business_size_category', 'Not set')}")
            print(f"   AI Summary: {updated.get('ai_business_summary', 'Not set')[:100] if updated.get('ai_business_summary') else 'Not set'}...")
            print(f"   AI Capabilities: {updated.get('ai_capability_description', 'Not set')[:100] if updated.get('ai_capability_description') else 'Not set'}...")
            
            if updated.get('ai_business_summary'):
                print("\n[SUCCESS] Contractor enriched with AI data in PROPER columns!")
                return updated
    
    return None

if __name__ == "__main__":
    result = asyncio.run(enrich_real_contractor())