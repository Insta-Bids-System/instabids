#!/usr/bin/env python3
"""
CIA Agent JAA Integration Test
Tests CIA Agent calling JAA service instead of direct bid card updates
"""

import asyncio
import sys
import os

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents'))

from agents.cia.agent import CustomerInterfaceAgent
from database_simple import db
import json

async def test_cia_jaa_integration():
    """Test CIA Agent → JAA service integration with real bid card verification"""
    
    print("CIA → JAA INTEGRATION TEST")
    print("=" * 50)
    
    # Step 1: Get an actual bid card from database
    print("\n1. FINDING ACTUAL BID CARD...")
    bid_cards = db.client.table("bid_cards").select("*").limit(1).execute()
    
    if not bid_cards.data:
        print("❌ No bid cards found in database")
        return False
        
    bid_card = bid_cards.data[0]
    bid_card_id = bid_card["id"]
    bid_card_number = bid_card["bid_card_number"]
    
    print(f"✅ Found bid card: {bid_card_number}")
    print(f"   ID: {bid_card_id}")
    print(f"   Project Type: {bid_card.get('project_type', 'Unknown')}")
    print(f"   Current Budget: ${bid_card.get('budget_min', 0):,} - ${bid_card.get('budget_max', 0):,}")
    
    # Step 2: Capture current state
    print("\n2. CAPTURING CURRENT BID CARD STATE...")
    original_budget_max = bid_card.get("budget_max", 15000)
    original_budget_min = bid_card.get("budget_min", 10000)
    original_metadata = bid_card.get("metadata")
    
    print(f"   Original Budget: ${original_budget_min:,} - ${original_budget_max:,}")
    print(f"   Original Metadata Keys: {list(json.loads(original_metadata or '{}').keys()) if original_metadata else 'None'}")
    
    # Step 3: Initialize CIA Agent
    print("\n3. INITIALIZING CIA AGENT...")
    api_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
    cia = CustomerInterfaceAgent(api_key)
    print("✅ CIA Agent initialized")
    
    # Step 4: Test CIA modification detection and JAA service call
    print("\n4. TESTING CIA MODIFICATION → JAA SERVICE...")
    test_message = f"I want to increase the budget to $25,000 for my {bid_card.get('project_type', 'kitchen')} project"
    
    print(f"   Test Message: '{test_message}'")
    print(f"   Target Bid Card: {bid_card_number}")
    
    try:
        # Call CIA handle_modification which should call JAA service
        result = await cia.handle_modification(
            message=test_message,
            bid_card_number=bid_card_number,
            bid_card_id=bid_card_id,
            user_id="test-user-123",
            session_id="cia-jaa-test-session"
        )
        
        print(f"\n   CIA Response: {json.dumps(result, indent=4)}")
        
        # Step 5: Verify JAA service was called successfully
        if result.get("success"):
            print("✅ CIA successfully called JAA service")
            
            # Check if JAA response is included
            jaa_response = result.get("jaa_response")
            if jaa_response:
                print(f"   JAA Update Summary: {jaa_response.get('update_summary', {})}")
                print(f"   Affected Contractors: {len(jaa_response.get('affected_contractors', []))}")
                
                # Step 6: Verify actual database changes
                print("\n5. VERIFYING DATABASE CHANGES...")
                updated_bid_card = db.client.table("bid_cards").select("*").eq("id", bid_card_id).single().execute()
                
                if updated_bid_card.data:
                    new_budget_max = updated_bid_card.data.get("budget_max")
                    new_budget_min = updated_bid_card.data.get("budget_min")
                    new_metadata = updated_bid_card.data.get("metadata")
                    
                    print(f"   Updated Budget: ${new_budget_min:,} - ${new_budget_max:,}")
                    print(f"   Budget Changed: {new_budget_max != original_budget_max}")
                    
                    if new_metadata:
                        new_meta_dict = json.loads(new_metadata)
                        print(f"   New Metadata Keys: {list(new_meta_dict.keys())}")
                        if "jaa_updates" in new_meta_dict:
                            print(f"   JAA Update Count: {len(new_meta_dict['jaa_updates'])}")
                    
                    # Verify the change was actually applied
                    if new_budget_max == 25000:
                        print("✅ BUDGET SUCCESSFULLY UPDATED TO $25,000")
                        test_passed = True
                    else:
                        print(f"❌ Budget not updated correctly. Expected: $25,000, Got: ${new_budget_max:,}")
                        test_passed = False
                else:
                    print("❌ Could not retrieve updated bid card")
                    test_passed = False
            else:
                print("❌ No JAA response in CIA result")
                test_passed = False
        else:
            print(f"❌ CIA modification failed: {result.get('error', 'Unknown error')}")
            test_passed = False
            
    except Exception as e:
        print(f"❌ ERROR during CIA → JAA test: {str(e)}")
        test_passed = False
    
    # Step 7: Results Summary
    print("\n" + "=" * 50)
    print("CIA → JAA INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    if test_passed:
        print("✅ TEST PASSED!")
        print("✅ CIA Agent successfully called JAA service")
        print("✅ JAA service updated bid card in database") 
        print("✅ Budget change verified: $25,000")
        print("✅ Integration working correctly")
    else:
        print("❌ TEST FAILED!")
        print("❌ CIA → JAA integration not working correctly")
    
    return test_passed

if __name__ == "__main__":
    success = asyncio.run(test_cia_jaa_integration())
    exit(0 if success else 1)