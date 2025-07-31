"""
Create a test bid card directly with JAA (bypassing CIA conversation)
"""
import requests
import json
import uuid
from datetime import datetime

def create_test_bid_card_direct():
    """Create a test bid card with rich project data"""
    print("Creating test bid card with rich data...")
    
    # Create mock conversation data that would come from CIA
    test_conversation_data = {
        "thread_id": f"test_rich_{uuid.uuid4().hex[:8]}",
        "user_id": "test_user_rich",
        "messages": [
            {
                "role": "user", 
                "content": "I need to completely renovate my master bathroom in Tampa, FL. It's about 120 sq ft and needs everything - new shower, vanity, flooring, lighting. Budget is $25,000-35,000."
            },
            {
                "role": "assistant",
                "content": "That sounds like an exciting bathroom renovation! Can you tell me more about your timeline and style preferences?"
            },
            {
                "role": "user",
                "content": "I'd like to start in 3 weeks and have it done within 6 weeks total. I want a modern spa-like feel with marble countertops, walk-in shower with glass doors, and good lighting. The house is at 456 Oak Street, Tampa, FL 33602."
            }
        ],
        "state": {
            "project_type": "bathroom_remodel", 
            "location": {
                "city": "Tampa",
                "state": "FL",
                "zip": "33602",
                "address": "456 Oak Street"
            },
            "budget_min": 25000,
            "budget_max": 35000,
            "timeline": "Start in 3 weeks, complete in 6 weeks",
            "urgency": "month",
            "project_details": {
                "room_size": "120 sq ft",
                "scope": "Complete renovation - new shower, vanity, flooring, lighting",
                "style_preferences": "Modern spa-like feel",
                "specific_features": [
                    "Marble countertops",
                    "Walk-in shower with glass doors", 
                    "Good lighting",
                    "New vanity",
                    "New flooring"
                ]
            },
            "property_type": "single_family_home"
        }
    }
    
    # First save the conversation to database
    try:
        from database_simple import db
        
        conversation_record = {
            'thread_id': test_conversation_data['thread_id'],
            'user_id': test_conversation_data['user_id'], 
            'messages': test_conversation_data['messages'],
            'state': test_conversation_data['state'],
            'status': 'ready_for_jaa',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Insert conversation
        result = db.client.table('cia_conversations').insert(conversation_record).execute()
        
        if result.data:
            print(f"[OK] Created rich conversation: {test_conversation_data['thread_id']}")
            
            # Now process with JAA
            jaa_response = requests.post(f"http://localhost:8000/api/jaa/process/{test_conversation_data['thread_id']}")
            
            if jaa_response.status_code == 200:
                jaa_result = jaa_response.json()
                if jaa_result.get('success'):
                    bid_card_id = jaa_result.get('database_id')
                    print(f"[OK] Created rich bid card: {bid_card_id}")
                    
                    # Print details
                    bid_data = jaa_result.get('bid_card_data', {})
                    print(f"   Project: {bid_data.get('project_type', 'N/A')}")
                    print(f"   Budget: {bid_data.get('budget_display', 'N/A')}")
                    print(f"   Location: {bid_data.get('location', {}).get('city', 'N/A')}")
                    print(f"   Timeline: {bid_data.get('timeline', {}).get('description', 'N/A')}")
                    
                    return bid_card_id
                else:
                    print(f"[FAIL] JAA failed: {jaa_result.get('error')}")
            else:
                print(f"[FAIL] JAA request failed: {jaa_response.status_code}")
                print(f"   Response: {jaa_response.text[:200]}")
        else:
            print("[FAIL] Failed to save conversation")
            
    except Exception as e:
        print(f"[FAIL] Error creating bid card: {e}")
    
    return None

def test_bid_card_display(bid_card_id):
    """Test bid card API and display data"""
    print(f"\n=== TESTING BID CARD DISPLAY ===")
    print(f"Bid Card ID: {bid_card_id}")
    
    try:
        response = requests.get(f"http://localhost:8000/api/bid-cards/{bid_card_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n[SUCCESS] Bid card API working!")
            print(f"Project Type: {data.get('project_type', 'N/A')}")
            print(f"Budget: {data.get('budget_display', 'N/A')}")
            print(f"Timeline: {data.get('timeline', 'N/A')}")
            print(f"Location: {data.get('location', {}).get('city', 'N/A')}, {data.get('location', {}).get('state', 'N/A')}")
            print(f"Created: {data.get('created_at', 'N/A')}")
            print(f"Days until deadline: {data.get('days_until_deadline', 'N/A')}")
            
            # Show project details
            project_details = data.get('project_details', {})
            if project_details:
                print(f"\nProject Details:")
                for key, value in project_details.items():
                    if isinstance(value, dict):
                        print(f"  {key}: {json.dumps(value, indent=4)}")
                    else:
                        print(f"  {key}: {value}")
            
            # Test URL that could be used in forms
            bid_card_url = f"http://localhost:8000/api/bid-cards/{bid_card_id}"
            print(f"\nBid Card API URL: {bid_card_url}")
            print("(This is what would be embedded in contractor forms)")
            
            return True
        else:
            print(f"[FAIL] API failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error testing bid card: {e}")
        return False

def main():
    """Create and test a rich bid card"""
    print("=" * 60)
    print("RICH BID CARD CREATION & TESTING")
    print("=" * 60)
    
    # Step 1: Create rich bid card
    bid_card_id = create_test_bid_card_direct()
    
    if not bid_card_id:
        print("\n[FAILED] Could not create rich bid card")
        return False
    
    # Step 2: Test display
    success = test_bid_card_display(bid_card_id)
    
    if success:
        print(f"\n[SUCCESS] Rich bid card created and tested!")
        print(f"Ready for contractor website testing with ID: {bid_card_id}")
        return bid_card_id
    else:
        print(f"\n[FAILED] Bid card testing failed")
        return None

if __name__ == "__main__":
    main()