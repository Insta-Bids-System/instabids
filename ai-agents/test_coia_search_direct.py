#!/usr/bin/env python3
"""
Direct test of COIA bid card search functionality
Tests the search system without the complex LangGraph workflow
"""

import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_direct_bid_search():
    """Test the bid card search directly"""
    
    try:
        # Import the search function
        from agents.coia.bid_card_search_node_fixed import _call_intelligent_job_search
        
        # Test search parameters (Austin, TX)
        test_params = {
            "contractor_zip": "78701",  # Austin ZIP
            "radius_miles": 30,
            "project_keywords": "kitchen remodel",
            "limit": 10
        }
        
        logger.info("🔍 Testing direct bid card search...")
        logger.info(f"Search params: {test_params}")
        
        # Call the search function directly
        bid_cards = await _call_intelligent_job_search(test_params)
        
        logger.info(f"✅ Search completed! Found {len(bid_cards)} bid cards")
        
        # Display results
        for i, card in enumerate(bid_cards[:5], 1):
            print(f"\n{i}. {card.get('title', 'Untitled')} ({card.get('project_type')})")
            print(f"   Location: {card.get('location', {}).get('city')}, {card.get('location', {}).get('state')}")
            print(f"   ZIP: {card.get('location', {}).get('zip_code')}")
            print(f"   Distance: {card.get('distance_miles')} miles")
            print(f"   Status: {card.get('status')}")
            print(f"   Bids: {card.get('bid_count')}/{card.get('contractor_count_needed')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Direct search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_zip_radius_tool():
    """Test the ZIP radius expansion tool directly"""
    
    try:
        from utils.radius_search_fixed import get_zip_codes_in_radius
        
        test_zip = "78701"  # Austin
        radius = 30
        
        logger.info(f"🌍 Testing ZIP radius expansion: {test_zip} within {radius} miles")
        
        zip_codes = get_zip_codes_in_radius(test_zip, radius)
        
        logger.info(f"✅ ZIP expansion found {len(zip_codes)} zip codes")
        logger.info(f"Sample ZIP codes: {zip_codes[:10]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ZIP radius test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all direct tests"""
    print("="*60)
    print("COIA BID CARD SEARCH - DIRECT TESTING")
    print("="*60)
    
    # Test 1: ZIP radius expansion
    print("\n1. Testing ZIP radius expansion tool...")
    zip_test = await test_zip_radius_tool()
    
    # Test 2: Direct bid card search
    print("\n2. Testing direct bid card search...")
    search_test = await test_direct_bid_search()
    
    # Results
    print("\n" + "="*60)
    print("TEST RESULTS:")
    print(f"ZIP Radius Tool: {'✅ PASS' if zip_test else '❌ FAIL'}")
    print(f"Bid Card Search: {'✅ PASS' if search_test else '❌ FAIL'}")
    
    if zip_test and search_test:
        print("\n🎉 ALL TESTS PASSED - Search system is working!")
        print("The issue is likely in COIA system initialization, not the search logic.")
    else:
        print("\n⚠️ Some tests failed - need to debug search system.")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())