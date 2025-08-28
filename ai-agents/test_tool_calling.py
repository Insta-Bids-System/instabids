#!/usr/bin/env python3
"""
Test if CIA agent is calling update_bid_card tool
"""

import asyncio
from agents.cia.agent import CustomerInterfaceAgent
import json

async def test_tool_calling():
    """Test if tools are being called"""
    print("="*80)
    print("TESTING CIA AGENT TOOL CALLING")
    print("="*80)
    
    # Initialize agent
    agent = CustomerInterfaceAgent()
    
    # Test messages that should trigger tool calls
    messages = [
        {
            "role": "user",
            "content": "I need artificial turf installed in my backyard. I'm in zip code 90210 and my email is test@example.com"
        }
    ]
    
    context = {
        "collected_info": {},
        "missing_fields": [],
        "current_phase": "information_gathering",
        "new_user": True
    }
    
    print("\nTest Message:")
    print(messages[0]["content"])
    print("\nExpected: Should call update_bid_card with project_type, location, and email")
    print("-"*40)
    
    # Process the message
    print("\nCalling agent.process()...")
    
    try:
        response = await agent.process(
            messages=messages,
            user_id="test-user-123",
            conversation_id="test-conv-123",
            context=context
        )
        
        print(f"\nResponse type: {type(response)}")
        
        if hasattr(response, '__aiter__'):
            # It's an async generator (streaming)
            print("Response is streaming...")
            full_response = ""
            tool_calls = []
            
            async for chunk in response:
                if isinstance(chunk, dict):
                    # Check for tool calls
                    if 'choices' in chunk:
                        for choice in chunk['choices']:
                            if 'delta' in choice:
                                delta = choice['delta']
                                if 'content' in delta:
                                    full_response += delta['content']
                                if 'tool_calls' in delta:
                                    tool_calls.append(delta['tool_calls'])
                    
            print(f"\nFull Response: {full_response[:500]}...")
            print(f"\nTool Calls Found: {len(tool_calls)}")
            
            if tool_calls:
                print("\nTool Calls Details:")
                for tc in tool_calls:
                    print(f"  - {tc}")
        else:
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Check the agent's tools
    print("\n" + "="*40)
    print("AGENT TOOLS CONFIGURATION:")
    print("-"*40)
    
    print(f"Number of tools: {len(agent.tools)}")
    for tool in agent.tools:
        print(f"\nTool: {tool['function']['name']}")
        print(f"Type: {tool['type']}")
        if 'description' in tool['function']:
            print(f"Description: {tool['function']['description'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_tool_calling())