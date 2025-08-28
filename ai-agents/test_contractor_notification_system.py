#!/usr/bin/env python3
"""
Test Contractor Notification System
Tests the new bid card change notification system with real data
"""

import asyncio
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.bid_card_change_notification_service import (
    BidCardChangeNotificationService,
    notify_contractors_of_bid_card_change,
    test_engagement_detection
)
from database import SupabaseDB
db = SupabaseDB()


async def test_engagement_detection_real_data():
    """Test engagement detection with real bid cards that have bids"""
    print("=" * 60)
    print("TESTING ENGAGEMENT DETECTION WITH REAL DATA")
    print("=" * 60)
    
    # Get bid cards with actual bids
    bid_result = db.client.table("contractor_bids").select("bid_card_id, contractor_id, amount").execute()
    
    if not bid_result.data:
        print("No bid data found - need to test with real data")
        return False
    
    # Test with the first bid card that has bids
    test_bid_card_id = bid_result.data[0]["bid_card_id"]
    print(f"Testing with bid card: {test_bid_card_id}")
    
    # Show raw bid data for this card
    card_bids = [bid for bid in bid_result.data if bid["bid_card_id"] == test_bid_card_id]
    print(f"Raw bids for this card: {len(card_bids)}")
    for bid in card_bids:
        print(f"  - Contractor {bid['contractor_id']}: ${float(bid['amount']):,.2f}")
    
    # Test engagement detection
    engagement_result = await test_engagement_detection(test_bid_card_id)
    
    print("\nENGAGEMENT DETECTION RESULTS:")
    print(f"Total engaged contractors: {engagement_result['total_engaged_contractors']}")
    
    for contractor in engagement_result["engagement_breakdown"]:
        print(f"\nContractor ID: {contractor['contractor_id']}")
        print(f"Engagement types: {contractor['engagement_types']}")
        
        for eng_type, data in contractor["engagement_data"].items():
            print(f"  {eng_type}: {data}")
    
    return engagement_result["total_engaged_contractors"] > 0


async def test_notification_system():
    """Test the actual notification system"""
    print("=" * 60) 
    print("TESTING NOTIFICATION SYSTEM")
    print("=" * 60)
    
    # Get a bid card with bids for testing
    bid_result = db.client.table("contractor_bids").select("bid_card_id").execute()
    
    if not bid_result.data:
        print("No bid data for testing")
        return False
    
    test_bid_card_id = bid_result.data[0]["bid_card_id"]
    print(f"Testing notifications for bid card: {test_bid_card_id}")
    
    # Test notification
    notification_result = await notify_contractors_of_bid_card_change(
        bid_card_id=test_bid_card_id,
        change_type="budget_change",
        description="Budget increased from $45,000 to $60,000 based on scope refinement",
        previous_value="$45,000",
        new_value="$60,000"
    )
    
    print("\nNOTIFICATION RESULTS:")
    print(f"Success: {notification_result['success']}")
    print(f"Contractors notified: {notification_result.get('contractors_notified', 0)}")
    
    if notification_result.get("engagement_breakdown"):
        print("Engagement breakdown:")
        for eng_type, count in notification_result["engagement_breakdown"].items():
            print(f"  {eng_type}: {count}")
    
    if notification_result.get("error"):
        print(f"Error: {notification_result['error']}")
    
    return notification_result["success"]


async def test_notification_table_data():
    """Check what notifications were actually created"""
    print("=" * 60)
    print("CHECKING CREATED NOTIFICATIONS")
    print("=" * 60)
    
    # Get recent notifications
    result = db.client.table("notifications").select("*").eq("notification_type", "bid_card_change").order("created_at", desc=True).limit(5).execute()
    
    print(f"Recent bid card change notifications: {len(result.data) if result.data else 0}")
    
    for notification in (result.data or [])[:3]:  # Show first 3
        print(f"\nNotification ID: {notification['id']}")
        print(f"Contractor ID: {notification['contractor_id']}")
        print(f"Bid Card ID: {notification['bid_card_id']}")
        print(f"Title: {notification['title']}")
        print(f"Created: {notification['created_at']}")
        print(f"Read: {notification['is_read']}")
        
        # Show first part of message
        message = notification.get("message", "")
        if len(message) > 150:
            message = message[:150] + "..."
        print(f"Message: {message}")
    
    return len(result.data) if result.data else 0


async def main():
    """Run all tests"""
    print("CONTRACTOR NOTIFICATION SYSTEM TEST")
    print("=" * 60)
    
    results = []
    
    # Test 1: Engagement detection
    print("\n[SEARCH] TEST 1: ENGAGEMENT DETECTION")
    test1_success = await test_engagement_detection_real_data()
    results.append(("Engagement Detection", test1_success))
    
    # Test 2: Notification system
    print("\n[NOTIFY] TEST 2: NOTIFICATION SYSTEM")  
    test2_success = await test_notification_system()
    results.append(("Notification System", test2_success))
    
    # Test 3: Database verification
    print("\n[DATABASE] TEST 3: DATABASE VERIFICATION")
    notifications_created = await test_notification_table_data()
    results.append(("Database Verification", notifications_created > 0))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n[SUCCESS] ALL TESTS PASSED")
        print("Contractor notification system is working!")
        print("\nSYSTEM READY FOR:")
        print("- Notifying contractors when bid cards change")
        print("- Tracking engagement (bids, messages, views)")
        print("- Integration with JAA service")
        print("- Real-time contractor UI updates")
    else:
        print("\n[FAILED] SOME TESTS FAILED")
        print("Check errors above for details")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)