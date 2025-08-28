"""
Test WebSocket Connectivity for COIA
Tests that WebSocket connections work and receive status updates
"""

import asyncio
import json
import websockets
import aiohttp
import time

async def test_websocket():
    """Test WebSocket connection and message reception"""
    session_id = f"test-ws-{int(time.time())}"
    uri = f"ws://localhost:8008/api/coia/ws/{session_id}"
    
    print("=" * 60)
    print("COIA WebSocket Connectivity Test")
    print("=" * 60)
    print(f"Session ID: {session_id}")
    print(f"Connecting to: {uri}")
    
    try:
        # First check if HTTP endpoint works
        async with aiohttp.ClientSession() as session:
            test_response = await session.get('http://localhost:8008/')
            print(f"[INFO] Backend HTTP check: Status {test_response.status}")
        
        async with websockets.connect(uri) as websocket:
            print("[PASSED] Connected to WebSocket")
            
            # Trigger a COIA request to generate WebSocket messages
            print("\nTriggering COIA request to generate WebSocket traffic...")
            
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    'http://localhost:8008/api/coia/landing',
                    json={
                        'session_id': session_id,
                        'message': 'Test WebSocket Company in Miami',
                        'company_name': 'Test WebSocket Company',
                        'location': 'Miami, FL'
                    }
                )
                
                if response.status == 200:
                    print("[PASSED] COIA request triggered successfully")
                else:
                    print(f"[WARNING] COIA request returned status: {response.status}")
            
            # Wait for WebSocket messages (with timeout)
            print("\nListening for WebSocket messages (10 second timeout)...")
            messages_received = []
            
            try:
                while len(messages_received) < 5:  # Collect up to 5 messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    messages_received.append(data)
                    
                    print(f"[MESSAGE {len(messages_received)}] Type: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'agent_status':
                        agent_name = data.get('agent_name', 'unknown')
                        status = data.get('status', 'unknown')
                        progress = data.get('progress', 0)
                        print(f"  Agent: {agent_name}, Status: {status}, Progress: {progress}%")
                    elif data.get('type') == 'conversation_update':
                        print(f"  Conversation update received")
                    else:
                        print(f"  Data: {str(data)[:100]}...")
                        
            except asyncio.TimeoutError:
                if messages_received:
                    print(f"\n[INFO] Timeout reached. Received {len(messages_received)} messages total")
                else:
                    print("\n[WARNING] No messages received within timeout period")
            
            # Summary
            print("\n" + "=" * 60)
            if messages_received:
                print(f"[PASSED] WebSocket Test Complete")
                print(f"  - Successfully connected")
                print(f"  - Received {len(messages_received)} messages")
                
                # Analyze message types
                message_types = {}
                for msg in messages_received:
                    msg_type = msg.get('type', 'unknown')
                    message_types[msg_type] = message_types.get(msg_type, 0) + 1
                
                print("\n  Message Types Received:")
                for msg_type, count in message_types.items():
                    print(f"    - {msg_type}: {count}")
                    
                return True
            else:
                print(f"[FAILED] No WebSocket messages received")
                print("  - This may indicate the WebSocket implementation is incomplete")
                return False
                
    except Exception as e:
        print(f"[FAILED] WebSocket connection failed: {e}")
        print("  - Make sure the backend is running on port 8008")
        print("  - Check Docker: docker-compose ps")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    
    if result:
        print("\n[SUCCESS] WebSocket connectivity verified!")
    else:
        print("\n[ERROR] WebSocket test failed - check implementation")