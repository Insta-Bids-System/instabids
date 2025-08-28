"""
Test real Google Places API implementation
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_real_google_api():
    try:
        # Test the actual Google Places API implementation
        from agents.coia.tools.google_api.places import GooglePlacesTool
        
        print('[TEST] Initializing Google Places API tool...')
        google_tool = GooglePlacesTool()
        
        print('[TEST] Testing with JM Holiday Lighting...')
        result = await google_tool.search_google_business('JM Holiday Lighting', 'Fort Lauderdale')
        
        if result:
            print(f'[SUCCESS] Found business data:')
            print(f'  Company: {result.get("company_name")}')
            print(f'  Address: {result.get("address")}')
            print(f'  Phone: {result.get("phone")}')
            print(f'  Website: {result.get("website")}')
            print(f'  Rating: {result.get("google_rating")}')
            print(f'  Reviews: {result.get("google_review_count")}')
            print(f'  Data Source: {result.get("data_source")}')
            return True
        else:
            print('[FAIL] No data returned from Google API')
            return False
            
    except Exception as e:
        print(f'[ERROR] Google API test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_real_google_api())
    print(f'\nGoogle API Test: {"PASSED" if result else "FAILED"}')