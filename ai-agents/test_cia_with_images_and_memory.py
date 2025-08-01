#!/usr/bin/env python3
"""
Test CIA agent with images and multi-project memory
Tests:
1. Agent recognizing existing projects
2. Creating new projects
3. Modifying existing bid cards
"""

import asyncio
import base64
import os
from agents.cia.agent import CustomerInterfaceAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Test user credentials
TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"  # test.homeowner@instabids.com

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def test_existing_project_recognition():
    """Test 1: Send kitchen images - should recognize existing kitchen project"""
    print("\n" + "="*50)
    print("TEST 1: Kitchen Images (Existing Project)")
    print("="*50)
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Load kitchen images
    kitchen_images = [
        encode_image(r"C:\Users\Not John Or Justin\Documents\instabids\test-images\current-state\kitchen-outdated-1.webp"),
        encode_image(r"C:\Users\Not John Or Justin\Documents\instabids\test-images\current-state\kitchen-outdated-2.webp")
    ]
    
    # First message with images
    result = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="I need help with my kitchen renovation. Here are some photos of the current state.",
        images=kitchen_images,
        session_id="test_session_kitchen_1"
    )
    
    print(f"\nAgent Response: {result['response']}")
    print(f"Phase: {result.get('phase', 'N/A')}")
    
    # Follow up to see if it recognizes existing project
    result2 = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="I'm thinking of changing the budget to around $40,000-45,000 instead. Can we update that?",
        session_id="test_session_kitchen_1"
    )
    
    print(f"\nAgent Response to budget change: {result2['response']}")
    
    return result2

async def test_new_project_creation():
    """Test 2: Send lawn images - should create new project"""
    print("\n" + "="*50)
    print("TEST 2: Lawn Images (New Project)")
    print("="*50)
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Load lawn images
    lawn_images = [
        encode_image(r"C:\Users\Not John Or Justin\Documents\instabids\test-images\current-state\lawn-problem-1.webp"),
        encode_image(r"C:\Users\Not John Or Justin\Documents\instabids\test-images\current-state\lawn-problem-2.webp")
    ]
    
    # First message with lawn images
    result = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="My lawn is in terrible shape. I need professional lawn care services. Looking for monthly maintenance.",
        images=lawn_images,
        session_id="test_session_lawn_1"
    )
    
    print(f"\nAgent Response: {result['response']}")
    print(f"Phase: {result.get('phase', 'N/A')}")
    
    # Provide more details
    result2 = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="Budget is around $200-300 per month. I need weekly mowing, fertilization, and weed control. Property is about 1/4 acre.",
        session_id="test_session_lawn_1"
    )
    
    print(f"\nAgent Response to details: {result2['response']}")
    
    return result2

async def test_cross_project_awareness():
    """Test 3: Start new conversation, see if agent remembers other projects"""
    print("\n" + "="*50)
    print("TEST 3: Cross-Project Memory Test")
    print("="*50)
    
    cia = CustomerInterfaceAgent(anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Load backyard images
    backyard_images = [
        encode_image(r"C:\Users\Not John Or Justin\Documents\instabids\test-images\current-state\backyard-neglected-1.webp")
    ]
    
    # New conversation about backyard
    result = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="I also need help with my backyard. It's completely neglected.",
        images=backyard_images,
        session_id="test_session_backyard_1"
    )
    
    print(f"\nAgent Response (should show awareness of other projects): {result['response']}")
    
    # Ask about relationship to lawn project
    result2 = await cia.handle_conversation(
        user_id=TEST_USER_ID,
        message="Would this be part of the lawn maintenance or a separate landscaping project?",
        session_id="test_session_backyard_1"
    )
    
    print(f"\nAgent Response about project relationship: {result2['response']}")
    
    return result2

async def main():
    """Run all tests"""
    print("Starting CIA Agent Tests with Images and Memory")
    print("User: test.homeowner@instabids.com")
    print("Testing multi-project awareness and bid card updates")
    
    # Test 1: Existing project recognition (Kitchen)
    await test_existing_project_recognition()
    
    # Wait a bit between tests
    await asyncio.sleep(2)
    
    # Test 2: New project creation (Lawn)
    await test_new_project_creation()
    
    # Wait a bit between tests
    await asyncio.sleep(2)
    
    # Test 3: Cross-project awareness (Backyard)
    await test_cross_project_awareness()
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("Check the dashboard to see updated bid cards")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())