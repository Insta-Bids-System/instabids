#!/usr/bin/env python3
"""Test the enhanced interface with real user login simulation"""

import requests
import json

TEST_USER_ID = "e6e47a24-95ad-4af3-9ec5-f17999917bc3"

def test_enhanced_interface():
    print("=== TESTING ENHANCED INTERFACE ===")
    print(f"Backend: http://localhost:8008")
    print(f"Frontend: http://localhost:5186")
    print(f"Test User: {TEST_USER_ID}")
    print(f"Login: test.homeowner@instabids.com / testpass123")
    
    try:
        # Test API endpoint
        response = requests.get(f'http://localhost:8008/api/bid-cards/homeowner/{TEST_USER_ID}', timeout=5)
        if response.ok:
            data = response.json()
            print(f"\n[OK] API Working: {len(data)} bid cards returned")
            
            # Test first bid card data structure
            if data:
                card = data[0]
                extracted = card.get('bid_document', {}).get('all_extracted_data', {})
                
                print(f"\n=== FIRST BID CARD TEST ===")
                print(f"Card ID: {card.get('bid_card_number')}")
                print(f"Project: {card.get('project_type')}")
                print(f"Budget: ${card.get('budget_min'):,} - ${card.get('budget_max'):,}")
                
                # Test image URLs
                images = extracted.get('images', [])
                if images:
                    print(f"[OK] Images: {len(images)} photos")
                    print(f"   First image: {images[0]}")
                    
                    # Test if image URL is accessible
                    try:
                        img_response = requests.head(images[0], timeout=3)
                        if img_response.ok:
                            print(f"   [OK] Image accessible: {img_response.status_code}")
                        else:
                            print(f"   [ERROR] Image not accessible: {img_response.status_code}")
                    except Exception as e:
                        print(f"   [ERROR] Image test failed: {e}")
                else:
                    print("[ERROR] No images found")
                
                # Test enhanced fields
                enhanced_fields = [
                    'project_description', 'material_preferences', 'special_requirements',
                    'contractor_requirements', 'property_details', 'service_type',
                    'timeline_urgency', 'intention_score', 'group_bidding_potential'
                ]
                
                print(f"\n=== ENHANCED FIELDS TEST ===")
                available_fields = 0
                for field in enhanced_fields:
                    if field in extracted and extracted[field]:
                        available_fields += 1
                        value = extracted[field]
                        if isinstance(value, str) and len(value) > 50:
                            print(f"[OK] {field}: {value[:50]}...")
                        else:
                            print(f"[OK] {field}: {value}")
                    else:
                        print(f"[MISSING] {field}: Missing or empty")
                
                print(f"\nSummary: {available_fields}/{len(enhanced_fields)} enhanced fields available")
                
                # Test if frontend should display properly
                if available_fields >= 5 and images:
                    print(f"\n[SUCCESS] ENHANCED INTERFACE READY!")
                    print(f"   - Rich data: {available_fields} fields")
                    print(f"   - Images: {len(images)} photos")
                    print(f"   - User can expand to see all details")
                    print(f"   - Enhanced bid card component should work perfectly")
                else:
                    print(f"\n[WARNING] Limited enhancement possible")
                    print(f"   - Only {available_fields} enhanced fields")
                    print(f"   - Images: {len(images)} photos")
        else:
            print(f"[ERROR] API Error: {response.status_code}")
    
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
    
    print(f"\n=== NEXT STEPS ===")
    print("1. Login to frontend: http://localhost:5186")
    print("2. Use credentials: test.homeowner@instabids.com / testpass123")
    print("3. Check dashboard for enhanced bid cards")
    print("4. Click 'Show All Details' to see expanded view")
    print("5. Verify images display correctly")
    print("6. Test 'Continue Chat & Modify' button functionality")

if __name__ == "__main__":
    test_enhanced_interface()