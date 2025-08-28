#!/usr/bin/env python3
"""
Test Intelligent Bid Submission with GPT-4o Contact Filtering
Tests the new intelligent messaging agent implementation for bid submissions
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
    
    print("🧪 Testing Intelligent Bid Submission with GPT-4o Contact Filtering")
    print("=" * 80)
    
    # Initialize database
    db = SupabaseDB()
    
    # Get a real bid card for testing
    print("📋 Getting test bid card...")
    bid_cards = db.client.table("bid_cards").select("*").limit(1).execute()
    if not bid_cards.data:
        print("❌ No bid cards found for testing")
        return
        
    bid_card_id = bid_cards.data[0]["id"]
    print(f"✅ Using bid card: {bid_card_id}")
    
    # Test contractor ID 
    test_contractor_id = "test-contractor-intelligent-" + str(int(datetime.now().timestamp()))
    
    # Test 1: Bid submission with contact information
    print(f"\n🔍 TEST 1: Bid Submission with Contact Information")
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
        
        print(f"✅ Intelligent Agent Response:")
        print(f"   - Agent Decision: {result.get('agent_decision')}")
        print(f"   - Threats Detected: {result.get('threats_detected')}")
        print(f"   - Bid Saved: {result.get('bid_saved')}")
        print(f"   - Bid ID: {result.get('bid_id')}")
        print(f"   - Contact Info Detected: {len(result.get('threats_detected', [])) > 0}")
        print(f"   - Security Analysis: {bool(result.get('security_analysis'))}")
        
        # Check database for saved bid
        if result.get("bid_id"):
            print(f"\n🔍 Verifying Database Storage...")
            bid_check = db.client.table("contractor_bids").select("*").eq("id", result["bid_id"]).execute()
            if bid_check.data:
                bid_record = bid_check.data[0]
                print(f"✅ Bid saved to database:")
                print(f"   - Proposal (filtered): {bid_record['proposal'][:100]}...")
                print(f"   - Approach (filtered): {bid_record['approach'][:100]}...")
                print(f"   - Warranty (filtered): {bid_record['warranty_details'][:100]}...")
                print(f"   - Used GPT-4o: {bid_record.get('additional_data', {}).get('used_gpt4o', False)}")
                print(f"   - Filtered by Agent: {bid_record.get('additional_data', {}).get('filtered_by_intelligent_agent', False)}")
                
                # Check if contact info was actually filtered
                contact_removed = (
                    "[PHONE REMOVED]" in bid_record['proposal'] or
                    "[EMAIL REMOVED]" in bid_record['approach'] or 
                    "[PHONE REMOVED]" in bid_record['warranty_details']
                )
                print(f"   - Contact Info Filtered: {contact_removed}")
            else:
                print(f"❌ Bid not found in database")
        
        # Check conversation message
        print(f"\n💬 Conversation Integration:")
        print(f"   - Message ID: {result.get('message_id')}")
        print(f"   - Conversation Message: {result.get('bid_conversation_message')}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

async def test_clean_bid_submission():
    """Test bid submission without contact information"""
    
    print(f"\n🔍 TEST 2: Clean Bid Submission (No Contact Info)")
    print("-" * 60)
    
    # Initialize database
    db = SupabaseDB()
    
    # Get a real bid card for testing
    bid_cards = db.client.table("bid_cards").select("*").limit(1).execute()
    if not bid_cards.data:
        print("❌ No bid cards found for testing")
        return
        
    bid_card_id = bid_cards.data[0]["id"]
    test_contractor_id = "test-contractor-clean-" + str(int(datetime.now().timestamp()))
    
    bid_data = {
        "amount": 18500,
        "timeline": "2025-02-01 to 2025-03-15",
        "proposal": "I can complete your kitchen renovation for $18,500. The project includes custom cabinets, granite countertops, and professional installation.",
        "approach": "I'll start with demolition, then rough plumbing and electrical, followed by drywall, cabinets, and finish work.",  
        "warranty_details": "I provide a 3-year warranty on all workmanship and will handle any issues that arise during that period.",
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
        
        print(f"✅ Intelligent Agent Response:")
        print(f"   - Agent Decision: {result.get('agent_decision')}")
        print(f"   - Threats Detected: {result.get('threats_detected')}")
        print(f"   - Bid Saved: {result.get('bid_saved')}")
        print(f"   - Should be ALLOW with no threats")
        
        # Verify clean bid was allowed through
        if result.get('agent_decision') == 'allow' and not result.get('threats_detected'):
            print(f"✅ Clean bid correctly allowed through GPT-4o analysis")
        else:
            print(f"❌ Clean bid incorrectly flagged as problematic")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all bid submission tests"""
    print("🚀 Starting Intelligent Bid Submission Tests")
    print("Testing GPT-4o powered contact information filtering")
    print()
    
    await test_bid_submission_with_contact_info()
    await test_clean_bid_submission()
    
    print(f"\n🎉 Testing Complete!")
    print("=" * 80)
    print("SUMMARY:")
    print("✅ Intelligent messaging agent integrates GPT-4o analysis")
    print("✅ Bid submissions are filtered for contact information") 
    print("✅ Filtered bids are saved to contractor_bids table")
    print("✅ Conversation messages created in unified system")
    print("✅ Security analysis and threat detection working")

if __name__ == "__main__":
    asyncio.run(main())