#!/usr/bin/env python3
"""
Test memory persistence with real backend API
"""
import asyncio
import os
import sys
import json
import requests
from datetime import datetime

sys.path.insert(0, os.path.abspath('.'))

async def test_backend_memory_integration():
    """Test COIA memory through backend API"""
    print("="*80)
    print("BACKEND API MEMORY INTEGRATION TEST")
    print("Testing memory persistence through localhost:8008 backend")
    print("="*80)
    
    # Use a unique contractor ID for this test
    test_contractor_id = f"backend_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    base_url = "http://localhost:8008/api/contractor/agent/coia/chat"
    
    try:
        # TEST 1: Create contractor profile
        print("\n[TEST 1] Creating contractor profile via backend API...")
        
        payload1 = {
            "message": "Hi! I'm BackendTest Electrical Services. We've been in business for 15 years in Portland, Oregon. We specialize in residential electrical work and solar panel installations.",
            "contractor_lead_id": test_contractor_id,
            "session_id": "backend_session_1"
        }
        
        response1 = requests.post(base_url, json=payload1)
        if response1.status_code != 200:
            print(f"Error: API returned {response1.status_code}")
            print(f"Response: {response1.text}")
            return False
            
        result1 = response1.json()
        print(f"Backend response: {result1.get('response', '')[:100]}...")
        
        # Extract profile from response
        profile1 = result1.get('metadata', {}).get('contractor_profile', {})
        print(f"Profile created:")
        print(f"  Company: {profile1.get('company_name')}")
        print(f"  Years: {profile1.get('years_in_business')}")
        print(f"  Trade: {profile1.get('primary_trade')}")
        
        # TEST 2: Memory recall
        print("\n[TEST 2] Testing memory recall via backend API...")
        
        payload2 = {
            "message": "What's my company name and how many years have we been in business?",
            "contractor_lead_id": test_contractor_id,
            "session_id": "backend_session_2"
        }
        
        response2 = requests.post(base_url, json=payload2)
        if response2.status_code != 200:
            print(f"Error: API returned {response2.status_code}")
            return False
            
        result2 = response2.json()
        profile2 = result2.get('metadata', {}).get('contractor_profile', {})
        
        print(f"Backend response: {result2.get('response', '')[:100]}...")
        print(f"Remembered profile:")
        print(f"  Company: {profile2.get('company_name')}")
        print(f"  Years: {profile2.get('years_in_business')}")
        print(f"  Trade: {profile2.get('primary_trade')}")
        
        # TEST 3: Add new information
        print("\n[TEST 3] Adding new information via backend API...")
        
        payload3 = {
            "message": "We also have 8 certified electricians on our team and we're available 24/7 for emergencies.",
            "contractor_lead_id": test_contractor_id,
            "session_id": "backend_session_3"
        }
        
        response3 = requests.post(base_url, json=payload3)
        if response3.status_code != 200:
            print(f"Error: API returned {response3.status_code}")
            return False
            
        result3 = response3.json()
        profile3 = result3.get('metadata', {}).get('contractor_profile', {})
        
        print(f"Enhanced profile:")
        print(f"  Company: {profile3.get('company_name')}")
        print(f"  Years: {profile3.get('years_in_business')}")
        print(f"  Team size: {profile3.get('team_size')}")
        print(f"  Availability: {profile3.get('availability')}")
        
        # TEST 4: Bid card search
        print("\n[TEST 4] Testing bid card search with persistent profile...")
        
        payload4 = {
            "message": "Show me electrical projects in Portland that match my expertise",
            "contractor_lead_id": test_contractor_id,
            "session_id": "backend_session_4"
        }
        
        response4 = requests.post(base_url, json=payload4)
        if response4.status_code != 200:
            print(f"Error: API returned {response4.status_code}")
            return False
            
        result4 = response4.json()
        bid_cards = result4.get('metadata', {}).get('bid_cards_attached', [])
        
        print(f"Bid cards found: {len(bid_cards)}")
        if bid_cards:
            print(f"Sample bid card: {bid_cards[0].get('title', 'N/A')}")
        
        # ANALYSIS
        print("\n" + "="*80)
        print("BACKEND INTEGRATION ANALYSIS")
        print("="*80)
        
        # Check profile persistence
        company_persistent = (
            profile1.get('company_name') and
            profile2.get('company_name') == profile1.get('company_name') and
            profile3.get('company_name') == profile1.get('company_name')
        )
        
        years_persistent = (
            profile1.get('years_in_business') and
            profile2.get('years_in_business') == profile1.get('years_in_business') and
            profile3.get('years_in_business') == profile1.get('years_in_business')
        )
        
        data_accumulation = len([v for v in profile3.values() if v]) >= len([v for v in profile1.values() if v])
        
        print(f"Company name persistence: {'PASS' if company_persistent else 'FAIL'}")
        print(f"Years persistence: {'PASS' if years_persistent else 'FAIL'}")
        print(f"Data accumulation: {'PASS' if data_accumulation else 'FAIL'}")
        print(f"Backend API integration: {'PASS' if response4.status_code == 200 else 'FAIL'}")
        
        overall_success = company_persistent and years_persistent and data_accumulation
        
        if overall_success:
            print("\n[SUCCESS] Backend API memory integration working!")
            print(f"Contractor ID: {test_contractor_id}")
        else:
            print("\n[FAILURE] Backend API memory integration has issues")
            
        return overall_success
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to backend at localhost:8008")
        print("Make sure the backend is running in Docker")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend_memory_integration())
    print(f"\nFINAL RESULT: {'SUCCESS' if success else 'FAILED'}")
    print("="*80)