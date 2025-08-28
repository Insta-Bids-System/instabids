"""Test IRIS with Trade Grouping Integration"""

import asyncio
import requests
import json
from datetime import datetime
from config.service_urls import get_backend_url

# Test configuration
BASE_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"  # Test homeowner ID
TEST_PROPERTY_ID = "property_001"  # Test property

async def test_trade_grouping_conversation():
    """Test IRIS conversation about trade grouping"""
    
    print("\n=== Testing IRIS Trade Grouping Integration ===\n")
    
    # Test messages simulating user asking about repairs
    test_messages = [
        "I have several maintenance issues at my property. Can you help organize them?",
        "Can you group my repairs by trade so I can hire the right contractors?",
        "What electrical issues do I have at my property?",
        "Should I create separate bid cards for each trade?",
        "How many different trades should I hire for all my repairs?"
    ]
    
    session_id = f"test_trade_{int(datetime.now().timestamp())}"
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: {message}")
        print("-" * 50)
        
        try:
            # Send message to IRIS
            response = requests.post(
                f"{BASE_URL}/api/iris/unified-chat",
                json={
                    "user_id": TEST_USER_ID,
                    "message": message,
                    "session_id": session_id,
                    "property_id": TEST_PROPERTY_ID,
                    "context_type": "property"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"IRIS Response: {data.get('response', 'No response')[:300]}...")
                
                # Show reasoning
                reasoning = data.get("reasoning", {})
                print(f"\nIntent detected: {reasoning.get('user_intent', 'unknown')}")
                print(f"Confidence: {reasoning.get('confidence', 0) * 100:.0f}%")
                
                # Show suggestions
                suggestions = data.get("suggestions", [])
                if suggestions:
                    print(f"Suggestions: {', '.join(suggestions[:3])}")
                
                # Show available tools
                tools = data.get("available_tools", [])
                if "trade_grouping" in tools:
                    print("Trade grouping tool available!")
                    
            else:
                print(f"Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Small delay between requests
        await asyncio.sleep(1)

async def test_direct_trade_grouping():
    """Test direct trade grouping API"""
    
    print("\n\n=== Testing Direct Trade Grouping API ===\n")
    
    try:
        # Get trade groups for the property
        response = requests.get(
            f"{BASE_URL}/api/project-grouping/{TEST_PROPERTY_ID}/trade-groups",
            params={"user_id": TEST_USER_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total issues: {data.get('total_issues', 0)}")
            print(f"Trades identified: {data.get('trades_identified', 0)}")
            
            trade_groups = data.get("trade_groups", {})
            for trade, info in trade_groups.items():
                print(f"\n{trade.upper()}:")
                print(f"  - Issues: {info.get('total_issues', 0)}")
                print(f"  - Rooms affected: {info.get('rooms_count', 0)}")
                print(f"  - Severity: {info.get('severity_breakdown', {})}")
                
                # Show first 2 issues
                issues = info.get("issues", [])
                for issue in issues[:2]:
                    print(f"    * {issue.get('description', 'No description')}")
                    
        else:
            print(f"Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run all tests"""
    
    # Test IRIS conversation about trade grouping
    await test_trade_grouping_conversation()
    
    # Test direct trade grouping API
    await test_direct_trade_grouping()
    
    print("\n=== Trade Grouping Integration Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main())