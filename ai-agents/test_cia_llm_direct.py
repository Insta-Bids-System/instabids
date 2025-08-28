#!/usr/bin/env python3
"""
Test CIA agent LLM calls directly to debug the issue
"""
import os
import asyncio
from agents.cia.agent import CustomerInterfaceAgent

async def test_cia_llm():
    """Test CIA agent LLM initialization and calls"""
    print("=== Testing CIA Agent LLM Integration ===")
    
    # Get API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print(f"OpenAI Key Available: {bool(openai_key)}")
    print(f"Anthropic Key Available: {bool(anthropic_key)}")
    
    # Test with OpenAI first
    if openai_key:
        print("\n--- Testing with OpenAI GPT-4o ---")
        try:
            cia = CustomerInterfaceAgent(f"openai:{openai_key}")
            print(f"CIA initialized with api_type: {cia.api_type}")
            print(f"CIA client: {type(cia.client) if cia.client else 'None'}")
            
            # Test LLM call directly
            test_messages = [{"role": "user", "content": "Hello, I need help with a kitchen remodel"}]
            result = cia._call_llm(test_messages, system="You are a helpful contractor assistant.")
            
            if result:
                print(f"✅ SUCCESS: LLM call worked!")
                print(f"Response: {result[:100]}...")
                return True
            else:
                print("❌ FAILED: LLM call returned None")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    # Test with Anthropic as fallback
    if anthropic_key:
        print("\n--- Testing with Anthropic Claude ---")
        try:
            cia = CustomerInterfaceAgent(anthropic_key)
            print(f"CIA initialized with api_type: {cia.api_type}")
            print(f"CIA client: {type(cia.client) if cia.client else 'None'}")
            
            # Test LLM call directly  
            test_messages = [{"role": "user", "content": "Hello, I need help with a kitchen remodel"}]
            result = cia._call_llm(test_messages, system="You are a helpful contractor assistant.")
            
            if result:
                print(f"✅ SUCCESS: LLM call worked!")
                print(f"Response: {result[:100]}...")
                return True
            else:
                print("❌ FAILED: LLM call returned None")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_cia_llm())
    if not success:
        print("\n❌ CRITICAL: CIA Agent LLM not working - must fix before unified migration")
        print("❌ This explains why unified conversation migration isn't working properly")
    else:
        print("\n✅ CIA Agent LLM working - unified migration should work")