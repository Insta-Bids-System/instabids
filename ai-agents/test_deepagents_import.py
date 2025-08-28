#!/usr/bin/env python3
"""
Test DeepAgents import and initialization
"""

import os
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "deepagents-system" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
root_env = Path(__file__).parent.parent / '.env'
if root_env.exists():
    load_dotenv(root_env, override=True)

# Set OpenAI API key 
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

print(f"OpenAI API Key set: {os.environ.get('OPENAI_API_KEY', '')[:20]}...")

try:
    # Test DeepAgents import
    print("\n1. Testing DeepAgents import...")
    from deepagents import create_deep_agent
    print("   SUCCESS: DeepAgents imported")
    
    # Test landing agent import
    print("\n2. Testing landing agent import...")
    from agents.coia.landing_deepagent import get_agent
    print("   SUCCESS: Landing agent imported")
    
    # Test creating agent
    print("\n3. Testing agent creation...")
    agent = get_agent()
    print(f"   SUCCESS: Agent created, type: {type(agent)}")
    
    # Test agent invocation
    print("\n4. Testing agent invocation...")
    test_input = {
        "messages": [
            {"role": "user", "content": "I run JM Holiday Lighting in Fort Lauderdale"}
        ]
    }
    
    import asyncio
    async def test_invoke():
        result = await agent.ainvoke(test_input)
        return result
    
    result = asyncio.run(test_invoke())
    print(f"   SUCCESS: Agent invoked")
    print(f"   Result type: {type(result)}")
    print(f"   Result keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
    
    if isinstance(result, dict) or hasattr(result, 'get'):
        # Check for response
        if "messages" in result:
            messages = result["messages"]
            if messages:
                last_message = messages[-1]
                # Handle AIMessage objects
                if hasattr(last_message, 'content'):
                    print(f"   Message type: {type(last_message).__name__}")
                    print(f"   Message content preview: {str(last_message.content)[:300]}")
                else:
                    print(f"   Last message: {last_message}")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()