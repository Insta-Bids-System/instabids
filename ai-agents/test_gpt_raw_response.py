#!/usr/bin/env python3
"""
Test to see what GPT-5 actually returns for contractor analysis
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.tools import COIATools

async def test_gpt_raw_response():
    """Test to see the raw GPT response"""
    print("Testing GPT-5 raw response...")
    
    tools = COIATools()
    
    # Test with JM Holiday Lighting
    web_data = await tools.web_search_company("JM Holiday Lighting", "Fort Lauderdale, FL")
    
    if web_data and "tavily_discovery_data" in web_data:
        tavily_data = web_data["tavily_discovery_data"]
        
        # Call the GPT intelligence directly
        extraction_result = await tools._extract_from_discovered_pages(tavily_data, "JM Holiday Lighting")
        
        print("\n=== GPT-5 INTELLIGENT RESPONSE ===")
        
        if "intelligent_analysis" in extraction_result:
            print("Raw GPT Response:")
            print(extraction_result["intelligent_analysis"])
        elif "error" in extraction_result:
            print(f"Error: {extraction_result['error']}")
        else:
            print("Parsed JSON result:")
            import json
            print(json.dumps(extraction_result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_gpt_raw_response())