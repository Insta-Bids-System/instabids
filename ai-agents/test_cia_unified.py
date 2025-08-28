import requests
import json
import time
from config.service_urls import get_backend_url

print("Testing CIA Agent with GPT-4o and Unified Conversation System")
print("=" * 60)

# Test CIA conversation
thread_id = "test-thread-cia-unified-" + str(int(time.time()))
cia_response = requests.post(f'{get_backend_url()}/api/cia/chat', json={
    "message": "I need to install a new deck in my backyard. Can you help me?",
    "session_id": thread_id,
    "user_id": "test-user-123"
})

print("\n1. CIA API Response:")
print(f"Status: {cia_response.status_code}")
if cia_response.status_code == 200:
    response_data = cia_response.json()
    print(f"Response text: {response_data.get('response')[:200]}...")
    print(f"Session ID: {response_data.get('session_id')}")
    print(f"Current phase: {response_data.get('current_phase')}")
    print(f"Ready for JAA: {response_data.get('ready_for_jaa')}")
else:
    print(f"Error: {cia_response.text}")

# Give it a moment to save
time.sleep(2)

# Now check if data was saved to unified tables
print("\n2. Checking Unified Tables...")

# Check unified_conversations
check_conversation = requests.post(f'{get_backend_url()}/api/conversations/list', json={
    "agent_type": "CIA"
})

if check_conversation.status_code == 200:
    conv_data = check_conversation.json()
    print(f"\nUnified Conversations: Found {len(conv_data.get('data', []))} conversations")
    if conv_data.get('data'):
        # Find our specific conversation
        our_conv = None
        for conv in conv_data['data']:
            if conv.get('metadata', {}).get('session_id') == thread_id:
                our_conv = conv
                break
        
        if our_conv:
            print(f"Found our conversation ID: {our_conv.get('id')}")
            print(f"Agent type: {our_conv.get('agent_type')}")
            
            # Check messages for this conversation
            check_messages = requests.post(f'{get_backend_url()}/api/conversations/messages', json={
                "conversation_id": our_conv.get('id')
            })
            
            if check_messages.status_code == 200:
                msg_data = check_messages.json()
                print(f"\nUnified Messages: Found {len(msg_data.get('data', []))} messages")
                for msg in msg_data.get('data', [])[:3]:
                    print(f"  - {msg.get('role')}: {msg.get('content')[:100]}...")
            else:
                print(f"Failed to get messages: {check_messages.text}")
                msg_data = {'data': []}
        else:
            print(f"Could not find our conversation with session_id: {thread_id}")
            msg_data = {'data': []}
else:
    print(f"Failed to list conversations: {check_conversation.text}")
    conv_data = {'data': []}
    msg_data = {'data': []}

print("\n3. Summary:")
print("CIA agent responded" if cia_response.status_code == 200 else "CIA agent failed")
print("Conversation saved to unified_conversations" if our_conv else "No conversation saved")
print("Messages saved to unified_messages" if msg_data.get('data') else "No messages saved")