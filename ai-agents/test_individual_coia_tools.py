#!/usr/bin/env python3
"""
Test Individual COIA Tools
Quick test to see which tool is hanging in the research_node
"""

import asyncio
import time
import logging
from agents.coia.tools import coia_tools

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_individual_tools():
    """Test each tool individually to identify the hanging one"""
    
    company_name = "TurfGrass Artificial Solutions"
    location = "South Florida"
    
    print(f"Testing COIA tools individually for: {company_name} in {location}")
    print("=" * 80)
    
    try:
        # Test 1: Google Business Search
        print(f"\n1. Testing Google Business Search...")
        start_time = time.time()
        try:
            google_result = await coia_tools.search_google_business(company_name, location)
            duration = time.time() - start_time
            print(f"   SUCCESS: {duration:.2f}s")
            print(f"   Result: {google_result.get('success', False) if google_result else False}")
        except Exception as e:
            duration = time.time() - start_time
            print(f"   ERROR: {duration:.2f}s - {e}")
        
        # Test 2: Web Search
        print(f"\n2. Testing Web Search...")
        start_time = time.time()
        try:
            web_result = await coia_tools.web_search_company(company_name, location)
            duration = time.time() - start_time
            print(f"   SUCCESS: {duration:.2f}s")
            print(f"   Result: {web_result.get('success', False) if web_result else False}")
        except Exception as e:
            duration = time.time() - start_time
            print(f"   ERROR: {duration:.2f}s - {e}")
        
        # Test 3: License Search
        print(f"\n3. Testing License Search...")
        start_time = time.time()
        try:
            license_result = await coia_tools.search_contractor_licenses(company_name, "FL")
            duration = time.time() - start_time
            print(f"   SUCCESS: {duration:.2f}s")
            print(f"   Result: {license_result.get('success', False) if license_result else False}")
        except Exception as e:
            duration = time.time() - start_time
            print(f"   ERROR: {duration:.2f}s - {e}")
        
        # Test 4: Profile Building
        print(f"\n4. Testing Profile Building...")
        start_time = time.time()
        try:
            # Use minimal data for profile building
            google_data = {"success": False, "company_name": company_name}
            web_data = {"success": False}
            license_data = {"success": False}
            
            profile_result = await coia_tools.build_contractor_profile(
                company_name, google_data, web_data, license_data
            )
            duration = time.time() - start_time
            print(f"   SUCCESS: {duration:.2f}s")
            print(f"   Result: {profile_result.get('completeness_score', 0) if profile_result else 0}")
        except Exception as e:
            duration = time.time() - start_time
            print(f"   ERROR: {duration:.2f}s - {e}")
        
        # Test 5: Bid Card Search
        print(f"\n5. Testing Bid Card Search...")
        start_time = time.time()
        try:
            profile = {"business_name": company_name, "specialties": ["landscaping"]}
            bid_result = await coia_tools.search_bid_cards(profile, location)
            duration = time.time() - start_time
            print(f"   SUCCESS: {duration:.2f}s")
            print(f"   Result: {len(bid_result) if isinstance(bid_result, list) else 0} bid cards found")
        except Exception as e:
            duration = time.time() - start_time
            print(f"   ERROR: {duration:.2f}s - {e}")
            
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
    
    print(f"\n" + "=" * 80)
    print(f"Individual tool testing complete")

if __name__ == "__main__":
    asyncio.run(test_individual_tools())