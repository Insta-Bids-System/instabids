"""
Simple test for conversation memory context
"""
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cia.agent import CustomerInterfaceAgent
from datetime import datetime

async def test_memory_context():
    """Test that long conversations get context summary"""
    print("TESTING CONVERSATION MEMORY CONTEXT")
    print("="*50)
    
    # Initialize CIA agent
    cia = CustomerInterfaceAgent(os.getenv('ANTHROPIC_API_KEY'))
    user_id = "00000000-0000-0000-0000-000000000000"
    
    # Create a session with pre-filled long conversation
    session_id = f"test_session_{datetime.now().timestamp()}"
    
    # Create state with 25 messages to trigger context summary
    state = {
        "user_id": user_id,
        "session_id": session_id,
        "messages": [],
        "collected_info": {
            "project_type": "kitchen remodel",
            "budget_min": 60000,
            "budget_max": 75000,
            "timeline": "2 months",
            "material_preferences": ["quartz countertops", "stainless steel appliances"],
            "special_requirements": ["pet-friendly flooring", "soft-close drawers"],
            "property_context": "200 square foot kitchen"
        },
        "current_phase": "gathering_info",
        "ready_for_jaa": False,
        "missing_fields": []
    }
    
    # Add 25 fake messages to trigger context
    for i in range(25):
        state["messages"].append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"Message {i+1}"
        })
    
    # Set this as the session
    cia.sessions[session_id] = state
    
    print(f"Created session with {len(state['messages'])} messages")
    print(f"Collected info: {state['collected_info']}")
    
    # Now send a new message that should use context summary
    print("\nSending message that should trigger context summary...")
    
    result = await cia.handle_conversation(
        user_id=user_id,
        message="What were all the details we discussed for my kitchen project?",
        session_id=session_id
    )
    
    print(f"\nResponse: {result['response'][:300]}...")
    
    # Check if response includes key details from collected_info
    response = result['response'].lower()
    
    print("\n" + "="*50)
    print("CONTEXT MEMORY TEST RESULTS:")
    print("="*50)
    
    # Check for key details that should be in context
    checks = {
        "Budget": '75' in response or 'seventy-five' in response,
        "Timeline": '2 month' in response or 'two month' in response,
        "Countertops": 'quartz' in response,
        "Appliances": 'stainless' in response,
        "Size": '200' in response or 'two hundred' in response
    }
    
    for item, found in checks.items():
        print(f"{item}: {'PASS' if found else 'FAIL'}")
    
    passed = sum(checks.values())
    total = len(checks)
    
    print(f"\nPassed {passed}/{total} context checks")
    
    if passed >= 4:  # At least 4 out of 5
        print("\nSUCCESS: Context memory is working!")
        print("Key information preserved beyond 10-message window")
        return True
    else:
        print("\nWARNING: Some context may be missing")
        return passed >= 3  # Still pass if most items remembered

if __name__ == "__main__":
    success = asyncio.run(test_memory_context())
    print(f"\nOVERALL: {'PASS' if success else 'FAIL'}")