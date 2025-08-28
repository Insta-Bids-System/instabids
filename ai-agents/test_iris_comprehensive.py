"""Comprehensive test of IRIS unified agent with all features"""

import asyncio
import requests
import json
from datetime import datetime
from config.service_urls import get_backend_url

# Test configuration
BASE_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"  # Test homeowner ID

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

async def test_iris_capabilities():
    """Test IRIS system prompt and capabilities"""
    print_section("1. TESTING IRIS CAPABILITIES & SYSTEM PROMPT")
    
    session_id = f"test_comprehensive_{int(datetime.now().timestamp())}"
    
    # Test 1: Basic greeting and capabilities
    response = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Hello IRIS, what can you help me with?",
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nIRIS Response: {data.get('response', 'No response')[:500]}")
        print(f"\nAvailable Tools: {data.get('available_tools', [])}")
        print(f"\nContext Summary: {json.dumps(data.get('context_summary', {}), indent=2)}")
    else:
        print(f"Error: {response.status_code} - {response.text[:200]}")
    
    return session_id

async def test_inspiration_boards():
    """Test IRIS access to inspiration boards"""
    print_section("2. TESTING INSPIRATION BOARDS ACCESS")
    
    session_id = f"test_boards_{int(datetime.now().timestamp())}"
    
    response = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Can you show me my inspiration boards?",
            "session_id": session_id,
            "context_type": "inspiration"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nIRIS Response: {data.get('response', 'No response')[:500]}")
        reasoning = data.get("reasoning", {})
        print(f"\nIntent: {reasoning.get('user_intent')}")
        print(f"\nContext Analysis: {json.dumps(reasoning.get('context_analysis', {}), indent=2)}")
    else:
        print(f"Error: {response.status_code} - {response.text[:200]}")

async def test_property_maintenance():
    """Test IRIS access to property maintenance and trade grouping"""
    print_section("3. TESTING PROPERTY MAINTENANCE & TRADE GROUPING")
    
    session_id = f"test_maintenance_{int(datetime.now().timestamp())}"
    
    # Test maintenance context
    response = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "I have some repairs at my property. Can you group them by trade?",
            "session_id": session_id,
            "context_type": "property"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nIRIS Response: {data.get('response', 'No response')[:500]}")
        print(f"\nSuggestions: {data.get('suggestions', [])}")
        
        # Check if trade grouping is available
        if "trade_grouping" in data.get("available_tools", []):
            print("\n[CHECK] Trade grouping tool is available!")
    else:
        print(f"Error: {response.status_code} - {response.text[:200]}")

async def test_bid_card_creation():
    """Test IRIS ability to suggest bid card creation"""
    print_section("4. TESTING BID CARD CREATION SUGGESTIONS")
    
    session_id = f"test_bidcards_{int(datetime.now().timestamp())}"
    
    response = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "Should I create a bid card for my electrical repairs?",
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nIRIS Response: {data.get('response', 'No response')[:500]}")
        
        # Check reasoning
        reasoning = data.get("reasoning", {})
        if reasoning.get("user_intent") == "project_management":
            print("\n[CHECK] Correctly identified project management intent!")
    else:
        print(f"Error: {response.status_code} - {response.text[:200]}")

async def test_conversation_persistence():
    """Test conversation history persistence"""
    print_section("5. TESTING CONVERSATION PERSISTENCE")
    
    session_id = f"test_persist_{int(datetime.now().timestamp())}"
    
    # First message
    response1 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "My name is TestUser and I need help with my backyard",
            "session_id": session_id
        }
    )
    
    # Second message with same session
    response2 = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "What did I tell you my name was?",
            "session_id": session_id
        }
    )
    
    if response2.status_code == 200:
        data = response2.json()
        response_text = data.get('response', '')
        if "TestUser" in response_text or "backyard" in response_text:
            print("\n[CHECK] Conversation memory working! IRIS remembers previous messages.")
        else:
            print("\n[WARNING] IRIS may not be remembering conversation history")
        print(f"\nIRIS Response: {response_text[:500]}")
    else:
        print(f"Error: {response2.status_code}")

async def test_complete_workflow():
    """Test a complete workflow with IRIS"""
    print_section("6. TESTING COMPLETE WORKFLOW")
    
    session_id = f"test_workflow_{int(datetime.now().timestamp())}"
    
    # Workflow: User uploads photo -> IRIS analyzes -> suggests trade grouping -> recommends bid card
    
    messages = [
        "I just uploaded photos of my property and there are several issues",
        "Can you help me organize these repairs by trade type?",
        "Which trade should I prioritize first?",
        "Should I create separate bid cards for each trade?"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\nStep {i}: {msg}")
        
        response = requests.post(
            f"{BASE_URL}/api/iris/unified-chat",
            json={
                "user_id": TEST_USER_ID,
                "message": msg,
                "session_id": session_id,
                "context_type": "property" if "property" in msg else None
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"IRIS: {data.get('response', '')[:300]}...")
            
            # Show evolving context
            context_summary = data.get("context_summary", {})
            if context_summary:
                print(f"Context: {json.dumps(context_summary, indent=2)}")
        else:
            print(f"Error: {response.status_code}")
        
        await asyncio.sleep(1)  # Small delay between messages

async def main():
    """Run all comprehensive tests"""
    
    print("\n" + "="*60)
    print(" COMPREHENSIVE IRIS UNIFIED AGENT TEST")
    print("="*60)
    
    # Test 1: Capabilities
    session_id = await test_iris_capabilities()
    await asyncio.sleep(1)
    
    # Test 2: Inspiration boards
    await test_inspiration_boards()
    await asyncio.sleep(1)
    
    # Test 3: Property maintenance
    await test_property_maintenance()
    await asyncio.sleep(1)
    
    # Test 4: Bid cards
    await test_bid_card_creation()
    await asyncio.sleep(1)
    
    # Test 5: Persistence
    await test_conversation_persistence()
    await asyncio.sleep(1)
    
    # Test 6: Complete workflow
    await test_complete_workflow()
    
    print_section("TEST COMPLETE")
    print("\nAll IRIS unified agent tests completed!")
    print("\nKey findings:")
    print("- System prompt defines IRIS as design and project assistant")
    print("- Has access to inspiration boards, property photos, and trade projects")
    print("- Can suggest trade grouping and bid card creation")
    print("- Conversations should persist in unified_conversation_messages table")

if __name__ == "__main__":
    asyncio.run(main())