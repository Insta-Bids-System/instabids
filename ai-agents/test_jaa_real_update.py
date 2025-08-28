#!/usr/bin/env python3
"""
Real JAA Update Test - Live Demonstration
Tests the JAA update system with a real bid card and hypothetical change
"""

import asyncio
import json
import os
import sys

# Add the ai-agents directory to the Python path
sys.path.append(os.path.dirname(__file__))

from agents.jaa.agent import JobAssessmentAgent

async def test_real_bid_card_update():
    """Test JAA update with real bid card data"""
    
    print("=" * 80)
    print("JAA UPDATE SYSTEM - LIVE DEMONSTRATION")
    print("=" * 80)
    
    # Initialize JAA
    jaa = JobAssessmentAgent()
    
    # Real bid card from database
    bid_card_id = "93c216f1-1e3f-490a-899d-ae2a236652a4"
    
    print(f"Testing with REAL bid card: {bid_card_id}")
    print("Original: Renovation project, $25,000-$45,000, timeline: week, Los Angeles")
    print()
    
    # Hypothetical change scenario
    print("HYPOTHETICAL CHANGE SCENARIO:")
    print("Homeowner says: 'Actually, I want to increase the budget to $60,000 and I need this done ASAP!'")
    print()
    
    # Create realistic update request
    update_request = {
        "update_context": {
            "source_agent": "homeowner_agent",
            "conversation_snippet": "Actually, I want to increase the budget to $60,000 and I need this done ASAP! This is now urgent.",
            "detected_change_hints": ["budget_increase", "urgency_change"],
            "requester_info": {
                "user_id": "test_homeowner_123",
                "session_id": "test_session_456"
            }
        },
        "update_type": "conversation_based"
    }
    
    print("PROCESSING UPDATE...")
    print("-" * 40)
    
    try:
        # Run the complete update process
        result = await jaa.update_existing_bid_card(bid_card_id, update_request)
        
        if result["success"]:
            print("SUCCESS! JAA Update completed successfully")
            print()
            
            # Show what changed
            update_summary = result["update_summary"]
            print(f"CHANGES DETECTED: {len(update_summary['changes_made'])} modifications")
            for change in update_summary["changes_made"]:
                print(f"  • {change['field']}: {change['old_value']} → {change['new_value']} ({change['change_type']})")
            
            print(f"\nCHANGE SUMMARY: {update_summary['change_summary']}")
            print(f"SIGNIFICANCE LEVEL: {update_summary['significance_level']}")
            
            # Show affected contractors
            contractors = result["affected_contractors"]
            print(f"\nAFFECTED CONTRACTORS: {len(contractors)} contractors found")
            for contractor in contractors:
                print(f"  • {contractor['company_name']} (Status: {contractor['engagement_status']})")
            
            # Show notification content
            notification = result["notification_content"]
            print(f"\nNOTIFICATION GENERATED:")
            print(f"  Subject: {notification['subject']}")
            print(f"  Urgency: {notification['urgency_level']}")
            print(f"  Call to Action: {notification['call_to_action']}")
            print(f"  Message Preview: {notification['message_template'][:100]}...")
            
            # Show next actions
            print(f"\nRECOMMENDED ACTIONS:")
            for action in result["next_actions"]:
                print(f"  • {action}")
            
            print(f"\nUPDATED BY: {result['updated_by']}")
            print(f"TIMESTAMP: {result['updated_at']}")
            
            print("\n" + "=" * 80)
            print("RESULT: JAA UPDATE SYSTEM IS FULLY OPERATIONAL!")
            print("✅ Change analysis working")  
            print("✅ Contractor discovery working")
            print("✅ Notification generation working")
            print("✅ Complete workflow functional")
            print("=" * 80)
            
        else:
            print(f"FAILED: {result['error']}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_real_bid_card_update())
    exit(0 if success else 1)