"""
Test the production API endpoints for Enhanced Campaign Orchestrator
"""
import requests
import json
import uuid
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8008"

def test_timing_calculation():
    """Test the timing calculation endpoint"""
    print("\n=== Testing Timing Calculation ===")
    
    data = {
        "bids_needed": 4,
        "timeline_hours": 6,  # Emergency timeline
        "tier1_available": 3,
        "tier2_available": 10,
        "tier3_available": 20,
        "project_type": "Emergency Plumbing",
        "location": {"city": "Denver", "state": "CO"}
    }
    
    response = requests.post(f"{BASE_URL}/api/timing/calculate", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("[SUCCESS] Timing calculation:")
        print(f"- Total contractors to contact: {result['total_contractors']}")
        print(f"- Expected responses: {result['expected_responses']}")
        print(f"- Confidence: {result['confidence']}%")
        print(f"- Urgency level: {result['urgency']}")
        return True
    else:
        print(f"[FAILED] Status: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_campaign_creation():
    """Test intelligent campaign creation"""
    print("\n=== Testing Campaign Creation ===")
    
    data = {
        "bid_card_id": str(uuid.uuid4()),
        "project_type": "Kitchen Remodel",
        "timeline_hours": 24,
        "urgency_level": "standard",
        "bids_needed": 4,
        "location": {"city": "Denver", "state": "CO"}
    }
    
    response = requests.post(f"{BASE_URL}/api/campaigns/create-intelligent", json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("[SUCCESS] Campaign created:")
            print(f"- Campaign ID: {result['campaign_id']}")
            print(f"- Total contractors: {result['total_contractors']}")
            return result['campaign_id']
        else:
            print(f"[FAILED] {result.get('error', 'Unknown error')}")
            return None
    else:
        print(f"[FAILED] Status: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def test_campaign_checkin(campaign_id):
    """Test campaign check-in endpoint"""
    print(f"\n=== Testing Campaign Check-in ===")
    
    response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}/check-in")
    
    if response.status_code == 200:
        result = response.json()
        print("[SUCCESS] Check-in status:")
        print(f"- Bids received: {result['bids_received']}")
        print(f"- Bids expected: {result['bids_expected']}")
        print(f"- On track: {result['on_track']}")
        print(f"- Escalation needed: {result['escalation_needed']}")
        return True
    else:
        print(f"[FAILED] Status: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_campaign_metrics(campaign_id):
    """Test campaign metrics endpoint"""
    print(f"\n=== Testing Campaign Metrics ===")
    
    response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}/metrics")
    
    if response.status_code == 200:
        result = response.json()
        print("[SUCCESS] Campaign metrics:")
        print(f"- Status: {result['status']}")
        print(f"- Total contractors: {result['metrics']['total_contractors']}")
        print(f"- Messages sent: {result['metrics']['messages_sent']}")
        print(f"- Response rate: {result['metrics']['response_rate']:.1f}%")
        return True
    else:
        print(f"[FAILED] Status: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_campaign_escalation(campaign_id):
    """Test campaign escalation endpoint"""
    print(f"\n=== Testing Campaign Escalation ===")
    
    data = {
        "additional_contractors": 3,
        "tier_preference": "tier2"
    }
    
    response = requests.post(f"{BASE_URL}/api/campaigns/{campaign_id}/escalate", json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("[SUCCESS] Campaign escalated:")
            print(f"- Contractors added: {result['contractors_added']}")
            print(f"- New total: {result['new_total']}")
        else:
            print(f"[WARNING] {result.get('error', 'Unknown error')}")
        return True
    else:
        print(f"[FAILED] Status: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def main():
    """Run all API tests"""
    print("Starting API endpoint tests...")
    print(f"Server: {BASE_URL}")
    print("="*60)
    
    # Test timing calculation
    timing_success = test_timing_calculation()
    
    # Test campaign creation (this might fail due to RLS)
    campaign_id = test_campaign_creation()
    
    if campaign_id:
        # Test other endpoints with the created campaign
        test_campaign_checkin(campaign_id)
        test_campaign_metrics(campaign_id)
        test_campaign_escalation(campaign_id)
    
    print("\n" + "="*60)
    print("API testing complete.")
    print("\nNOTE: If campaign creation failed with 'Invalid API key' or RLS error,")
    print("run the SQL script: 009_disable_rls_campaigns.sql in Supabase")

if __name__ == "__main__":
    main()