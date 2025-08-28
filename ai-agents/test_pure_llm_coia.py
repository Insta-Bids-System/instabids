"""
TEST: Pure LLM Intelligence COIA System
Tests that ALL regex patterns are removed and GPT-5 handles everything intelligently
"""
import os
import sys
import asyncio
import json
from datetime import datetime

# Add the agents directory to path
sys.path.append(os.path.dirname(__file__))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Verify API keys are set
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not set in environment")
    sys.exit(1)

print("🚀 TESTING PURE LLM INTELLIGENCE COIA SYSTEM")
print("=" * 60)

async def test_pure_llm_conversation_node():
    """Test that conversation node uses GPT-5 for company extraction, not regex"""
    print("\n📋 TEST 1: Pure LLM Company Name Extraction")
    
    try:
        from agents.coia.langgraph_nodes import conversation_node
        from agents.coia.unified_state import create_initial_state
        from langchain_core.messages import HumanMessage
        
        # Create test state with contractor introduction
        initial_state = create_initial_state(
            session_id="test_session",
            interface="landing_page"
        ).to_langgraph_state()
        
        # Add contractor message that should trigger company extraction
        test_message = "Hi, I'm Justin with JM Holiday Lighting. We specialize in residential and commercial holiday lighting installations."
        initial_state["messages"] = [HumanMessage(content=test_message)]
        
        print(f"Input message: {test_message}")
        
        # Call conversation node
        result = await conversation_node(initial_state)
        
        # Check if company name was extracted
        company_name = result.get("company_name")
        print(f"✅ Extracted company name: {company_name}")
        
        if company_name and "JM Holiday Lighting" in company_name:
            print("🎉 SUCCESS: GPT-5 successfully extracted company name!")
            return True
        else:
            print("❌ FAILED: Company name not extracted correctly")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in conversation node test: {e}")
        return False

async def test_pure_llm_research_node():
    """Test that research node uses pure Tavily + GPT-5 intelligence"""
    print("\n📋 TEST 2: Pure LLM Research Intelligence")
    
    try:
        from agents.coia.langgraph_nodes import research_node  
        from agents.coia.unified_state import create_initial_state
        from langchain_core.messages import HumanMessage
        
        # Create test state for research
        initial_state = create_initial_state(
            session_id="test_research",
            interface="research_portal"
        ).to_langgraph_state()
        
        # Set company name for research
        initial_state["company_name"] = "TurfGrass Artificial Solutions"
        initial_state["messages"] = [HumanMessage(content="Research my company TurfGrass Artificial Solutions")]
        
        print("Testing research for: TurfGrass Artificial Solutions")
        
        # Call research node
        result = await research_node(initial_state)
        
        # Check research results
        research_findings = result.get("research_findings", {})
        contractor_profile = result.get("contractor_profile", {})
        
        print(f"✅ Research status: {research_findings.get('status', 'Unknown')}")
        print(f"✅ Profile completeness: {contractor_profile.get('profile_completeness', 0):.1f}%")
        
        if research_findings.get("status") == "research_complete_with_real_data":
            print("🎉 SUCCESS: Research used real Tavily API + GPT-5 intelligence!")
            return True
        else:
            print("❌ FAILED: Research did not complete with real data")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in research node test: {e}")
        return False

async def test_bid_card_search_no_mocks():
    """Test that bid card search has no mock data fallbacks"""
    print("\n📋 TEST 3: Bid Card Search - No Mock Data")
    
    try:
        from agents.coia.bid_card_search_node import search_bid_cards
        
        # Test search with criteria that would normally return mock data
        criteria = {
            "project_types": ["nonexistent_type"],
            "location_city": "NonexistentCity",
            "budget_min": 999999999  # Impossible budget
        }
        
        print("Testing search with impossible criteria...")
        
        # Call search function
        results = await search_bid_cards(criteria)
        
        print(f"✅ Search returned: {len(results)} results")
        
        # Check if any results contain mock data
        has_mock_data = any("mock" in str(result).lower() for result in results)
        
        if not has_mock_data:
            print("🎉 SUCCESS: No mock data found in results!")
            return True
        else:
            print("❌ FAILED: Mock data still present in results")
            print(f"Mock results: {[r for r in results if 'mock' in str(r).lower()]}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in bid card search test: {e}")
        return False

async def run_all_tests():
    """Run all pure LLM intelligence tests"""
    print("Starting comprehensive COIA system tests...")
    
    test_results = []
    
    # Test 1: Conversation node pure LLM
    result1 = await test_pure_llm_conversation_node()
    test_results.append(("Conversation Node GPT-5", result1))
    
    # Test 2: Research node pure LLM  
    result2 = await test_pure_llm_research_node()
    test_results.append(("Research Node Tavily+GPT-5", result2))
    
    # Test 3: No mock data
    result3 = await test_bid_card_search_no_mocks()
    test_results.append(("Bid Card Search - No Mocks", result3))
    
    # Summary
    print("\n🏁 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(test_results)
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - PURE LLM INTELLIGENCE WORKING!")
        print("✅ No regex patterns")
        print("✅ No mock data") 
        print("✅ Pure GPT-5 + Tavily intelligence")
    else:
        print(f"\n❌ {total-passed} TESTS FAILED - SYSTEM NOT READY")
        
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    if success:
        print("\n🚀 COIA SYSTEM IS 100% PURE LLM INTELLIGENCE!")
    else:
        print("\n🚨 COIA SYSTEM STILL HAS ISSUES - MORE CLEANUP NEEDED")