#!/usr/bin/env python3
"""
Test the intelligent messaging agent directly to find where it's hanging
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.intelligent_messaging_agent import process_intelligent_message, MessageType

async def test_intelligent_agent():
    print("Testing intelligent messaging agent directly...")
    
    try:
        print("Calling process_intelligent_message with contact info...")
        start_time = asyncio.get_event_loop().time()
        
        result = await process_intelligent_message(
            content="Call me at 555-TEST-123 for quick discussion",
            sender_type="contractor", 
            sender_id="test-contractor-123",
            bid_card_id="78c3f7cb-64d8-496e-b396-32b24d790252",
            message_type=MessageType.BID_SUBMISSION
        )
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        print(f"SUCCESS in {duration:.2f}s")
        print(f"Result: {result}")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_intelligent_agent())