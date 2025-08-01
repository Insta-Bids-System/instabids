#!/usr/bin/env python3
"""
Manual Campaign Trigger - Test Complete Flow
Triggers a campaign for our Miami lawn care bid card and traces the complete execution
"""

import requests
import json
import time
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:8009"
BID_CARD_ID = "769961f6-84f8-460f-a320-4d942c66d3c4"  # Our test Miami lawn care bid card
TEST_EMAIL = "nextlevelpressurewashing@gmail.com"

def trigger_campaign():
    """Trigger the intelligent campaign system"""
    
    print("MANUAL CAMPAIGN TRIGGER TEST")
    print("=" * 50)
    print(f"Bid Card ID: {BID_CARD_ID}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Campaign request data
    campaign_data = {
        'bid_card_id': BID_CARD_ID,
        'project_type': 'lawn_care',
        'location': {
            'city': 'Miami', 
            'state': 'FL', 
            'zip_codes': ['33101', '33102', '33103', '33125', '33126']
        },
        'timeline_hours': 48,  # 2 days
        'urgency_level': 'standard',
        'bids_needed': 4,
        'channels': ['email', 'website_form']  # Test both channels
    }
    
    print("CAMPAIGN REQUEST:")
    print(json.dumps(campaign_data, indent=2))
    print()
    
    try:
        print("Sending request to campaign API...")
        response = requests.post(
            f"{SERVER_URL}/api/campaigns/create-intelligent",
            json=campaign_data,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("CAMPAIGN CREATED SUCCESSFULLY!")
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                campaign_id = result.get('campaign_id')
                print(f"\nCampaign ID: {campaign_id}")
                print(f"Total Contractors: {result.get('total_contractors', 'Unknown')}")
                
                # Get campaign details
                print(f"\nCampaign Strategy:")
                strategy = result.get('strategy', {})
                if strategy:
                    print(f"- Tier 1 (Internal): {strategy.get('tier_1_contractors', 0)}")
                    print(f"- Tier 2 (Previous): {strategy.get('tier_2_contractors', 0)}")
                    print(f"- Tier 3 (Cold): {strategy.get('tier_3_contractors', 0)}")
                    print(f"- Expected Response Rate: {strategy.get('expected_responses', 'N/A')}")
                    print(f"- Confidence: {strategy.get('confidence_percentage', 'N/A')}%")
                
                return campaign_id
            else:
                print(f"Campaign failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def check_campaign_status(campaign_id):
    """Check the status of the campaign"""
    if not campaign_id:
        return
        
    print(f"\nCHECKING CAMPAIGN STATUS")
    print("=" * 30)
    
    try:
        # Check campaign status
        response = requests.get(f"{SERVER_URL}/api/campaigns/{campaign_id}/status")
        
        if response.status_code == 200:
            status = response.json()
            print("Campaign Status:")
            print(json.dumps(status, indent=2))
        else:
            print(f"Failed to get status: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Status check failed: {e}")

def check_website_submissions():
    """Instructions for checking website form submissions"""
    print(f"\nWEBSITE FORM TESTING")
    print("=" * 30)
    print("To check if website forms are being filled:")
    print(f"1. Open: C:\\Users\\Not John Or Justin\\Documents\\instabids\\test-sites\\lawn-care-contractor\\index.html")
    print("2. Look at the 'Form Submissions (For Testing)' panel at the bottom")
    print("3. Check for new submissions with our test data")
    print(f"4. All submissions should use email: {TEST_EMAIL}")

def main():
    """Run the complete manual campaign test"""
    print("INSTABIDS MANUAL CAMPAIGN TEST")
    print("=" * 60)
    
    # Step 1: Trigger the campaign
    campaign_id = trigger_campaign()
    
    if campaign_id:
        # Step 2: Wait a moment for processing
        print(f"\nWaiting 5 seconds for campaign processing...")
        time.sleep(5)
        
        # Step 3: Check campaign status
        check_campaign_status(campaign_id)
        
        # Step 4: Instructions for manual verification
        check_website_submissions()
        
        print(f"\nMANUAL CAMPAIGN TRIGGER COMPLETE")
        print(f"Campaign ID: {campaign_id}")
        print("Check the above sources to verify campaign execution!")
        
    else:
        print(f"\nCAMPAIGN TRIGGER FAILED")
        print("Check server logs and fix issues before retrying")

if __name__ == "__main__":
    main()