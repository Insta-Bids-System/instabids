#!/usr/bin/env python3
"""
Test bid submission through the API with intelligent messaging integration
This test will prove whether GPT-4o filtering is working
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from config.service_urls import get_backend_url

def test_bid_submission_api():
    """Test bid submission through bid card API"""
    
    print("=" * 80)
    print("TESTING BID SUBMISSION WITH INTELLIGENT MESSAGING INTEGRATION")
    print("=" * 80)
    
    # Test bid with contact information
    bid_data = {
        "bid_card_id": "78c3f7cb-64d8-496e-b396-32b24d790252",
        "contractor_id": str(uuid.uuid4()),  # Generate random contractor UUID
        "amount": 35000.0,
        "timeline_start": datetime.now().isoformat(),
        "timeline_end": (datetime.now() + timedelta(days=60)).isoformat(),
        "proposal": """I can complete your kitchen renovation. 
        Call me at 555-TEST-123 or email me at contractor@test.com
        Visit my website at www.testcontractor.com for more info.
        Let's meet at 123 Main Street to discuss details.""",
        "approach": "First, I'll meet you at my office. Email john@contractor.com to schedule",
        "materials_included": True,
        "warranty_details": "5-year warranty. For claims, text 555-999-8888 directly",
        "milestones": []
    }
    
    print("\n1. SUBMITTING BID WITH CONTACT INFO:")
    print("-" * 40)
    print("Proposal contains: phone, email, website, address")
    print("Approach contains: email address")
    print("Warranty contains: phone number")
    
    # Submit the bid
    print("\n2. SENDING TO API...")
    try:
        response = requests.post(
            f"{get_backend_url()}/api/bid-cards-simple/submit-bid",
            json=bid_data,
            timeout=180
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"\nSUCCESS: Bid submitted")
            print(f"Bid ID: {result.get('bid_id')}")
            print(f"Message: {result.get('message')}")
            
            # Now check what the intelligent messaging agent did
            print("\n3. CHECKING INTELLIGENT MESSAGING INTEGRATION:")
            print("-" * 40)
            
            # Query database directly to see what was saved
            import os
            from supabase import create_client
            
            supabase_url = "https://xrhgrthdcaymxuqcgrmj.supabase.co"
            supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyaGdydGhkY2F5bXh1cWNncm1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM2NTcyMDYsImV4cCI6MjA2OTIzMzIwNn0.BriGLA2FE_e_NJl8B-3ps1W6ZAuK6a5HpTwBGy-6rmE"
            supabase = create_client(supabase_url, supabase_key)
            
            if result.get('bid_id'):
                bid_check = supabase.table("contractor_bids").select("*").eq("id", result['bid_id']).execute()
                if bid_check.data:
                    saved_bid = bid_check.data[0]
                    print(f"Bid found in database: YES")
                    
                    # Check if contact info was filtered
                    original_has_contact = (
                        "555-TEST-123" in bid_data['proposal'] or
                        "contractor@test.com" in bid_data['proposal'] or
                        "john@contractor.com" in bid_data['approach'] or
                        "555-999-8888" in bid_data['warranty_details']
                    )
                    
                    saved_has_contact = (
                        "555-TEST-123" in (saved_bid.get('proposal') or "") or
                        "contractor@test.com" in (saved_bid.get('proposal') or "") or
                        "john@contractor.com" in (saved_bid.get('approach') or "") or
                        "555-999-8888" in (saved_bid.get('warranty_details') or "")
                    )
                    
                    print(f"Original had contact info: {original_has_contact}")
                    print(f"Saved has contact info: {saved_has_contact}")
                    
                    if original_has_contact and not saved_has_contact:
                        print("\nCONTACT INFO WAS FILTERED - INTELLIGENT AGENT WORKING!")
                    elif "[PHONE REMOVED]" in saved_bid.get('proposal', '') or "[EMAIL REMOVED]" in saved_bid.get('approach', ''):
                        print("\nCONTACT INFO WAS REPLACED - FILTERING WORKING!")
                    else:
                        print("\nWARNING: Contact info may not have been filtered")
                        print(f"Saved proposal: {saved_bid.get('proposal', '')[:100]}...")
                        print(f"Saved approach: {saved_bid.get('approach', '')[:100]}...")
                else:
                    print("ERROR: Bid not found in database")
            
            return True
            
        else:
            print(f"ERROR: API returned {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test the API
    success = test_bid_submission_api()
    
    print("\n" + "=" * 80)
    if success:
        print("TEST RESULT: API call successful")
        print("Check above to see if intelligent filtering worked")
    else:
        print("TEST RESULT: API call failed")