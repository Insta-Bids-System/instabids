#!/usr/bin/env python3
"""
Test CIA conversation context - verify messages are maintained across turns
"""

import asyncio
import logging
import sys
import io
import requests
import time
import uuid

# Fix Windows encoding issues with emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE = "http://localhost:8008"

def test_conversation_context():
    """Test that CIA maintains conversation context across multiple turns"""
    print("=" * 80)
    print("🧪 TESTING CIA CONVERSATION CONTEXT")
    print("=" * 80)
    
    # Create unique session ID for this test
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    print(f"\n📝 Test Setup:")
    print(f"   Session ID: {session_id}")
    print(f"   User ID: {user_id}")
    
    # Turn 1: Initial message
    print("\n--- Turn 1: Initial Project Description ---")
    response1 = requests.post(
        f"{API_BASE}/api/cia/stream",
        json={
            "messages": [{"role": "user", "content": "I need to renovate my kitchen. It's about 200 sq ft."}],
            "user_id": user_id,
            "conversation_id": session_id
        },
        stream=True,
        timeout=30
    )
    
    response1_text = ""
    for line in response1.iter_lines():
        if line and line.startswith(b'data: '):
            response1_text += "."  # Just track that we got data
    print(f"✅ Got response (length: {len(response1_text)} chunks)")
    
    # Wait briefly
    time.sleep(2)
    
    # Turn 2: Add budget info (should acknowledge kitchen project)
    print("\n--- Turn 2: Adding Budget Info ---")
    print("💬 Sending: My budget is $30,000")
    
    response2 = requests.post(
        f"{API_BASE}/api/cia/stream", 
        json={
            "messages": [{"role": "user", "content": "My budget is $30,000"}],
            "user_id": user_id,
            "conversation_id": session_id
        },
        stream=True,
        timeout=30
    )
    
    # Collect actual response text this time
    response2_text = ""
    for line in response2.iter_lines():
        if line and line.startswith(b'data: '):
            try:
                import json
                data = json.loads(line[6:])
                if 'choices' in data and data['choices']:
                    content = data['choices'][0].get('delta', {}).get('content', '')
                    response2_text += content
            except:
                pass
    
    print(f"🤖 CIA Response: {response2_text[:200]}...")
    
    # Check if response acknowledges kitchen project from Turn 1
    context_maintained = False
    if any(word in response2_text.lower() for word in ['kitchen', '200', 'sq ft', 'square feet', 'renovation']):
        print("✅ SUCCESS: CIA remembered the kitchen renovation context!")
        context_maintained = True
    else:
        print("❌ FAILURE: CIA did not reference the kitchen project from Turn 1")
        
    # Also check if it's not the generic opening
    if "Hi! I'm Alex" in response2_text:
        print("❌ FAILURE: CIA returned generic opening message instead of contextual response")
        context_maintained = False
    
    # Turn 3: Add timeline (should acknowledge both kitchen and budget)
    print("\n--- Turn 3: Adding Timeline ---")
    print("💬 Sending: I need this done in 6 weeks")
    
    response3 = requests.post(
        f"{API_BASE}/api/cia/stream",
        json={
            "messages": [{"role": "user", "content": "I need this done in 6 weeks"}],
            "user_id": user_id,
            "conversation_id": session_id
        },
        stream=True,
        timeout=30
    )
    
    response3_text = ""
    for line in response3.iter_lines():
        if line and line.startswith(b'data: '):
            try:
                import json
                data = json.loads(line[6:])
                if 'choices' in data and data['choices']:
                    content = data['choices'][0].get('delta', {}).get('content', '')
                    response3_text += content
            except:
                pass
    
    print(f"🤖 CIA Response: {response3_text[:200]}...")
    
    # Check if response acknowledges previous context
    if any(word in response3_text.lower() for word in ['kitchen', '$30', '30,000', 'budget']):
        print("✅ SUCCESS: CIA maintained full conversation context!")
    else:
        print("❌ FAILURE: CIA lost previous conversation context")
    
    # Final verdict
    print("\n" + "=" * 80)
    if context_maintained:
        print("✅ TEST PASSED: CIA maintains conversation context correctly")
    else:
        print("❌ TEST FAILED: CIA is not maintaining conversation context")
    print("=" * 80)
    
    return context_maintained

if __name__ == "__main__":
    try:
        success = test_conversation_context()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)