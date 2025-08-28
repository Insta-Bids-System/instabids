"""
Manual CIA Testing - Real conversations with state management
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import uuid
from config.service_urls import get_backend_url

async def test_cia_conversation():
    """Test CIA with manual back-and-forth conversation"""
    
    base_url = get_backend_url()
    conversation_id = f"manual_test_{uuid.uuid4().hex[:8]}"
    user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    
    # Store conversation history
    messages = []
    
    # Test conversation flow
    test_messages = [
        "I need to remodel my bathroom but I'm on a really tight budget. How much do these things usually cost?",
        "But what about all the fees? I've heard contractors charge extra for everything",
        "Can I really save money compared to using Angie's List or HomeAdvisor?",
        "What if I just want a basic update, nothing fancy?",
        "How do I know the contractors won't overcharge me?",
        "Is there a way to get multiple bids to compare prices?",
        "What about payment plans or financing?",
        "Do you charge homeowners anything?",
        "How much do contractors pay you?",
        "What if the project goes over budget?"
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, user_message in enumerate(test_messages, 1):
            print(f"\n{'='*80}")
            print(f"Turn {i}")
            print(f"{'='*80}")
            print(f"USER: {user_message}")
            
            # Add user message to history
            messages.append({"role": "user", "content": user_message})
            
            # Send request
            url = f"{base_url}/api/cia/stream"
            payload = {
                "messages": messages.copy(),
                "conversation_id": conversation_id,
                "user_id": user_id
            }
            
            start_time = time.time()
            response_text = ""
            
            try:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"ERROR: HTTP {response.status}: {error_text}")
                        break
                    
                    # Process SSE stream
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            
                            try:
                                chunk = json.loads(data)
                                if chunk.get('type') == 'content':
                                    response_text += chunk.get('content', '')
                            except json.JSONDecodeError:
                                continue
                                
            except asyncio.TimeoutError:
                print("ERROR: Timeout after 120 seconds")
                break
            except Exception as e:
                print(f"ERROR: {e}")
                break
                
            latency = time.time() - start_time
            
            if response_text:
                # Add assistant response to history
                messages.append({"role": "assistant", "content": response_text})
                
                print(f"\nCIA ({latency:.2f}s): {response_text[:500]}{'...' if len(response_text) > 500 else ''}")
                
                # Check for key phrases
                if 'bid card' in response_text.lower():
                    print("  [BID CARD MENTIONED]")
                if any(phrase in response_text.lower() for phrase in ['sign up', 'get started', 'create account']):
                    print("  [SIGNUP PROMPTED]")
                if '$400 billion' in response_text or '400 billion' in response_text:
                    print("  [CORPORATE EXTRACTION MENTIONED]")
            else:
                print("No response received")
                break
                
            # Small delay between messages
            await asyncio.sleep(1)
            
    print(f"\n{'='*80}")
    print("CONVERSATION COMPLETE")
    print(f"Total turns: {len(messages) // 2}")
    print(f"Conversation ID: {conversation_id}")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(test_cia_conversation())