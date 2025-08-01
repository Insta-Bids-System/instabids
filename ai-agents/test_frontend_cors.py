#!/usr/bin/env python3
"""Test frontend API call with CORS"""

import requests

def test_frontend_cors():
    print("=== TESTING FRONTEND CORS ISSUE ===")
    
    test_user_id = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"
    api_url = f"http://localhost:8008/api/bid-cards/homeowner/{test_user_id}"
    
    try:
        # Simulate frontend request with proper headers
        headers = {
            'Origin': 'http://localhost:5186',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        print(f"Testing API call: {api_url}")
        print(f"Origin: {headers['Origin']}")
        
        response = requests.get(api_url, headers=headers, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.ok:
            data = response.json()
            print(f"Success: {len(data)} bid cards returned")
            
            if data:
                card = data[0]
                print(f"First card: {card.get('bid_card_number')} - {card.get('project_type')}")
                
                # Check if images are included
                extracted = card.get('bid_document', {}).get('all_extracted_data', {})
                images = extracted.get('images', [])
                photo_urls = extracted.get('photo_urls', [])
                
                print(f"Images field: {len(images)} photos")
                print(f"Photo URLs field: {len(photo_urls)} photos")
                
                if images or photo_urls:
                    print("[SUCCESS] Images are included in API response")
                else:
                    print("[WARNING] No images in API response")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            if response.status_code == 403:
                print("[CORS ERROR] This is likely a CORS issue")
                
    except Exception as e:
        print(f"Request failed: {e}")
    
    print(f"\n=== FRONTEND TEST INSTRUCTIONS ===")
    print("1. Open browser to: http://localhost:5186")
    print("2. Login with: test.homeowner@instabids.com / testpass123")
    print("3. Check browser console (F12) for CORS or API errors")
    print("4. Look for bid cards on dashboard")

if __name__ == "__main__":
    test_frontend_cors()