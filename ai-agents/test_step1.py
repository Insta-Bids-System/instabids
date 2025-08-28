import asyncio
import os
from dotenv import load_dotenv

load_dotenv('../.env')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')

from agents.coia.tools import coia_tools

async def test_step1():
    print('=== STEP 1: Google Business Search ===')
    result = await coia_tools.search_google_business('TurfGrass Artificial Solutions', 'South Florida')
    print('RESULT:')
    for key, value in result.items():
        if key == 'search_results':
            print(f'{key}: {len(value)} results found')
            for i, res in enumerate(value):
                print(f'  Result {i+1}: {res.get("title", "No title")}')
                print(f'    URL: {res.get("url", "No URL")}')
                print(f'    Content: {res.get("content", "")}')
        else:
            print(f'{key}: {value}')

asyncio.run(test_step1())