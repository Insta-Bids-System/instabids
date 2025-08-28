"""
Test Sub-Agent Status Messages
Tests that the BSA agent sends proper status messages during sub-agent execution

Created: August 17, 2025
Purpose: Verify status messages appear in chat feed during sub-agent calls
"""

import asyncio
import json
from datetime import datetime

from agents.bsa.agent import process_contractor_input_streaming

async def test_status_messages():
    """Test that sub-agent status messages are sent during execution"""
    print("Testing Sub-Agent Status Messages")
    print("=" * 50)
    
    contractor_id = "22222222-2222-2222-2222-222222222222"
    message = "find kitchen projects near me"
    session_id = f"test_status_{datetime.now().timestamp()}"
    
    print(f"Message: '{message}'")
    print(f"Expected status messages:")
    print("1. Calling Bid Card Finder sub-agent...")
    print("2. Searching for kitchen projects within 30 miles...")
    print("3. Sub-agent found X projects! Displaying below...")
    
    print("\nActual messages received:")
    print("-" * 30)
    
    status_messages = []
    bid_cards_found = False
    conversation_chunks = []
    
    try:
        async for chunk in process_contractor_input_streaming(
            bid_card_id="test_status_messages",
            contractor_id=contractor_id,
            input_type="text",
            input_data=message,
            session_id=session_id
        ):
            # Capture sub-agent status messages
            if chunk.get('type') == 'sub_agent_status':
                status_messages.append(chunk)
                print(f"STATUS: {chunk.get('message', 'No message')}")
                print(f"        Sub-agent: {chunk.get('sub_agent', 'Unknown')}")
                print(f"        Status: {chunk.get('status', 'Unknown')}")
                print()
                
            # Capture bid cards found
            elif chunk.get('type') == 'bid_cards_found':
                bid_cards_found = True
                count = len(chunk.get('bid_cards', []))
                print(f"BID CARDS: Found {count} projects")
                print()
                
            # Capture conversation chunks
            elif chunk.get('choices') and chunk['choices'][0].get('delta', {}).get('content'):
                content = chunk['choices'][0]['delta']['content']
                conversation_chunks.append(content)
                
            # Stop after reasonable number of chunks
            if len(status_messages) >= 3 and bid_cards_found and len(conversation_chunks) > 5:
                break
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nTEST RESULTS:")
    print("=" * 30)
    print(f"Status messages received: {len(status_messages)}")
    print(f"Bid cards found event: {'YES' if bid_cards_found else 'NO'}")
    print(f"Conversation chunks: {len(conversation_chunks)}")
    
    # Verify status message sequence
    if len(status_messages) >= 3:
        print("\nStatus message sequence:")
        for i, msg in enumerate(status_messages[:3]):
            print(f"{i+1}. {msg.get('message', 'No message')}")
            
        print("\nSTATUS MESSAGES WORKING!")
    else:
        print(f"\nFAIL: EXPECTED 3+ STATUS MESSAGES, GOT {len(status_messages)}")
        
    if bid_cards_found:
        print("BID CARDS FOUND EVENT WORKING!")
    else:
        print("FAIL: BID CARDS FOUND EVENT MISSING")
        
    if len(conversation_chunks) > 0:
        print("CONVERSATION STREAMING WORKING!")
        full_response = ''.join(conversation_chunks)
        print(f"Sample response: {full_response[:100]}...")
    else:
        print("FAIL: CONVERSATION STREAMING NOT WORKING")

if __name__ == "__main__":
    asyncio.run(test_status_messages())