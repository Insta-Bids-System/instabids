#!/usr/bin/env python3
"""
Test IRIS Actions Direct - Bypass heavy context loading and test actions directly
"""

import asyncio
import json
import logging
import requests
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8008"

async def test_iris_actions_direct():
    """Test IRIS actions by calling action endpoints directly"""
    
    print("Testing IRIS Actions Direct - Bypass Context Loading")
    print("=" * 60)
    
    # Step 1: Create test bid card
    print("Step 1: Creating test bid card...")
    
    test_bid_card = {
        "bid_card_number": f"IRIS-DIRECT-{int(datetime.now().timestamp())}",
        "title": "General Repairs Project",
        "description": "Test project for IRIS direct actions",
        "budget_min": 5000,
        "budget_max": 10000,
        "urgency_level": "week",
        "project_type": "general_contractor",
        "status": "generated",
        "contractor_count_needed": 3
    }
    
    try:
        # Create bid card directly in database
        from database_simple import db
        
        # Insert bid card directly
        insert_result = db.client.table("bid_cards").insert(test_bid_card).execute()
        
        if not insert_result.data:
            print("FAILED to create test bid card in database")
            return False
            
        bid_card_data = insert_result.data[0]
        bid_card_id = bid_card_data.get("id")
        
        print(f"SUCCESS: Created test bid card: {bid_card_id}")
        print(f"   Title: {test_bid_card['title']}")
        print(f"   Urgency: {test_bid_card['urgency_level']}")
        
    except Exception as e:
        print(f"Error creating test bid card: {e}")
        return False
    
    # Step 2: Test IRIS actions directly via action API
    print(f"\nStep 2: Testing IRIS actions directly...")
    
    try:
        # Test title update action
        title_action_payload = {
            "request_id": f"test-{int(datetime.now().timestamp())}",
            "agent_name": "IRIS", 
            "user_id": "test-user-iris-direct",
            "bid_card_id": bid_card_id,
            "updates": {
                "title": "ASAP Wife is Mad"
            }
        }
        
        print(f"Testing title update...")
        title_response = requests.post(
            f"{BACKEND_URL}/api/iris/actions/update-bid-card",
            json=title_action_payload,
            timeout=10
        )
        
        if title_response.status_code == 200:
            print(f"SUCCESS: Title update action completed")
        else:
            print(f"FAILED: Title update action failed: {title_response.text}")
            return False
        
        # Test urgency update action
        urgency_action_payload = {
            "request_id": f"test-urgency-{int(datetime.now().timestamp())}",
            "agent_name": "IRIS",
            "user_id": "test-user-iris-direct", 
            "bid_card_id": bid_card_id,
            "updates": {
                "urgency_level": "urgent"
            }
        }
        
        print(f"Testing urgency update...")
        urgency_response = requests.post(
            f"{BACKEND_URL}/api/iris/actions/update-bid-card",
            json=urgency_action_payload,
            timeout=10
        )
        
        if urgency_response.status_code == 200:
            print(f"SUCCESS: Urgency update action completed")
        else:
            print(f"FAILED: Urgency update action failed: {urgency_response.text}")
            return False
            
    except Exception as e:
        print(f"Error calling action API: {e}")
        return False
    
    # Step 3: Verify the changes were actually made
    print(f"\nStep 3: Verifying changes were made to database...")
    
    try:
        # Query database directly to verify changes
        verify_result = db.client.table("bid_cards").select("title, urgency_level").eq("id", bid_card_id).execute()
        
        if not verify_result.data:
            print(f"FAILED to get updated bid card from database")
            return False
            
        updated_bid_card = verify_result.data[0]
        
        # Check if changes were made
        current_title = updated_bid_card.get("title", "")
        current_urgency = updated_bid_card.get("urgency_level", "")
        
        print(f"Current bid card state:")
        print(f"   Title: '{current_title}'")
        print(f"   Urgency: '{current_urgency}'")
        
        # Verify changes
        title_changed = current_title == "ASAP Wife is Mad"
        urgency_changed = current_urgency == "urgent"
        
        print(f"\nVerification Results:")
        if title_changed:
            print(f"SUCCESS: Title correctly changed to: '{current_title}'")
        else:
            print(f"FAILED: Title NOT changed correctly (got: '{current_title}')")
            
        if urgency_changed:
            print(f"SUCCESS: Urgency correctly changed to: '{current_urgency}'")
        else:
            print(f"FAILED: Urgency NOT changed correctly (got: '{current_urgency}')")
        
        # Overall result
        actions_worked = title_changed and urgency_changed
        
        if actions_worked:
            print(f"\nSUCCESS: IRIS action system is working!")
            print(f"   Both title and urgency changes confirmed in database")
            return True
        else:
            print(f"\nPARTIAL SUCCESS: Some changes not applied correctly")
            return False
            
    except Exception as e:
        print(f"Error verifying changes: {e}")
        return False

async def main():
    """Main test runner"""
    print("Starting IRIS Direct Actions Test")
    print(f"Testing against: {BACKEND_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    success = await test_iris_actions_direct()
    
    print()
    print("=" * 60)
    if success:
        print("IRIS DIRECT ACTIONS TEST: PASSED")
        print("IRIS action endpoints work correctly!")
    else:
        print("IRIS DIRECT ACTIONS TEST: FAILED") 
        print("IRIS action endpoints need debugging")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())