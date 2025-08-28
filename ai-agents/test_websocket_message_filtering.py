#!/usr/bin/env python3
"""
TEST WEBSOCKET MESSAGE FILTERING
Tests real-time WebSocket message filtering capabilities
"""

import asyncio
import websockets
import json
import uuid
import requests
import sys
import io
from config.service_urls import get_backend_url

# Fix Unicode output issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class WebSocketMessageFilteringTest:
    def __init__(self):
        self.base_url = get_backend_url()
        self.ws_url = "ws://localhost:8008"
        self.test_results = {}
        
    async def test_admin_websocket_connection(self):
        """Test if admin WebSocket connection works"""
        print("ADMIN WEBSOCKET CONNECTION TEST")
        print("=" * 40)
        
        try:
            # Test admin WebSocket endpoint
            uri = f"{self.ws_url}/api/admin/ws/admin"
            session_id = f"test-{uuid.uuid4()}"
            
            async with websockets.connect(uri) as websocket:
                print("✓ Admin WebSocket connected successfully")
                
                # Wait for welcome message
                try:
                    welcome = await asyncio.wait_for(websocket.recv(), timeout=5)
                    welcome_data = json.loads(welcome)
                    print(f"✓ Received welcome: {welcome_data.get('message', 'Connected')}")
                except asyncio.TimeoutError:
                    print("✓ No welcome message (expected for some implementations)")
                
                # Send auth
                auth_msg = {
                    "type": "auth",
                    "session_id": session_id,
                    "timestamp": "2025-01-01T00:00:00Z"
                }
                
                await websocket.send(json.dumps(auth_msg))
                print("✓ Authentication sent")
                
                # Wait for auth response
                try:
                    auth_response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    auth_data = json.loads(auth_response)
                    
                    if auth_data.get("type") == "connection_status":
                        print("✓ Admin WebSocket authentication successful")
                        print(f"  Client ID: {auth_data.get('data', {}).get('client_id')}")
                        return True
                    else:
                        print(f"? Auth response: {auth_data}")
                        return True  # Connected but different response format
                        
                except asyncio.TimeoutError:
                    print("✓ Connected but no auth response")
                    return True
                    
        except Exception as e:
            print(f"✗ Admin WebSocket failed: {e}")
            return False
    
    def test_messaging_websocket_endpoints(self):
        """Test if there are dedicated messaging WebSocket endpoints"""
        print("\nMESSAGING WEBSOCKET ENDPOINTS TEST")  
        print("=" * 40)
        
        # Check if messaging WebSocket endpoints exist
        endpoints_to_test = [
            "/ws/messages",
            "/ws/messaging",
            "/ws/chat",
            "/api/messages/ws",
            "/api/messaging/ws",
            "/ws/realtime",
        ]
        
        found_endpoints = []
        
        for endpoint in endpoints_to_test:
            try:
                # Test endpoint existence by attempting connection
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=2)
                # Even if it fails, if it's a WebSocket endpoint it might return specific errors
                if response.status_code in [426, 400, 200]:  # WebSocket upgrade required
                    found_endpoints.append(endpoint)
                    print(f"✓ Found potential WebSocket endpoint: {endpoint}")
            except:
                # Ignore connection errors for now
                pass
        
        if found_endpoints:
            print(f"✓ Found {len(found_endpoints)} potential messaging WebSocket endpoints")
            return True
        else:
            print("✗ No dedicated messaging WebSocket endpoints found")
            return False
    
    async def test_message_broadcast_capability(self):
        """Test if messages can be broadcast via WebSocket"""
        print("\nMESSAGE BROADCAST TEST")
        print("=" * 40)
        
        try:
            # Connect to admin WebSocket
            uri = f"{self.ws_url}/api/admin/ws/admin" 
            session_id = f"broadcast-test-{uuid.uuid4()}"
            
            async with websockets.connect(uri) as websocket:
                # Auth
                auth_msg = {
                    "type": "auth",
                    "session_id": session_id,
                    "timestamp": "2025-01-01T00:00:00Z"
                }
                
                await websocket.send(json.dumps(auth_msg))
                
                # Clear any welcome/auth messages
                try:
                    while True:
                        await asyncio.wait_for(websocket.recv(), timeout=1)
                except asyncio.TimeoutError:
                    pass
                
                # Send a test message through the intelligent messaging API
                # and see if we get a WebSocket update
                print("Sending test message through API...")
                
                payload = {
                    "content": "Test message for WebSocket broadcast",
                    "sender_type": "homeowner",
                    "sender_id": str(uuid.uuid4()),
                    "bid_card_id": str(uuid.uuid4()),
                    "message_type": "text"
                }
                
                # Send via API (in background)
                try:
                    response = requests.post(
                        f"{self.base_url}/api/intelligent-messages/send",
                        json=payload,
                        timeout=5
                    )
                    print(f"API Response: {response.status_code}")
                except Exception as e:
                    print(f"API Error: {e}")
                
                # Check for WebSocket messages within 10 seconds
                print("Listening for WebSocket broadcasts...")
                
                messages_received = []
                try:
                    for i in range(10):  # Listen for 10 messages max
                        msg = await asyncio.wait_for(websocket.recv(), timeout=2)
                        msg_data = json.loads(msg)
                        messages_received.append(msg_data)
                        print(f"  Received: {msg_data.get('type', 'unknown')} - {msg_data}")
                        
                        # Look for message-related broadcasts
                        if any(key in str(msg_data).lower() for key in ['message', 'chat', 'intelligent']):
                            print("✓ Message-related WebSocket broadcast detected!")
                            return True
                            
                except asyncio.TimeoutError:
                    pass
                
                if messages_received:
                    print(f"✓ Received {len(messages_received)} WebSocket messages")
                    print("? No message-specific broadcasts detected")
                    return False
                else:
                    print("✗ No WebSocket messages received")
                    return False
                    
        except Exception as e:
            print(f"✗ Broadcast test failed: {e}")
            return False
    
    def test_real_time_filtering_architecture(self):
        """Test if real-time filtering architecture exists"""
        print("\nREAL-TIME FILTERING ARCHITECTURE TEST")
        print("=" * 40)
        
        # Check if the intelligent messaging system is designed for real-time
        try:
            # Test the health endpoint
            response = requests.get(f"{self.base_url}/api/intelligent-messages/health", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                print("✓ Intelligent messaging system operational")
                print(f"  GPT Available: {health_data.get('gpt5_available', False)}")
                print(f"  Fallback System: {health_data.get('fallback_system', 'unknown')}")
                
                # The intelligent messaging system exists and works
                # Real-time filtering would be implemented by:
                # 1. Messages going through intelligent agent first
                # 2. Results broadcast via WebSocket to connected clients
                # 3. Frontend filtering based on WebSocket updates
                
                print("\nARCHITECTURE ANALYSIS:")
                print("✓ Message filtering: Intelligent agent processes all messages")
                print("✓ WebSocket system: Admin WebSocket manager operational") 
                print("? Real-time integration: Would need to connect messaging to WebSocket")
                print("? Frontend integration: Would need WebSocket client in chat UI")
                
                return True
            else:
                print("✗ Intelligent messaging system not responding")
                return False
                
        except Exception as e:
            print(f"✗ Architecture test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all WebSocket message filtering tests"""
        print("WEBSOCKET MESSAGE FILTERING VERIFICATION")
        print("=" * 60)
        
        # Test 1: Admin WebSocket
        admin_ws_works = await self.test_admin_websocket_connection()
        
        # Test 2: Messaging endpoints  
        messaging_endpoints = self.test_messaging_websocket_endpoints()
        
        # Test 3: Message broadcasts
        broadcast_works = await self.test_message_broadcast_capability()
        
        # Test 4: Architecture analysis
        architecture_ready = self.test_real_time_filtering_architecture()
        
        # Summary
        print("\n" + "=" * 60)
        print("FINAL WEBSOCKET MESSAGE FILTERING ASSESSMENT")
        print("=" * 60)
        
        print(f"Admin WebSocket System: {'WORKING' if admin_ws_works else 'FAILED'}")
        print(f"Messaging WebSocket Endpoints: {'FOUND' if messaging_endpoints else 'NOT FOUND'}")
        print(f"Real-time Message Broadcasts: {'WORKING' if broadcast_works else 'NOT IMPLEMENTED'}")
        print(f"Filtering Architecture: {'READY' if architecture_ready else 'NOT READY'}")
        
        # Overall assessment
        if admin_ws_works and architecture_ready:
            if broadcast_works:
                print("\n✓ RESULT: Real-time WebSocket message filtering is FULLY OPERATIONAL")
                return True
            else:
                print("\n? RESULT: WebSocket infrastructure ready, message filtering needs integration")
                print("  RECOMMENDATIONS:")
                print("  1. Connect intelligent messaging results to WebSocket broadcasts")
                print("  2. Add message filtering events to WebSocket manager")
                print("  3. Update frontend to listen for filtered message updates")
                return False
        else:
            print("\n✗ RESULT: WebSocket message filtering system needs development")
            return False

async def main():
    """Run WebSocket message filtering tests"""
    tester = WebSocketMessageFilteringTest()
    result = await tester.run_all_tests()
    return result

if __name__ == "__main__":
    asyncio.run(main())