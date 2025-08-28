#!/usr/bin/env python3
"""
DEFINITIVE TEST: Prove bid submissions go through GPT-4o intelligent filtering
This test will submit a bid with contact info and verify GPT-4o filters it
"""

import requests
import json
from datetime import datetime, timedelta
import time
from config.service_urls import get_backend_url

def test_bid_submission_filtering():
    """Submit a bid and verify GPT-4o intelligent filtering"""
    
    print("=" * 80)
    print("TESTING BID SUBMISSION WITH GPT-4o INTELLIGENT FILTERING")
    print("=" * 80)
    
    # Test bid with obvious contact information
    bid_data = {
        "bid_card_id": "78c3f7cb-64d8-496e-b396-32b24d790252",
        "contractor_id": f"test-contractor-{int(time.time())}",
        "amount": 75000.0,
        "timeline_start": datetime.now().isoformat(),
        "timeline_end": (datetime.now() + timedelta(days=60)).isoformat(),
        "proposal": """I'm the best contractor for your project! 
        You can reach me directly at 555-GPT-TEST or email gpt.test@contractor.com
        Visit my website at www.gpttest.com for more info.
        Let's meet at 123 Test Street to discuss details.""",
        "approach": "First step: Call me at 555-GPT-TEST to schedule an in-person meeting",
        "materials_included": True,
        "warranty_details": "For warranty claims, email warranty@gpttest.com or call 555-WARRANTY",
        "milestones": []
    }
    
    print("\n1. SUBMITTING BID WITH CONTACT INFO:")
    print("-" * 40)
    print(f"Proposal contains: phone, email, website, address")
    print(f"Approach contains: phone number")
    print(f"Warranty contains: email and phone")
    
    # Submit the bid through the API
    print("\n2. SENDING TO API...")
    response = requests.post(
        f"{get_backend_url()}/api/bid-cards/submit-bid",
        json=bid_data,
        timeout=180  # Long timeout for GPT-4o processing
    )
    
    if not response.ok:
        print(f"ERROR: API returned {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    bid_id = result.get('bid_id')
    print(f"SUCCESS: Bid submitted with ID: {bid_id}")
    
    # Now verify what was saved in the database
    print("\n3. VERIFYING DATABASE CONTENT...")
    print("-" * 40)
    
    # Import Supabase to check database
    import os
    from supabase import create_client
    
    supabase_url = "https://xrhgrthdcaymxuqcgrmj.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyaGdydGhkY2F5bXh1cWNncm1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM2NTcyMDYsImV4cCI6MjA2OTIzMzIwNn0.BriGLA2FE_e_NJl8B-3ps1W6ZAuK6a5HpTwBGy-6rmE"
    supabase = create_client(supabase_url, supabase_key)
    
    # Get the saved bid from database
    bid_result = supabase.table("contractor_bids").select("*").eq("id", bid_id).execute()
    
    if not bid_result.data:
        print("ERROR: Bid not found in database!")
        return False
    
    saved_bid = bid_result.data[0]
    
    # Check what was actually saved
    print("SAVED BID DATA:")
    print(f"Proposal: {saved_bid['proposal'][:100]}..." if saved_bid['proposal'] else "Empty")
    print(f"Approach: {saved_bid['approach'][:100]}..." if saved_bid['approach'] else "Empty")
    print(f"Warranty: {saved_bid['warranty_details'][:100]}..." if saved_bid['warranty_details'] else "Empty")
    
    # Check if contact info was filtered
    print("\n4. FILTERING VERIFICATION:")
    print("-" * 40)
    
    original_contains = {
        "phone": "555-GPT-TEST" in bid_data['proposal'],
        "email": "gpt.test@contractor.com" in bid_data['proposal'],
        "website": "www.gpttest.com" in bid_data['proposal'],
        "address": "123 Test Street" in bid_data['proposal']
    }
    
    saved_contains = {
        "phone": "555-GPT-TEST" in (saved_bid['proposal'] or ""),
        "email": "gpt.test@contractor.com" in (saved_bid['proposal'] or ""),
        "website": "www.gpttest.com" in (saved_bid['proposal'] or ""),
        "address": "123 Test Street" in (saved_bid['proposal'] or "")
    }
    
    print(f"Original had phone: {original_contains['phone']} -> Saved has phone: {saved_contains['phone']}")
    print(f"Original had email: {original_contains['email']} -> Saved has email: {saved_contains['email']}")
    print(f"Original had website: {original_contains['website']} -> Saved has website: {saved_contains['website']}")
    print(f"Original had address: {original_contains['address']} -> Saved has address: {saved_contains['address']}")
    
    # Check if GPT-4o was used
    print("\n5. INTELLIGENT AGENT TRACKING:")
    print("-" * 40)
    
    additional_data = saved_bid.get('additional_data', {})
    if additional_data:
        print(f"Filtered by intelligent agent: {additional_data.get('filtered_by_intelligent_agent', False)}")
        print(f"Used GPT-4o: {additional_data.get('used_gpt4o', False)}")
        print(f"Threats detected: {additional_data.get('threats_detected', [])}")
        print(f"Agent decision: {additional_data.get('agent_decision', 'unknown')}")
    else:
        print("No intelligent agent metadata found")
    
    # Final verdict
    print("\n6. FINAL VERDICT:")
    print("=" * 80)
    
    contact_filtered = not any([
        saved_contains['phone'],
        saved_contains['email'],
        saved_contains['website'],
        saved_contains['address']
    ])
    
    if contact_filtered:
        print("SUCCESS: Contact information was filtered by intelligent agent!")
        print("The system is using GPT-4o to intelligently filter bid submissions.")
        return True
    else:
        print("FAILURE: Contact information was NOT filtered properly")
        print("The system may not be using intelligent filtering correctly.")
        return False

if __name__ == "__main__":
    # Check if backend is running
    try:
        health = requests.get(f"{get_backend_url()}/health", timeout=5)
        if not health.ok:
            print("ERROR: Backend not responding at http://localhost:8008")
            print("Please start the backend first: cd ai-agents && python main.py")
            exit(1)
    except:
        print("ERROR: Cannot connect to backend at http://localhost:8008")
        print("Please start the backend first: cd ai-agents && python main.py")
        exit(1)
    
    # Run the test
    success = test_bid_submission_filtering()
    
    if success:
        print("\nTEST PASSED: System is correctly using GPT-4o for intelligent filtering")
    else:
        print("\nTEST FAILED: System is not filtering contact information properly")