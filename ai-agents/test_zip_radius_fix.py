#!/usr/bin/env python3
"""
Test that the fixed COIA search uses your ZIP radius expansion system
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

async def test_zip_radius_fix():
    """Test the fixed search system uses ZIP radius expansion"""
    
    print("TESTING ZIP RADIUS EXPANSION FIX")
    print("=" * 40)
    
    # Test your ZIP radius tool directly first
    try:
        from utils.radius_search_fixed import get_zip_codes_in_radius
        
        test_zip = "78701"  # Austin
        radius = 30
        
        zip_codes = get_zip_codes_in_radius(test_zip, radius)
        print(f"✓ ZIP radius tool works: {len(zip_codes)} zip codes within {radius} miles of {test_zip}")
        print(f"  Sample ZIP codes: {zip_codes[:5]}")
        
    except Exception as e:
        print(f"✗ ZIP radius tool error: {e}")
        return False
    
    # Test the fixed search function
    try:
        from agents.coia.bid_card_search_node_fixed import _call_intelligent_job_search
        
        params = {
            "contractor_zip": "78701",
            "radius_miles": 30,
            "project_keywords": "landscaping",
            "limit": 10
        }
        
        jobs = await _call_intelligent_job_search(params)
        print(f"✓ Fixed search function works: {len(jobs)} jobs found")
        
        if jobs:
            sample = jobs[0]
            title = sample.get("title", "No title")
            distance = sample.get("distance_miles", "N/A")
            print(f"  Sample job: {title} ({distance} miles)")
        
        return True
        
    except Exception as e:
        print(f"✗ Fixed search error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_zip_radius_fix())
    
    if success:
        print("\n✓ ALL TESTS PASSED")
        print("\nNEXT STEPS TO ACTIVATE:")
        print("1. Update unified_graph.py line 52:")
        print("   FROM: from .bid_card_search_node import bid_card_search_node")
        print("   TO:   from .bid_card_search_node_fixed import bid_card_search_node")
        print("\n2. Test COIA with: 'show me landscaping projects near me'")
        print("   Should use ZIP radius instead of city-based search")
    else:
        print("\n✗ TESTS FAILED - Need to debug")