import asyncio
import os
from dotenv import load_dotenv

load_dotenv('../.env')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')

from agents.coia.tools import coia_tools

async def test_step2():
    print('=== STEP 2: Web Research ===')
    result = await coia_tools.web_search_company('TurfGrass Artificial Solutions', 'South Florida')
    print('RESULT:')
    if result:
        print(f'data_sources: {result.get("data_sources", [])}')
        
        extracted = result.get('extracted_info', {})
        if extracted:
            print('EXTRACTED INFO:')
            for key, value in extracted.items():
                if isinstance(value, list) and len(value) > 3:
                    print(f'  {key}: {len(value)} items - {value[:2]}...')
                else:
                    print(f'  {key}: {value}')
        else:
            print('No extracted_info found')
    else:
        print('No result returned')

asyncio.run(test_step2())