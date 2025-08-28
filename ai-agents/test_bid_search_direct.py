"""
Test bid card search node directly
"""
import asyncio
from agents.coia.bid_card_search_node_fixed import bid_card_search_node
from agents.coia.unified_state import create_initial_state
from langchain_core.messages import HumanMessage

async def test_bid_search_direct():
    """Test the bid card search node directly"""
    
    print("=== TESTING BID CARD SEARCH NODE DIRECTLY ===")
    
    # Create state with contractor info that should trigger search
    initial_state = create_initial_state(
        session_id="test-direct-123",
        interface="landing_page",
        contractor_lead_id="test-contractor-123"
    )
    
    # Set up contractor profile
    initial_state.contractor_profile = {
        "company_name": "ABC Construction",
        "primary_trade": "General Contractor",
        "years_in_business": 8,
        "service_areas": ["Miami, FL"],
        "specializations": ["kitchen remodeling", "home renovations"],
        "zip_code": "33101"  # Miami ZIP code
    }
    
    # Add message that should trigger bid search
    initial_state.messages = [
        HumanMessage(content="Please show me available kitchen remodeling projects in Miami")
    ]
    
    # Convert to LangGraph state format - use dict directly 
    state = {
        "contractor_profile": initial_state.contractor_profile,
        "company_name": "ABC Construction",
        "messages": initial_state.messages,
        "session_id": "test-direct-123",
        "contractor_lead_id": "test-contractor-123"
    }
    
    print(f"Input state company_name: {state.get('company_name')}")
    print(f"Input state contractor_profile: {state.get('contractor_profile')}")
    print(f"Input state messages: {[m.content for m in state.get('messages', [])]}")
    print()
    
    # Call the bid card search node directly
    print("Calling bid_card_search_node...")
    result = await bid_card_search_node(state)
    
    print("=== BID CARD SEARCH RESULT ===")
    print(f"Result type: {type(result)}")
    print(f"Result keys: {list(result.keys())}")
    print()
    
    # Check bid_cards_attached
    bid_cards_attached = result.get("bid_cards_attached", [])
    print(f"bid_cards_attached: {len(bid_cards_attached)} items")
    
    if bid_cards_attached:
        print("SUCCESS: Found bid cards!")
        for i, card in enumerate(bid_cards_attached):
            print(f"  Card {i+1}: {card.get('title')} ({card.get('project_type')})")
            print(f"    Location: {card.get('location_city')}, {card.get('location_state')}")
            print(f"    ID: {card.get('id')}")
            print(f"    Keys: {list(card.keys())}")
    else:
        print("PROBLEM: No bid cards found")
        
    # Check tool_results
    tool_results = result.get("tool_results", {})
    if tool_results:
        print(f"\nTool results: {tool_results}")
        bid_search_result = tool_results.get("bid_card_search", {})
        if bid_search_result:
            print(f"  Total found: {bid_search_result.get('total_found')}")
            print(f"  Displayed: {bid_search_result.get('displayed')}")
            print(f"  Intelligent search: {bid_search_result.get('intelligent_search')}")
    
    # Check response message
    messages = result.get("messages", [])
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            content = last_message.content
            print(f"\nResponse message: {content[:300]}...")
    
    print("\n=== END TEST ===")

if __name__ == "__main__":
    asyncio.run(test_bid_search_direct())