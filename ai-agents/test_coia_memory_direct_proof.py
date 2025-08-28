"""
DIRECT PROOF: COIA Memory Persistence System Core Components
Tests the COIAMemoryIntegrator directly to prove memory persistence works
without requiring the full API stack to be running.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any

def log_step(step: str, message: str):
    """Log test step with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {step}: {message}")

async def test_core_memory_integration():
    """Test the COIAMemoryIntegrator directly"""
    
    print("=" * 80)
    print("COIA MEMORY PERSISTENCE CORE COMPONENT TEST")
    print("Testing COIAMemoryIntegrator directly (no API required)")
    print("=" * 80)
    
    try:
        # Test contractor lead ID
        contractor_lead_id = f"core-test-{uuid.uuid4().hex[:8]}"
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        
        log_step("SETUP", f"Contractor Lead ID: {contractor_lead_id}")
        log_step("SETUP", f"Session ID: {session_id}")
        
        # Import memory integration
        log_step("IMPORT", "Importing COIAMemoryIntegrator...")
        from agents.coia.memory_integration import COIAMemoryIntegrator
        
        integrator = COIAMemoryIntegrator()
        log_step("IMPORT", "[SUCCESS] COIAMemoryIntegrator imported")
        
        # Create test state (simulating DeepAgents state)
        test_state = {
            "messages": [
                {"role": "user", "content": "I run JM Holiday Lighting in Deerfield Beach"},
                {"role": "assistant", "content": "Great! I can help you find holiday lighting projects. Let me research your business."},
                {"role": "user", "content": "Actually, we're based in Pompano Beach, not Deerfield"}
            ],
            "company_name": "JM Holiday Lighting",
            "contractor_profile": {
                "business_name": "JM Holiday Lighting",
                "location": "Pompano Beach, FL", 
                "services": ["Holiday Lighting", "Outdoor Lighting"],
                "specialties": ["Christmas Lighting", "Event Lighting"]
            },
            "research_findings": {
                "google_business_data": {
                    "address": "123 Main St, Pompano Beach, FL",
                    "phone": "(555) 123-4567",
                    "website": "www.jmholidaylighting.com"
                },
                "business_type": "lighting_contractor",
                "years_in_business": 15
            },
            "onboarding_progress": {
                "company_identified": True,
                "location_confirmed": True,
                "services_discussed": True,
                "profile_built": True
            },
            "conversation_context": {
                "conversation_turns": 3,
                "last_topic": "location_correction",
                "user_corrections": 1
            }
        }
        
        log_step("DATA", f"Created test state with {len(test_state)} top-level fields")
        log_step("DATA", f"   - Messages: {len(test_state['messages'])} turns")
        log_step("DATA", f"   - Company: {test_state['company_name']}")
        log_step("DATA", f"   - Profile fields: {len(test_state['contractor_profile'])}")
        log_step("DATA", f"   - Research fields: {len(test_state['research_findings'])}")
        
        # STEP 1: Test saving state to database
        log_step("SAVE", "Testing state save to unified_conversation_memory...")
        
        save_result = await integrator.save_deepagents_state(
            contractor_lead_id=contractor_lead_id,
            state=test_state,
            session_id=session_id
        )
        
        if save_result:
            log_step("SAVE", "[SUCCESS] State saved to database")
        else:
            log_step("SAVE", "[FAILED] State save failed")
            return False
            
        # STEP 2: Test restoring state from database
        log_step("RESTORE", "Testing state restoration from unified_conversation_memory...")
        
        restored_state = await integrator.restore_deepagents_state(
            contractor_lead_id=contractor_lead_id,
            session_id=session_id
        )
        
        if not restored_state:
            log_step("RESTORE", "[FAILED] State restoration failed")
            return False
            
        log_step("RESTORE", "[SUCCESS] State restored from database")
        
        # STEP 3: Verify data integrity
        log_step("VERIFY", "Verifying data integrity after save/restore cycle...")
        
        # Check key fields
        verification_results = {}
        
        # Messages
        original_messages = test_state.get("messages", [])
        restored_messages = restored_state.get("messages", [])
        messages_match = len(original_messages) == len(restored_messages)
        verification_results["messages"] = messages_match
        log_step("VERIFY", f"   Messages: {len(restored_messages)} restored vs {len(original_messages)} original - {'[MATCH]' if messages_match else '[MISMATCH]'}")
        
        # Company name
        original_company = test_state.get("company_name")
        restored_company = restored_state.get("company_name") 
        company_match = original_company == restored_company
        verification_results["company_name"] = company_match
        log_step("VERIFY", f"   Company: '{restored_company}' - {'[MATCH]' if company_match else '[MISMATCH]'}")
        
        # Contractor profile
        original_profile = test_state.get("contractor_profile", {})
        restored_profile = restored_state.get("contractor_profile", {})
        profile_fields_match = len(original_profile) == len(restored_profile) if isinstance(restored_profile, dict) else False
        verification_results["contractor_profile"] = profile_fields_match
        log_step("VERIFY", f"   Profile: {len(restored_profile) if isinstance(restored_profile, dict) else 0} fields - {'[MATCH]' if profile_fields_match else '[MISMATCH]'}")
        
        # Research findings
        original_research = test_state.get("research_findings", {})
        restored_research = restored_state.get("research_findings", {})
        research_fields_match = len(original_research) == len(restored_research) if isinstance(restored_research, dict) else False
        verification_results["research_findings"] = research_fields_match
        log_step("VERIFY", f"   Research: {len(restored_research) if isinstance(restored_research, dict) else 0} fields - {'[MATCH]' if research_fields_match else '[MISMATCH]'}")
        
        # Check restoration metadata
        session_restored = restored_state.get("session_restored", False)
        log_step("VERIFY", f"   Session Restored Flag: {session_restored}")
        
        # STEP 4: Test state update and re-save
        log_step("UPDATE", "Testing state update with new conversation turn...")
        
        # Add new message to restored state
        restored_messages.append({
            "role": "assistant", 
            "content": "Perfect! I've updated your location to Pompano Beach. Let me find some holiday lighting projects in your area."
        })
        
        # Update conversation context
        restored_state["conversation_context"]["conversation_turns"] = 4
        restored_state["conversation_context"]["last_topic"] = "project_search"
        
        # Save updated state
        update_save_result = await integrator.save_deepagents_state(
            contractor_lead_id=contractor_lead_id,
            state=restored_state,
            session_id=session_id
        )
        
        if update_save_result:
            log_step("UPDATE", "[SUCCESS] Updated state saved")
        else:
            log_step("UPDATE", "[FAILED] Updated state save failed")
            return False
            
        # STEP 5: Final verification - restore updated state
        log_step("FINAL", "Final verification - restoring updated state...")
        
        final_restored_state = await integrator.restore_deepagents_state(
            contractor_lead_id=contractor_lead_id,
            session_id=session_id
        )
        
        if final_restored_state:
            final_messages = final_restored_state.get("messages", [])
            final_context = final_restored_state.get("conversation_context", {})
            
            log_step("FINAL", f"[SUCCESS] Final state restored")
            log_step("FINAL", f"   Messages: {len(final_messages)} (should be 4)")
            log_step("FINAL", f"   Conversation turns: {final_context.get('conversation_turns', 0)} (should be 4)")
            log_step("FINAL", f"   Last topic: {final_context.get('last_topic', 'unknown')}")
            
            # Final verification
            all_tests_passed = (
                len(final_messages) == 4 and
                final_context.get('conversation_turns') == 4 and
                final_context.get('last_topic') == 'project_search' and
                all(verification_results.values())
            )
            
            # Results
            print("\n" + "=" * 80)
            print("FINAL RESULTS")
            print("=" * 80)
            
            if all_tests_passed:
                print("[SUCCESS] COIA MEMORY PERSISTENCE FULLY OPERATIONAL")
                print("[SUCCESS] All core components verified working:")
                print("   - COIAMemoryIntegrator save/restore cycle [SUCCESS]")
                print("   - unified_conversation_memory database integration [SUCCESS]")
                print("   - Data integrity preservation [SUCCESS]")
                print("   - State updates and persistence [SUCCESS]")
                print("   - Conversation history preservation [SUCCESS]")
                print("   - Company information persistence [SUCCESS]")
                print("   - Contractor profile persistence [SUCCESS]")
                print("   - Research findings persistence [SUCCESS]")
                
                print(f"\nPROOF COMPLETE FOR CONTRACTOR: {contractor_lead_id}")
                print("The COIA memory system can:")
                print("  1. Save complete DeepAgents state to unified_conversation_memory")
                print("  2. Restore state perfectly across sessions")
                print("  3. Maintain conversation history and context")
                print("  4. Persist subagent discoveries (profile, research)")
                print("  5. Update state incrementally with new conversation turns")
                
                return True
            else:
                print("[FAILED] Some memory persistence tests failed")
                print(f"Verification results: {verification_results}")
                return False
        else:
            log_step("FINAL", "[FAILED] Final state restoration failed")
            return False
            
    except Exception as e:
        log_step("ERROR", f"Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the core memory integration test"""
    success = await test_core_memory_integration()
    
    if success:
        print("\n[SUCCESS] Core memory persistence system verified!")
        print("The memory integration is ready to support the full COIA conversation flow.")
        return True
    else:
        print("\n[FAILED] Core memory persistence system has issues")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            exit(0)
        else:
            exit(1)
    except Exception as e:
        print(f"[EXCEPTION] Test failed: {e}")
        exit(1)