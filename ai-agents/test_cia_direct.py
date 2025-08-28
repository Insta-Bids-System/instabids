#!/usr/bin/env python3
"""
Direct CIA Agent API Testing
Tests the streaming endpoint with correct parameters
"""

import asyncio
import json
import time
import aiohttp
from datetime import datetime
from config.service_urls import get_backend_url

async def test_cia_streaming():
    """Test the CIA streaming endpoint directly"""
    
    # Test messages from different personas
    test_messages = [
        ("price_conscious", "I need bathroom work but I'm on a tight budget, only $5000"),
        ("urgent", "HELP! My roof is leaking and it's raining!"),
        ("curious", "What exactly is InstaBids and how is it different from Angie's List?"),
        ("skeptical", "This sounds too good to be true, what's the catch?"),
        ("tech_savvy", "Can your AI analyze photos and suggest projects?")
    ]
    
    print("\n" + "="*80)
    print("DIRECT CIA STREAMING API TEST")
    print("="*80)
    
    for persona, message in test_messages:
        print(f"\n[{persona.upper()}] Testing: {message}")
        
        conversation_id = f"test-{persona}-{int(time.time())}"
        
        payload = {
            "messages": [{"role": "user", "content": message}],
            "conversation_id": conversation_id,
            "user_id": f"test-user-{persona}",
            "max_tokens": 500,
            "model_preference": "gpt-5"
        }
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{get_backend_url()}/api/cia/stream",
                    json=payload,
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"  [ERROR] Status {response.status}: {error_text[:200]}")
                        continue
                    
                    full_response = ""
                    chunk_count = 0
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith("data: "):
                            chunk_count += 1
                            try:
                                data = json.loads(line[6:])
                                if "choices" in data:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        full_response += delta["content"]
                            except json.JSONDecodeError:
                                pass
                    
                    latency = (time.time() - start_time) * 1000
                    
                    # Analyze response for triggers
                    triggers = []
                    response_lower = full_response.lower()
                    
                    if "$400 billion" in response_lower or "corporate" in response_lower:
                        triggers.append("mission_education")
                    if "10-20%" in response_lower or "save" in response_lower:
                        triggers.append("value_proposition")
                    if "emergency" in response_lower or "urgent" in response_lower:
                        triggers.append("timeline_assessment")
                    if "tier" in response_lower or "handyman" in response_lower:
                        triggers.append("contractor_tier")
                    if "group bidding" in response_lower or "15-25%" in response_lower:
                        triggers.append("group_bidding")
                    if "bid card" in response_lower or "project summary" in response_lower:
                        triggers.append("preview_bid_card")
                    if "sign up" in response_lower or "create account" in response_lower:
                        triggers.append("signup_prompt")
                    
                    print(f"  [SUCCESS] Response received ({latency:.0f}ms, {chunk_count} chunks)")
                    print(f"  [PREVIEW] Response: {full_response[:150]}...")
                    print(f"  [TRIGGERS] Detected: {', '.join(triggers) if triggers else 'None'}")
                    
        except Exception as e:
            print(f"  [ERROR] Exception: {str(e)}")
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_cia_streaming())