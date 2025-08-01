#!/usr/bin/env python3
"""Test dashboard API directly"""

import requests
import json
from database_simple import db

TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"

def test_direct_database():
    """Test direct database access for dashboard data"""
    print("=== DIRECT DATABASE TEST ===")
    
    # Get bid cards directly from database
    bid_cards = db.client.table('bid_cards').select('*').order('created_at', desc=True).limit(5).execute()
    
    if bid_cards.data:
        print(f"Found {len(bid_cards.data)} bid cards in database")
        
        for card in bid_cards.data:
            print(f"\nBid Card: {card['bid_card_number']}")
            print(f"  Type: {card['project_type']}")
            print(f"  Budget: ${card['budget_min']:,} - ${card['budget_max']:,}")
            
            # Check bid_document structure
            if card.get('bid_document'):
                bid_doc = card['bid_document']
                print(f"  Bid document keys: {list(bid_doc.keys())}")
                
                if 'all_extracted_data' in bid_doc:
                    extracted = bid_doc['all_extracted_data']
                    print(f"  Extracted data keys: {list(extracted.keys())}")
                    
                    # Check for images
                    images = extracted.get('images', [])
                    photo_urls = extracted.get('photo_urls', [])
                    
                    print(f"  Images field: {len(images) if images else 0}")
                    print(f"  Photo URLs field: {len(photo_urls) if photo_urls else 0}")
                    
                    if images:
                        print(f"  First image: {images[0][:60]}...")
                    if photo_urls:
                        print(f"  First photo URL: {photo_urls[0][:60]}...")
                        
                    # Check location data
                    location = extracted.get('location', {})
                    if location:
                        print(f"  Location: {location}")
    else:
        print("No bid cards found")

def test_api_endpoint():
    """Test API endpoint if server is running"""
    print("\n=== API ENDPOINT TEST ===")
    
    try:
        response = requests.get(f"http://localhost:8008/api/bid-cards/homeowner/{TEST_USER_ID}", timeout=10)
        
        print(f"API Status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"API returned {len(data)} bid cards")
            
            if data:
                first_card = data[0]
                print(f"\nFirst card: {first_card['bid_card_number']}")
                
                # Check if photo_urls field exists for frontend
                bid_doc = first_card.get('bid_document', {})
                extracted = bid_doc.get('all_extracted_data', {})
                
                if 'photo_urls' in extracted:
                    print("[OK] photo_urls field exists (frontend compatible)")
                    print(f"Photo URLs count: {len(extracted['photo_urls'])}")
                elif 'images' in extracted:
                    print("[WARNING] Only 'images' field exists - needs mapping to 'photo_urls'")
                    print(f"Images count: {len(extracted['images'])}")
                else:
                    print("[ERROR] No photo fields found")
        else:
            print(f"API Error: {response.text}")
            
    except requests.exceptions.ConnectError:
        print("Server not running at localhost:8008")
    except requests.exceptions.Timeout:
        print("API request timed out")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    test_direct_database()
    test_api_endpoint()