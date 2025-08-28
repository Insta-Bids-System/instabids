#!/usr/bin/env python3
"""
Single Persona Complete Conversation Test
"""

import asyncio
import json
import time
import aiohttp
from config.service_urls import get_backend_url

async def test_price_conscious_persona():
    """Test price conscious persona with complete flow"""
    
    session_id = f"price-conscious-{int(time.time())}"
    base_url = get_backend_url()
    
    messages = [
        "Hi, I need some work done but I'm on a tight budget",
        "It's a bathroom remodel but I can only spend about $5000", 
        "How much can I really save with InstaBids compared to other sites?",
        "What if I'm flexible on timing? Can I save even more?",
        "Tell me more about this group bidding thing",
        "How do I know the contractors are legitimate for such low prices?",
        "What information do you need from me to get started?",
        "Ok show me what the bid card would look like for my bathroom project"
    ]
    
    print("PRICE CONSCIOUS PERSONA - COMPLETE CONVERSATION")
    print("=" * 60)
    
    for turn, message in enumerate(messages, 1):
        print(f"\n[TURN {turn}] USER: {message}")
        print("-" * 60)
        
        # Send message
        start_time = time.time()
        
        payload = {
            "messages": [{"role": "user", "content": message}],
            "conversation_id": session_id,
            "user_id": f"user-{session_id}",
            "max_tokens": 800,
            "model_preference": "gpt-5"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/cia/stream",
                    json=payload,
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"ERROR {response.status}: {error_text}")
                        continue
                    
                    full_response = ""
                    
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith("data: "):
                            try:
                                data = json.loads(line_text[6:])
                                if "choices" in data:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        content = delta["content"]
                                        full_response += content
                                        print(content, end="", flush=True)
                            except json.JSONDecodeError:
                                pass
                    
                    latency = (time.time() - start_time) * 1000
                    
                    print(f"\n\n[RESPONSE TIME: {latency:.0f}ms]")
                    
                    # Quick analysis
                    response_lower = full_response.lower()
                    triggers = []
                    
                    if "$400 billion" in response_lower or "corporate" in response_lower:
                        triggers.append("MISSION_EDUCATION")
                    if "10-20%" in response_lower or "save" in response_lower:
                        triggers.append("VALUE_PROPOSITION")
                    if "group bidding" in response_lower or "15-25%" in response_lower:
                        triggers.append("GROUP_BIDDING")
                    if "bid card" in response_lower:
                        triggers.append("BID_CARD_MENTION")
                    
                    if triggers:
                        print(f"[TRIGGERS: {', '.join(triggers)}]")
                    
                    print("=" * 60)
                    
        except Exception as e:
            print(f"ERROR: {str(e)}")
            
        # Wait between turns
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(test_price_conscious_persona())