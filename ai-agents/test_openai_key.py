#!/usr/bin/env python3

import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def test_openai_key():
    """Test if OpenAI API key is working"""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("ERROR: No OPENAI_API_KEY found in environment")
        return False
    
    print(f"SUCCESS: Found OpenAI API key: {api_key[:10]}...")
    
    try:
        client = AsyncOpenAI(api_key=api_key)
        
        # Test simple completion
        response = await client.chat.completions.create(
            model="gpt-4o",  # Use gpt-4o for testing
            messages=[
                {"role": "user", "content": "Say hello in exactly 3 words"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"SUCCESS: OpenAI API working: {result}")
        return True
        
    except Exception as e:
        print(f"ERROR: OpenAI API error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openai_key())
    if success:
        print("OpenAI API key is working properly")
    else:
        print("OpenAI API key has issues")