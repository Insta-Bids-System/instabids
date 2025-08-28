#!/usr/bin/env python3
"""
Fixed Persona Test with Proper UUIDs
"""

import asyncio
import json
import time
import uuid
import aiohttp
from config.service_urls import get_backend_url

async def send_message(session_id, user_id, message):
    """Send message with proper UUID format"""
    
    payload = {
        "messages": [{"role": "user", "content": message}],
        "conversation_id": session_id,
        "user_id": user_id,
        "max_tokens": 800,
        "model_preference": "gpt-5"
    }
    
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{get_backend_url()}/api/cia/stream",
                json=payload,
                headers={"Accept": "text/event-stream"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    return f"ERROR {response.status}: {error_text}", 0
                
                full_response = ""
                
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith("data: "):
                        try:
                            data = json.loads(line_text[6:])
                            if "choices" in data:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    full_response += delta["content"]
                        except json.JSONDecodeError:
                            pass
                
                latency = (time.time() - start_time) * 1000
                return full_response, latency
                
    except Exception as e:
        return f"EXCEPTION: {str(e)}", 0

async def test_price_conscious_complete():
    """Test complete price conscious conversation"""
    
    # Generate proper UUIDs
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
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
    
    print("COMPLETE PRICE CONSCIOUS PERSONA CONVERSATION")
    print("=" * 80)
    print(f"Session ID: {session_id}")
    print(f"User ID: {user_id}")
    print("=" * 80)
    
    for turn, message in enumerate(messages, 1):
        print(f"\n[TURN {turn}] USER:")
        print(f"'{message}'")
        print("-" * 60)
        print("[CIA RESPONSE:]")
        
        response, latency = await send_message(session_id, user_id, message)
        
        print(response)
        print(f"\n[TIMING: {latency:.0f}ms]")
        
        # Quick analysis
        response_lower = response.lower()
        triggers = []
        
        if "$400 billion" in response_lower or "corporate" in response_lower:
            triggers.append("MISSION_EDUCATION")
        if "10-20%" in response_lower or "save" in response_lower:
            triggers.append("VALUE_PROPOSITION")
        if "group bidding" in response_lower or "15-25%" in response_lower:
            triggers.append("GROUP_BIDDING")
        if "bid card" in response_lower:
            triggers.append("BID_CARD_MENTION")
        if "sign up" in response_lower or "create account" in response_lower:
            triggers.append("SIGNUP_PROMPT")
        
        if triggers:
            print(f"[TRIGGERS: {', '.join(triggers)}]")
        
        print("=" * 80)
        
        # Wait between turns
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_price_conscious_complete())