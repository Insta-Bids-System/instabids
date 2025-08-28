#!/usr/bin/env python3
"""
Simple CIA conversation test - one message at a time
"""

import requests
import json
import time
from config.service_urls import get_backend_url

# Track conversation state
conversation_history = []
conversation_id = f"test_simple_{int(time.time())}"
user_id = "test_user_123"

def send_message(message):
    """Send a single message and get response"""
    print(f"\n{'='*60}")
    print(f"USER: {message}")
    print(f"{'='*60}")
    
    # Add to history
    conversation_history.append({"role": "user", "content": message})
    
    url = f"{get_backend_url()}/api/cia/stream"
    
    payload = {
        "messages": conversation_history.copy(),
        "conversation_id": conversation_id,
        "user_id": user_id,
        "max_tokens": 500,
        "model_preference": "gpt-5"  # Try GPT-5 first
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }, stream=True, timeout=120)
        
        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            return None
        
        full_text = ""
        
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data_part = line_text[6:]
                    if data_part.strip() == '[DONE]':
                        break
                    try:
                        chunk_data = json.loads(data_part)
                        if 'choices' in chunk_data and chunk_data['choices']:
                            delta = chunk_data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                full_text += delta['content']
                    except json.JSONDecodeError:
                        continue
        
        elapsed = time.time() - start_time
        
        if full_text:
            # Add to history
            conversation_history.append({"role": "assistant", "content": full_text})
            
            print(f"\nCIA ({elapsed:.2f}s):")
            print(full_text)
            
            # Check for key phrases
            if 'bid card' in full_text.lower():
                print("\n  [CHECK] BID CARD MENTIONED")
            if any(phrase in full_text.lower() for phrase in ['sign up', 'get started', 'create account']):
                print("  [CHECK] SIGNUP PROMPTED")
            if '$400 billion' in full_text or '400 billion' in full_text:
                print("  [CHECK] CORPORATE EXTRACTION MENTIONED")
                
            return full_text
        else:
            print("No response received")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("CIA SIMPLE CONVERSATION TEST")
    print(f"Conversation ID: {conversation_id}")
    print("="*60)
    
    # Test conversation flow - Price conscious persona
    messages = [
        "I need to remodel my bathroom but I'm on a really tight budget. How much do these things usually cost?",
        "But what about all the fees? I've heard contractors charge extra for everything",
        "Can I really save money compared to using Angie's List or HomeAdvisor?",
        "What if I just want a basic update, nothing fancy?",
        "How do I know the contractors won't overcharge me?"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        response = send_message(msg)
        
        if not response:
            print(f"\nStopping at turn {i} due to error")
            break
            
        # Small pause between messages
        time.sleep(2)
    
    print("\n" + "="*60)
    print("CONVERSATION COMPLETE")
    print(f"Total turns: {len([m for m in conversation_history if m['role'] == 'user'])}")
    print("="*60)

if __name__ == "__main__":
    main()