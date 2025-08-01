#!/usr/bin/env python3
"""Check the actual bid_cards table structure"""

from database_simple import db

def check_bid_cards_table():
    print("=== CHECKING BID_CARDS TABLE STRUCTURE ===")
    
    try:
        # Get all bid cards to see the actual structure
        cards = db.client.table('bid_cards').select('*').limit(3).execute()
        
        if cards.data:
            print(f"Found {len(cards.data)} bid cards")
            first_card = cards.data[0]
            
            print(f"\n=== BID CARD FIELDS ===")
            for key, value in first_card.items():
                if isinstance(value, dict):
                    print(f"{key}: dict with {len(value)} keys")
                elif isinstance(value, list):
                    print(f"{key}: list with {len(value)} items")
                else:
                    print(f"{key}: {type(value).__name__} = {value}")
            
            # Look for user/homeowner reference fields
            user_fields = []
            for key in first_card.keys():
                if 'user' in key.lower() or 'owner' in key.lower() or 'created' in key.lower():
                    user_fields.append(key)
            
            print(f"\n=== POTENTIAL USER REFERENCE FIELDS ===")
            for field in user_fields:
                print(f"{field}: {first_card.get(field)}")
            
            # Check if any bid card belongs to our test user
            test_user_id = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"
            print(f"\n=== SEARCHING FOR TEST USER ID IN ALL FIELDS ===")
            found_match = False
            
            for card in cards.data:
                for key, value in card.items():
                    if str(value) == test_user_id:
                        print(f"[FOUND] Card {card.get('bid_card_number', 'unknown')} has test user ID in field '{key}'")
                        found_match = True
            
            if not found_match:
                print("[NOT FOUND] Test user ID not found in any bid card fields")
                print("This explains why frontend shows no bid cards!")
                
        else:
            print("No bid cards found in database")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_bid_cards_table()