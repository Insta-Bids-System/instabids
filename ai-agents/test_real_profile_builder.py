"""
Test real profile builder with actual Google data
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_real_profile_builder():
    try:
        # Test with real Google data
        from agents.coia.tools.google_api.places import GooglePlacesTool
        from agents.coia.tools.ai_extraction.profile_builder import ProfileBuilderTool
        
        print('[TEST] Getting real Google data...')
        google_tool = GooglePlacesTool()
        google_data = await google_tool.search_google_business('JM Holiday Lighting', 'Fort Lauderdale')
        
        print('[TEST] Building profile with real data...')
        profile_tool = ProfileBuilderTool()
        profile = await profile_tool.build_contractor_profile(
            'JM Holiday Lighting',
            google_data=google_data
        )
        
        print('[SUCCESS] Profile built:')
        print(f'  Company: {profile.get("business_name")}')
        print(f'  Phone: {profile.get("phone")}')
        print(f'  Address: {profile.get("address")}')
        print(f'  Website: {profile.get("website")}')
        print(f'  City: {profile.get("city")}')
        print(f'  State: {profile.get("state")}')
        print(f'  Completeness: {profile.get("completeness_score")}%')
        print(f'  Lead Score: {profile.get("lead_score")}')
        print(f'  Data Sources: {profile.get("data_sources")}')
        print(f'  Insights: {profile.get("profile_insights")}')
        
        # Check if it was saved to database
        if profile.get("database_saved"):
            print(f'  Database: SAVED (ID: {profile.get("contractor_lead_id")})')
        else:
            print('  Database: NOT SAVED (WRITE_LEADS_ON_RESEARCH=false)')
        
        return True
        
    except Exception as e:
        print(f'[ERROR] Profile builder test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_real_profile_builder())
    print(f'\nProfile Builder Test: {"PASSED" if result else "FAILED"}')