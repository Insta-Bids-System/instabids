#!/usr/bin/env python3
"""
Simple test of AI memory system without OpenAI
"""

import asyncio
import sys
import os
import logging

# Setup logging to see debug output
logging.basicConfig(level=logging.INFO)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.contractor_ai_memory import ContractorAIMemory

async def test_simple():
    ai_memory = ContractorAIMemory()
    contractor_id = "523c0f63-e75c-4d65-963e-561d7f4169db"
    
    print("Testing basic memory operations...")
    
    # Test 1: Get empty memory
    memory = await ai_memory.get_contractor_memory(contractor_id)
    print(f"Initial memory: {memory}")
    
    # Test 2: Try to update memory (this will test OpenAI)
    conversation_data = {
        'input': "I prefer quality over speed",
        'response': "Noted",
        'context': "test",
        'project_type': 'test'
    }
    
    result = await ai_memory.update_contractor_memory(contractor_id, conversation_data)
    print(f"Update result: {result}")

if __name__ == "__main__":
    asyncio.run(test_simple())