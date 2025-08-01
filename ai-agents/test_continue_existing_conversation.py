#!/usr/bin/env python3
"""
Test continuing an existing conversation to modify bid card
"""

import asyncio
import os
from agents.cia.agent import CustomerInterfaceAgent
from database_simple import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Test user credentials
TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"  # test.homeowner@instabids.com

async def test_continue_kitchen_conversation():
    """Continue the existing kitchen conversation to modify it"""
    print("\n" + "="*50)
    print("TEST: Continue Existing Kitchen Conversation")
    print("="*50)
    
    # Use the original kitchen thread ID
    kitchen_thread_id = "cia_anonymous_1753934812.957596"
    
    # First check current bid card state
    bid_cards = db.client.table('bid_cards').select('*').eq('cia_thread_id', kitchen_thread_id).execute()
    if bid_cards.data:
        card = bid_cards.data[0]
        print(f"\nCurrent Kitchen Bid Card:")
        print(f"- Budget: ${card['budget_min']:,} - ${card['budget_max']:,}")
        print(f"- Status: {card['status']}")
        print(f"- Created: {card['created_at']}")
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Continue the conversation
    result = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="I've been thinking about the kitchen remodel and I want to increase the budget. Can we update it to $40,000-50,000? I want to get really nice appliances.",
        session_id=kitchen_thread_id  # Use the original thread ID
    )
    
    print(f"\nAgent Response: {result['response']}")
    
    # Check if bid card was updated
    await asyncio.sleep(2)
    updated_cards = db.client.table('bid_cards').select('*').eq('cia_thread_id', kitchen_thread_id).execute()
    if updated_cards.data:
        card = updated_cards.data[0]
        print(f"\nUpdated Kitchen Bid Card:")
        print(f"- Budget: ${card['budget_min']:,} - ${card['budget_max']:,}")
        print(f"- Status: {card['status']}")
    
    return result

async def test_create_new_roof_project():
    """Create a completely new project (roof) to test multi-project awareness"""
    print("\n" + "="*50)
    print("TEST: Create New Roof Project")
    print("="*50)
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # New conversation about roof
    result = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="Hi, I need help with a roof repair. It's been leaking during heavy rains. The roof is about 20 years old, asphalt shingles. Location is Tampa, FL 33602. Budget is around $8,000-10,000. Need it fixed within the next 2 weeks.",
        session_id="test_roof_urgent"
    )
    
    print(f"\nAgent Response: {result['response']}")
    print(f"Ready for JAA: {result.get('ready_for_jaa', False)}")
    print(f"Missing fields: {result.get('missing_fields', [])}")
    
    return result

async def main():
    """Run the tests"""
    print("Testing Bid Card Modification and Multi-Project Creation")
    print("User: test.homeowner@instabids.com")
    
    # Test 1: Continue existing kitchen conversation
    await test_continue_kitchen_conversation()
    
    await asyncio.sleep(3)
    
    # Test 2: Create new roof project
    await test_create_new_roof_project()
    
    print("\n" + "="*50)
    print("Tests completed!")
    print("Check the dashboard for:")
    print("1. Updated kitchen budget")
    print("2. New roof repair bid card")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())