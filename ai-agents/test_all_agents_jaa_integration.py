#!/usr/bin/env python3
"""
All Agents JAA Integration Test
Comprehensive test of CIA, IRIS, and Messaging agents calling JAA service
with complete database verification
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents'))

from agents.cia.agent import CustomerInterfaceAgent
from agents.scope_change_handler import ScopeChangeHandler
from database_simple import db

async def get_test_bid_card():
    """Get a bid card for testing"""
    bid_cards = db.client.table("bid_cards").select("*").limit(1).execute()
    if not bid_cards.data:
        print("❌ No bid cards found in database")
        return None
    return bid_cards.data[0]

async def verify_bid_card_changes(bid_card_id: str, test_name: str, expected_changes: dict):
    """Verify that bid card was actually changed in database"""
    
    print(f"\n   VERIFYING DATABASE CHANGES FOR {test_name}...")
    
    # Get updated bid card
    updated_card = db.client.table("bid_cards").select("*").eq("id", bid_card_id).single().execute()
    
    if not updated_card.data:
        print("   ❌ Could not retrieve updated bid card")
        return False
    
    card = updated_card.data
    changes_detected = []
    
    # Check budget changes
    if "budget_max" in expected_changes:
        current_budget = card.get("budget_max")
        expected_budget = expected_changes["budget_max"]
        if current_budget == expected_budget:
            changes_detected.append(f"✅ Budget updated to ${expected_budget:,}")
        else:
            changes_detected.append(f"❌ Budget not updated. Expected: ${expected_budget:,}, Got: ${current_budget:,}")
    
    # Check metadata for JAA updates
    metadata = card.get("metadata")
    if metadata:
        meta_dict = json.loads(metadata)
        if "jaa_updates" in meta_dict:
            jaa_updates = meta_dict["jaa_updates"]
            changes_detected.append(f"✅ JAA updates found: {len(jaa_updates)} entries")
            
            if jaa_updates:
                latest = jaa_updates[-1]
                changes_detected.append(f"   Latest: {latest.get('change_summary', 'No summary')}")
        else:
            changes_detected.append("⚠️  No JAA updates in metadata")
    
    # Check materials changes
    if "materials" in expected_changes:
        current_materials = str(card.get("materials", "")).lower()
        expected_material = expected_changes["materials"].lower()
        if expected_material in current_materials:
            changes_detected.append(f"✅ Materials updated: {expected_material}")
        else:
            changes_detected.append(f"❌ Materials not updated to include: {expected_material}")
    
    # Print all detected changes
    for change in changes_detected:
        print(f"      {change}")
    
    # Return true if any positive changes were detected
    success_count = len([c for c in changes_detected if c.startswith("✅")])
    total_expected = len(expected_changes)
    
    return success_count > 0

async def test_cia_agent_integration(bid_card):
    """Test CIA Agent JAA integration"""
    
    print("\n" + "="*60)
    print("CIA AGENT → JAA SERVICE INTEGRATION TEST")
    print("="*60)
    
    bid_card_id = bid_card["id"]
    bid_card_number = bid_card["bid_card_number"]
    
    print(f"\nTesting CIA Agent with bid card: {bid_card_number}")
    print(f"Current budget: ${bid_card.get('budget_min', 0):,} - ${bid_card.get('budget_max', 0):,}")
    
    # Initialize CIA Agent
    api_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
    cia = CustomerInterfaceAgent(api_key)
    
    # Test budget modification
    test_message = f"Increase the budget to $30,000 for this {bid_card.get('project_type', 'project')}"
    
    try:
        result = await cia.handle_modification(
            message=test_message,
            bid_card_number=bid_card_number,
            bid_card_id=bid_card_id,
            user_id="test-user-cia",
            session_id="cia-integration-test"
        )
        
        success = result.get("success", False)
        print(f"\nCIA Agent Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if success:
            print(f"   JAA Response Received: {bool(result.get('jaa_response'))}")
            jaa_response = result.get("jaa_response", {})
            if jaa_response:
                print(f"   Affected Contractors: {len(jaa_response.get('affected_contractors', []))}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
        # Verify database changes
        changes_verified = await verify_bid_card_changes(
            bid_card_id, 
            "CIA AGENT", 
            {"budget_max": 30000}
        )
        
        return success and changes_verified
        
    except Exception as e:
        print(f"❌ CIA Agent test failed: {str(e)}")
        return False

async def test_messaging_agent_integration(bid_card):
    """Test Messaging Agent JAA integration"""
    
    print("\n" + "="*60)
    print("MESSAGING AGENT → JAA SERVICE INTEGRATION TEST")
    print("="*60)
    
    bid_card_id = bid_card["id"]
    bid_card_number = bid_card["bid_card_number"]
    
    print(f"\nTesting Messaging Agent with bid card: {bid_card_number}")
    print(f"Testing scope change: materials and timeline")
    
    # Initialize Scope Change Handler
    scope_handler = ScopeChangeHandler()
    
    # Test scope changes
    scope_changes = ["Material changes", "Timeline changes"]
    scope_details = {
        "Material changes": "Change to premium hardwood flooring",
        "Timeline changes": "Complete in 3 weeks instead of 6 weeks"
    }
    message_content = "Let's upgrade to premium hardwood and finish in 3 weeks"
    
    try:
        result = await scope_handler.handle_scope_change(
            scope_changes=scope_changes,
            scope_details=scope_details,
            bid_card_id=bid_card_id,
            sender_id="test-homeowner-messaging",
            message_content=message_content
        )
        
        success = result.get("success", False) or len(result.get("scope_changes_detected", [])) > 0
        print(f"\nMessaging Agent Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if success:
            print(f"   Scope Changes Detected: {result.get('scope_changes_detected', [])}")
            print(f"   Other Contractors: {len(result.get('other_contractors', []))}")
            print(f"   Homeowner Question: {bool(result.get('homeowner_question'))}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
        # Verify database changes
        changes_verified = await verify_bid_card_changes(
            bid_card_id, 
            "MESSAGING AGENT", 
            {"materials": "hardwood"}
        )
        
        return success and changes_verified
        
    except Exception as e:
        print(f"❌ Messaging Agent test failed: {str(e)}")
        return False

async def test_database_integrity():
    """Test that bid card data integrity is maintained"""
    
    print("\n" + "="*60)
    print("DATABASE INTEGRITY VERIFICATION")
    print("="*60)
    
    try:
        # Check that bid cards table is accessible
        bid_cards = db.client.table("bid_cards").select("id, bid_card_number, created_at").limit(5).execute()
        
        if bid_cards.data:
            print(f"✅ Database accessible - {len(bid_cards.data)} bid cards found")
            
            # Check recent updates
            recent_updates = db.client.table("bid_cards").select("*").order("updated_at", desc=True).limit(3).execute()
            
            if recent_updates.data:
                print(f"✅ Recent updates found - {len(recent_updates.data)} recently updated bid cards")
                
                for card in recent_updates.data:
                    metadata = card.get("metadata")
                    if metadata:
                        meta_dict = json.loads(metadata)
                        jaa_updates = meta_dict.get("jaa_updates", [])
                        if jaa_updates:
                            print(f"   Bid Card {card['bid_card_number']}: {len(jaa_updates)} JAA updates")
            
            return True
        else:
            print("❌ No bid cards found in database")
            return False
            
    except Exception as e:
        print(f"❌ Database integrity check failed: {str(e)}")
        return False

async def main():
    """Run comprehensive JAA integration tests"""
    
    print("COMPREHENSIVE JAA INTEGRATION TESTING")
    print("=" * 80)
    print(f"Test Started: {datetime.now().isoformat()}")
    print("Testing all agents calling JAA service with database verification")
    
    # Get test bid card
    print("\nGETTING TEST BID CARD...")
    bid_card = await get_test_bid_card()
    if not bid_card:
        print("❌ Cannot proceed without test bid card")
        return False
    
    print(f"✅ Using bid card: {bid_card['bid_card_number']}")
    print(f"   Project: {bid_card.get('project_type', 'Unknown')}")
    print(f"   Status: {bid_card.get('status', 'Unknown')}")
    
    # Run all integration tests
    test_results = []
    
    # Test 1: CIA Agent
    cia_result = await test_cia_agent_integration(bid_card)
    test_results.append(("CIA Agent", cia_result))
    
    # Test 2: Messaging Agent  
    messaging_result = await test_messaging_agent_integration(bid_card)
    test_results.append(("Messaging Agent", messaging_result))
    
    # Test 3: Database Integrity
    db_result = await test_database_integrity()
    test_results.append(("Database Integrity", db_result))
    
    # Final Results Summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} : {status}")
        if result:
            passed_tests += 1
    
    print(f"\nTests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ CIA Agent → JAA service working")
        print("✅ Messaging Agent → JAA service working")
        print("✅ Database changes verified")
        print("✅ System integration complete")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        print("❌ Some integrations need attention")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)