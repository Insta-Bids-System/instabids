#!/usr/bin/env python3
"""
Test just the Tavily Extract API to see full content quality
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_tavily_extract():
    """Test Tavily Extract API directly"""
    print("Testing Tavily Extract API...")
    
    try:
        from tavily import TavilyClient
        api_key = "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"
        client = TavilyClient(api_key=api_key)
        
        # Test URL
        test_url = "https://jmholidaylighting.com/"
        
        print(f"Extracting from: {test_url}")
        
        # Extract with advanced depth
        response = client.extract(
            test_url,
            extract_depth="advanced",
            format="markdown"
        )
        
        if response and 'results' in response:
            for result in response['results']:
                content = result.get('raw_content', '')
                print(f"\nExtracted {len(content)} characters")
                print("\nFirst 1000 characters:")
                print(content[:1000])
                print("\n...")
                print("\nLast 500 characters:")
                print(content[-500:])
                
                # Look for specific business info
                content_lower = content.lower()
                
                print("\n=== BUSINESS INFO FOUND ===")
                if 'since' in content_lower or 'founded' in content_lower:
                    print("✓ Found founding/since information")
                if 'service' in content_lower:
                    print("✓ Found services information") 
                if 'about' in content_lower:
                    print("✓ Found about information")
                if 'team' in content_lower or 'staff' in content_lower:
                    print("✓ Found team/staff information")
                if 'license' in content_lower or 'insur' in content_lower:
                    print("✓ Found license/insurance information")
                    
        else:
            print("No results returned from Extract API")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tavily_extract())