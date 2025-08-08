#!/usr/bin/env python3
"""
Test WebSocket Connection for Admin Dashboard
Tests if authentication fixes allow WebSocket connection
"""

import asyncio
import json
import sys
import io
import uuid
import websockets

# Fix Unicode output issues on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def test_admin_websocket():
    """Test admin WebSocket connection with mock authentication"""
    
    print("🧪 Testing Admin WebSocket Connection...")
    
    # First, create a mock session ID in the format our auth service expects
    session_id = f"admin-{uuid.uuid4()}"
    print(f"📝 Using session ID: {session_id}")
    
    try:
        # Connect to admin WebSocket
        uri = "ws://localhost:8008/api/admin/ws/admin"
        print(f"🔌 Connecting to: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established")
            
            # Wait for test message
            print("⏳ Waiting for test message...")
            test_response = await asyncio.wait_for(websocket.recv(), timeout=5)
            test_data = json.loads(test_response)
            print(f"📨 Received test message: {test_data}")
            
            # Send authentication message
            auth_message = {
                "type": "auth",
                "session_id": session_id,
                "timestamp": "2025-01-01T00:00:00Z"
            }
            
            print(f"🔐 Sending auth message: {auth_message}")
            await websocket.send(json.dumps(auth_message))
            
            # Wait for authentication response
            print("⏳ Waiting for auth response...")
            auth_response = await asyncio.wait_for(websocket.recv(), timeout=5)
            auth_data = json.loads(auth_response)
            print(f"🔓 Authentication response: {auth_data}")
            
            if auth_data.get("type") == "connection_status" and auth_data.get("data", {}).get("status") == "connected":
                print("🎉 WEBSOCKET AUTHENTICATION SUCCESSFUL!")
                print(f"👤 Admin user: {auth_data.get('data', {}).get('admin_user_id')}")
                
                # Wait for dashboard data or auth_success
                print("⏳ Waiting for next message...")
                next_response = await asyncio.wait_for(websocket.recv(), timeout=10)
                next_data = json.loads(next_response)
                print(f"📨 Next message type: {next_data.get('type')}")
                
                # Send ping to test bidirectional communication
                ping_message = {
                    "type": "ping",
                    "timestamp": "2025-01-01T00:00:00Z"
                }
                
                print("🏓 Sending ping...")
                await websocket.send(json.dumps(ping_message))
                
                # Wait for pong
                pong_response = await asyncio.wait_for(websocket.recv(), timeout=5)
                pong_data = json.loads(pong_response)
                print(f"🏓 Received pong: {pong_data}")
                
                if pong_data.get("type") == "pong":
                    print("✅ WEBSOCKET BIDIRECTIONAL COMMUNICATION WORKING!")
                    return True
                else:
                    print(f"❌ Expected pong, got: {pong_data}")
                    return False
                    
            elif auth_data.get("type") == "error":
                print(f"❌ Authentication failed: {auth_data.get('message')}")
                return False
            else:
                print(f"❌ Unexpected auth response: {auth_data}")
                return False
                
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ WebSocket connection closed: {e}")
        return False
    except asyncio.TimeoutError:
        print("❌ WebSocket connection timed out")
        return False
    except Exception as e:
        print(f"❌ WebSocket connection error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 WEBSOCKET CONNECTION TEST")
    print("=" * 60)
    
    # Test WebSocket connection
    success = await test_admin_websocket()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 WEBSOCKET TEST PASSED - Real-time updates should work!")
        print("💡 Try refreshing the admin dashboard to see if 'Disconnected' changes to 'Connected'")
    else:
        print("❌ WEBSOCKET TEST FAILED - Real-time updates not working")
        print("🔧 Check backend logs for authentication issues")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())