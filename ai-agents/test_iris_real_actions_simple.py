#!/usr/bin/env python3
"""
Test IRIS Real Actions - Verify IRIS can actually make bid card changes
Tests the complete flow from user message to database update
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

async def test_iris_real_actions():
    """Test IRIS can actually make real changes to bid cards"""
    
    print("Testing IRIS Real Actions - Bid Card Changes")
    print("=" * 60)
    
    # Step 1: Create a test bid card first
    print("Step 1: Creating test bid card...")
    
    test_bid_card = {
        "bid_card_number": f"IRIS-TEST-{int(datetime.now().timestamp())}",
        "title": "General Repairs Project",
        "description": "Test project for IRIS actions",
        "budget_min": 5000,
        "budget_max": 10000,
        "urgency_level": "week",
        "project_type": "general_contractor",
        "status": "generated",
        "contractor_count_needed": 3
    }
    
    try:
        # Create bid card directly in database for testing
        from database_simple import db
        
        # Insert bid card directly
        insert_result = db.client.table("bid_cards").insert(test_bid_card).execute()
        
        if not insert_result.data:
            print(f"FAILED to create test bid card in database")
            return False
            
        bid_card_data = insert_result.data[0]
        bid_card_id = bid_card_data.get("id")
        
        if not bid_card_id:
            print(f"No bid card ID returned from database")
            return False
            
        print(f"SUCCESS: Created test bid card: {bid_card_id}")
        print(f"   Title: {test_bid_card['title']}")
        print(f"   Urgency: {test_bid_card['urgency_level']}")
        
    except Exception as e:
        print(f"Error creating test bid card: {e}")
        return False
    
    # Step 2: Test IRIS action - rename and make urgent
    print(f"\nStep 2: Testing IRIS actions...")
    
    test_user_id = "test-user-iris-actions"
    
    # Create context that includes the bid card ID
    iris_request = {
        "message": f"Please rename 'General Repairs Project' to 'ASAP Wife is Mad' and make it urgent",
        "user_id": test_user_id,
        "session_id": f"iris_test_{int(datetime.now().timestamp())}",
        "context_type": "property"
    }
    
    # Add bid card ID to conversation history simulation
    # First save a message that mentions the bid card ID so IRIS can find it
    setup_message = {
        "message": f"I'm working on project {bid_card_id} called General Repairs Project",
        "user_id": test_user_id,
        "session_id": iris_request["session_id"]
    }
    
    try:
        # First, set up context by mentioning the bid card
        print(f"Setting up context with bid card ID...")
        setup_response = requests.post(
            f"{BACKEND_URL}/api/iris/unified-chat",
            json=setup_message,
            timeout=30
        )
        
        if setup_response.status_code == 200:
            print(f"SUCCESS: Context setup successful")
        else:
            print(f"WARNING: Context setup failed, but continuing: {setup_response.text}")
        
        # Now test the actual action
        print(f"Sending action request to IRIS...")
        print(f"   Message: '{iris_request['message']}'")
        
        iris_response = requests.post(
            f"{BACKEND_URL}/api/iris/unified-chat",
            json=iris_request,
            timeout=30
        )
        
        if iris_response.status_code != 200:
            print(f"FAILED: IRIS request failed: {iris_response.text}")
            return False
            
        response_data = iris_response.json()
        print(f"SUCCESS: IRIS responded successfully")
        print(f"   Response: {response_data.get('response', 'No response')[:200]}...")
        
    except Exception as e:
        print(f"Error calling IRIS: {e}")
        return False
    
    # Step 3: Verify the changes were actually made
    print(f"\nStep 3: Verifying changes were made to database...")
    
    try:
        # Get updated bid card
        verify_response = requests.get(
            f"{BACKEND_URL}/api/bid-cards/{bid_card_id}",
            timeout=10
        )
        
        if verify_response.status_code != 200:
            print(f"FAILED to get updated bid card: {verify_response.text}")
            return False
            
        updated_bid_card = verify_response.json()
        
        # Check if changes were made
        current_title = updated_bid_card.get("title", "")
        current_urgency = updated_bid_card.get("urgency_level", "")
        
        print(f"Current bid card state:")
        print(f"   Title: '{current_title}'")
        print(f"   Urgency: '{current_urgency}'")
        
        # Verify title change
        title_changed = current_title != "General Repairs Project"
        urgency_changed = current_urgency != "week"
        
        print(f"\nVerification Results:")
        if title_changed:
            print(f"SUCCESS: Title changed: '{current_title}'")
        else:
            print(f"FAILED: Title NOT changed (still: '{current_title}')")
            
        if urgency_changed:
            print(f"SUCCESS: Urgency changed: '{current_urgency}'")
        else:
            print(f"FAILED: Urgency NOT changed (still: '{current_urgency}')")
        
        # Overall result
        actions_worked = title_changed or urgency_changed
        
        if actions_worked:
            print(f"\nSUCCESS: IRIS actions are working!")
            print(f"   IRIS made real changes to the database")
            return True
        else:
            print(f"\nFAILED: IRIS actions did not work")
            print(f"   No changes detected in database")
            return False
            
    except Exception as e:
        print(f"Error verifying changes: {e}")
        return False

async def main():
    """Main test runner"""
    print("Starting IRIS Real Actions Test")
    print(f"Testing against: {BACKEND_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    success = await test_iris_real_actions()
    
    print()
    print("=" * 60)
    if success:
        print("IRIS REAL ACTIONS TEST: PASSED")
        print("IRIS can make real changes to bid cards!")
    else:
        print("IRIS REAL ACTIONS TEST: FAILED") 
        print("IRIS action system needs debugging")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())