#!/usr/bin/env python3
"""
Test script to check current admin API response structure
This will help us understand what the running backend is actually returning
"""

import requests
import json
from datetime import datetime

def test_admin_session():
    """Test admin login to get a valid session"""
    try:
        login_url = "http://localhost:8008/api/admin/login"
        login_data = {
            "email": "admin@instabids.com",
            "password": "admin123"
        }
        
        print("Testing admin login...")
        response = requests.post(login_url, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                session_id = data["session"]["session_id"]
                print(f"Login successful! Session ID: {session_id[:20]}...")
                return session_id
            else:
                print(f"Login failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"Login request failed: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Login error: {e}")
    
    return None

def test_bid_cards_api(session_id):
    """Test the bid cards API to see current response structure"""
    try:
        url = "http://localhost:8008/api/admin/bid-cards"
        headers = {"Authorization": f"Bearer {session_id}"}
        
        print(f"\nTesting bid cards API...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            bid_cards = data.get("bid_cards", [])
            
            print(f"API call successful!")
            print(f"Total bid cards returned: {len(bid_cards)}")
            
            if bid_cards:
                # Check first bid card structure
                first_card = bid_cards[0]
                print(f"\nFirst bid card structure:")
                print(f"   ID: {first_card.get('id', 'MISSING')}")
                print(f"   Number: {first_card.get('bid_card_number', 'MISSING')}")
                print(f"   Status: {first_card.get('status', 'MISSING')}")
                print(f"   Progress Field: {first_card.get('progress', 'MISSING')}")
                print(f"   Bids Received Field: {first_card.get('bids_received', 'MISSING')}")
                print(f"   Progress Percentage Field: {first_card.get('progress_percentage', 'MISSING')}")
                print(f"   Target Bids Field: {first_card.get('target_bids', 'MISSING')}")
                print(f"   Contractor Count Needed: {first_card.get('contractor_count_needed', 'MISSING')}")
                print(f"   Urgency Level: {first_card.get('urgency_level', 'MISSING')}")
                
                # Check for problematic values
                progress_percentage = first_card.get('progress_percentage')
                if progress_percentage and progress_percentage > 100:
                    print(f"ISSUE FOUND: Progress percentage is {progress_percentage}% (over 100%)")
                
                urgency = first_card.get('urgency_level')
                if not urgency or urgency == 'flexible':
                    print(f"ISSUE FOUND: Urgency level is '{urgency}' (should be emergency/urgent/week/month)")
                    
                # Check if we have the old field names vs new field names
                if 'progress' in first_card and 'bids_received' not in first_card:
                    print(f"CONFIRMED: API still using OLD field names (progress, target_bids)")
                    print(f"NEED: Switch to NEW field names (bids_received, progress_percentage)")
                elif 'bids_received' in first_card:
                    print(f"CONFIRMED: API using NEW field names (bids_received, progress_percentage)")
                
                print(f"\nSample bid card details:")
                for key, value in first_card.items():
                    print(f"   {key}: {value}")
                    
            else:
                print("No bid cards returned")
                
        else:
            print(f"API call failed: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"API test error: {e}")

def main():
    print("Testing current admin API response structure...")
    print(f"Test time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Get admin session
    session_id = test_admin_session()
    
    if session_id:
        # Test bid cards API
        test_bid_cards_api(session_id)
    else:
        print("Cannot test bid cards API without valid session")
    
    print("\n" + "=" * 60)
    print("Test completed")

if __name__ == "__main__":
    main()