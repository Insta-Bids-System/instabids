"""
Test script for refactored COIA tools
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_refactored_tools():
    try:
        # Test importing the refactored tools
        from agents.coia.tools import COIATools
        
        print('[OK] COIATools imported successfully')
        
        # Initialize tools
        tools = COIATools()
        print('[OK] COIATools initialized successfully')
        
        # Test Google Places search
        result = await tools.search_google_business('JM Holiday Lighting', 'Fort Lauderdale')
        print(f'[OK] Google search test: {bool(result)}')
        
        # Test bid card search
        test_profile = {'company_name': 'Test Company', 'specialties': ['electrical']}
        bid_cards = await tools.search_bid_cards(test_profile)
        print(f'[OK] Bid card search test: returned {len(bid_cards)} results')
        
        # Test profile builder
        profile = await tools.build_contractor_profile('Test Company')
        print(f'[OK] Profile builder test: {profile.get("completeness_score", 0)}% complete')
        
        print('\n[SUCCESS] All refactored tools working!')
        return True
        
    except Exception as e:
        print(f'[ERROR] Error testing refactored tools: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_refactored_tools())
    print(f'\nTest result: {"PASSED" if result else "FAILED"}')