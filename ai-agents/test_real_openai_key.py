#!/usr/bin/env python3

import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def test_real_key():
    """Test the actual OpenAI key from the base .env file"""
    
    # Load from the correct .env location
    load_dotenv("C:/Users/Not John Or Justin/Documents/instabids/.env")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("No key found")
        return False
    
    print(f"Testing key: {api_key[:20]}...")
    
    try:
        client = AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"SUCCESS: {result}")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_key())