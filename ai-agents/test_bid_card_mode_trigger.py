"""
Test bid card search mode triggering
"""

import requests
import json
import uuid
from config.service_urls import get_backend_url

BACKEND_URL = get_backend_url()

def test_mode_triggers():
    """Test different phrases to trigger bid_card_search mode"""
    
    print("BID CARD MODE TRIGGER TEST")
    print("=" * 50)
    
    # Test phrases that should trigger bid_card_search mode
    test_phrases = [
        "find projects",
        "show projects", 
        "opportunities",
        "bid on",
        "Show me projects I can bid on",
        "Find projects for me",
        "What opportunities are available?"
    ]
    
    for phrase in test_phrases:
        print(f"\nTesting: '{phrase}'")
        print("-" * 40)
        
        contractor_lead_id = f"landing-{str(uuid.uuid4())[:8]}"
        
        # Setup
        setup_data = {
            "message": "Hi, I'm a contractor in Miami",
            "session_id": contractor_lead_id,
            "contractor_lead_id": contractor_lead_id
        }
        requests.post(f"{BACKEND_URL}/api/coia/landing", json=setup_data)
        
        # Test phrase
        test_data = {
            "message": phrase,
            "session_id": contractor_lead_id,
            "contractor_lead_id": contractor_lead_id
        }
        
        response = requests.post(f"{BACKEND_URL}/api/coia/landing", json=test_data)
        result = response.json()
        
        mode = result.get('current_mode')
        bid_cards = result.get('bidCards')
        
        print(f"  Mode: {mode}")
        print(f"  bidCards field: {'Present' if 'bidCards' in result else 'Missing'}")
        
        if mode == 'bid_card_search':
            print("  [SUCCESS] Triggered bid_card_search mode!")
            if bid_cards:
                print(f"  [SUCCESS] Got {len(bid_cards)} bid cards")
            else:
                print("  [WARNING] Mode correct but no cards returned")
        else:
            print(f"  [FAIL] Got {mode} mode instead")

if __name__ == "__main__":
    test_mode_triggers()