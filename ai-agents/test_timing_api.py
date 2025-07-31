#!/usr/bin/env python3
"""
Test the timing API endpoints
"""
import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8008"

def test_timing_calculation():
    """Test the timing calculation endpoint"""
    print("=== Testing Timing Calculation Endpoint ===\n")
    
    # Test case 1: Emergency scenario (6 hours)
    print("Test 1: Emergency Plumbing (6 hours)")
    emergency_data = {
        "bids_needed": 4,
        "timeline_hours": 6,
        "tier1_available": 3,
        "tier2_available": 15,
        "tier3_available": 50,
        "project_type": "emergency plumbing"
    }
    
    response = requests.post(f"{BASE_URL}/api/timing/calculate", json=emergency_data)
    if response.status_code == 200:
        result = response.json()
        print(f"[SUCCESS]")
        print(f"   Total contractors: {result['total_contractors']}")
        print(f"   Expected responses: {result['expected_responses']}")
        print(f"   Confidence: {result['confidence']}%")
        print(f"   Urgency: {result['urgency']}")
        print(f"   Tier breakdown:")
        print(f"     - Tier 1: {result['tier_breakdown']['tier1']['to_contact']} contractors")
        print(f"     - Tier 2: {result['tier_breakdown']['tier2']['to_contact']} contractors")
        print(f"     - Tier 3: {result['tier_breakdown']['tier3']['to_contact']} contractors")
    else:
        print(f"[FAILED] {response.status_code} - {response.text}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test case 2: Standard scenario (24 hours)
    print("Test 2: Kitchen Remodel (24 hours)")
    standard_data = {
        "bids_needed": 4,
        "timeline_hours": 24,
        "tier1_available": 5,
        "tier2_available": 20,
        "tier3_available": 100,
        "project_type": "kitchen remodel"
    }
    
    response = requests.post(f"{BASE_URL}/api/timing/calculate", json=standard_data)
    if response.status_code == 200:
        result = response.json()
        print(f"[SUCCESS]")
        print(f"   Total contractors: {result['total_contractors']}")
        print(f"   Expected responses: {result['expected_responses']}")
        print(f"   Confidence: {result['confidence']}%")
        print(f"   Check-in times: {len(result['check_in_times'])} scheduled")
        if result['recommendations']:
            print(f"   Recommendations:")
            for rec in result['recommendations']:
                print(f"     - {rec}")
    else:
        print(f"[FAILED] {response.status_code} - {response.text}")

def test_campaign_creation():
    """Test the intelligent campaign creation endpoint"""
    print("\n=== Testing Campaign Creation Endpoint ===\n")
    
    # Use a valid UUID for testing
    import uuid
    test_bid_card_id = str(uuid.uuid4())
    
    campaign_data = {
        "bid_card_id": test_bid_card_id,
        "project_type": "Kitchen Remodel",
        "timeline_hours": 24,
        "urgency_level": "urgent",
        "bids_needed": 4,
        "location": {
            "city": "Austin",
            "state": "TX",
            "zip": "78701"
        }
    }
    
    print(f"Creating campaign for: {campaign_data['project_type']}")
    print(f"Timeline: {campaign_data['timeline_hours']} hours")
    
    response = requests.post(f"{BASE_URL}/api/campaigns/create-intelligent", json=campaign_data)
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"[SUCCESS] Campaign created!")
            print(f"   Campaign ID: {result.get('campaign_id', 'N/A')}")
            print(f"   Total contractors: {result.get('total_contractors', 'N/A')}")
        else:
            print(f"[FAILED] Campaign creation: {result.get('error', 'Unknown error')}")
    else:
        print(f"[FAILED] {response.status_code} - {response.text}")

def test_campaign_checkin():
    """Test the campaign check-in endpoint"""
    print("\n=== Testing Campaign Check-in Endpoint ===\n")
    
    # Use a valid UUID for test campaign ID
    import uuid
    campaign_id = str(uuid.uuid4())
    
    print(f"Checking status for campaign: {campaign_id}")
    
    response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}/check-in")
    if response.status_code == 200:
        result = response.json()
        print(f"[SUCCESS] Check-in complete!")
        print(f"   Bids received: {result['bids_received']}")
        print(f"   Bids expected: {result['bids_expected']}")
        print(f"   On track: {'Yes' if result['on_track'] else 'No'}")
        print(f"   Escalation needed: {'Yes' if result['escalation_needed'] else 'No'}")
        if result['escalation_needed']:
            print(f"   Additional contractors needed:")
            for tier, count in result['additional_contractors_needed'].items():
                print(f"     - {tier}: {count}")
    else:
        print(f"[FAILED] {response.status_code} - {response.text}")

def main():
    print("INSTABIDS TIMING API TEST")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run tests
    test_timing_calculation()
    test_campaign_creation()
    test_campaign_checkin()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()