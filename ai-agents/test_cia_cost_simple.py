"""
Simple test of CIA Agent with Cost Tracking - bypass database issues
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_cost_tracker import get_tracked_openai_client, llm_cost_tracker
from openai import AsyncOpenAI

async def test_cia_simple():
    """Simple direct test of OpenAI with cost tracking"""
    print("\n" + "="*60)
    print("TESTING OPENAI (CIA) WITH COST TRACKING - SIMPLE")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] No OpenAI API key found")
        return
    
    # Get tracked OpenAI client
    print("[INFO] Creating tracked OpenAI client...")
    client = get_tracked_openai_client(
        agent_name="CIA",
        api_key=api_key,
        is_async=True
    )
    print("[OK] Tracked OpenAI client created")
    
    # Make a simple API call
    print("\n[PROCESSING] Making OpenAI API call...")
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o as GPT-5 might not be available
            messages=[
                {"role": "system", "content": "You are a helpful home renovation assistant."},
                {"role": "user", "content": "I need to renovate my kitchen. It's about 200 square feet. What should I consider?"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        print("[SUCCESS] OpenAI API call completed!")
        print(f"[RESPONSE] {response.choices[0].message.content[:200]}...")
        
        # Check usage
        if response.usage:
            print("\n[TOKENS] Token Usage:")
            print(f"  - Input Tokens: {response.usage.prompt_tokens}")
            print(f"  - Output Tokens: {response.usage.completion_tokens}")
            print(f"  - Total Tokens: {response.usage.total_tokens}")
            
            # Calculate cost
            from services.llm_cost_tracker import LLMCostCalculator
            calc = LLMCostCalculator()
            cost = calc.calculate_cost(
                provider="openai",
                model="gpt-4o",
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens
            )
            print(f"  - Estimated Cost: ${cost:.6f}")
        
    except Exception as e:
        print(f"[ERROR] API call failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_cia_simple())