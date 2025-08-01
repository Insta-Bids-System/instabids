#!/usr/bin/env python3
"""Check API vs database for bid cards"""

import requests
from database_simple import db

TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"

def check_api():
    print("=== CHECKING API ===")
    try:
        response = requests.get(f'http://localhost:8008/api/bid-cards/homeowner/{TEST_USER_ID}', timeout=5)
        if response.ok:
            data = response.json()
            print(f'API returned {len(data)} bid cards')
            for card in data:
                print(f'  - {card["bid_card_number"]}: {card["project_type"]} (${card["budget_min"]:,}-${card["budget_max"]:,})')
                
                # Check photos
                bid_doc = card.get('bid_document', {})
                extracted = bid_doc.get('all_extracted_data', {})
                images = extracted.get('images', [])
                if images:
                    print(f'    Photos: {len(images)} - {images[0][:60]}...')
        else:
            print(f'API error: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'Error: {e}')

def check_database():
    print('\n=== CHECKING DATABASE ===')
    bid_cards = db.client.table('bid_cards').select('*').order('created_at', desc=True).limit(10).execute()
    print(f'Database has {len(bid_cards.data)} total bid cards')

    recent_kitchen_cards = [c for c in bid_cards.data if c['project_type'] == 'kitchen remodel']
    print(f'Recent kitchen remodel cards: {len(recent_kitchen_cards)}')

    for card in recent_kitchen_cards[:3]:
        print(f'  - {card["bid_card_number"]}: Budget ${card["budget_min"]}-${card["budget_max"]}')
        images = card.get('bid_document', {}).get('all_extracted_data', {}).get('images', [])
        print(f'    Photos: {len(images)}')
        if images:
            print(f'    First photo: {images[0][:60]}...')

if __name__ == "__main__":
    check_api()
    check_database()