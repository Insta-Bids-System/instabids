import asyncio
import os
from dotenv import load_dotenv

load_dotenv('../.env')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')

from agents.coia.tools import coia_tools

async def test_contact_extraction():
    print('=== TESTING CONTACT EXTRACTION FIX ===')
    
    # Test web research first
    web_result = await coia_tools.web_search_company('TurfGrass Artificial Solutions', 'South Florida')
    
    if web_result and web_result.get('extracted_info'):
        extracted = web_result['extracted_info']
        print('EXTRACTED FROM WEB RESEARCH:')
        print(f'  phone: {extracted.get("phone", "NOT FOUND")}')
        print(f'  email: {extracted.get("email", "NOT FOUND")}')
        print(f'  services: {len(extracted.get("services", []))} found')
        print()
        
        # Now test profile building
        print('TESTING PROFILE BUILDING:')
        profile = await coia_tools.build_contractor_profile(
            'TurfGrass Artificial Solutions',
            {'success': True, 'website': 'https://aglgrass.com/'}, 
            web_result,
            {'licenses': []}
        )
        
        print('PROFILE RESULT:')
        print(f'  phone in profile: {profile.get("phone", "NOT FOUND")}')
        print(f'  email in profile: {profile.get("email", "NOT FOUND")}')
        print(f'  database_saved: {profile.get("database_saved", False)}')
        if profile.get("contractor_lead_id"):
            print(f'  contractor_lead_id: {profile["contractor_lead_id"]}')

asyncio.run(test_contact_extraction())