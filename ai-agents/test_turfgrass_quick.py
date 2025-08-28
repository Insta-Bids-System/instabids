"""
Quick COIA Test - TurfGrass Artificial Solutions
Testing real business research and database save
"""
import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')
os.environ['USE_TAVILY'] = 'true'
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['WRITE_LEADS_ON_RESEARCH'] = 'true'

async def test_turfgrass():
    print("=" * 80)
    print("QUICK COIA TEST - TurfGrass Artificial Solutions")
    print("=" * 80)
    
    from agents.coia.tools import coia_tools
    
    company = "TurfGrass Artificial Solutions"
    location = "South Florida"
    
    # Only run Google Business Search first
    print(f"TESTING Google Business Search for: {company}")
    
    try:
        result = await coia_tools.search_google_business(company, location)
        print("SUCCESS - Google Business Search Results:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_turfgrass())