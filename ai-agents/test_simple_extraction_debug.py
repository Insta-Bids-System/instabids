#!/usr/bin/env python3
"""
Simple debug test for extraction issues
"""

import asyncio
import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.enhanced_contractor_memory import EnhancedContractorMemory

# Test contractor
CONTRACTOR_ID = "523c0f63-e75c-4d65-963e-561d7f4169db"

async def debug_extraction():
    """Debug the extraction process step by step"""
    print("SIMPLE EXTRACTION DEBUG TEST")
    print("="*50)
    
    memory = EnhancedContractorMemory()
    
    if not memory.openai_client:
        print("ERROR: No OpenAI client")
        return
    
    # Simple conversation data
    conversation_data = {
        'input': "We use ServiceTitan for CRM and have 15 employees. We markup materials 25% and labor 40%.",
        'response': "Thank you for sharing that information.",
        'project_type': 'bathroom_remodel'
    }
    
    print("Testing business memory extraction...")
    
    try:
        # Test just one memory type at a time
        result = await memory._update_business_memory(CONTRACTOR_ID, conversation_data)
        
        if result:
            print(f"SUCCESS: Business memory extracted")
            print(f"Result keys: {result.keys()}")
            for key, value in result.items():
                if key not in ['contractor_id', 'last_updated', 'total_updates']:
                    print(f"  {key}: {value}")
        else:
            print("WARNING: No business memory result")
            
    except Exception as e:
        print(f"ERROR in business memory: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_extraction())