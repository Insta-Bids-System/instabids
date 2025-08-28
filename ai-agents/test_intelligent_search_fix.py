#!/usr/bin/env python3
"""
Test the fixed intelligent bid card search system
Verifies COIA now uses your existing ZIP radius + LLM intelligence
"""
import asyncio
import sys
import os

# Add current directory to path  
sys.path.append(os.path.dirname(__file__))

import requests
from config.service_urls import get_backend_url

async def test_intelligent_search_fix():
    """Test that COIA search now uses your intelligent systems"""
    
    print("TESTING FIXED INTELLIGENT BID CARD SEARCH")
    print("=" * 50)
    
    # Test 1: Verify your existing intelligent API works
    print("\n1. TESTING YOUR EXISTING INTELLIGENT API")
    print("-" * 40)
    
    try:
        response = requests.get(f"{get_backend_url()}/api/contractor-jobs/agent-search", params={
            "contractor_zip": "78701",  # Austin
            "radius_miles": 30,
            "project_keywords": "landscaping artificial turf",
            "limit": 10
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("job_opportunities", [])
            print(f"✅ Your intelligent API works: {len(jobs)} jobs found")
            print(f"   ZIP radius: {data.get('zip_codes_searched', 0)} zip codes searched")
            print(f"   Radius: {data.get('radius_miles')} miles")
            
            if jobs:
                sample = jobs[0]
                distance = sample.get("distance_miles", "N/A")
                title = sample.get("title", "No title")
                print(f"   Sample: {title} ({distance} miles)")
        else:
            print(f"❌ Your intelligent API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing your intelligent API: {e}")
    
    # Test 2: Test COIA with the fixed search
    print("\n2. TESTING COIA WITH FIXED SEARCH")
    print("-" * 40)
    
    test_message = {
        "message": "show me landscaping projects near me",
        "session_id": f"test_intelligent_{int(__import__('time').time())}",
        "contractor_lead_id": "test_contractor_intelligent",
        "context": {
            "company_name": "Green Thumb Landscaping",
            "zip_code": "78701",  # Austin
            "specialties": ["landscaping", "artificial_turf"],
            "service_radius_miles": 30
        }
    }
    
    try:
        response = requests.post(
            f'{get_backend_url()}/api/coia/chat',
            json=test_message,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if intelligent search was used
            tool_results = data.get("tool_results", {})
            search_results = tool_results.get("bid_card_search", {})
            
            if search_results.get("intelligent_search"):
                print("✅ COIA now uses intelligent search!")
                print(f"   ZIP radius used: {search_results.get('zip_radius_used')}")
                print(f"   Projects found: {search_results.get('total_found', 0)}")
                
                # Check if bid cards were returned
                bid_cards = data.get("bid_cards_attached", [])
                if bid_cards:
                    print(f"   Bid cards attached: {len(bid_cards)}")
                    sample = bid_cards[0]
                    title = sample.get("title", "No title")
                    distance = sample.get("distance_miles", "N/A")
                    print(f"   Sample bid card: {title} ({distance} miles)")
                else:
                    print("   No bid cards attached (might be empty results)")
            else:
                print("❌ COIA still using old search system")
                print("   Need to update unified_graph.py to import the fixed version")
                
        else:
            print(f"❌ COIA API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing COIA: {e}")
    
    print("\n3. IMPLEMENTATION STATUS")
    print("-" * 40)
    print("✅ Fixed search node created: bid_card_search_node_fixed.py")
    print("⏳ Next step: Update unified_graph.py to use fixed version")
    print("⏳ Replace: from .bid_card_search_node import bid_card_search_node")
    print("⏳ With: from .bid_card_search_node_fixed import bid_card_search_node")

if __name__ == "__main__":
    asyncio.run(test_intelligent_search_fix())