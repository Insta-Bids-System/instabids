#!/usr/bin/env python3
"""
Test CIA agent locally to verify GPT-4 migration worked
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment - OVERRIDE system variables
load_dotenv(override=True)

# Add current directory to path
sys.path.append(os.getcwd())

async def test_cia_local():
    try:
        from agents.cia.agent import CustomerInterfaceAgent
        
        print('Testing CIA Agent Locally...')
        
        # Initialize CIA agent
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print('ERROR: No OpenAI API key found')
            return
            
        agent = CustomerInterfaceAgent(openai_key)
        print('SUCCESS: CIA Agent initialized with GPT-4')
        
        # Test message
        result = await agent.handle_conversation(
            user_id='test-local-001',
            session_id='local-test-session',
            message='I want to remodel my kitchen with a 20k budget'
        )
        
        print('SUCCESS: GPT-4 Call Successful!')
        print('Response preview:', result.get('response', '')[:100])
        print('Full test passed - agents work locally!')
        
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run test
    asyncio.run(test_cia_local())