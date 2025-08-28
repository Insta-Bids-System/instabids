"""
Test bid card search with specific location and project type
=============================================================

We know the database has:
- holiday lighting projects
- Projects in Florida (Miami, Fort Lauderdale, etc.)

Let's test with a contractor that matches these.
"""

import requests
import json
import uuid
from config.service_urls import get_backend_url

BACKEND_URL = get_backend_url()

def test_bid_card_search():
    """Test with contractor that should match existing bid cards"""
    
    print("BID CARD SEARCH FIX TEST")
    print("=" * 50)
    
    contractor_lead_id = f"landing-{str(uuid.uuid4())[:8]}"
    print(f"Session: {contractor_lead_id}")
    
    # Stage 1: Contractor with Miami location and holiday lighting specialty
    print("\n[1] SETUP: Miami contractor specializing in holiday lighting")
    print("-" * 50)
    
    stage1_data = {
        "message": "Hi, I'm Mike from Holiday Lights Miami. We specialize in holiday lighting installation and electrical work. We're based in Miami, Florida and service a 30 mile radius including Fort Lauderdale, West Palm Beach, and Coral Springs. We've been doing holiday decorations for 10 years.",
        "session_id": contractor_lead_id,
        "contractor_lead_id": contractor_lead_id
    }
    
    response1 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage1_data)
    if response1.status_code != 200:
        print(f"Setup failed: {response1.status_code}")
        return False
    
    result1 = response1.json()
    print(f"Mode: {result1.get('current_mode')}")
    
    # Check what was extracted
    response_text = result1.get('response', '').lower()
    print("\nExtracted from conversation:")
    print(f"  Miami mentioned: {'miami' in response_text}")
    print(f"  Holiday lighting mentioned: {'holiday' in response_text}")
    print(f"  30 mile radius mentioned: {'30' in response_text}")
    
    # Stage 2: Explicitly ask for bid cards in the area
    print("\n[2] SEARCH: Request bid cards with location emphasis")
    print("-" * 50)
    
    stage2_data = {
        "message": "Great! Now show me available holiday lighting projects and electrical work in my area. I'm in Miami and can travel up to 30 miles. Looking for projects I can bid on.",
        "session_id": contractor_lead_id,
        "contractor_lead_id": contractor_lead_id
    }
    
    response2 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage2_data)
    if response2.status_code != 200:
        print(f"Search failed: {response2.status_code}")
        return False
    
    result2 = response2.json()
    
    print(f"Mode: {result2.get('current_mode')}")
    print(f"Success: {result2.get('success')}")
    
    # Check bid cards field
    bid_cards = result2.get('bidCards')
    
    if bid_cards is None:
        print("\n[ERROR] 'bidCards' field not in response")
    elif bid_cards == []:
        print("\n[WARNING] 'bidCards' field exists but is EMPTY")
        
        # Debug: Check what search criteria was used
        print("\nDEBUG: Checking backend logs for search criteria...")
        
    else:
        print(f"\n[SUCCESS] Found {len(bid_cards)} bid cards!")
        
        # Display first few cards
        for i, card in enumerate(bid_cards[:3], 1):
            print(f"\nCard {i}:")
            print(f"  Title: {card.get('title')}")
            print(f"  Type: {card.get('project_type')}")
            print(f"  Location: {card.get('location_city')}, {card.get('location_state')}")
            print(f"  Budget: ${card.get('budget_min')} - ${card.get('budget_max')}")
    
    # Stage 3: Try more generic search
    if not bid_cards:
        print("\n[3] FALLBACK: Try more generic search")
        print("-" * 50)
        
        stage3_data = {
            "message": "Show me all available projects in Florida that need electrical work or installation services.",
            "session_id": contractor_lead_id,
            "contractor_lead_id": contractor_lead_id
        }
        
        response3 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage3_data)
        result3 = response3.json()
        
        bid_cards_fallback = result3.get('bidCards')
        
        if bid_cards_fallback and len(bid_cards_fallback) > 0:
            print(f"[SUCCESS] Fallback search found {len(bid_cards_fallback)} cards")
            for i, card in enumerate(bid_cards_fallback[:3], 1):
                print(f"\nCard {i}:")
                print(f"  Type: {card.get('project_type')}")
                print(f"  Location: {card.get('location_city')}, {card.get('location_state')}")
        else:
            print("[ERROR] Still no bid cards found")
    
    # Final diagnosis
    print("\n" + "=" * 50)
    print("DIAGNOSIS:")
    
    if bid_cards and len(bid_cards) > 0:
        print("[SUCCESS] Bid card search is working!")
        print("ChatBidCardAttachment component can display these")
        return True
    else:
        print("[ISSUE] Search criteria not matching database records")
        print("\nPossible issues:")
        print("1. Location extraction not working (Miami not being used)")
        print("2. Project type not matching (holiday lighting vs 'holiday lighting')")
        print("3. Radius search not implemented in search function")
        print("4. Search defaulting to wrong criteria")
        return False

if __name__ == "__main__":
    success = test_bid_card_search()
    exit(0 if success else 1)