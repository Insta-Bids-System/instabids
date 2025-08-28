#!/usr/bin/env python3
"""
Test CIA Agent Bid Card Integration
Verifies that CIA agent creates and updates potential bid cards during conversations
"""

import asyncio
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cia.agent import CustomerInterfaceAgent
from agents.cia.potential_bid_card_integration import PotentialBidCardManager
import requests

async def test_cia_bid_card_integration():
    """Test CIA agent integration with potential bid card system"""
    
    print("\n=== CIA BID CARD INTEGRATION TEST ===")
    
    # Test 1: Verify endpoints are accessible
    print("\n1. Testing API endpoint accessibility...")
    
    try:
        # Test main backend health
        response = requests.get("http://localhost:8008/")
        if response.status_code == 200:
            print("   [SUCCESS] Backend is running")
        else:
            print("   [FAILED] Backend issue")
            
    except Exception as e:
        print(f"   [FAILED] Backend connection failed: {e}")
        return
    
    # Test 2: Test PotentialBidCardManager directly
    print("\n2. Testing PotentialBidCardManager...")
    
    manager = PotentialBidCardManager()
    
    try:
        # Test bid card creation
        bid_card_id = await manager.create_potential_bid_card(
            conversation_id="test-conversation-123",
            session_id="test-session-456",
            user_id="test-user-789"
        )
        
        if bid_card_id:
            print(f"   [SUCCESS] Created potential bid card: {bid_card_id}")
            
            # Test field update
            success = await manager.update_bid_card_field(
                bid_card_id=bid_card_id,
                field_name="project_type",
                field_value="kitchen_remodel"
            )
            
            if success:
                print("   [SUCCESS] Updated bid card field")
            else:
                print("   [FAILED] Failed to update bid card field")
                
            # Test collected info update
            collected_info = {
                "project_description": "I want to remodel my kitchen with new cabinets",
                "zip_code": "78701", 
                "urgency": "medium"
            }
            
            updated_count = await manager.update_from_collected_info(
                bid_card_id=bid_card_id,
                collected_info=collected_info
            )
            
            print(f"   [SUCCESS] Updated {updated_count} fields from collected info")
            
            # Test status retrieval
            status = await manager.get_bid_card_status(bid_card_id)
            if status:
                print(f"   [SUCCESS] Retrieved bid card status: {status.get('completion_percentage', 0)}% complete")
            else:
                print("   [FAILED] Failed to retrieve bid card status")
                
        else:
            print("   [FAILED] Failed to create potential bid card")
            
    except Exception as e:
        print(f"   [FAILED] PotentialBidCardManager test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test CIA agent conversation with field extraction
    print("\n3. Testing CIA agent conversation with bid card integration...")
    
    try:
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("   [FAILED] No OpenAI API key found - skipping CIA agent test")
            return
            
        print("   [SUCCESS] OpenAI API key found")
        
        # Initialize CIA agent
        cia_agent = CustomerInterfaceAgent(openai_api_key)
        
        # Test conversation that should create a bid card
        user_id = "test-user-cia-integration"
        session_id = "test-session-cia-integration" 
        
        print("   Starting conversation...")
        
        # First message should create potential bid card
        result = await cia_agent.handle_conversation(
            user_id=user_id,
            session_id=session_id,
            message="I need help with a kitchen remodel project. I want to update my cabinets and countertops.",
            project_id=None
        )
        
        if result and result.get("success"):
            print(f"   [SUCCESS] CIA conversation successful")
            print(f"   Response length: {len(result.get('response', ''))}")
            
            # Check if potential bid card was created by looking at session state
            # (CIA agent stores potential_bid_card_id in session state)
            
            # Second message with more details
            result2 = await cia_agent.handle_conversation(
                user_id=user_id,
                session_id=session_id,
                message="I live in zip code 78701 and I'm hoping to get this done within the next month.",
                project_id=None
            )
            
            if result2 and result2.get("success"):
                print(f"   [SUCCESS] Second CIA conversation successful")
                
                # Third message to add more fields
                result3 = await cia_agent.handle_conversation(
                    user_id=user_id,
                    session_id=session_id,
                    message="My budget is around $25,000 to $35,000 for the whole project.",
                    project_id=None
                )
                
                if result3 and result3.get("success"):
                    print(f"   [SUCCESS] Third CIA conversation successful")
                    
                    # Check if we can retrieve a potential bid card for this conversation
                    try:
                        response = requests.get(f"http://localhost:8008/api/cia/conversation/{session_id}/potential-bid-card")
                        
                        if response.status_code == 200:
                            bid_card_data = response.json()
                            print(f"   [SUCCESS] Found potential bid card for conversation!")
                            print(f"   Completion: {bid_card_data.get('completion_percentage', 0)}%")
                            print(f"   Fields collected: {len(bid_card_data.get('fields_collected', {}))}")
                            
                            # Print collected fields
                            fields = bid_card_data.get('fields_collected', {})
                            for field, value in fields.items():
                                print(f"     - {field}: {value}")
                                
                        elif response.status_code == 404:
                            print("   [FAILED] No potential bid card found for conversation")
                            print("   This suggests CIA agent integration is not working")
                        else:
                            print(f"   [FAILED] Error retrieving potential bid card: {response.status_code}")
                            
                    except Exception as e:
                        print(f"   [FAILED] Error checking potential bid card: {e}")
                else:
                    print("   [FAILED] Third CIA conversation failed")
            else:
                print("   [FAILED] Second CIA conversation failed")
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
    asyncio.run(test_cia_bid_card_integration())