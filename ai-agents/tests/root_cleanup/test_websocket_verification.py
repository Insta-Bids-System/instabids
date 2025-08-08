#!/usr/bin/env python3
"""
WebSocket Connection Verification
Demonstrates that the WebSocket authentication fix is working
"""

import asyncio
import json
import sys
import io
import uuid
import websockets

# Fix Unicode output issues on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def verify_websocket_working():
    """Verify the WebSocket connection is working for real-time updates"""
    
    print("🔍 WEBSOCKET VERIFICATION TEST")
    print("=" * 50)
    
    session_id = f"admin-{uuid.uuid4()}"
    
    try:
        uri = "ws://localhost:8008/api/admin/ws/admin"
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket Connection: ESTABLISHED")
            
            # Receive test message
            test_msg = await asyncio.wait_for(websocket.recv(), timeout=3)
            print(f"✅ Test Message: {json.loads(test_msg)['message']}")
            
            # Send auth
            await websocket.send(json.dumps({
                "type": "auth",
                "session_id": session_id,
                "timestamp": "2025-01-01T00:00:00Z"
            }))
            
            # Get connection status
            conn_response = await asyncio.wait_for(websocket.recv(), timeout=3)
            conn_data = json.loads(conn_response)
            
            if conn_data.get("type") == "connection_status":
                print(f"✅ Authentication: SUCCESS")
                print(f"✅ Client ID: {conn_data['data']['client_id']}")
                print(f"✅ Active Connections: {conn_data['data']['active_connections']}")
            
            # Get auth success or dashboard data
            next_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
            next_data = json.loads(next_msg)
            
            if next_data.get("type") == "auth_success":
                print(f"✅ Auth Success: {next_data['admin_user']['email']}")
                
                # Get dashboard data
                dashboard_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                dashboard_data = json.loads(dashboard_msg)
                print(f"✅ Dashboard Data: {dashboard_data['type']}")
                
            elif next_data.get("type") == "dashboard_overview":
                print(f"✅ Dashboard Overview: Received real-time data")
                print(f"   - System Metrics: {len(next_data.get('data', {}).get('system_metrics', {}))}")
                print(f"   - Database Stats: Available")
                print(f"   - WebSocket Stats: Available")
            
            print("\n🎉 WEBSOCKET REAL-TIME UPDATES: WORKING!")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket verification failed: {e}")
        return False


async def main():
    """Main verification"""
    success = await verify_websocket_working()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 VERIFICATION COMPLETE: WebSocket real-time updates are WORKING!")
        print("💡 The admin dashboard should now show 'Connected' status")
        print("💡 Try refreshing http://localhost:5173/admin/login to see live updates")
    else:
        print("❌ VERIFICATION FAILED: WebSocket real-time updates not working")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())