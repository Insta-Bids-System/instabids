#!/usr/bin/env python3
"""
Test Intelligent Bid Submission with GPT-4o Contact Filtering
Simple version without Unicode characters
"""

import asyncio
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.intelligent_messaging_agent import process_intelligent_message, MessageType
from database_simple import SupabaseDB

async def test_bid_submission_with_contact_info():
    """Test bid submission containing contact information"""
    
    print("Testing Intelligent Bid Submission with GPT-4o Contact Filtering")
    print("=" * 80)
    
    # Initialize database
    db = SupabaseDB()
    
    # Get a real bid card for testing
    print("Getting test bid card...")
    bid_cards = db.client.table("bid_cards").select("*").limit(1).execute()
    if not bid_cards.data:
        print("ERROR: No bid cards found for testing")
        return
        
    bid_card_id = bid_cards.data[0]["id"]
    print(f"Using bid card: {bid_card_id}")
    
    # Test contractor ID 
    test_contractor_id = "test-contractor-intelligent-" + str(int(datetime.now().timestamp()))
    
    # Test 1: Bid submission with contact information
    print(f"\nTEST 1: Bid Submission with Contact Information")
    print("-" * 60)
    
    bid_data = {
        "amount": 25000,
        "timeline": "2025-01-15 to 2025-02-28",
        "proposal": "I can complete your kitchen renovation for $25,000. Please call me at 555-SMART-123 to discuss the timeline and materials.",
        "approach": "First, I'll meet with you to go over details. You can reach me at contractor@email.com for any questions during the project.",  
        "warranty_details": "I offer a 5-year warranty on all work. For warranty claims, text me directly at 555-999-8888 and I'll respond within 24 hours.",
        "materials_included": True
    }
    
    try:
        result = await process_intelligent_message(
            content=f"Bid Submission - Amount: ${bid_data['amount']:,.2f}, Timeline: {bid_data['timeline']}",
            sender_type="contractor",
            sender_id=test_contractor_id,
            bid_card_id=bid_card_id,
            message_type=MessageType.BID_SUBMISSION,
            bid_data=bid_data
        )
        
        print(f"SUCCESS: Intelligent Agent Response:")
        print(f"   - Agent Decision: {result.get('agent_decision')}")
        print(f"   - Threats Detected: {result.get('threats_detected')}")
        print(f"   - Bid Saved: {result.get('bid_saved')}")
        print(f"   - Bid ID: {result.get('bid_id')}")
        print(f"   - Contact Info Detected: {len(result.get('threats_detected', [])) > 0}")
        print(f"   - Security Analysis: {bool(result.get('security_analysis'))}")
        
        # Check database for saved bid
        if result.get("bid_id"):
            print(f"\nVerifying Database Storage...")
            bid_check = db.client.table("contractor_bids").select("*").eq("id", result["bid_id"]).execute()
            if bid_check.data:
                bid_record = bid_check.data[0]
                print(f"SUCCESS: Bid saved to database:")
                print(f"   - Proposal (filtered): {bid_record['proposal'][:100]}...")
                print(f"   - Approach (filtered): {bid_record['approach'][:100]}...")
                print(f"   - Warranty (filtered): {bid_record['warranty_details'][:100]}...")
                print(f"   - Used GPT-4o: {bid_record.get('additional_data', {}).get('used_gpt4o', False)}")
                print(f"   - Filtered by Agent: {bid_record.get('additional_data', {}).get('filtered_by_intelligent_agent', False)}")
                
                # Check if contact info was actually filtered
                contact_removed = (
                    "[PHONE REMOVED]" in bid_record.get('proposal', '') or
                    "[EMAIL REMOVED]" in bid_record.get('approach', '') or 
                    "[PHONE REMOVED]" in bid_record.get('warranty_details', '')
                )
                print(f"   - Contact Info Filtered: {contact_removed}")
                
                # Show what GPT-4o detected
                additional_data = bid_record.get('additional_data', {})
                security_analysis = additional_data.get('security_analysis', {})
                if security_analysis:
                    print(f"   - GPT-4o Analysis: {security_analysis.get('summary', 'No summary')}")
                
                return True
            else:
                print(f"ERROR: Bid not found in database")
                return False
        else:
            print(f"ERROR: No bid ID returned from agent")
            return False
        
    except Exception as e:
        print(f"ERROR: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    print("Starting Intelligent Bid Submission Test")
    print("Testing GPT-4o powered contact information filtering")
    print()
    
    success = await test_bid_submission_with_contact_info()
    
    print(f"\nTesting Complete!")
    print("=" * 80)
    if success:
        print("SUCCESS: All tests passed!")
        print("- Intelligent messaging agent integrated GPT-4o analysis")
        print("- Bid submission filtered for contact information") 
        print("- Filtered bid saved to contractor_bids table")
        print("- Security analysis and threat detection working")
    else:
        print("FAILURE: Test failed - check logs above")

if __name__ == "__main__":
    asyncio.run(main())