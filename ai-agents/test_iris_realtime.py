"""
Test IRIS agent real-time updates with visual effects
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_iris_realtime():
    """Test IRIS agent actions with real-time WebSocket broadcasts"""
    
    print("\n=== TESTING IRIS REAL-TIME UPDATES ===\n")
    
    # Base URL for backend
    BASE_URL = "http://localhost:8008"
    
    # Test user and bid card IDs
    USER_ID = "550e8400-e29b-41d4-a716-446655440001"  # Demo Homeowner
    BID_CARD_ID = "78c3f7cb-64d8-496e-b396-32b24d790252"  # Test bid card
    
    async with aiohttp.ClientSession() as session:
        # 1. Test IRIS conversation with budget update
        print("1. Testing IRIS conversation with budget update...")
        
        iris_message = {
            "message": "Update the backyard transformation budget to $45,000 to $55,000 and mark it as urgent",
            "user_id": USER_ID,
            "bid_card_id": BID_CARD_ID,
            "context": {
                "current_budget_min": 35000,
                "current_budget_max": 45000,
                "project_type": "backyard_transformation"
            }
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/iris/chat",
                json=iris_message,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"  [OK] IRIS Response: {result.get('response', '')[:100]}...")
                    print(f"  [OK] Action triggered: {result.get('action_type', 'none')}")
                else:
                    print(f"  [FAIL] IRIS chat failed: {response.status}")
                    error_text = await response.text()
                    print(f"  [FAIL] Error: {error_text[:200]}")
        except Exception as e:
            print(f"  [FAIL] IRIS chat error: {e}")
        
        await asyncio.sleep(2)
        
        # 2. Trigger WebSocket broadcast for visual effects
        print("\n2. Broadcasting agent activity for visual effects...")
        
        broadcast_data = {
            "type": "agent_activity",
            "agent": "iris",
            "action": "bid_card_updated",
            "target_type": "bid_card",
            "target_id": BID_CARD_ID,
            "details": {
                "budget_min": 45000,
                "budget_max": 55000,
                "urgency": "urgent",
                "updated_fields": ["budget_min", "budget_max", "urgency"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/websocket/broadcast",
                json=broadcast_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    print("  [OK] WebSocket broadcast sent successfully")
                else:
                    print(f"  [FAIL] Broadcast failed: {response.status}")
        except Exception as e:
            print(f"  [FAIL] Broadcast error: {e}")
        
        await asyncio.sleep(2)
        
        # 3. Test IRIS analyzing property photos
        print("\n3. Testing IRIS photo analysis...")
        
        photo_analysis = {
            "message": "Analyze the backyard photo and identify any issues that need attention",
            "user_id": USER_ID,
            "context": {
                "photo_url": "https://example.com/backyard.jpg",
                "property_id": "d1ce83f1-900a-4677-bbdc-375db1f7bcca"
            }
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/iris/analyze-photo",
                json=photo_analysis,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"  [OK] Photo analysis: {result.get('analysis', '')[:100]}...")
                    
                    # Broadcast photo analysis activity
                    broadcast_data = {
                        "type": "agent_activity",
                        "agent": "iris",
                        "action": "photo_analyzed",
                        "target_type": "property",
                        "target_id": "d1ce83f1-900a-4677-bbdc-375db1f7bcca",
                        "details": {
                            "issues_found": result.get('issues_found', []),
                            "recommendations": result.get('recommendations', [])
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    async with session.post(
                        f"{BASE_URL}/api/websocket/broadcast",
                        json=broadcast_data
                    ) as ws_response:
                        if ws_response.status == 200:
                            print("  [OK] Photo analysis broadcast sent")
                else:
                    print(f"  [FAIL] Photo analysis failed: {response.status}")
        except Exception as e:
            print(f"  [FAIL] Photo analysis error: {e}")
        
        await asyncio.sleep(2)
        
        # 4. Test IRIS creating a potential bid card
        print("\n4. Testing IRIS creating potential bid card...")
        
        create_bid_card = {
            "message": "Create a bid card for roof repair with budget $8,000 to $12,000",
            "user_id": USER_ID,
            "context": {
                "property_id": "d1ce83f1-900a-4677-bbdc-375db1f7bcca",
                "suggested_trade": "roofing"
            }
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/iris/create-bid-card",
                json=create_bid_card,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    new_bid_card_id = result.get('bid_card_id')
                    print(f"  [OK] Created bid card: {new_bid_card_id}")
                    
                    # Broadcast bid card creation
                    broadcast_data = {
                        "type": "agent_activity",
                        "agent": "iris",
                        "action": "bid_card_created",
                        "target_type": "bid_card",
                        "target_id": new_bid_card_id,
                        "details": {
                            "title": "Roof Repair",
                            "budget_min": 8000,
                            "budget_max": 12000,
                            "trade": "roofing"
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    async with session.post(
                        f"{BASE_URL}/api/websocket/broadcast",
                        json=broadcast_data
                    ) as ws_response:
                        if ws_response.status == 200:
                            print("  [OK] Bid card creation broadcast sent")
                else:
                    print(f"  [FAIL] Bid card creation failed: {response.status}")
        except Exception as e:
            print(f"  [FAIL] Bid card creation error: {e}")
        
        # 5. Test WebSocket connection directly
        print("\n5. Testing WebSocket connection...")
        
        try:
            ws_url = "ws://localhost:8008/ws/agent-activity"
            async with session.ws_connect(ws_url) as ws:
                print(f"  [OK] Connected to WebSocket: {ws_url}")
                
                # Send a test message
                test_msg = {
                    "type": "test",
                    "agent": "iris",
                    "message": "Testing real-time updates"
                }
                await ws.send_str(json.dumps(test_msg))
                print("  [OK] Test message sent")
                
                # Wait for response (with timeout)
                try:
                    msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        print(f"  [OK] Received: {msg.data}")
                    else:
                        print(f"  [OK] Received message type: {msg.type}")
                except asyncio.TimeoutError:
                    print("  [INFO] No response received (timeout)")
                
                await ws.close()
        except Exception as e:
            print(f"  [FAIL] WebSocket error: {e}")
        
        print("\n=== TEST COMPLETE ===")
        print("\nCheck the UI at http://localhost:5173 for:")
        print("  • Purple glowing borders on updated elements")
        print("  • Agent badges showing 'IRIS' with activity icons")
        print("  • Real-time updates in bid cards")
        print("  • Activity notifications in the UI")

if __name__ == "__main__":
    asyncio.run(test_iris_realtime())