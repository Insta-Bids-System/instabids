#!/usr/bin/env python3
"""
Test Timeline Event Tracking System
Verifies that all bid card lifecycle events are properly tracked
"""

import asyncio
import json
from datetime import datetime
from uuid import uuid4
import requests
import sys
import io

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test configuration
API_BASE = "http://localhost:8008"
TEST_HOMEOWNER_ID = "11111111-1111-1111-1111-111111111111"
TEST_CONTRACTOR_ID = "22222222-2222-2222-2222-222222222222"


def create_test_bid_card():
    """Create a test bid card and track its creation"""
    print("\n🎯 Creating test bid card with event tracking...")
    
    # Create a bid card using the bid_card_utils function
    response = requests.post(f"{API_BASE}/api/bid-cards/test-data")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("bid_cards"):
            bid_card = result["bid_cards"][0]
            print(f"✅ Created bid card: {bid_card['bid_card_number']}")
            return bid_card
    
    print("❌ Failed to create bid card")
    return None


def track_discovery_event(bid_card_id: str):
    """Track contractor discovery event"""
    print("\n🔍 Tracking contractor discovery event...")
    
    event_data = {
        "bid_card_id": bid_card_id,
        "event_type": "contractor_discovery",
        "event_description": "Discovered 12 contractors across 3 tiers",
        "event_details": {
            "total_contractors": 12,
            "tier_1_internal": 3,
            "tier_2_previous": 5,
            "tier_3_cold": 4
        },
        "created_by_type": "system"
    }
    
    response = requests.post(f"{API_BASE}/api/bid-card-events/track", json=event_data)
    
    if response.status_code == 200:
        print("✅ Contractor discovery event tracked")
        return True
    else:
        print(f"❌ Failed to track discovery: {response.text}")
        return False


def track_campaign_creation(bid_card_id: str):
    """Track campaign creation event"""
    print("\n📢 Tracking campaign creation event...")
    
    campaign_id = str(uuid4())
    event_data = {
        "bid_card_id": bid_card_id,
        "event_type": "campaign_created",
        "event_description": f"Outreach campaign 'Test Campaign' created",
        "event_details": {
            "campaign_id": campaign_id,
            "campaign_name": "Test Campaign for Timeline",
            "max_contractors": 10
        },
        "created_by_type": "system"
    }
    
    response = requests.post(f"{API_BASE}/api/bid-card-events/track", json=event_data)
    
    if response.status_code == 200:
        print("✅ Campaign creation event tracked")
        return campaign_id
    else:
        print(f"❌ Failed to track campaign: {response.text}")
        return None


def track_outreach_events(bid_card_id: str):
    """Track multiple outreach events"""
    print("\n📧 Tracking outreach events...")
    
    contractors = [
        ("Elite Builders", "email"),
        ("Pro Construction", "form"),
        ("Quality Renovations", "sms")
    ]
    
    for contractor_name, channel in contractors:
        event_data = {
            "bid_card_id": bid_card_id,
            "event_type": "outreach_sent",
            "event_description": f"Outreach sent to {contractor_name} via {channel}",
            "event_details": {
                "contractor_name": contractor_name,
                "channel": channel,
                "contractor_id": str(uuid4())
            },
            "created_by_type": "system"
        }
        
        response = requests.post(f"{API_BASE}/api/bid-card-events/track", json=event_data)
        
        if response.status_code == 200:
            print(f"  ✅ Tracked outreach to {contractor_name}")
        else:
            print(f"  ❌ Failed to track outreach to {contractor_name}")


def submit_test_bid(bid_card_id: str, contractor_name: str, bid_amount: float):
    """Submit a test bid through the API"""
    print(f"\n💰 Submitting bid from {contractor_name}...")
    
    proposal_data = {
        "bid_card_id": bid_card_id,
        "contractor_id": str(uuid4()),
        "contractor_name": contractor_name,
        "bid_amount": bid_amount,
        "timeline_days": 7,
        "proposal_text": f"Test proposal from {contractor_name}"
    }
    
    response = requests.post(f"{API_BASE}/api/contractor-proposals/submit", json=proposal_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"  ✅ Bid submitted: ${bid_amount:,.2f}")
            return True
    
    print(f"  ❌ Failed to submit bid: {response.text}")
    return False


def track_status_change(bid_card_id: str, old_status: str, new_status: str):
    """Track status change event"""
    print(f"\n🔄 Tracking status change: {old_status} → {new_status}")
    
    event_data = {
        "bid_card_id": bid_card_id,
        "event_type": "status_changed",
        "event_description": f"Status changed from {old_status} to {new_status}",
        "event_details": {
            "old_status": old_status,
            "new_status": new_status,
            "reason": "Target number of bids reached"
        },
        "created_by_type": "system"
    }
    
    response = requests.post(f"{API_BASE}/api/bid-card-events/track", json=event_data)
    
    if response.status_code == 200:
        print("✅ Status change tracked")
        return True
    else:
        print(f"❌ Failed to track status change: {response.text}")
        return False


def get_timeline(bid_card_id: str):
    """Get the complete timeline for a bid card"""
    print("\n📋 Fetching complete timeline...")
    
    response = requests.get(f"{API_BASE}/api/bid-card-events/{bid_card_id}/timeline")
    
    if response.status_code == 200:
        timeline_data = response.json()
        print(f"\n✅ Timeline contains {timeline_data['total_events']} events:")
        
        for event in timeline_data["timeline"]:
            timestamp = event.get("timestamp", "")[:19]  # Trim to seconds
            event_type = event.get("event_type", "unknown")
            description = event.get("description", "")
            print(f"  📍 {timestamp} - [{event_type}] {description}")
        
        return timeline_data
    else:
        print(f"❌ Failed to get timeline: {response.text}")
        return None


def analyze_timeline(bid_card_id: str):
    """Analyze the timeline for completeness"""
    print("\n📊 Analyzing timeline completeness...")
    
    response = requests.get(f"{API_BASE}/api/bid-card-events/{bid_card_id}/timeline-analysis")
    
    if response.status_code == 200:
        analysis = response.json()
        
        print(f"\n📈 Timeline Analysis:")
        print(f"  Total Events: {analysis['total_events']}")
        print(f"  Duration: {analysis['duration_hours']} hours")
        print(f"  Completeness Score: {analysis['completeness_score']:.1f}%")
        
        print(f"\n🎯 Milestone Checklist:")
        milestones = analysis["milestones"]
        for milestone, completed in milestones.items():
            status = "✅" if completed else "❌"
            print(f"  {status} {milestone.replace('_', ' ').title()}")
        
        print(f"\n📊 Event Breakdown:")
        for event_type, count in analysis["event_breakdown"].items():
            print(f"  • {event_type}: {count} events")
        
        return analysis
    else:
        print(f"❌ Failed to analyze timeline: {response.text}")
        return None


def main():
    """Run complete timeline tracking test"""
    print("=" * 60)
    print("🚀 BID CARD TIMELINE TRACKING TEST")
    print("=" * 60)
    
    # Step 1: Create a test bid card
    bid_card = create_test_bid_card()
    if not bid_card:
        print("❌ Test failed: Could not create bid card")
        return
    
    bid_card_id = bid_card["id"]
    print(f"\n📝 Testing with bid card ID: {bid_card_id}")
    
    # Step 2: Track contractor discovery
    track_discovery_event(bid_card_id)
    
    # Step 3: Track campaign creation
    campaign_id = track_campaign_creation(bid_card_id)
    
    # Step 4: Track outreach events
    track_outreach_events(bid_card_id)
    
    # Step 5: Track status change to collecting_bids
    track_status_change(bid_card_id, "generated", "collecting_bids")
    
    # Step 6: Submit test bids (these should auto-track)
    submit_test_bid(bid_card_id, "Quality Contractors", 8500)
    submit_test_bid(bid_card_id, "Elite Renovations", 9200)
    submit_test_bid(bid_card_id, "Pro Builders", 7800)
    submit_test_bid(bid_card_id, "Master Craftsmen", 8900)
    
    # Step 7: Track status change to bids_complete
    track_status_change(bid_card_id, "collecting_bids", "bids_complete")
    
    # Step 8: Get and display the complete timeline
    timeline = get_timeline(bid_card_id)
    
    # Step 9: Analyze the timeline
    analysis = analyze_timeline(bid_card_id)
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ TIMELINE TRACKING TEST COMPLETE")
    print("=" * 60)
    
    if analysis and analysis["completeness_score"] >= 80:
        print("🎉 SUCCESS: Timeline is tracking all major events!")
    else:
        print("⚠️  WARNING: Some events may not be tracked properly")
    
    print(f"\n🔗 View full timeline at:")
    print(f"   {API_BASE}/api/bid-card-events/{bid_card_id}/timeline")


if __name__ == "__main__":
    main()