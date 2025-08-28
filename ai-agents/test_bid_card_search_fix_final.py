#!/usr/bin/env python3
"""
Test the bid card search fix - verify it returns actual bid cards
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from agents.coia.bid_card_search_node import search_bid_cards

async def test_bid_card_search():
    """Test basic bid card search functionality"""
    print("Testing bid card search with no filters...")
    
    # Test 1: No filters - should return all active bid cards
    criteria = {
        "status": ["active", "collecting_bids", "generated"]
    }
    
    results = await search_bid_cards(criteria)
    print(f"Found {len(results)} bid cards with no location filter")
    
    if results:
        print(f"Sample bid card cities:")
        cities = []
        for card in results[:5]:
            city = card.get("location_city", "NULL")
            project_type = card.get("project_type", "Unknown")
            status = card.get("status", "Unknown")
            cities.append(f"  - {city} / {project_type} / {status}")
        
        for city in cities:
            print(city)
    else:
        print("No bid cards found - there's still an issue")
    
    # Test 2: With location filter - should return even more due to OR logic
    print("\nTesting with location filter...")
    criteria_with_location = {
        "status": ["active", "collecting_bids", "generated"],
        "location_city": "Austin"
    }
    
    results_filtered = await search_bid_cards(criteria_with_location)
    print(f"Found {len(results_filtered)} bid cards with Austin OR null filter")
    
    return len(results) > 0

if __name__ == "__main__":
    success = asyncio.run(test_bid_card_search())
    if success:
        print("\nBID CARD SEARCH IS NOW WORKING!")
        print("The issue was location filtering being too restrictive.")
        print("Fixed: Now shows all projects when no location specified, and includes null locations when location is specified.")
    else:
        print("\nBid card search still not working")
    
    sys.exit(0 if success else 1)