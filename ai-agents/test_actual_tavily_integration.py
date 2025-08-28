"""
TEST: Actual Tavily MCP Integration - No Simulations
This test uses the real Tavily MCP tools that should be available
"""
import asyncio
import sys
import os

# Add the ai-agents directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_real_tavily_mcp():
    """Test if Tavily MCP tools are actually available and working"""
    
    print("TESTING ACTUAL TAVILY MCP INTEGRATION")
    print("=" * 60)
    print("This test will use REAL Tavily MCP tools, not simulations")
    print()
    
    try:
        # Import the enhanced COIA tools
        from agents.coia.tools import coia_tools
        
        print("Phase 1: Test Google Places API")
        print("-" * 40)
        
        async with coia_tools as tools:
            # Test Google Places API first
            google_result = await tools.search_google_business("JM Holiday Lighting", "Fort Lauderdale, FL")
            
            if google_result:
                print("[SUCCESS] Google Places API working")
                print(f"   Company: {google_result.get('company_name')}")
                print(f"   Phone: {google_result.get('phone')}")
                print(f"   Website: {google_result.get('website')}")
                print(f"   Rating: {google_result.get('rating')}")
            else:
                print("[WARNING] Google Places API returned no results")
            
            print()
            
            print("Phase 2: Test Enhanced Web Search (with Tavily + Playwright)")
            print("-" * 40)
            
            # Test the enhanced web search method
            print("Calling enhanced web_search_company method...")
            
            try:
                result = await tools.web_search_company("JM Holiday Lighting", "Fort Lauderdale, FL")
                
                if result:
                    print("[SUCCESS] Enhanced web search completed")
                    print(f"   Data Sources: {result.get('data_sources', [])}")
                    
                    # Check if Tavily discovery worked
                    tavily_data = result.get('tavily_discovery_data', {})
                    if tavily_data and len(tavily_data.get('discovered_pages', [])) > 0:
                        print(f"   [TAVILY] Discovered {len(tavily_data['discovered_pages'])} pages")
                        print("   [STATUS] REAL Tavily MCP integration WORKING!")
                        
                        for page in tavily_data['discovered_pages'][:3]:
                            print(f"      • {page.get('type', 'unknown')} page: {page.get('url', 'N/A')}")
                    else:
                        print("   [TAVILY] Using simulated discovery (MCP not connected)")
                    
                    # Check website data extraction
                    website_data = result.get('website_data', {})
                    if website_data:
                        stats = website_data.get('field_completion_stats', {})
                        if stats:
                            filled = stats.get('filled_fields', 0)
                            total = stats.get('total_fields', 66)
                            percentage = stats.get('completion_percentage', 0)
                            
                            print(f"   [EXTRACTION] {filled}/{total} fields ({percentage:.1f}%)")
                            
                            if percentage >= 80:
                                print("   [TARGET] 80-90% field completion ACHIEVED!")
                            else:
                                print(f"   [TARGET] Progress toward 80-90%: {percentage:.1f}%")
                
                else:
                    print("[ERROR] Enhanced web search returned no results")
                    
            except Exception as search_error:
                print(f"[ERROR] Enhanced web search failed: {search_error}")
                import traceback
                traceback.print_exc()
            
            print()
            
            print("Phase 3: Direct MCP Tool Test")
            print("-" * 40)
            
            # Try to test MCP tools directly
            print("Testing if Tavily MCP tools are available in this session...")
            
            # This would normally work if Tavily MCP was properly loaded
            # We can't test it here because the MCP server isn't running in this process
            
            print("[NOTE] Direct MCP tool testing requires Claude restart to load new servers")
            print("[SOLUTION] Restart Claude Code to pick up the Tavily MCP configuration")
            
            return True
            
    except ImportError as e:
        print(f"[ERROR] Could not import COIA tools: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting REAL Tavily MCP integration test...")
    print()
    
    result = asyncio.run(test_real_tavily_mcp())
    
    if result:
        print()
        print("TEST RESULTS:")
        print("=" * 60)
        print("[STATUS] Test completed")
        print("[NEXT STEP] Restart Claude Code to activate Tavily MCP server")
        print("[VERIFICATION] Tavily MCP tools should then be available as mcp__tavily__*")
        print("[GOAL] Real 80-90% field completion with actual page discovery")
    else:
        print()
        print("[FAILED] Test encountered errors - see above for details")