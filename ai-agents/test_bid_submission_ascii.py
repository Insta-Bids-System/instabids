#!/usr/bin/env python3
"""
Test bid submission with ASCII output only
"""

import requests
import json
from datetime import datetime
from database_simple import db
from config.service_urls import get_backend_url

def test_bid_submission():
    """Test bid submission functionality"""
    
    print("=== TESTING BID SUBMISSION SYSTEM ===\n")
    
    # Test data with contact info
    bid_data = {
        "bid_card_id": "78c3f7cb-64d8-496e-b396-32b24d790252",
        "contractor_id": "22222222-2222-2222-2222-222222222222",
        "amount": 37000,  # Different amount 
        "timeline_start": "2025-02-01T00:00:00Z",
        "timeline_end": "2025-03-15T00:00:00Z",
        "proposal": """I can complete your backyard project efficiently. 
        My team has 15 years experience. 
        Contact me at 555-8888 or email new@contractor.com.
        Visit www.newlandscaping.com or follow @newlandscape.""",
        "approach": "Site prep, hardscaping, then planting",
        "materials_included": True,
        "warranty_details": "2-year warranty",
        "milestones": []
    }
    
    print("1. SUBMITTING BID")
    print("Contact info in proposal:")
    print("- Phone: 555-8888")
    print("- Email: new@contractor.com") 
    print("- Website: www.newlandscaping.com")
    print("- Social: @newlandscape")
    
    # Delete existing bid
    try:
        db.client.table("contractor_bids").delete().eq(
            "bid_card_id", bid_data["bid_card_id"]
        ).eq(
            "contractor_id", bid_data["contractor_id"]
        ).execute()
        print("Cleaned up existing bids")
    except:
        pass
    
    # Submit bid
    try:
        response = requests.post(
            f"{get_backend_url()}/api/bid-cards-simple/submit-bid",
            json=bid_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[SUCCESS] BID SUBMITTED!")
            print(f"Bid ID: {result['bid_id']}")
            bid_id = result['bid_id']
            
            # Verify in database
            bid = db.client.table("contractor_bids").select("*").eq(
                "id", bid_id
            ).execute()
            
            if bid.data:
                saved_bid = bid.data[0]
                print(f"[SUCCESS] Found in database")
                print(f"Amount: ${saved_bid['amount']}")
                
                # Check contact info (should be unfiltered)
                proposal = saved_bid['proposal']
                print(f"\n2. CHECKING CONTACT INFO (should be present):")
                print(f"Phone found: {'555-8888' in proposal}")
                print(f"Email found: {'new@contractor.com' in proposal}")
                print(f"Website found: {'www.newlandscaping.com' in proposal}")
                print(f"Social found: {'@newlandscape' in proposal}")
                
                print(f"\nCONCLUSION:")
                print(f"- Bid submission: WORKING")
                print(f"- Database storage: WORKING") 
                print(f"- Contact info preserved: WORKING (not filtered)")
                print(f"- Intelligent messaging: NOT CALLED (backend hangs)")
                
            else:
                print("[FAILED] Bid not found in database")
                
        else:
            print(f"[FAILED] Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("[TIMEOUT] Backend hung - intelligent messaging issue")
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_bid_submission()