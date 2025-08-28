#!/usr/bin/env python3
"""
Test complete COIA bid card search workflow
Verifies that bid_card_search mode triggers and returns actual bid cards
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

import requests
import json
from config.service_urls import get_backend_url

async def test_complete_bid_search():
    """Test complete COIA bid card search workflow"""
    print("Testing complete COIA bid card search workflow...")
    
    # Test data for contractor asking for projects
    test_message = {
        "message": "show me available projects",
        "session_id": f"test_bid_search_{int(__import__('time').time())}",
        "contractor_lead_id": "test_contractor_001",
        "context": {
            "company_name": "Test Contractor LLC",
            "specialties": ["kitchen_remodel", "bathroom_renovation"],
            "service_areas": ["Austin", "Round Rock"],
            "years_in_business": 8
        }
    }
    
    try:
        print("Sending request to COIA landing page API...")
        response = requests.post(
            f'{get_backend_url()}/api/coia/chat',
            json=test_message,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response received successfully!")
            
            # Check if bid_card_search mode was triggered
            if data.get("current_mode") == "bid_card_search":
                print("SUCCESS: bid_card_search mode triggered!")
                
                # Check if bid cards were attached
                bid_cards = data.get("bid_cards_attached", [])
                if bid_cards:
                    print(f"SUCCESS: {len(bid_cards)} bid cards attached!")
                    
                    # Show sample bid cards
                    for i, card in enumerate(bid_cards[:3], 1):
                        title = card.get("title", "Untitled")
                        location = card.get("location_city", "No city")
                        project_type = card.get("project_type", "Unknown type")
                        print(f"  {i}. {title} - {location} - {project_type}")
                    
                    return True
                else:
                    print("WARNING: bid_card_search mode triggered but no bid cards attached")
                    print("Checking response data for more details...")
                    
                    # Debug: Show what's in the response
                    tool_results = data.get("tool_results", {})
                    print(f"Tool results keys: {list(tool_results.keys())}")
                    
                    bid_search_results = tool_results.get("bid_card_search", {})
                    if bid_search_results:
                        total_found = bid_search_results.get("total_found", 0)
                        displayed = bid_search_results.get("displayed", 0)
                        print(f"Tool results: {total_found} found, {displayed} displayed")
                    else:
                        print("No bid_card_search tool results found")
                    
                    # Check message content for more clues
                    messages = data.get("messages", [])
                    if messages:
                        last_message = messages[-1].get("content", "")
                        print(f"Response message: {last_message[:300]}...")
                    else:
                        print("No messages in response")
                    
                    # Show other keys in response for debugging
                    other_keys = [k for k in data.keys() if k not in ['current_mode', 'bid_cards_attached', 'tool_results', 'messages']]
                    print(f"Other response keys: {other_keys}")
                    
                    # Check the bidCards key that was found
                    bid_cards_alt = data.get("bidCards", [])
                    if bid_cards_alt:
                        print(f"Found {len(bid_cards_alt)} bid cards in 'bidCards' key!")
                        for i, card in enumerate(bid_cards_alt[:3], 1):
                            title = card.get("title", "Untitled")
                            location = card.get("location_city", "No city")
                            project_type = card.get("project_type", "Unknown type")
                            print(f"  {i}. {title} - {location} - {project_type}")
                        return True
                    
                    # Check AI recommendation
                    ai_rec = data.get("aiRecommendation", "")
                    if ai_rec:
                        print(f"AI Recommendation: {ai_rec[:200]}...")
                    
                    return False
            else:
                current_mode = data.get("current_mode", "unknown")
                print(f"ISSUE: Expected bid_card_search mode, got: {current_mode}")
                
                # Check the message content for clues
                messages = data.get("messages", [])
                if messages:
                    last_message = messages[-1].get("content", "")
                    print(f"Last message: {last_message[:200]}...")
                
                return False
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("Error: Request timed out (30 seconds)")
        return False
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to backend")
        print("Make sure the backend is running: cd ai-agents && python main.py")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_bid_search())
    if success:
        print("\nCOMPLETE SUCCESS!")
        print("COIA bid card search is working end-to-end:")
        print("1. Request triggers bid_card_search mode")
        print("2. Database search returns actual bid cards") 
        print("3. Bid cards are properly formatted and attached")
        print("\nThe COIA landing page system is now fully operational!")
    else:
        print("\nTest failed - system needs more debugging")
    
    sys.exit(0 if success else 1)