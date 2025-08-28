#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import uuid
import time
from config.service_urls import get_backend_url

async def test_cia_streaming_simple():
    """Test CIA streaming API with simple request to verify fix worked"""
    
    print("Testing CIA streaming API after fix...")
    print("=" * 50)
    
    # Test data
    test_request = {
        "messages": [{"role": "user", "content": "I need bathroom work but I'm on a tight budget, only $5000"}],
        "conversation_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "max_completion_tokens": 500,
        "model_preference": "gpt-5"
    }
    
    url = f"{get_backend_url()}/api/cia/stream"
    
    try:
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=test_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                
                print(f"HTTP Status: {response.status}")
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ ERROR: {error_text}")
                    return False
                
                # Read streaming response
                response_chunks = []
                error_found = False
                
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text:
                        print(f"Stream: {line_text}")
                        response_chunks.append(line_text)
                        
                        # Check for error messages
                        if "technical difficulties" in line_text.lower():
                            error_found = True
                            print("❌ FOUND ERROR: Technical difficulties message")
                        
                        # Stop after getting some response 
                        if len(response_chunks) > 5:
                            break
                
                elapsed = time.time() - start_time
                print(f"\n⏱️  Response time: {elapsed:.2f} seconds")
                
                if error_found:
                    print("❌ FIX FAILED: Still getting technical difficulties")
                    return False
                elif response_chunks:
                    print("✅ FIX SUCCESS: Getting proper CIA responses")
                    return True
                else:
                    print("⚠️  No response chunks received")
                    return False
                
    except asyncio.TimeoutError:
        print("❌ TIMEOUT: Request took too long")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_cia_streaming_simple())
    if result:
        print("\n🎉 CIA STREAMING FIX VERIFIED!")
    else:
        print("\n💔 CIA STREAMING STILL BROKEN - NEED MORE FIXES")