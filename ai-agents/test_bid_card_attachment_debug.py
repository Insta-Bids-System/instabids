"""
Bid Card Attachment Debug Test
=============================

Test if COIA is actually returning bid card data in the response
and if the frontend ChatBidCard component should be displaying them.
"""

import requests
import json
from config.service_urls import get_backend_url

BACKEND_URL = get_backend_url()

def test_bid_card_attachment():
    """Test if bid cards are being attached to COIA responses"""
    
    print("BID CARD ATTACHMENT DEBUG TEST")
    print("=" * 50)
    
    # Generate unique session
    import uuid
    contractor_lead_id = f"landing-{str(uuid.uuid4())[:8]}"
    print(f"Using contractor_lead_id: {contractor_lead_id}")
    
    # Stage 1: Setup contractor
    print("\nSTAGE 1: Setup Contractor Profile")
    print("-" * 40)
    
    stage1_data = {
        "message": "Hi, I'm John from TurfGrass Artificial Solutions in Miami. We do artificial grass and landscape design. I'd like to join your platform.",
        "session_id": contractor_lead_id,
        "contractor_lead_id": contractor_lead_id
    }
    
    response1 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage1_data)
    if response1.status_code != 200:
        print(f"Stage 1 failed: {response1.status_code}")
        return False
        
    print("[SUCCESS] Profile setup complete")
    
    # Stage 2: Request bid cards specifically
    print("\nSTAGE 2: Request Bid Cards with Debug")
    print("-" * 40)
    
    stage2_data = {
        "message": "Show me available projects I can bid on. I want to see bid cards.",
        "session_id": contractor_lead_id,
        "contractor_lead_id": contractor_lead_id
    }
    
    print("Requesting bid cards...")
    response2 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage2_data)
    
    if response2.status_code != 200:
        print(f"Stage 2 failed: {response2.status_code}")
        return False
    
    # Parse the full response
    result = response2.json()
    
    print("\n[ANALYSIS] FULL API RESPONSE:")
    print(f"Status: {result.get('success')}")
    print(f"Mode: {result.get('current_mode')}")
    print(f"Response text length: {len(result.get('response', ''))}")
    
    # Check if bid_cards are in the response
    bid_cards = result.get('bid_cards')
    
    if bid_cards is None:
        print("[ERROR] NO 'bid_cards' field in response")
    elif bid_cards == []:
        print("[WARNING] 'bid_cards' field exists but is EMPTY")
    else:
        print(f"[SUCCESS] 'bid_cards' field contains {len(bid_cards)} cards")
        
        # Analyze first bid card structure
        if len(bid_cards) > 0:
            first_card = bid_cards[0]
            print(f"\n[CARD] FIRST BID CARD STRUCTURE:")
            print(f"   ID: {first_card.get('id')}")
            print(f"   Title: {first_card.get('title')}")
            print(f"   Budget: ${first_card.get('budget_min')} - ${first_card.get('budget_max')}")
            print(f"   Location: {first_card.get('location_city')}, {first_card.get('location_state')}")
            print(f"   Timeline: {first_card.get('timeline')}")
            print(f"   Status: {first_card.get('status')}")
            
            # Check all required fields for ChatBidCard component
            required_fields = [
                'id', 'bid_card_number', 'title', 'description', 'project_type',
                'location_city', 'location_state', 'budget_min', 'budget_max'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in first_card or first_card[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"[ERROR] MISSING REQUIRED FIELDS: {missing_fields}")
            else:
                print("[SUCCESS] ALL REQUIRED FIELDS PRESENT")
    
    # Check response for bid card references
    response_text = result.get('response', '').lower()
    bid_card_mentions = [
        'project' in response_text,
        'bid' in response_text,
        'budget' in response_text,
        'timeline' in response_text,
        'location' in response_text
    ]
    
    print(f"\n[TEXT] RESPONSE ANALYSIS:")
    print(f"   Mentions projects: {'YES' if bid_card_mentions[0] else 'NO'}")
    print(f"   Mentions bidding: {'YES' if bid_card_mentions[1] else 'NO'}")
    print(f"   Mentions budget: {'YES' if bid_card_mentions[2] else 'NO'}")
    print(f"   Mentions timeline: {'YES' if bid_card_mentions[3] else 'NO'}")
    print(f"   Mentions location: {'YES' if bid_card_mentions[4] else 'NO'}")
    
    # Final diagnosis
    print(f"\n[DIAGNOSIS] RESULTS:")
    
    if bid_cards and len(bid_cards) > 0:
        print("[SUCCESS] Backend IS returning bid card data")
        print("[SUCCESS] ChatBidCard component should be able to display them")
        print("[ISSUE] Frontend might not be using the ChatBidCard component")
    elif bid_cards == []:
        print("[WARNING] Backend is trying to return bid cards but database is empty")
        print("[ISSUE] No bid cards in database OR search criteria not matching")
    else:
        print("[ERROR] Backend is NOT returning bid card data")
        print("[ISSUE] COIA flow not reaching bid_card_search mode")
    
    # Check if the actual issue is in the UI implementation
    print(f"\n[UI] IMPLEMENTATION CHECK:")
    print("Frontend should be:")
    print("1. Reading the 'bid_cards' field from API response")
    print("2. Passing bid_cards to ChatBidCardAttachment component")
    print("3. Displaying cards with budget, timeline, location data")
    
    return bid_cards is not None

if __name__ == "__main__":
    success = test_bid_card_attachment()
    exit(0 if success else 1)