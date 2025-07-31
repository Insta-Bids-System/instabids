"""
Create bid card directly through JAA agent (simpler approach)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.jaa.agent import JobAssessmentAgent
import json

def create_bid_card_directly():
    """Create bid card directly using JAA agent"""
    print("Creating bid card directly with JAA agent...")
    
    # Mock conversation data that JAA would receive
    mock_conversation = {
        "thread_id": "direct_test_123",
        "messages": [
            {
                "role": "user",
                "content": "I need to renovate my kitchen in Orlando, FL. It's about 200 sq ft and needs new cabinets, countertops, granite, and all new appliances. My budget is around $45,000 and I'd like to start within 2-3 weeks."
            },
            {
                "role": "assistant", 
                "content": "That sounds like a comprehensive kitchen renovation! Can you tell me more about your style preferences?"
            },
            {
                "role": "user",
                "content": "I want a modern look with white cabinets, quartz countertops, and stainless steel appliances. The house is at 789 Pine Avenue, Orlando, FL 32801. This is for my single-family home."
            }
        ],
        "state": {
            "project_type": "kitchen_remodel",
            "budget_min": 40000,
            "budget_max": 50000,
            "timeline": "Start in 2-3 weeks",
            "urgency": "week",
            "location": {
                "city": "Orlando", 
                "state": "FL",
                "zip": "32801",
                "address": "789 Pine Avenue"
            },
            "project_details": {
                "room_size": "200 sq ft",
                "scope": "Complete kitchen renovation",
                "features": [
                    "New cabinets",
                    "New countertops", 
                    "Granite surfaces",
                    "All new appliances"
                ],
                "style": "Modern with white cabinets, quartz countertops, stainless steel appliances"
            },
            "property_type": "single_family_home"
        }
    }
    
    try:
        # Initialize JAA agent
        jaa = JobAssessmentAgent()
        print("[OK] JAA agent initialized")
        
        # Create the bid card directly
        print("Processing conversation with JAA...")
        
        # We need to save this conversation first so JAA can find it
        from database_simple import db
        from datetime import datetime
        
        conversation_record = {
            'thread_id': mock_conversation['thread_id'],
            'user_id': 'direct_test_user',
            'messages': mock_conversation['messages'],
            'state': mock_conversation['state'],
            'status': 'ready_for_jaa',
            'created_at': datetime.now().isoformat()
        }
        
        # Insert conversation
        result = db.client.table('cia_conversations').insert(conversation_record).execute()
        
        if result.data:
            print(f"[OK] Saved conversation: {mock_conversation['thread_id']}")
            
            # Now process with JAA
            jaa_result = jaa.process_conversation(mock_conversation['thread_id'])
            
            if jaa_result.get('success'):
                bid_card_id = jaa_result.get('database_id')
                print(f"[SUCCESS] Created bid card: {bid_card_id}")
                
                # Print details
                bid_data = jaa_result.get('bid_card_data', {})
                print(f"   Project: {bid_data.get('project_type', 'N/A')}")
                print(f"   Budget: {bid_data.get('budget_display', 'N/A')}")
                print(f"   Timeline: {bid_data.get('timeline', {}).get('description', 'N/A')}")
                print(f"   Urgency: {bid_data.get('urgency_level', 'N/A')}")
                
                return bid_card_id
            else:
                print(f"[FAIL] JAA processing failed: {jaa_result.get('error', 'Unknown error')}")
        else:
            print("[FAIL] Could not save conversation")
            
    except Exception as e:
        print(f"[FAIL] Error creating bid card: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def test_created_bid_card(bid_card_id):
    """Test the created bid card via API"""
    print(f"\n=== TESTING CREATED BID CARD ===")
    
    import requests
    
    try:
        response = requests.get(f"http://localhost:8000/api/bid-cards/{bid_card_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Bid card API working!")
            print(f"Project: {data.get('project_type', 'N/A')}")
            print(f"Budget: {data.get('budget_display', 'N/A')}")
            print(f"Timeline: {data.get('timeline', 'N/A')}")
            print(f"Location: {data.get('location', {}).get('city', 'N/A')}")
            
            # Show full JSON for debugging
            print(f"\nFull bid card data:")
            print(json.dumps(data, indent=2))
            
            return True
        else:
            print(f"[FAIL] API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error testing: {e}")
        return False

def main():
    """Create and test bid card"""
    print("=" * 50)
    print("DIRECT BID CARD CREATION")
    print("=" * 50)
    
    # Create bid card
    bid_card_id = create_bid_card_directly()
    
    if bid_card_id:
        # Test it
        success = test_created_bid_card(bid_card_id)
        
        if success:
            print(f"\n[FINAL SUCCESS] Created working bid card: {bid_card_id}")
            print(f"API URL: http://localhost:8000/api/bid-cards/{bid_card_id}")
            return bid_card_id
    
    print("\n[FINAL FAIL] Could not create working bid card")
    return None

if __name__ == "__main__":
    main()