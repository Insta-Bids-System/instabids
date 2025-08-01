"""
Test long conversation memory management
"""
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cia.agent import CustomerInterfaceAgent

async def test_long_conversation():
    """Test how CIA handles long conversations with context summarization"""
    print("TESTING LONG CONVERSATION MEMORY MANAGEMENT")
    print("="*50)
    
    # Initialize CIA agent
    cia = CustomerInterfaceAgent(os.getenv('ANTHROPIC_API_KEY'))
    user_id = "00000000-0000-0000-0000-000000000000"
    
    # Start a conversation about a kitchen project
    print("\nSTARTING CONVERSATION...")
    result = await cia.handle_conversation(
        user_id=user_id,
        message="I need help with a kitchen remodel"
    )
    session_id = result.get('session_id')
    print(f"Session started: {session_id}")
    
    # Simulate 25 messages to trigger context summary
    messages = [
        "My budget is around $50,000",
        "I prefer modern style",
        "The kitchen is about 200 square feet",
        "I want quartz countertops",
        "Stainless steel appliances would be nice",
        "Timeline is 2-3 months",
        "I have pets so need durable flooring",
        "White cabinets preferred",
        "Need good lighting",
        "Want an island if possible",
        "Open to backsplash ideas",
        "Prefer undermount sink",
        "Gas range is a must",
        "Need lots of storage",
        "Want soft-close drawers",
        "Thinking about pendant lights",
        "Maybe a wine fridge",
        "Double oven would be great",
        "Pull out trash bins",
        "Corner cabinet solutions needed",
        "Actually, let's increase the budget to $65,000",
        "And I changed my mind about the timeline - need it in 2 months",
        "Oh and I forgot to mention I want heated floors"
    ]
    
    print(f"\nSIMULATING {len(messages)} MESSAGES...")
    for i, msg in enumerate(messages):
        print(f"Message {i+2}: {msg[:50]}...")
        result = await cia.handle_conversation(
            user_id=user_id,
            message=msg,
            session_id=session_id
        )
        # Just track that it processed
        if not result.get('response'):
            print(f"ERROR: No response for message {i+2}")
            break
    
    # Now test with message 26 - should trigger context summary
    print("\n" + "="*50)
    print("MESSAGE 26 - SHOULD USE CONTEXT SUMMARY")
    print("="*50)
    
    # Get state to check message count
    state = cia.sessions.get(session_id)
    if state:
        print(f"Total messages in conversation: {len(state['messages'])}")
        print(f"Collected info: {state.get('collected_info', {}).keys()}")
    
    # Ask a question that requires memory
    final_result = await cia.handle_conversation(
        user_id=user_id,
        message="Can you remind me what my current budget and timeline are?",
        session_id=session_id
    )
    
    print(f"\nFINAL RESPONSE: {final_result['response'][:200]}...")
    
    # Check if it remembered the changed budget ($65k) and timeline (2 months)
    response = final_result['response'].lower()
    
    print("\n" + "="*50)
    print("MEMORY TEST RESULTS:")
    print("="*50)
    
    budget_remembered = '65' in response or 'sixty-five' in response
    timeline_remembered = '2 month' in response or 'two month' in response
    
    print(f"Budget remembered ($65k): {'PASS' if budget_remembered else 'FAIL'}")
    print(f"Timeline remembered (2 months): {'PASS' if timeline_remembered else 'FAIL'}")
    
    if budget_remembered and timeline_remembered:
        print("\nSUCCESS: Long conversation memory working!")
        print("Context summary is preserving key information beyond 10-message window")
    else:
        print("\nFAIL: Memory not working properly")
        print(f"Response: {final_result['response']}")
    
    return budget_remembered and timeline_remembered

if __name__ == "__main__":
    success = asyncio.run(test_long_conversation())
    print(f"\nOVERALL: {'PASS' if success else 'FAIL'}")