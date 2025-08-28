import asyncio
import os
from dotenv import load_dotenv

load_dotenv('../.env')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')

from agents.coia.tools import coia_tools

async def test_step2_raw():
    print('=== CHECKING RAW TAVILY DATA ===')
    result = await coia_tools.web_search_company('TurfGrass Artificial Solutions', 'South Florida')
    
    # Look for raw content that might contain phone/email
    if result and result.get('raw_tavily_data'):
        raw = result['raw_tavily_data']
        
        # Check search results for phone numbers
        results = raw.get('results', [])
        for i, res in enumerate(results):
            print(f'=== RESULT {i+1} ===')
            print(f'URL: {res.get("url", "")}')
            print(f'Title: {res.get("title", "")}')
            content = res.get('content', '')
            
            # Look for phone patterns
            import re
            phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', content)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
            
            if phones:
                print(f'PHONES FOUND: {phones}')
            if emails:
                print(f'EMAILS FOUND: {emails}')
                
            print(f'Content preview: {content[:200]}...')
            print()
    else:
        print('No raw_tavily_data found')

asyncio.run(test_step2_raw())