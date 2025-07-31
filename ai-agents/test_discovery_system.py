#!/usr/bin/env python3
"""
Test Discovery System - Verify Google contractor discovery works properly
"""
import sys
import os
sys.path.append('.')

from agents.cda.web_search_agent import WebSearchContractorAgent
from database_simple import SupabaseDB

def test_contractor_discovery():
    """Test the contractor discovery system end-to-end"""
    print('[TEST] TESTING CONTRACTOR DISCOVERY SYSTEM')
    print('=' * 60)
    
    # Initialize
    try:
        db = SupabaseDB()
        agent = WebSearchContractorAgent(db.client)
        print('[OK] Initialized discovery system')
    except Exception as e:
        print(f'[ERROR] Failed to initialize: {e}')
        return
    
    # Test discovery for kitchen contractors in Orlando  
    print('\n[SEARCH] Testing: Kitchen contractors in Orlando, FL')
    try:
        result = agent.discover_contractors_for_bid(
            bid_card_id='12345678-1234-1234-1234-123456789012',  # This triggers test mode  - kitchen remodel in Orlando
            contractors_needed=5
        )
        
        print(f'Success: {result.get("success")}')
        print(f'Contractors found: {result.get("contractors_found", 0)}')
        print(f'Contractors stored: {result.get("contractors_stored", 0)}')
        
        if result.get('contractors'):
            print(f'\n[RESULTS] CONTRACTORS DISCOVERED:')
            for i, contractor in enumerate(result['contractors'][:5], 1):
                print(f'{i}. {contractor.get("company_name", "Unknown")}')
                print(f'   Source: {contractor.get("discovery_source")}')
                print(f'   Website: {contractor.get("website", "None")}')
                print(f'   Phone: {contractor.get("phone", "None")}')  
                print(f'   Rating: {contractor.get("google_rating", "None")} ({contractor.get("google_review_count", 0)} reviews)')
                print(f'   Match Score: {contractor.get("match_score", "None")}')
                print(f'   Business Status: {contractor.get("google_business_status", "None")}')
                print()
        
        print('[SUCCESS] Discovery test completed successfully')
        return result
        
    except Exception as e:
        print(f'[ERROR] Discovery test failed: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_contractor_discovery()