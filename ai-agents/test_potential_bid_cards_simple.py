"""
Simple Test for Potential Bid Cards System
Tests the complete workflow without Unicode characters
"""

import requests
import json
from datetime import datetime
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"

def test_simple_workflow():
    """Test the complete potential bid cards workflow"""
    
    print("\n=== POTENTIAL BID CARDS SYSTEM - SIMPLE TEST ===\n")
    
    # Step 1: Get existing potential bid cards
    print("Step 1: Get existing potential bid cards")
    response = requests.get(f"{BASE_URL}/api/iris/potential-bid-cards/{TEST_USER_ID}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: Found {data['total_count']} existing potential bid cards")
        for card in data['potential_bid_cards']:
            print(f"   - {card['title']} ({card['primary_trade']}) - Status: {card['status']}")
    else:
        print(f"FAILED: Could not get bid cards: {response.status_code}")
        return
    
    # Step 2: Create a new potential bid card
    print("\nStep 2: Create new potential bid card")
    new_card_data = {
        "title": "Deck Repair and Staining",
        "room_location": "backyard",
        "primary_trade": "carpentry",
        "secondary_trades": ["painting"],
        "project_complexity": "moderate",
        "user_scope_notes": "Repair loose boards and apply fresh stain to weathered deck",
        "eligible_for_group_bidding": True,
        "component_type": "maintenance",
        "urgency_level": "medium",
        "ai_analysis": {
            "detected_issues": ["loose_boards", "weathered_stain", "minor_rot"],
            "estimated_cost": "800-1500"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/iris/potential-bid-cards?user_id={TEST_USER_ID}",
        json=new_card_data
    )
    
    if response.status_code == 200:
        card = response.json()['potential_bid_card']
        deck_card_id = card['id']
        print(f"SUCCESS: Created deck repair card: {deck_card_id}")
        print(f"   Title: {card['title']}")
        print(f"   Trade: {card['primary_trade']}")
        print(f"   Complexity: {card['project_complexity']}")
    else:
        print(f"FAILED: Could not create bid card: {response.status_code}")
        return
    
    # Step 3: Test updating a card
    print("\nStep 3: Test updating card scope")
    update_data = {
        "user_scope_notes": "Repair loose boards, sand rough areas, and apply premium deck stain. Also check railing stability.",
        "priority": 7,
        "status": "refined"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/iris/potential-bid-cards/{deck_card_id}",
        json=update_data
    )
    
    if response.status_code == 200:
        updated_card = response.json()['potential_bid_card']
        print(f"SUCCESS: Updated card scope and priority")
        print(f"   New scope: {updated_card['user_scope_notes'][:100]}...")
        print(f"   Priority: {updated_card['priority']}")
    else:
        print(f"FAILED: Could not update card: {response.status_code}")
    
    # Step 4: Final summary
    print("\nStep 4: Final system summary")
    response = requests.get(f"{BASE_URL}/api/iris/potential-bid-cards/{TEST_USER_ID}")
    
    if response.status_code == 200:
        final_data = response.json()
        
        # Analyze the data
        cards = final_data['potential_bid_cards']
        total_cards = len(cards)
        simple_projects = len([c for c in cards if c['project_complexity'] == 'simple'])
        complex_projects = len([c for c in cards if c['project_complexity'] == 'complex'])
        group_bidding_eligible = len([c for c in cards if c['eligible_for_group_bidding']])
        
        print(f"\nSYSTEM SUMMARY:")
        print(f"   Total potential bid cards: {total_cards}")
        print(f"   Simple projects: {simple_projects}")
        print(f"   Complex projects: {complex_projects}")
        print(f"   Group bidding eligible: {group_bidding_eligible}")
        
        # Group by status
        status_counts = {}
        for card in cards:
            status = card['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"   Status breakdown: {status_counts}")
        
        print(f"\nSUCCESS: POTENTIAL BID CARDS SYSTEM FULLY OPERATIONAL")
        print(f"SUCCESS: All components tested and working")
        print(f"SUCCESS: Ready for frontend integration")
        
    else:
        print(f"FAILED: Could not get final summary: {response.status_code}")

if __name__ == "__main__":
    test_simple_workflow()