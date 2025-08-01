#!/usr/bin/env python3
"""
Simpler test of multi-project memory and bid card modifications
No images to avoid API token limits
"""

import asyncio
import os
from agents.cia.agent import CustomerInterfaceAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Test user credentials
TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"  # test.homeowner@instabids.com

async def test_modify_kitchen_budget():
    """Test modifying the existing kitchen project budget"""
    print("\n" + "="*50)
    print("TEST: Modify Existing Kitchen Project Budget")
    print("="*50)
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Ask to modify kitchen budget
    result = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="I want to update my kitchen remodel budget. Can we change it to $40,000-50,000? The original was too low.",
        session_id="test_modify_kitchen"
    )
    
    print(f"\nAgent Response: {result['response']}")
    
    # Provide more context
    result2 = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="Yes, the kitchen remodel project. I realized I need to budget more for the high-end appliances I want.",
        session_id="test_modify_kitchen"
    )
    
    print(f"\nAgent Response 2: {result2['response']}")
    
    return result2

async def test_new_project_with_memory():
    """Test creating new project while agent remembers existing ones"""
    print("\n" + "="*50)
    print("TEST: New Project with Cross-Project Awareness")
    print("="*50)
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Start conversation about roof
    result = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="I also need help with my roof. It's been leaking during heavy rains. Need to get it fixed ASAP.",
        session_id="test_roof_project"
    )
    
    print(f"\nAgent Response: {result['response']}")
    
    # Provide details
    result2 = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="Budget is around $8,000-10,000. It's an asphalt shingle roof, about 20 years old. Location is Tampa, FL 33602.",
        session_id="test_roof_project"
    )
    
    print(f"\nAgent Response 2: {result2['response']}")
    
    # Test if ready for JAA
    if result2.get('ready_for_jaa'):
        print("\n✓ Project is ready for JAA processing!")
        print(f"Missing fields: {result2.get('missing_fields', [])}")
    
    return result2

async def test_check_existing_projects():
    """Test if agent can tell us about existing projects"""
    print("\n" + "="*50)
    print("TEST: Check Existing Projects")
    print("="*50)
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Ask about existing projects
    result = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="Can you remind me what projects I have going on? I think I had a kitchen and bathroom project.",
        session_id="test_check_projects"
    )
    
    print(f"\nAgent Response: {result['response']}")
    
    return result

async def main():
    """Run all tests"""
    print("Starting Multi-Project Memory and Modification Tests")
    print("User: test.homeowner@instabids.com")
    
    # Test 1: Check existing projects
    await test_check_existing_projects()
    await asyncio.sleep(2)
    
    # Test 2: Modify kitchen budget
    await test_modify_kitchen_budget()
    await asyncio.sleep(2)
    
    # Test 3: Create new project (roof)
    await test_new_project_with_memory()
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("Check the dashboard for:")
    print("1. Updated kitchen budget (should be $40K-50K)")
    print("2. New roof repair bid card")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())