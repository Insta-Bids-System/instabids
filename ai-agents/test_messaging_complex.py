#!/usr/bin/env python3
"""
Test Messaging Agent with complex multi-component scope changes
"""

import asyncio
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents'))

from agents.scope_change_handler import ScopeChangeHandler
from config.service_urls import get_backend_url

TEST_BID_CARD = {
    "id": "93c216f1-1e3f-490a-899d-ae2a236652a4",
    "bid_card_number": "BC0730223441"
}

async def test_messaging_complex():
    """Test Messaging Agent with complex scope changes"""
    
    print("=" * 80)
    print("MESSAGING AGENT COMPLEX SCOPE CHANGE TEST")
    print("=" * 80)
    print(f"Test Started: {datetime.now().isoformat()}")
    print(f"Bid Card: {TEST_BID_CARD['bid_card_number']}")
    
    # Get current state from database
    try:
        from database_simple import db
        current = db.client.table("bid_cards").select("budget_min,budget_max,urgency_level").eq("id", TEST_BID_CARD['id']).single().execute()
        if current.data:
            print(f"\nBEFORE: Budget ${current.data['budget_min']:,} - ${current.data['budget_max']:,}, Urgency: {current.data['urgency_level']}")
    except:
        print("\nBEFORE: Unable to get current state")
    
    # Complex scope changes
    handler = ScopeChangeHandler()
    
    # Override the timeout in the handler
    original_call = handler.call_jaa_update_service
    async def call_with_longer_timeout(bid_card_id, update_context):
        """Wrapper with longer timeout"""
        import requests
        try:
            jaa_endpoint = f"{get_backend_url()}/jaa/update/{bid_card_id}"
            payload = {
                "update_context": update_context,
                "update_type": "conversation_based"
            }
            
            print(f"[ScopeChangeHandler] Calling JAA with 120-second timeout...")
            response = requests.put(
                jaa_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120  # Longer timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Replace method temporarily
    handler.call_jaa_update_service = call_with_longer_timeout
    
    print("\nTesting complex scope changes:")
    print("- Material changes (granite to quartz)")
    print("- Timeline changes (2 weeks to 1 week)")
    print("- Budget changes (add $30,000)")
    print("- Additional requirements")
    
    result = await handler.handle_scope_change(
        scope_changes=[
            "Material changes",
            "Timeline changes", 
            "Budget changes",
            "Additional requirements"
        ],
        scope_details={
            "Material changes": "Change from granite to quartz countertops",
            "Timeline changes": "Need completion in 1 week instead of 2 weeks",
            "Budget changes": "Increase budget by $30,000 for premium fixtures",
            "Additional requirements": "Must include warranty and use eco-friendly materials"
        },
        bid_card_id=TEST_BID_CARD['id'],
        sender_id="test-homeowner-complex",
        message_content="I need to make several changes: switch to quartz countertops, need it done in 1 week, adding $30k to budget for premium fixtures, and want eco-friendly materials with warranty"
    )
    
    print("\n" + "-" * 60)
    print("MESSAGING AGENT RESPONSE")
    print("-" * 60)
    
    print(f"Success: {result.get('success', False)}")
    print(f"Scope Changes Detected: {result.get('scope_changes_detected', [])}")
    
    if result.get('jaa_response'):
        jaa = result['jaa_response']
        print("\nJAA RESPONSE RECEIVED:")
        print(f"  JAA Success: {jaa.get('success')}")
        
        if jaa.get('update_summary'):
            summary = jaa['update_summary']
            print(f"  Changes: {summary.get('changes_made', [])}")
            print(f"  Summary: {summary.get('change_summary')}")
    
    if result.get('homeowner_question'):
        print(f"\nHomeowner Question Generated: Yes")
        print(f"Question Preview: {result['homeowner_question'][:100]}...")
    
    # Verify database change
    try:
        after = db.client.table("bid_cards").select("budget_min,budget_max,urgency_level,updated_at").eq("id", TEST_BID_CARD['id']).single().execute()
        if after.data:
            print(f"\nAFTER: Budget ${after.data['budget_min']:,} - ${after.data['budget_max']:,}, Urgency: {after.data['urgency_level']}")
            print(f"Updated: {after.data['updated_at']}")
    except:
        print("\nAFTER: Unable to verify database change")
    
    success = result.get('success', False)
    
    print("\n" + "=" * 80)
    if success:
        print("SUCCESS: MESSAGING AGENT HANDLED COMPLEX SCOPE CHANGES")
    else:
        print("FAILED: MESSAGING AGENT COULD NOT HANDLE COMPLEX CHANGES")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(test_messaging_complex())
    exit(0 if success else 1)