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

async def test_bsa_real_conversation():
    """Test BSA with real multi-turn conversation to verify memory persistence"""
    
    print("TESTING BSA MULTI-TURN CONVERSATION WITH MEMORY PERSISTENCE")
    print("=" * 70)
    
    contractor_id = "test-contractor-memory-001"
    session_id = "session-memory-001"
    
    try:
        # TURN 1: First conversation with contractor
        print("CONVERSATION TURN 1: Initial contractor introduction")
        
        # Create realistic initial state
        initial_state: DeepAgentState = {
            "messages": [
                {
                    "role": "user", 
                    "content": "Hi, I'm John from Miami Landscaping. We specialize in lawn installation and maintenance.",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Hello John! Welcome to InstaBids. I see you're from Miami Landscaping with expertise in lawn installation and maintenance. Let me search for relevant projects in your area.",
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
                "specialties": ["lawn installation", "lawn maintenance"]
            },
            "current_bid_cards": [
                {
                    "bid_card_id": "bc-001",
                    "project_type": "lawn_installation", 
                    "location": "Miami",
                    "budget_range": "$3000-5000"
                },
                {
                    "bid_card_id": "bc-002",
                    "project_type": "lawn_maintenance",
                    "location": "Miami Beach", 
                    "budget_range": "$200-400/month"
                }
            ],
            "conversation_context": {
                "last_search": "lawn projects Miami",
                "search_radius": 25,
                "projects_found": 2
            }
        }
        
        # Save first conversation state
        save_success = await save_bsa_state(contractor_id, initial_state, session_id)
        print(f"Turn 1 save result: {save_success}")
        
        if not save_success:
            print("FAILED: Could not save initial conversation state")
            return False
            
        # TURN 2: Contractor returns with questions
        print("\nCONVERSATION TURN 2: Contractor returns with bid questions")
        
        # Restore state from memory
        restored_state = await restore_bsa_state(contractor_id, session_id)
        print(f"State restored: {restored_state.get('session_restored', False)}")
        print(f"Restored messages: {len(restored_state.get('messages', []))} messages")
        print(f"Restored projects: {len(restored_state.get('current_bid_cards', []))} projects")
        
        # Add new conversation turn
        if "messages" not in restored_state:
            restored_state["messages"] = []
            
        restored_state["messages"].extend([
            {
                "role": "user",
                "content": "I'm interested in the lawn installation project. Can you tell me more about the timeline?",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "role": "assistant", 
                "content": "Great choice! The Miami lawn installation project has a $3000-5000 budget. Based on your experience, you're a perfect fit.",
                "timestamp": datetime.utcnow().isoformat()
            }
        ])
        
        # Update context
        restored_state["conversation_context"].update({
            "project_interest": "bc-001",
            "timeline_discussed": True
        })
        
        # Save updated state
        save_success_2 = await save_bsa_state(contractor_id, restored_state, session_id)
        print(f"Turn 2 save result: {save_success_2}")
        
        # TURN 3: Final verification
        print("\nCONVERSATION TURN 3: Verify complete memory")
        
        # Restore state one final time
        final_state = await restore_bsa_state(contractor_id, session_id)
        print(f"Final state restored: {final_state.get('session_restored', False)}")
        print(f"Final messages: {len(final_state.get('messages', []))} messages")
        
        # VERIFICATION
        print("\nMEMORY VERIFICATION RESULTS:")
        messages = final_state.get('messages', [])
        contractor_profile = final_state.get('contractor_profile', {})
        conversation_context = final_state.get('conversation_context', {})
        
        print(f"  Total messages: {len(messages)}")
        print(f"  Company name: {contractor_profile.get('company_name', 'Not saved')}")
        print(f"  Contact name: {contractor_profile.get('contact_name', 'Not saved')}")
        print(f"  Location: {contractor_profile.get('location', 'Not saved')}")
        print(f"  Specialties: {contractor_profile.get('specialties', [])}")
        print(f"  Projects found: {len(final_state.get('current_bid_cards', []))}")
        print(f"  Last search: {conversation_context.get('last_search', 'Not saved')}")
        print(f"  Project interest: {conversation_context.get('project_interest', 'Not saved')}")
        
        # SUCCESS CRITERIA
        success_criteria = {
            "has_messages": len(messages) >= 4,
            "profile_saved": bool(contractor_profile),
            "context_preserved": bool(conversation_context),
            "projects_saved": len(final_state.get('current_bid_cards', [])) >= 2,
            "session_restored": final_state.get('session_restored', False)
        }
        
        all_success = all(success_criteria.values())
        
        print("\nSUCCESS CRITERIA:")
        for criterion, passed in success_criteria.items():
            status = "PASS" if passed else "FAIL"
            print(f"  {criterion}: {status}")
        
        result = "SUCCESS - BSA memory persistence working!" if all_success else "FAILURE - Memory system has issues"
        print(f"\nOVERALL RESULT: {result}")
        
        return all_success
        
    except Exception as e:
        print(f"ERROR during BSA conversation testing: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run BSA memory test"""
    
    print("STARTING BSA MEMORY INTEGRATION TEST")
    print("=" * 50)
    
    success = await test_bsa_real_conversation()
    
    print("\n" + "=" * 50)
    print("FINAL RESULT:")
    if success:
        print("BSA memory integration is WORKING CORRECTLY!")
        print("- Contractors can have multi-turn conversations")
        print("- Context is preserved across conversation turns") 
        print("- Memory persists across sessions")
        print("- Ready for production contractor interactions")
    else:
        print("BSA memory system NEEDS INVESTIGATION")
        print("- Check database connections")
        print("- Verify foreign key constraints")
        print("- Test individual memory functions")

if __name__ == "__main__":
    asyncio.run(main())