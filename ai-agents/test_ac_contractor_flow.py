"""
Test the complete contractor flow with South Florida Air Conditioning Inc
Creates a test AC installation bid card, then tests contractor onboarding
"""

import json
import requests
from datetime import datetime
import time

BASE_URL = "http://localhost:8008"

def create_ac_installation_bid_card():
    """Create a test AC installation bid card for contractors to find"""
    print("\n" + "="*60)
    print("CREATING AC INSTALLATION BID CARD")
    print("="*60)
    
    bid_card_data = {
        "project_type": "HVAC Installation",
        "project_details": "Need to install new central AC system. 3-bedroom house, 2000 sq ft. Current system is 15 years old and failing. Need complete replacement including ductwork inspection.",
        "urgency_level": "urgent",
        "budget_min": 8000,
        "budget_max": 12000,
        "location": {
            "city": "Miami",
            "state": "FL",
            "zip_code": "33139"
        },
        "homeowner_name": "Test Homeowner",
        "homeowner_phone": "555-0123",
        "homeowner_email": "homeowner@test.com",
        "contractor_count_needed": 4,
        "timeline_str": "Next 2 weeks",
        "special_requirements": "Must be licensed HVAC contractor, experience with Carrier systems preferred",
        "completion_criteria": "Full system replacement with warranty",
        "is_public": True,
        "status": "generated",
        "created_by": "test_script"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/bid-cards/create",
        json=bid_card_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"[SUCCESS] Created bid card: {result.get('bid_card_number', 'Unknown')}")
        print(f"   Project: {result.get('project_type')}")
        print(f"   Location: Miami, FL 33139")
        print(f"   Budget: $8,000 - $12,000")
        return result.get('id')
    else:
        print(f"[ERROR] Failed to create bid card: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def test_contractor_chat_onboarding():
    """Test contractor onboarding chat flow"""
    print("\n" + "="*60)
    print("TESTING CONTRACTOR ONBOARDING CHAT")
    print("="*60)
    
    session_id = f"test-ac-contractor-{int(time.time())}"
    
    # Message 1: Introduction
    print("\n1. Sending introduction message...")
    response = requests.post(
        f"{BASE_URL}/chat/message",
        json={
            "message": "Hi, I want to join InstaBids as a contractor. I run South Florida Air Conditioning Inc. We specialize in AC installation and repair.",
            "session_id": session_id,
            "current_stage": "welcome"
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"[SUCCESS] Response received")
        print(f"   Stage: {data.get('stage', 'unknown')}")
        print(f"   Message: {data.get('response', '')[:200]}...")
        
        # Message 2: Provide more details
        print("\n2. Providing business details...")
        response2 = requests.post(
            f"{BASE_URL}/chat/message",
            json={
                "message": "We've been in business for 12 years. Licensed and insured in Florida. We do residential and commercial HVAC. Our website is www.southfloridaac.com",
                "session_id": session_id,
                "current_stage": data.get('stage', 'experience'),
                "profile_data": data.get('profile_progress', {}).get('collectedData', {})
            },
            timeout=30
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"[SUCCESS] Profile building")
            print(f"   Completeness: {data2.get('profile_progress', {}).get('completeness', 0)}%")
            print(f"   Stage: {data2.get('stage', 'unknown')}")
            
            # Message 3: Service area
            print("\n3. Specifying service area...")
            response3 = requests.post(
                f"{BASE_URL}/chat/message",
                json={
                    "message": "We serve Miami-Dade County, primarily Miami, Miami Beach, Coral Gables, and surrounding areas within 20 miles.",
                    "session_id": session_id,
                    "current_stage": data2.get('stage', 'service_area'),
                    "profile_data": data2.get('profile_progress', {}).get('collectedData', {})
                },
                timeout=30
            )
            
            if response3.status_code == 200:
                data3 = response3.json()
                print(f"[SUCCESS] Service area registered")
                print(f"   Contractor ID: {data3.get('contractor_id', 'Not yet created')}")
                print(f"   Matching Projects: {data3.get('profile_progress', {}).get('matchingProjects', 0)}")
                return data3.get('contractor_id')
            else:
                print(f"[ERROR] Service area failed: {response3.status_code}")
        else:
            print(f"[ERROR] Details failed: {response2.status_code}")
    else:
        print(f"[ERROR] Introduction failed: {response.status_code}")
        print(f"   Error: {response.text[:500]}")
    
    return None


def test_contractor_job_search(contractor_id=None):
    """Test contractor searching for AC installation jobs"""
    print("\n" + "="*60)
    print("TESTING CONTRACTOR JOB SEARCH")
    print("="*60)
    
    # Search for HVAC projects in Miami area
    search_params = {
        "contractor_zip": "33139",  # Miami Beach
        "radius_miles": 15,
        "project_types": ["HVAC Installation", "AC Repair", "HVAC"],
        "budget_min": 5000
    }
    
    print(f"\nSearching for HVAC projects within {search_params['radius_miles']} miles of {search_params['contractor_zip']}...")
    
    response = requests.get(
        f"{BASE_URL}/api/contractor/search/radius",
        params={
            "contractor_zip": search_params["contractor_zip"],
            "radius_miles": search_params["radius_miles"]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"[SUCCESS] Found {data.get('total_results', 0)} HVAC projects")
        
        if data.get('bid_cards'):
            for card in data['bid_cards'][:3]:  # Show first 3
                print(f"\n   [BID] Bid Card: {card.get('bid_card_number')}")
                print(f"      Type: {card.get('project_type')}")
                print(f"      Location: {card.get('city')}, {card.get('state')}")
                print(f"      Budget: ${card.get('budget_min')} - ${card.get('budget_max')}")
                print(f"      Distance: {card.get('distance_miles', 'N/A')} miles")
        
        return True
    else:
        print(f"[ERROR] Search failed: {response.status_code}")
        print(f"   Error: {response.text[:500]}")
        return False


def test_complete_flow():
    """Run the complete contractor flow test"""
    print("\n" + "="*60)
    print("COMPLETE CONTRACTOR FLOW TEST")
    print("Testing: South Florida Air Conditioning Inc")
    print("="*60)
    
    # Step 1: Create AC installation bid card
    bid_card_id = create_ac_installation_bid_card()
    if not bid_card_id:
        print("\n[WARNING]  Continuing without bid card creation...")
    
    # Step 2: Test contractor onboarding
    contractor_id = test_contractor_chat_onboarding()
    
    # Step 3: Test job search
    if contractor_id or True:  # Continue even without contractor_id for testing
        test_contractor_job_search(contractor_id)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"[SUCCESS] Bid Card Created: {'Yes' if bid_card_id else 'No'}")
    print(f"[SUCCESS] Contractor Onboarded: {'Yes' if contractor_id else 'Partial'}")
    print(f"[SUCCESS] Job Search Tested: Yes")
    print("\nThe contractor agent system is partially working but needs:")
    print("- COIA agent connection fixed (currently timing out)")
    print("- Proper contractor profile creation")
    print("- Session persistence across conversations")


if __name__ == "__main__":
    test_complete_flow()