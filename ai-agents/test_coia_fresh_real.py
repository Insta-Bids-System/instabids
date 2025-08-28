"""
FRESH COIA TEST - Real Business Research Verification
Tests JM Holiday Lighting with completely clean database
"""
import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables and set them
load_dotenv('../.env')

# Print to verify keys are loading
print(f"TAVILY_API_KEY: {os.getenv('TAVILY_API_KEY', 'NOT_FOUND')[:10]}...")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT_FOUND')[:10]}...")

os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')
os.environ['USE_TAVILY'] = 'true'
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY', '')
os.environ['WRITE_LEADS_ON_RESEARCH'] = 'true'

async def test_fresh_turfgrass_artificial_solutions():
    print("=" * 80)
    print("FRESH COIA TEST - TurfGrass Artificial Solutions")
    print("Completely clean database - testing real business research")
    print("=" * 80)
    
    from agents.coia.tools import coia_tools
    
    company = "TurfGrass Artificial Solutions"
    location = "South Florida"
    
    print(f"TESTING: {company} in {location}")
    print("This should be a REAL business we can verify")
    print()
    
    # STEP 1: Google Business Search - what does it actually find?
    print("STEP 1: Google Business Search (Real API)")
    print("-" * 50)
    try:
        google_result = await coia_tools.search_google_business(company, location)
        print("Google API Result:")
        if google_result:
            for key, value in google_result.items():
                print(f"  {key}: {value}")
        else:
            print("  No result returned")
        print()
    except Exception as e:
        print(f"ERROR: {e}")
        google_result = {}
    
    # STEP 2: Web Research - what does Tavily actually find?
    print("STEP 2: Web Research with Tavily API")
    print("-" * 50)
    try:
        web_result = await coia_tools.web_search_company(company, location)
        print("Tavily API Result:")
        if web_result:
            print(f"  Data Sources: {web_result.get('data_sources', [])}")
            print(f"  Extracted Info Keys: {list(web_result.get('extracted_info', {}).keys())}")
            extracted = web_result.get('extracted_info', {})
            if extracted:
                print("  Extracted Details:")
                for key, value in extracted.items():
                    if isinstance(value, (list, dict)):
                        print(f"    {key}: {json.dumps(value, indent=6)}")
                    else:
                        print(f"    {key}: {value}")
        else:
            print("  No result returned")
        print()
    except Exception as e:
        print(f"ERROR: {e}")
        web_result = {}
    
    # STEP 3: Business Intelligence - what does OpenAI generate?
    print("STEP 3: Business Intelligence (OpenAI API)")
    print("-" * 50)
    try:
        research_result = await coia_tools.research_business(company, location)
        print("OpenAI Business Analysis Result:")
        if research_result:
            for key, value in research_result.items():
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {json.dumps(value, indent=4)}")
                else:
                    print(f"  {key}: {value}")
        else:
            print("  No result returned")
        print()
    except Exception as e:
        print(f"ERROR: {e}")
        research_result = {}
    
    # STEP 4: Profile Building and Database Save
    print("STEP 4: Profile Building and Database Save")
    print("-" * 50)
    try:
        profile_result = await coia_tools.build_contractor_profile(
            company, 
            google_result or {}, 
            web_result or {}, 
            {'licenses': []}
        )
        print("Profile Building Result:")
        if profile_result:
            for key, value in profile_result.items():
                if key == 'raw_data':
                    print(f"  {key}: [Large data object - skipping display]")
                elif isinstance(value, (list, dict)):
                    print(f"  {key}: {json.dumps(value, indent=4)}")
                else:
                    print(f"  {key}: {value}")
        else:
            print("  No result returned")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print()
    print("=" * 80)
    print("VERIFICATION QUESTIONS:")
    print("1. Does the Google result match real JM Holiday Lighting business?")
    print("2. Do the Tavily data sources show real websites?") 
    print("3. Does the OpenAI analysis make sense for a real lighting company?")
    print("4. Was the profile actually saved to the database?")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_fresh_turfgrass_artificial_solutions())