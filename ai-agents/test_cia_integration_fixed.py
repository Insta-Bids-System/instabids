#!/usr/bin/env python3
"""
Test CIA Agent Bid Card Integration - Fixed with proper UUIDs
Verifies that CIA agent creates and updates potential bid cards during conversations
"""

import asyncio
import json
import sys
import os
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cia.agent import CustomerInterfaceAgent
import requests

async def test_cia_bid_card_integration_fixed():
    """Test CIA agent integration with proper UUID format"""
    
    print("\n=== CIA BID CARD INTEGRATION TEST (FIXED) ===")
    
    # Test with proper UUID format
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    print(f"Using user_id: {user_id}")
    print(f"Using session_id: {session_id}")
    
    # Test 1: Direct API test with proper UUIDs
    print("\n1. Testing potential bid card API directly...")
    
    try:
        # Test creating potential bid card directly
        payload = {
            "conversation_id": session_id,
            "session_id": session_id,
            "user_id": user_id,
            "title": "Test Kitchen Remodel"
        }
        
        response = requests.post("http://localhost:8008/api/cia/potential-bid-cards", json=payload)
        
        if response.status_code == 200:
            bid_card_data = response.json()
            bid_card_id = bid_card_data.get("id")
            print(f"   [SUCCESS] Created potential bid card: {bid_card_id}")
            
            # Test field update
            field_payload = {
                "field_name": "project_type",
                "field_value": "kitchen_remodel",
                "confidence": 1.0
            }
            
            field_response = requests.put(f"http://localhost:8008/api/cia/potential-bid-cards/{bid_card_id}/field", json=field_payload)
            
            if field_response.status_code == 200:
                print("   [SUCCESS] Updated field successfully")
            else:
                print(f"   [FAILED] Field update failed: {field_response.status_code}")
                print(f"   Response: {field_response.text}")
                
            # Check status
            status_response = requests.get(f"http://localhost:8008/api/cia/potential-bid-cards/{bid_card_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"   [SUCCESS] Retrieved status: {status_data.get('completion_percentage', 0)}% complete")
            else:
                print(f"   [FAILED] Status check failed: {status_response.status_code}")
                
        else:
            print(f"   [FAILED] API call failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   [FAILED] API test failed: {e}")
    
    # Test 2: CIA agent with proper UUIDs
    print("\n2. Testing CIA agent with proper UUIDs...")
    
    try:
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("   [FAILED] No OpenAI API key found")
            return
            
        print("   [SUCCESS] OpenAI API key found")
        
        # Initialize CIA agent
        cia_agent = CustomerInterfaceAgent(openai_api_key)
        
        print("   Starting CIA conversation...")
        
        # First message
        result = await cia_agent.handle_conversation(
            user_id=user_id,
            session_id=session_id,
            message="I want to remodel my kitchen. I need new cabinets and granite countertops.",
            project_id=None
        )
        
        if result and result.get("success"):
            print(f"   [SUCCESS] CIA conversation successful")
            print(f"   Response preview: {result.get('response', '')[:100]}...")
            
            # Wait a moment for any async operations
            await asyncio.sleep(2)
            
            # Check if potential bid card was created
            try:
                response = requests.get(f"http://localhost:8008/api/cia/conversation/{session_id}/potential-bid-card")
                
                if response.status_code == 200:
                    bid_card_data = response.json()
                    print(f"   [SUCCESS] Potential bid card found!")
                    print(f"   Completion: {bid_card_data.get('completion_percentage', 0)}%")
                    
                    fields = bid_card_data.get('fields_collected', {})
                    print(f"   Fields collected: {len(fields)}")
                    for field, value in fields.items():
                        print(f"     - {field}: {value}")
                        
                    # Test second message
                    print("\n   Second message...")
                    result2 = await cia_agent.handle_conversation(
                        user_id=user_id,
                        session_id=session_id,
                        message="I live in Austin, Texas, ZIP code 78701. I need this done urgently.",
                        project_id=None
                    )
                    
                    if result2 and result2.get("success"):
                        print("   [SUCCESS] Second message successful")
                        
                        # Wait and check again
                        await asyncio.sleep(2)
                        
                        response2 = requests.get(f"http://localhost:8008/api/cia/conversation/{session_id}/potential-bid-card")
                        if response2.status_code == 200:
                            bid_card_data2 = response2.json()
                            print(f"   [SUCCESS] Updated completion: {bid_card_data2.get('completion_percentage', 0)}%")
                            
                            fields2 = bid_card_data2.get('fields_collected', {})
                            print(f"   Updated fields: {len(fields2)}")
                            for field, value in fields2.items():
                                print(f"     - {field}: {value}")
                        
                elif response.status_code == 404:
                    print("   [FAILED] No potential bid card found")
                    print("   CIA agent may not be calling the API")
                else:
                    print(f"   [FAILED] Error checking bid card: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"   [FAILED] Error checking potential bid card: {e}")
                
        else:
            print("   [FAILED] CIA conversation failed")
            if result:
                print(f"   Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"   [FAILED] CIA agent test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_cia_bid_card_integration_fixed())