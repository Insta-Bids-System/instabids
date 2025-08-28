#!/usr/bin/env python3
"""
Test IRIS Minimal Action - Test action execution with minimal context to avoid timeout
"""

import asyncio
import json
import logging
import requests
from datetime import datetime
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8008"

async def test_iris_minimal_action():
    """Test IRIS actions with minimal context to avoid performance issues"""
    
    print("Testing IRIS Minimal Action - Direct Action Execution")
    print("=" * 60)
    
    # Use proper UUID format for user_id to avoid database errors
    test_user_id = str(uuid.uuid4())
    
    # Step 0: Create test user profile first to satisfy foreign key
    print("Step 0: Creating test user profile...")
    try:
        from database_simple import db
        
        # Create minimal profile for test user
        profile_data = {
            "id": test_user_id,
            "email": f"test-iris-{int(datetime.now().timestamp())}@test.com",
            "full_name": "Test IRIS User"
        }
        
        profile_result = db.client.table("profiles").insert(profile_data).execute()
        if profile_result.data:
            print(f"SUCCESS: Created test profile for user: {test_user_id}")
        else:
            print(f"WARNING: Could not create test profile")
            
    except Exception as e:
        print(f"Warning: Error creating test profile: {e}")
        # Continue anyway - maybe the profile already exists
    
    # Step 1: Create test bid card with minimal data
    print("\nStep 1: Creating test bid card...")
    
    test_bid_card = {
        "bid_card_number": f"IRIS-MIN-{int(datetime.now().timestamp())}",
        "title": "Test Project",
        "description": "Minimal test for IRIS actions",
        "budget_min": 1000,
        "budget_max": 2000,
        "urgency_level": "week",
        "project_type": "general",
        "status": "generated",
        "contractor_count_needed": 1,
        "user_id": test_user_id
    }
    
    try:
        # Insert bid card directly (db already imported above)
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
    
    # Step 2: Test IRIS with minimal message that includes bid card context
    print(f"\nStep 2: Testing IRIS with minimal context...")
    
    try:
        # Create minimal IRIS request with explicit bid card reference
        iris_request = {
            "message": f"Please rename the project {bid_card_id} to 'URGENT FIX' and make it urgent",
            "user_id": test_user_id,
            "session_id": f"minimal_test_{int(datetime.now().timestamp())}",
            "context_type": "property"
        }
        
        print(f"Sending minimal request to IRIS...")
        print(f"   Message: '{iris_request['message']}'")
        print(f"   User ID: {test_user_id}")
        
        # Use shorter timeout and expect it to work quickly
        iris_response = requests.post(
            f"{BACKEND_URL}/api/iris/unified-chat",
            json=iris_request,
            timeout=15  # Shorter timeout - should complete quickly
        )
        
        if iris_response.status_code == 200:
            response_data = iris_response.json()
            print(f"SUCCESS: IRIS responded")
            print(f"   Response: {response_data.get('response', 'No response')[:150]}...")
        else:
            print(f"FAILED: IRIS request failed: {iris_response.status_code}")
            print(f"   Error: {iris_response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"TIMEOUT: IRIS request timed out (>15 seconds)")
        print(f"   This indicates performance issues in context loading")
        return False
    except Exception as e:
        print(f"Error calling IRIS: {e}")
        return False
    
    # Step 3: Verify changes were made
    print(f"\nStep 3: Verifying changes...")
    
    try:
        # Query database directly to check for changes
        verify_result = db.client.table("bid_cards").select("title, urgency_level").eq("id", bid_card_id).execute()
        
        if not verify_result.data:
            print(f"FAILED to get updated bid card from database")
            return False
            
        updated_bid_card = verify_result.data[0]
        
        current_title = updated_bid_card.get("title", "")
        current_urgency = updated_bid_card.get("urgency_level", "")
        
        print(f"Database state after IRIS processing:")
        print(f"   Title: '{current_title}'")
        print(f"   Urgency: '{current_urgency}'")
        
        # Check for any changes from original values
        title_changed = current_title != "Test Project"
        urgency_changed = current_urgency != "week"
        
        print(f"\nChange detection:")
        if title_changed:
            print(f"SUCCESS: Title changed: '{current_title}'")
        else:
            print(f"FAILED: Title unchanged: '{current_title}'")
            
        if urgency_changed:
            print(f"SUCCESS: Urgency changed: '{current_urgency}'")
        else:
            print(f"FAILED: Urgency unchanged: '{current_urgency}'")
        
        # Overall result
        any_changes = title_changed or urgency_changed
        
        if any_changes:
            print(f"\nSUCCESS: IRIS action system made database changes!")
            return True
        else:
            print(f"\nNO CHANGES: IRIS processed request but made no database changes")
            print(f"   This suggests action detection or execution is not working")
            return False
            
    except Exception as e:
        print(f"Error verifying changes: {e}")
        return False

async def main():
    """Main test runner"""
    print("Starting IRIS Minimal Action Test")
    print(f"Testing against: {BACKEND_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    success = await test_iris_minimal_action()
    
    print()
    print("=" * 60)
    if success:
        print("IRIS MINIMAL ACTION TEST: PASSED")
        print("SUCCESS: IRIS action system can make real database changes!")
    else:
        print("IRIS MINIMAL ACTION TEST: FAILED") 
        print("ERROR: IRIS action system needs optimization or debugging")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())