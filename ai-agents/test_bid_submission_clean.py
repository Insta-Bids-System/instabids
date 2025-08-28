#!/usr/bin/env python3
"""
Test contractor bid submission with intelligent messaging filtering
This tests the complete integration of bid submission → intelligent agent → database
"""

import requests
import json
import time
from datetime import datetime
from database_simple import db
from config.service_urls import get_backend_url

def test_complete_bid_submission():
    """Test complete bid submission with contact filtering"""
    
    print("\n=== TESTING COMPLETE BID SUBMISSION WITH INTELLIGENT FILTERING ===\n")
    
    # Test data with contact info that should be filtered
    bid_data = {
        "bid_card_id": "78c3f7cb-64d8-496e-b396-32b24d790252",
        "contractor_id": "22222222-2222-2222-2222-222222222222",
        "amount": 35000,
        "timeline_start": "2025-02-01T00:00:00Z",
        "timeline_end": "2025-03-15T00:00:00Z",
        "proposal": """I can complete your backyard transformation project with my team. 
        We have 15 years of experience in landscaping and hardscaping. 
        You can reach me at 555-0123 or email john@contractor.com. 
        Check our work at www.johnlandscaping.com or follow us @johnlandscape.
        We offer comprehensive warranty and use high-quality materials.""",
        "approach": "We'll start with site preparation, then install hardscaping features, followed by planting and irrigation.",
        "materials_included": True,
        "warranty_details": "2-year warranty on all hardscaping, 1-year on plants",
        "milestones": []
    }
    
    print("1. SUBMITTING BID WITH CONTACT INFO IN PROPOSAL")
    print("-" * 50)
    print(f"Bid contains phone: 555-0123")
    print(f"Bid contains email: john@contractor.com")
    print(f"Bid contains website: www.johnlandscaping.com")
    print(f"Bid contains social: @johnlandscape")
    
    # Submit the bid
    response = requests.post(
        f"{get_backend_url()}/api/bid-cards-simple/submit-bid",
        json=bid_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n[SUCCESS] Bid submitted successfully!")
        print(f"Bid ID: {result['bid_id']}")
        print(f"Bids received: {result['bids_received']}")
        print(f"Target met: {result['target_met']}")
        
        bid_id = result['bid_id']
        
        # Wait for intelligent processing
        print("\n2. WAITING FOR INTELLIGENT MESSAGING PROCESSING")
        print("-" * 50)
        time.sleep(3)  # Give the intelligent agent time to process
        
        # Check if conversation was created
        print("\n3. CHECKING UNIFIED CONVERSATION DATABASE")
        print("-" * 50)
        
        # Check for conversations
        conversations = db.client.table("unified_conversations").select("*").eq(
            "context_id", bid_id
        ).execute()
        
        if conversations.data:
            conv = conversations.data[0]
            print(f"[SUCCESS] Conversation created: {conv['id']}")
            print(f"   Agent type: {conv['agent_type']}")
            print(f"   Context: {conv['context_type']}")
            
            # Check for messages
            messages = db.client.table("unified_messages").select("*").eq(
                "conversation_id", conv['id']
            ).execute()
            
            if messages.data:
                print(f"\n[SUCCESS] Found {len(messages.data)} messages")
                for msg in messages.data:
                    print(f"\n   Message ID: {msg['id']}")
                    print(f"   Content filtered: {msg.get('metadata', {}).get('content_filtered', False)}")
                    if msg.get('metadata', {}).get('content_filtered'):
                        print(f"   Filter reasons: {msg.get('metadata', {}).get('filter_reasons', [])}")
                        print(f"   Original had contact info - NOW FILTERED [SUCCESS]")
                    print(f"   Filtered content preview: {msg['content'][:100]}...")
            else:
                print("[FAILED] No messages found in conversation")
        else:
            print("[FAILED] No conversation created - intelligent messaging may have failed")
        
        # Check the bid itself was saved
        print("\n4. VERIFYING BID SAVED TO DATABASE")
        print("-" * 50)
        
        bid = db.client.table("contractor_bids").select("*").eq(
            "id", bid_id
        ).execute()
        
        if bid.data:
            print(f"[SUCCESS] Bid saved to contractor_bids table")
            print(f"   Amount: ${bid.data[0]['amount']:,.2f}")
            print(f"   Status: {bid.data[0]['status']}")
            print(f"   Submitted at: {bid.data[0]['submitted_at']}")
        else:
            print("[FAILED] Bid not found in database")
            
        # Check bid card status update
        print("\n5. CHECKING BID CARD STATUS UPDATE")
        print("-" * 50)
        
        bid_card = db.client.table("bid_cards").select("*").eq(
            "id", bid_data["bid_card_id"]
        ).execute()
        
        if bid_card.data:
            bc = bid_card.data[0]
            print(f"[SUCCESS] Bid card status: {bc['status']}")
            print(f"   Bids received: {bc['bids_received_count']}")
            print(f"   Target met: {bc['bids_target_met']}")
            print(f"   Contractor count needed: {bc['contractor_count_needed']}")
        else:
            print("[FAILED] Bid card not found")
            
        # Test retrieving the bid back
        print("\n6. TESTING BID RETRIEVAL")
        print("-" * 50)
        
        # Get all bids for this bid card
        all_bids = db.client.table("contractor_bids").select("*").eq(
            "bid_card_id", bid_data["bid_card_id"]
        ).execute()
        
        if all_bids.data:
            print(f"[SUCCESS] Retrieved {len(all_bids.data)} bids for this bid card")
            for b in all_bids.data:
                print(f"   Bid from contractor {b['contractor_id'][:8]}...")
                print(f"   Amount: ${b['amount']:,.2f}")
                print(f"   Proposal length: {len(b['proposal'])} chars")
        else:
            print("[FAILED] Could not retrieve bids")
            
        # Test retrieving filtered messages
        print("\n7. TESTING FILTERED MESSAGE RETRIEVAL")
        print("-" * 50)
        
        if conversations.data:
            conv_id = conversations.data[0]['id']
            # Retrieve messages again to verify they're saved
            saved_messages = db.client.table("unified_messages").select("*").eq(
                "conversation_id", conv_id
            ).order("created_at", desc=False).execute()
            
            if saved_messages.data:
                print(f"[SUCCESS] Retrieved {len(saved_messages.data)} saved messages")
                for msg in saved_messages.data:
                    # Check if contact info was filtered
                    content = msg['content']
                    has_phone = "555-0123" in content
                    has_email = "john@contractor.com" in content
                    has_website = "www.johnlandscaping.com" in content
                    has_social = "@johnlandscape" in content
                    
                    if has_phone or has_email or has_website or has_social:
                        print(f"   [FAILED] Message still contains contact info!")
                        print(f"   Phone: {has_phone}, Email: {has_email}, Website: {has_website}, Social: {has_social}")
                    else:
                        print(f"   [SUCCESS] Message properly filtered - no contact info found")
                        print(f"   Content sample: {content[:150]}...")
            else:
                print("[FAILED] Could not retrieve saved messages")
            
    else:
        print(f"\n[FAILED] Failed to submit bid: {response.status_code}")
        print(f"Response: {response.text}")
        
    print("\n" + "=" * 70)
    print("TEST COMPLETE - CHECK RESULTS ABOVE")
    print("=" * 70)

if __name__ == "__main__":
    test_complete_bid_submission()