#!/usr/bin/env python3
"""
Quick CIA Persona Testing - Working Version
"""

import asyncio
import json
import time
import aiohttp
from config.service_urls import get_backend_url

async def test_persona(persona, message):
    """Test a single persona and analyze response"""
    
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
                    return
                
                full_response = ""
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if "choices" in data:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    full_response += delta["content"]
                        except json.JSONDecodeError:
                            pass
                
                latency = (time.time() - start_time) * 1000
                
                # Analyze for key triggers
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
                
                print(f"  [RESPONSE] ({latency:.0f}ms): {full_response[:200]}...")
                print(f"  [TRIGGERS] {', '.join(triggers) if triggers else 'None'}")
                
                return full_response, triggers, latency
                
    except Exception as e:
        print(f"  [ERROR] Exception: {str(e)}")
        return None, [], 0

async def main():
    """Run quick persona tests"""
    
    test_cases = [
        ("price_conscious", "I need bathroom work but I'm on a tight budget, only $5000"),
        ("urgent", "HELP! My roof is leaking and it's raining!"),
        ("curious", "What exactly is InstaBids and how is it different from Angie's List?"),
        ("skeptical", "This sounds too good to be true, what's the catch?"),
        ("tech_savvy", "Can your AI analyze photos and suggest projects?")
    ]
    
    print("=" * 80)
    print("QUICK CIA PERSONA TESTING - WORKING VERSION")
    print("=" * 80)
    
    results = {}
    
    for persona, message in test_cases:
        response, triggers, latency = await test_persona(persona, message)
        results[persona] = {
            "response": response,
            "triggers": triggers,
            "latency": latency
        }
        await asyncio.sleep(3)  # Delay between tests
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY ANALYSIS")
    print("=" * 80)
    
    for persona, data in results.items():
        if data["response"]:
            print(f"\n{persona.upper()}:")
            print(f"  Triggers: {', '.join(data['triggers']) if data['triggers'] else 'None'}")
            print(f"  Latency: {data['latency']:.0f}ms")
            print(f"  Response length: {len(data['response'])} characters")
            
            # Key insight analysis
            if "mission_education" in data["triggers"]:
                print("  ✓ Triggered mission education about corporate extraction")
            if "value_proposition" in data["triggers"]:
                print("  ✓ Emphasized cost savings value proposition") 
            if "timeline_assessment" in data["triggers"]:
                print("  ✓ Assessed timeline/urgency appropriately")

if __name__ == "__main__":
    asyncio.run(main())