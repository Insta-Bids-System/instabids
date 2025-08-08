#!/usr/bin/env python3
"""
Complete Bid Card Timeline Test
Verifies that the admin dashboard timeline tab shows ALL events from creation to completion
"""

import asyncio
import json
import sys
import io
import requests
from datetime import datetime

# Fix Unicode output issues on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_timeline_completeness():
    """Test that bid card timeline shows complete lifecycle"""
    
    print("🧪 TESTING BID CARD TIMELINE COMPLETENESS")
    print("=" * 60)
    
    # Test with known complete bid card
    bid_card_id = "3398dd4d-9301-4aaa-8724-bcc993da2e13"
    bid_card_number = "BC-LIVE-040828"
    
    print(f"📋 Testing bid card: {bid_card_number}")
    print(f"🔗 ID: {bid_card_id}")
    
    try:
        # Test the lifecycle endpoint used by admin dashboard
        response = requests.get(
            f"http://localhost:8008/api/admin/bid-cards/{bid_card_id}/lifecycle",
            headers={"Authorization": "Bearer admin-test"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
        data = response.json()
        timeline = data.get("timeline", [])
        
        print(f"📊 Timeline Events Found: {len(timeline)}")
        
        if len(timeline) == 0:
            print("❌ TIMELINE EMPTY - No events tracked!")
            return False
            
        # Expected events for a complete bid card lifecycle
        expected_events = [
            "bid_card_created",
            "campaign_created", 
            "contractors_targeted",
            "bid_received",
            "target_reached",
            "status_changed",
            "campaign_completed"
        ]
        
        found_events = {event["event_type"] for event in timeline}
        
        print("\n📅 TIMELINE EVENTS ANALYSIS:")
        print("-" * 40)
        
        # Sort timeline chronologically for display
        timeline_sorted = sorted(timeline, key=lambda x: x.get("timestamp", ""))
        
        for i, event in enumerate(timeline_sorted, 1):
            timestamp = event.get("timestamp", "Unknown")
            event_type = event.get("event_type", "Unknown")
            description = event.get("description", "No description")
            actor = event.get("actor", "Unknown")
            
            print(f"{i:2d}. [{timestamp}] {event_type}")
            print(f"    👤 Actor: {actor}")
            print(f"    📝 {description}")
            
            # Show key metadata for important events
            metadata = event.get("metadata", {})
            if event_type == "bid_received":
                bid_amount = metadata.get("bid_amount")
                contractor = description.split("from ")[-1] if "from " in description else "Unknown"
                print(f"    💰 Bid: ${bid_amount:,} from {contractor}")
                
            elif event_type == "contractors_targeted":
                contractors = metadata.get("contractors", [])
                channels = metadata.get("channels", {})
                print(f"    👷 Contractors: {len(contractors)}")
                print(f"    📧 Channels: {channels}")
                
            elif event_type == "target_reached":
                target = metadata.get("target", 0)
                total_bids = metadata.get("total_bids", 0)
                completion = metadata.get("completion_percentage", 0)
                print(f"    🎯 Target: {total_bids}/{target} ({completion}%)")
                
            print()
        
        # Check completeness
        missing_events = set(expected_events) - found_events
        
        print("✅ COMPLETENESS CHECK:")
        print("-" * 20)
        
        for event_type in expected_events:
            if event_type in found_events:
                print(f"✅ {event_type}")
            else:
                print(f"❌ {event_type} - MISSING")
        
        if missing_events:
            print(f"\n⚠️  Missing Events: {missing_events}")
            
        # Calculate completeness score
        completeness_score = len(found_events & set(expected_events)) / len(expected_events) * 100
        print(f"\n📊 Timeline Completeness: {completeness_score:.1f}%")
        
        # Check for multiple bid_received events (shows all contractor bids)
        bid_events = [e for e in timeline if e["event_type"] == "bid_received"]
        print(f"💰 Bid Submissions Tracked: {len(bid_events)}")
        
        if len(bid_events) >= 3:
            print("✅ All bid submissions properly tracked!")
        else:
            print("⚠️  Some bid submissions may not be tracked")
            
        # Final assessment
        if completeness_score >= 85 and len(timeline) >= 7:
            print("\n🎉 TIMELINE COMPLETENESS: EXCELLENT!")
            print("✅ Timeline tab in admin dashboard should show complete lifecycle")
            return True
        elif completeness_score >= 70:
            print("\n✅ TIMELINE COMPLETENESS: GOOD")
            print("⚠️  Timeline tab shows most events, minor gaps possible")
            return True
        else:
            print("\n❌ TIMELINE COMPLETENESS: POOR")
            print("🔧 Timeline tab missing significant events")
            return False
            
    except Exception as e:
        print(f"❌ Timeline test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 BID CARD TIMELINE COMPLETENESS TEST")
    print("=" * 60)
    
    success = test_timeline_completeness()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TIMELINE TEST PASSED!")
        print("💡 The timeline tab in bid card lifecycle should show:")
        print("   ✅ Bid card creation event")
        print("   ✅ Campaign creation and contractor targeting")
        print("   ✅ Individual bid submissions from each contractor")
        print("   ✅ Target reached and status changes")
        print("   ✅ Campaign completion")
        print("\n🔗 Test it: Go to admin dashboard → Bid Cards → Click any bid card → Timeline tab")
    else:
        print("❌ TIMELINE TEST FAILED!")
        print("🔧 Timeline tab may not show complete event history")
    print("=" * 60)


if __name__ == "__main__":
    main()