#!/usr/bin/env python3
"""
Test BSA memory integration with real multi-turn conversations
Verifies that contractor context is properly saved and restored across sessions
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

from agents.bsa.memory_integration import (
    BSAMemoryIntegrator, 
    save_bsa_state, 
    restore_bsa_state
)
from deepagents.state import DeepAgentState

async def test_bsa_multi_turn_conversation():
    """Test BSA with real multi-turn conversation to verify memory persistence"""
    
    print("🧪 TESTING BSA MULTI-TURN CONVERSATION WITH MEMORY PERSISTENCE")
    print("=" * 80)
    
    contractor_id = "test-contractor-memory-001"
    session_id = "session-memory-001"
    
    try:
        # ============================================================================
        # TURN 1: First conversation with contractor
        # ============================================================================
        print("📞 CONVERSATION TURN 1: Initial contractor introduction")
        
        # Create initial state
        initial_state: DeepAgentState = {
            "messages": [
                {
                    "role": "user", 
                    "content": "Hi, I'm John from Miami Landscaping. We specialize in lawn installation and maintenance.",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Hello John! Welcome to InstaBids. I see you're from Miami Landscaping with expertise in lawn installation and maintenance. Let me search for relevant projects in your area. I found 3 lawn projects available for bidding in Miami.",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "todos": [],
            "files": {},
            "contractor_id": contractor_id,
            "session_id": session_id,
            "contractor_profile": {
                "company_name": "Miami Landscaping",
                "contact_name": "John",
                "location": "Miami",
                "specialties": ["lawn installation", "lawn maintenance"],
                "years_in_business": None,
                "rating": None
            },
            "current_bid_cards": [
                {
                    "bid_card_id": "bc-001",
                    "project_type": "lawn_installation", 
                    "location": "Miami",
                    "budget_range": "$3000-5000",
                    "urgency": "standard"
                },
                {
                    "bid_card_id": "bc-002",
                    "project_type": "lawn_maintenance",
                    "location": "Miami Beach", 
                    "budget_range": "$200-400/month",
                    "urgency": "ongoing"
                },
                {
                    "bid_card_id": "bc-003",
                    "project_type": "sod_installation",
                    "location": "Coral Gables",
                    "budget_range": "$2000-3500", 
                    "urgency": "emergency"
                }
            ],
            "conversation_context": {
                "last_search": "lawn projects Miami",
                "search_radius": 25,
                "projects_found": 3,
                "contractor_interested": True
            },
            "sub_agent_calls": [
                {
                    "agent": "SEARCH-AGENT",
                    "query": "lawn installation projects Miami",
                    "results": 3,
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        
        # Save first conversation state
        save_success = await save_bsa_state(contractor_id, initial_state, session_id)
        print(f"💾 Conversation 1 save result: {save_success}")
        
        if not save_success:
            print("❌ FAILED: Could not save initial conversation state")
            return False
            
        # ============================================================================
        # TURN 2: Contractor returns with questions
        # ============================================================================
        print("\n📞 CONVERSATION TURN 2: Contractor returns with bid questions")
        
        # Restore state from memory
        restored_state = await restore_bsa_state(contractor_id, session_id)
        print(f"🔄 State restored: {restored_state.get('session_restored', False)}")
        print(f"📊 Restored messages: {len(restored_state.get('messages', []))} messages")
        print(f"🏗️ Restored projects: {len(restored_state.get('current_bid_cards', []))} projects")
        
        # Add new conversation turn
        if "messages" not in restored_state:
            restored_state["messages"] = []
            
        restored_state["messages"].extend([
            {
                "role": "user",
                "content": "I'm interested in the emergency sod installation project in Coral Gables. Can you tell me more about the timeline and requirements?",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "role": "assistant", 
                "content": "Great choice! The Coral Gables sod installation is an emergency project with a $2000-3500 budget. Based on your lawn installation expertise, you're a perfect fit. The homeowner needs this completed within 48 hours. The project involves installing 1,200 sq ft of premium sod with soil preparation.",
                "timestamp": datetime.utcnow().isoformat()
            }
        ])
        
        # Update context with new information
        restored_state["conversation_context"].update({
            "project_interest": "bc-003",
            "project_name": "Coral Gables sod installation",
            "timeline_discussed": "48 hours",
            "budget_discussed": "$2000-3500"
        })
        
        # Add sub-agent call for project details
        restored_state["sub_agent_calls"].append({
            "agent": "BID-ANALYSIS-AGENT",
            "project_id": "bc-003",
            "analysis": "Contractor matches: lawn installation experience, Miami location, emergency availability",
            "recommendation": "High match - recommend immediate bid submission",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Save updated state
        save_success_2 = await save_bsa_state(contractor_id, restored_state, session_id)
        print(f"💾 Conversation 2 save result: {save_success_2}")
        
        # ============================================================================
        # TURN 3: Contractor submits bid
        # ============================================================================
        print("\n📞 CONVERSATION TURN 3: Contractor submits bid")
        
        # Restore state again
        final_state = await restore_bsa_state(contractor_id, session_id)
        print(f"🔄 Final state restored: {final_state.get('session_restored', False)}")
        print(f"📊 Final messages: {len(final_state.get('messages', []))} messages")
        
        # Add bid submission conversation
        final_state["messages"].extend([
            {
                "role": "user",
                "content": "I'd like to submit a bid for $2,750 for the Coral Gables project. I can complete it in 36 hours with premium Bermuda sod and include 1-year maintenance warranty.",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "role": "assistant",
                "content": "Excellent! Your bid of $2,750 has been submitted for the Coral Gables sod installation project. Your 36-hour timeline and premium Bermuda sod with warranty makes this a competitive offer. The homeowner will review bids and contact you within 24 hours.",
                "timestamp": datetime.utcnow().isoformat()
            }
        ])
        
        # Update with bid submission
        final_state["submission_history"] = [{
            "bid_card_id": "bc-003",
            "bid_amount": 2750,
            "timeline": "36 hours",
            "sod_type": "Premium Bermuda",
            "warranty": "1 year maintenance",
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "submitted"
        }]
        
        final_state["conversation_context"].update({
            "bid_submitted": True,
            "bid_amount": 2750,
            "next_action": "await_homeowner_response"
        })
        
        # Save final state
        save_success_3 = await save_bsa_state(contractor_id, final_state, session_id)
        print(f"💾 Conversation 3 save result: {save_success_3}")
        
        # ============================================================================
        # VERIFICATION: Test memory persistence across sessions
        # ============================================================================
        print("\n🔍 VERIFICATION: Testing complete conversation memory")
        
        # Restore complete conversation state
        complete_state = await restore_bsa_state(contractor_id, session_id)
        
        print(f"📈 MEMORY VERIFICATION RESULTS:")
        print(f"   Total messages: {len(complete_state.get('messages', []))}")
        print(f"   Contractor profile saved: {'contractor_profile' in complete_state}")
        print(f"   Projects context saved: {len(complete_state.get('current_bid_cards', []))} projects")
        print(f"   Sub-agent calls saved: {len(complete_state.get('sub_agent_calls', []))} calls")
        print(f"   Bid history saved: {len(complete_state.get('submission_history', []))} bids")
        print(f"   Session restored: {complete_state.get('session_restored', False)}")
        
        # Verify key conversation elements are preserved
        messages = complete_state.get('messages', [])
        if len(messages) >= 6:
            print(f"   First message: {messages[0]['content'][:50]}...")
            print(f"   Last message: {messages[-1]['content'][:50]}...")
        
        contractor_profile = complete_state.get('contractor_profile', {})
        if contractor_profile:
            print(f"   Company: {contractor_profile.get('company_name', 'Not saved')}")
            print(f"   Contact: {contractor_profile.get('contact_name', 'Not saved')}")
            print(f"   Specialties: {contractor_profile.get('specialties', [])}")
        
        conversation_context = complete_state.get('conversation_context', {})
        if conversation_context:
            print(f"   Last search: {conversation_context.get('last_search', 'Not saved')}")
            print(f"   Project interest: {conversation_context.get('project_interest', 'Not saved')}")
            print(f"   Bid submitted: {conversation_context.get('bid_submitted', False)}")
        
        # ============================================================================
        # SUCCESS CRITERIA
        # ============================================================================
        success_criteria = {
            "conversation_turns_saved": len(messages) >= 6,
            "contractor_profile_preserved": bool(contractor_profile),
            "project_context_maintained": len(complete_state.get('current_bid_cards', [])) == 3,
            "sub_agent_calls_tracked": len(complete_state.get('sub_agent_calls', [])) >= 2,
            "bid_submission_recorded": len(complete_state.get('submission_history', [])) == 1,
            "session_memory_working": complete_state.get('session_restored', False)
        }
        
        all_success = all(success_criteria.values())
        
        print(f"\n✅ SUCCESS CRITERIA:")
        for criterion, passed in success_criteria.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {criterion}: {status}")
        
        print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS - BSA memory persistence working!' if all_success else '❌ FAILURE - Memory system has issues'}")
        
        return all_success
        
    except Exception as e:
        print(f"❌ ERROR during BSA conversation testing: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cross_session_memory():
    """Test that contractor context persists across different sessions"""
    
    print("\n🔄 TESTING CROSS-SESSION MEMORY PERSISTENCE")
    print("=" * 50)
    
    contractor_id = "test-contractor-cross-session"
    
    try:
        # Session 1: Initial conversation
        session_1_state: DeepAgentState = {
            "messages": [
                {
                    "role": "user",
                    "content": "I'm Maria from Elite Pool Services. We do pool installation and maintenance in Tampa Bay area.",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "contractor_profile": {
                "company_name": "Elite Pool Services",
                "contact_name": "Maria", 
                "location": "Tampa Bay",
                "specialties": ["pool installation", "pool maintenance"],
                "service_radius": 30
            },
            "conversation_context": {
                "location_preference": "Tampa Bay",
                "radius_miles": 30,
                "service_types": ["pool installation", "pool maintenance"]
            }
        }
        
        # Save session 1
        save_1 = await save_bsa_state(contractor_id, session_1_state, "session-001")
        print(f"💾 Session 1 saved: {save_1}")
        
        # Session 2: Different session, should restore context
        session_2_state = await restore_bsa_state(contractor_id, "session-002")
        print(f"🔄 Session 2 restored: {session_2_state.get('session_restored', False)}")
        print(f"👤 Company name preserved: {session_2_state.get('contractor_profile', {}).get('company_name', 'Not found')}")
        print(f"📍 Location preserved: {session_2_state.get('conversation_context', {}).get('location_preference', 'Not found')}")
        
        # Add to session 2
        session_2_state["messages"].append({
            "role": "user", 
            "content": "Show me pool maintenance projects within 50 miles of Tampa.",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        session_2_state["conversation_context"]["radius_miles"] = 50
        
        # Save session 2
        save_2 = await save_bsa_state(contractor_id, session_2_state, "session-002")
        print(f"💾 Session 2 saved: {save_2}")
        
        # Session 3: Verify latest context
        session_3_state = await restore_bsa_state(contractor_id, "session-003")
        radius = session_3_state.get('conversation_context', {}).get('radius_miles', 0)
        print(f"🎯 Latest radius setting preserved: {radius} miles")
        
        success = (
            session_2_state.get('contractor_profile', {}).get('company_name') == "Elite Pool Services" and
            radius == 50
        )
        
        print(f"🎯 Cross-session memory test: {'✅ SUCCESS' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        print(f"❌ ERROR in cross-session test: {e}")
        return False

async def main():
    """Run all BSA memory tests"""
    
    print("🚀 STARTING BSA MEMORY INTEGRATION TESTS")
    print("=" * 80)
    
    # Test 1: Multi-turn conversation memory
    test_1_success = await test_bsa_multi_turn_conversation()
    
    # Test 2: Cross-session memory persistence  
    test_2_success = await test_cross_session_memory()
    
    # Overall results
    print("\n" + "=" * 80)
    print("📋 FINAL TEST RESULTS:")
    print(f"   Multi-turn conversation memory: {'✅ PASS' if test_1_success else '❌ FAIL'}")
    print(f"   Cross-session memory persistence: {'✅ PASS' if test_2_success else '❌ FAIL'}")
    
    overall_success = test_1_success and test_2_success
    print(f"\n🎯 OVERALL BSA MEMORY SYSTEM: {'✅ FULLY OPERATIONAL' if overall_success else '❌ NEEDS FIXES'}")
    
    if overall_success:
        print("\n🎉 BSA memory integration is working correctly!")
        print("   ✅ Contractors can have multi-turn conversations")
        print("   ✅ Context is preserved across conversation turns")
        print("   ✅ Memory persists across different sessions")
        print("   ✅ All conversation data and analysis is saved")
        print("   ✅ Ready for production contractor interactions")
    else:
        print("\n⚠️  BSA memory system needs investigation")
        print("   Check database connections and table structure")
        print("   Verify foreign key constraints are working")
        print("   Test individual memory functions")

if __name__ == "__main__":
    asyncio.run(main())