#!/usr/bin/env python3
"""Check detailed API response to understand data structure"""

import requests
import json

TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"

def check_api_detailed():
    print("=== CHECKING API DETAILED ===")
    try:
        response = requests.get(f'http://localhost:8008/api/bid-cards/homeowner/{TEST_USER_ID}', timeout=10)
        if response.ok:
            data = response.json()
            if not data:
                print("No bid cards returned")
                return
                
            # Get first bid card
            card = data[0]
            print(f"\nBid Card: {card.get('bid_card_number')}")
            print(f"Project Type: {card.get('project_type')}")
            
            # Check what fields are at the top level
            print(f"\n=== TOP LEVEL FIELDS ===")
            for key, value in card.items():
                print(f"{key}: {type(value).__name__}")
            
            # Check bid_document structure
            bid_document = card.get('bid_document', {})
            print(f"\n=== BID DOCUMENT STRUCTURE ===")
            for key, value in bid_document.items():
                print(f"{key}: {type(value).__name__}")
            
            # Check all_extracted_data
            all_extracted_data = bid_document.get('all_extracted_data', {})
            print(f"\n=== ALL EXTRACTED DATA FIELDS ({len(all_extracted_data)} total) ===")
            for key, value in all_extracted_data.items():
                print(f"{key}: {type(value).__name__}")
                if isinstance(value, list) and len(value) > 0:
                    print(f"  Sample: {str(value[0])[:100]}...")
                elif isinstance(value, dict):
                    print(f"  Keys: {list(value.keys())}")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"  Value: {value[:100]}...")
                else:
                    print(f"  Value: {value}")
                    
            # Check what's missing from frontend
            print(f"\n=== FIELDS NOT SHOWN IN CURRENT FRONTEND ===")
            current_frontend_fields = [
                'project_type', 'budget_min', 'budget_max', 'urgency_level', 
                'contractor_count_needed', 'location', 'project_details', 'photo_urls'
            ]
            
            missing_from_frontend = []
            for key in all_extracted_data.keys():
                if key not in current_frontend_fields:
                    missing_from_frontend.append(key)
                    value = all_extracted_data[key]
                    print(f"[MISSING] {key}: {type(value).__name__} - {str(value)[:100] if isinstance(value, str) else value}")
            
            print(f"\nSummary: {len(missing_from_frontend)} fields not displayed in current frontend")
            
        else:
            print(f'API error: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    check_api_detailed()