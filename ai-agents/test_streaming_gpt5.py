#!/usr/bin/env python3
"""
Quick test to verify GPT-5 streaming works before full implementation
"""
import asyncio
import time
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv(override=True)

async def test_streaming():
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Keep responses brief."},
        {"role": "user", "content": "Tell me about streaming responses in 2-3 sentences."}
    ]
    
    print("Testing GPT-4o streaming...")
    start_time = time.time()
    first_token_time = None
    accumulated = ""
    
    try:
        stream = await client.chat.completions.create(
            model="gpt-4o",  # Testing GPT-4o speed
            messages=messages,
            stream=True
            # Note: reasoning_effort and verbosity not yet in SDK
        )
        
        async for chunk in stream:
            if first_token_time is None and chunk.choices[0].delta.content:
                first_token_time = time.time() - start_time
                print(f"\n[OK] First token latency: {first_token_time*1000:.0f}ms")
                
            content = chunk.choices[0].delta.content or ""
            accumulated += content
            print(content, end="", flush=True)
            
        total_time = time.time() - start_time
        print(f"\n\n[OK] Total time: {total_time:.2f}s")
        print(f"[OK] Response length: {len(accumulated)} chars")
        
    except Exception as e:
        print(f"\n[ERROR] GPT-5 failed: {e}")
        print("\nTrying GPT-4o fallback...")
        
        # Fallback test
        stream = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
        print("\n[OK] GPT-4o fallback worked")

if __name__ == "__main__":
    asyncio.run(test_streaming())