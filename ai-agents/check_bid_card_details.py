#!/usr/bin/env python3
"""Check detailed bid card data to understand what fields are available"""

from database_simple import db
import json

TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"

def check_bid_card_details():
    print("=== CHECKING BID CARD DETAILS ===")
    
    # Get latest bid card for user (check for user_id field instead)
    bid_cards = db.client.table('bid_cards').select('*').eq('user_id', TEST_USER_ID).order('created_at', desc=True).limit(1).execute()
    
    if not bid_cards.data:
        print("No bid cards found")
        return
    
    card = bid_cards.data[0]
    print(f"\nBid Card: {card['bid_card_number']}")
    print(f"Project Type: {card['project_type']}")
    print(f"Budget: ${card['budget_min']:,} - ${card['budget_max']:,}")
    
    # Extract all data from bid_document
    bid_document = card.get('bid_document', {})
    all_extracted_data = bid_document.get('all_extracted_data', {})
    
    print(f"\n=== ALL EXTRACTED DATA FIELDS ===")
    for key, value in all_extracted_data.items():
        print(f"{key}: {type(value).__name__}")
        if isinstance(value, list) and len(value) > 0:
            print(f"  Sample: {value[0] if isinstance(value[0], str) else str(value[0])[:100]}")
        elif isinstance(value, dict):
            print(f"  Keys: {list(value.keys())}")
        elif isinstance(value, str) and len(value) > 100:
            print(f"  Value: {value[:100]}...")
        else:
            print(f"  Value: {value}")
    
    print(f"\n=== MISSING FIELDS IN CURRENT INTERFACE ===")
    # Fields that should be displayed but might not be
    important_fields = [
        'timeline', 'urgency_level', 'materials_specified', 'scope_of_work', 
        'special_requirements', 'accessibility_needs', 'permit_requirements',
        'contractor_preferences', 'project_description', 'images', 'location'
    ]
    
    missing_fields = []
    available_fields = []
    
    for field in important_fields:
        if field in all_extracted_data:
            available_fields.append(field)
            print(f"✅ {field}: {type(all_extracted_data[field]).__name__}")
        else:
            missing_fields.append(field)
            print(f"❌ {field}: Missing")
    
    print(f"\nSummary: {len(available_fields)}/{len(important_fields)} fields available")
    print(f"Total extracted fields: {len(all_extracted_data)}")

if __name__ == "__main__":
    check_bid_card_details()