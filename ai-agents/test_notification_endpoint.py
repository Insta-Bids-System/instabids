#!/usr/bin/env python3
"""
Test JAA Endpoint with Contractor Notifications
Tests the integrated JAA + notification system via API
"""

import asyncio
import requests
import json
from config.service_urls import get_backend_url

async def test_jaa_endpoint_with_notifications():
    """Test JAA endpoint that should now include contractor notifications"""
    
    print("=" * 60)
    print("TESTING JAA ENDPOINT WITH CONTRACTOR NOTIFICATIONS")
    print("=" * 60)
    
    # Use a bid card that has contractor bids
    bid_card_id = "97775060-76ed-4735-afb9-39069d9f62fa"
    print(f"Testing bid card: {bid_card_id}")
    
    # Create update request
    update_request = {
        "budget_max": 75000,
        "description": "Updated project scope - adding premium materials and extended timeline",
        "urgency_level": "standard"
    }
    
    print("Update request:")
    print(json.dumps(update_request, indent=2))
    
    try:
        # Call JAA update endpoint
        response = requests.put(
            f"{get_backend_url()}/jaa/update/{bid_card_id}",
            json=update_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nJAA UPDATE RESULTS:")
            print(f"Success: {result.get('success')}")
            print(f"Update summary: {result.get('update_summary')}")
            print(f"Affected contractors: {result.get('affected_contractors')}")
            
            # NEW: Check contractor notification results
            contractor_notifications = result.get("contractor_notifications", {})
            print(f"\nCONTRACTOR NOTIFICATIONS:")
            print(f"Success: {contractor_notifications.get('success')}")
            print(f"Contractors notified: {contractor_notifications.get('contractors_notified', 0)}")
            
            engagement_breakdown = contractor_notifications.get("engagement_breakdown", {})
            if engagement_breakdown:
                print("Engagement breakdown:")
                for eng_type, count in engagement_breakdown.items():
                    print(f"  {eng_type}: {count}")
            
            if contractor_notifications.get("error"):
                print(f"Notification error: {contractor_notifications['error']}")
            
            return result.get("success") and contractor_notifications.get("contractors_notified", 0) > 0
            
        else:
            print(f"API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False


async def main():
    """Test the JAA endpoint with contractor notifications"""
    print("JAA + CONTRACTOR NOTIFICATION INTEGRATION TEST")
    print("=" * 60)
    
    success = await test_jaa_endpoint_with_notifications()
    
    if success:
        print("\n[SUCCESS] JAA endpoint with contractor notifications working!")
        print("System ready for production use:")
        print("- Bid card updates via JAA")
        print("- Automatic contractor notifications")
        print("- Engagement-based targeting")
    else:
        print("\n[FAILED] Integration needs debugging")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)