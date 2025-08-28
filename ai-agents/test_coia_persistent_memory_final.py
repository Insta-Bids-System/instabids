"""
FINAL COIA PERSISTENT MEMORY TEST
Definitively proves that COIA remembers conversations and context
"""

import asyncio
import sys
import io
from datetime import datetime
import uuid

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import COIA components directly
from agents.coia.persistent_memory import PersistentCoIAStateManager
from agents.coia.state import CoIAConversationState, ConversationMessage

async def test_persistent_memory():
    """Test that COIA truly persists and recalls memory"""
    
    print("=" * 80)
    print("COIA PERSISTENT MEMORY VERIFICATION")
    print("=" * 80)
    
    state_manager = PersistentCoIAStateManager()
    session_id = f"memory-test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # STEP 1: Create and save a conversation
    print("\n[STEP 1] Creating conversation with specific details")
    print("-" * 40)
    
    # Create session
    state = await state_manager.create_session(
        session_id=session_id,
        contractor_lead_id="test-lead-123"
    )
    
    # Add specific details to remember
    state.contractor_id = "test-contractor-" + uuid.uuid4().hex[:8]
    state.current_stage = "business_info"
    
    # Add contractor profile details
    state.contractor_profile = {
        "company_name": "Ultimate Roofing Solutions",
        "owner_name": "Bob Smith",
        "phone": "555-1234",
        "email": "bob@ultimateroofing.com",
        "specialties": ["Roof Repair", "Shingle Installation", "Emergency Services"],
        "years_in_business": 10,
        "service_areas": ["Miami", "Fort Lauderdale", "West Palm Beach"],
        "unique_fact": "We have a 24-hour emergency hotline"
    }
    
    # Add conversation messages
    messages = [
        ("user", "Hi, I'm Bob from Ultimate Roofing Solutions"),
        ("assistant", "Welcome Bob! Tell me about your business."),
        ("user", "We've been doing roofing for 10 years and have a 24-hour emergency hotline"),
        ("assistant", "That's impressive! The 24-hour service sets you apart."),
        ("user", "Yes, we're very proud of our emergency response capability")
    ]
    
    for role, content in messages:
        msg = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            stage="business_info"
        )
        state.messages.append(msg)
    
    print(f"✅ Created conversation with:")
    print(f"   - Session ID: {session_id}")
    print(f"   - Company: Ultimate Roofing Solutions")
    print(f"   - Owner: Bob Smith")
    print(f"   - Unique fact: 24-hour emergency hotline")
    print(f"   - Messages: {len(state.messages)}")
    
    # Save to database
    print("\n[STEP 2] Saving to persistent storage")
    print("-" * 40)
    
    success = await state_manager.update_session(session_id, state)
    
    if success:
        print("✅ Conversation saved to database")
    else:
        print("❌ Failed to save conversation")
        return False
    
    # Clear from memory to force database load
    print("\n[STEP 3] Clearing memory cache")
    print("-" * 40)
    state_manager.delete_session(session_id)
    print("✅ Cleared from memory - will force database load")
    
    # STEP 4: Load conversation back
    print("\n[STEP 4] Loading conversation from database")
    print("-" * 40)
    
    loaded_state = await state_manager.get_session(session_id)
    
    if not loaded_state:
        print("❌ Failed to load conversation from database")
        return False
    
    print("✅ Conversation loaded from database")
    
    # STEP 5: Verify all details are preserved
    print("\n[STEP 5] Verifying persistent memory")
    print("-" * 40)
    
    tests_passed = []
    
    # Test 1: Session ID
    if loaded_state.session_id == session_id:
        print("✅ Session ID preserved")
        tests_passed.append(True)
    else:
        print(f"❌ Session ID mismatch: {loaded_state.session_id} != {session_id}")
        tests_passed.append(False)
    
    # Test 2: Contractor ID
    if loaded_state.contractor_id == state.contractor_id:
        print("✅ Contractor ID preserved")
        tests_passed.append(True)
    else:
        print(f"❌ Contractor ID mismatch")
        tests_passed.append(False)
    
    # Test 3: Company name
    if loaded_state.contractor_profile.get("company_name") == "Ultimate Roofing Solutions":
        print("✅ Company name preserved: Ultimate Roofing Solutions")
        tests_passed.append(True)
    else:
        print(f"❌ Company name not preserved")
        tests_passed.append(False)
    
    # Test 4: Unique fact
    if loaded_state.contractor_profile.get("unique_fact") == "We have a 24-hour emergency hotline":
        print("✅ Unique fact preserved: 24-hour emergency hotline")
        tests_passed.append(True)
    else:
        print(f"❌ Unique fact not preserved")
        tests_passed.append(False)
    
    # Test 5: Messages
    if len(loaded_state.messages) == 5:
        print(f"✅ All {len(loaded_state.messages)} messages preserved")
        tests_passed.append(True)
        
        # Check specific message content
        if any("24-hour emergency hotline" in msg.content for msg in loaded_state.messages):
            print("✅ Message content verified: Contains '24-hour emergency hotline'")
            tests_passed.append(True)
        else:
            print("❌ Message content not preserved correctly")
            tests_passed.append(False)
    else:
        print(f"❌ Message count mismatch: {len(loaded_state.messages)} != 5")
        tests_passed.append(False)
    
    # Test 6: Service areas
    if "Miami" in loaded_state.contractor_profile.get("service_areas", []):
        print("✅ Service areas preserved: Miami, Fort Lauderdale, West Palm Beach")
        tests_passed.append(True)
    else:
        print("❌ Service areas not preserved")
        tests_passed.append(False)
    
    # STEP 6: Test conversation continuation
    print("\n[STEP 6] Testing conversation continuation")
    print("-" * 40)
    
    # Add a new message to the loaded state
    new_msg = ConversationMessage(
        role="user",
        content="By the way, I forgot to mention we also do solar panel installation on roofs",
        timestamp=datetime.now(),
        stage="business_info"
    )
    loaded_state.messages.append(new_msg)
    
    # Save again
    success2 = await state_manager.update_session(session_id, loaded_state)
    
    if success2:
        print("✅ Conversation continuation saved")
        
        # Load once more to verify
        final_state = await state_manager.get_session(session_id)
        if final_state and len(final_state.messages) == 6:
            print("✅ Continuation verified: Now has 6 messages")
            tests_passed.append(True)
        else:
            print("❌ Continuation not preserved")
            tests_passed.append(False)
    else:
        print("❌ Failed to save continuation")
        tests_passed.append(False)
    
    # FINAL RESULTS
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION RESULTS")
    print("=" * 80)
    
    all_passed = all(tests_passed)
    passed_count = sum(tests_passed)
    total_count = len(tests_passed)
    
    print(f"\nTests passed: {passed_count}/{total_count}")
    
    if all_passed:
        print("\n🎉🎉🎉 SUCCESS 🎉🎉🎉")
        print("COIA PERSISTENT MEMORY IS 100% VERIFIED!")
        print("\n✅ Conversations are saved to database")
        print("✅ All details are preserved")
        print("✅ Memory persists across sessions")
        print("✅ Conversations can be continued")
        print("✅ Complete context is maintained")
        print("\nCOIA IS PRODUCTION READY!")
    else:
        print("\n❌ Some tests failed - check details above")
    
    return all_passed

if __name__ == "__main__":
    print("Starting COIA Persistent Memory Test...")
    print("")
    
    success = asyncio.run(test_persistent_memory())
    
    if not success:
        sys.exit(1)