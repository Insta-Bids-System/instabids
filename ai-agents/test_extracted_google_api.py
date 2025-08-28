"""
Test EXTRACTED Google Places API implementation with REAL API calls
Verifies the actual implementation extracted from tools_legacy.py
"""
import asyncio
import sys
import os

# Add the ai-agents directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_extracted_google_places():
    """Test the EXTRACTED Google Places implementation"""
    print("[TEST] Testing EXTRACTED Google Places API implementation...")
    
    try:
        # Import the extracted implementation
        from agents.coia.tools.google_api.places import GooglePlacesTool
        
        # Initialize the tool
        google_tool = GooglePlacesTool()
        
        # Test with JM Holiday Lighting
        print("[INFO] Testing with JM Holiday Lighting in Fort Lauderdale...")
        result = await google_tool.search_google_business("JM Holiday Lighting", "Fort Lauderdale, FL")
        
        if result and not result.get("error"):
            print("[SUCCESS] Google Places API returned real data!")
            print(f"   Company: {result.get('company_name', 'N/A')}")
            print(f"   Address: {result.get('address', 'N/A')}")
            print(f"   Phone: {result.get('phone', 'N/A')}")
            print(f"   Website: {result.get('website', 'N/A')}")
            print(f"   Rating: {result.get('rating', 'N/A')}")
            print(f"   Reviews: {result.get('review_count', 'N/A')}")
            print(f"   Data Source: {result.get('data_source', 'N/A')}")
            return True
        else:
            print("[ERROR] Google Places API failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"[IMPORT ERROR] Could not import extracted implementation: {e}")
        return False
    except Exception as e:
        print(f"[EXCEPTION] Unexpected error: {e}")
        return False

async def test_extracted_coia_tools():
    """Test the main COIATools class with extracted implementations"""
    print("\n[TEST] Testing EXTRACTED COIATools class...")
    
    try:
        # Import the main COIATools class
        from agents.coia.tools import COIATools
        
        # Initialize the tools
        coia_tools = COIATools()
        
        # Test Google search through COIATools
        print("[INFO] Testing Google search through COIATools...")
        result = await coia_tools.search_google_business("JM Holiday Lighting", "Fort Lauderdale, FL")
        
        if result and not result.get("error"):
            print("[SUCCESS] COIATools Google search working!")
            print(f"   Company: {result.get('company_name', 'N/A')}")
            print(f"   Data Source: {result.get('data_source', 'N/A')}")
            return True
        else:
            print("[ERROR] COIATools Google search failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"[EXCEPTION] COIATools test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("[START] Testing EXTRACTED REAL implementations from tools_legacy.py")
    print("=" * 60)
    
    # Test individual Google Places tool
    google_success = await test_extracted_google_places()
    
    # Test main COIATools class
    coia_success = await test_extracted_coia_tools()
    
    print("\n" + "=" * 60)
    print("[RESULTS] TEST SUMMARY:")
    print(f"   Google Places Tool: {'PASS' if google_success else 'FAIL'}")
    print(f"   COIATools Integration: {'PASS' if coia_success else 'FAIL'}")
    
    if google_success and coia_success:
        print("\n[COMPLETE] ALL TESTS PASSED - Extracted implementations working!")
        print("   [OK] Google Places API returns real business data")
        print("   [OK] COIATools delegation pattern working")
        print("   [OK] Ready for full COIA testing")
    else:
        print("\n[WARNING] SOME TESTS FAILED - Check implementations")

if __name__ == "__main__":
    asyncio.run(main())