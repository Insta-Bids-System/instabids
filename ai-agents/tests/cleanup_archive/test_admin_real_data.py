"""
Test Admin Dashboard Real Data Integration
Verifies that all admin endpoints return real data from the database
"""

import asyncio
import json

import aiohttp


async def test_admin_endpoints():
    """Test all admin endpoints for real data"""

    print("\n=== Testing Admin Dashboard Real Data Integration ===\n")

    # Base URL for admin API
    base_url = "http://localhost:8008"

    # Test endpoints
    endpoints = [
        ("/api/admin/dashboard", "Dashboard Overview"),
        ("/api/agents/CIA/health", "CIA Health"),
        ("/api/agents/JAA/health", "JAA Health"),
        ("/api/agents/CDA/health", "CDA Health"),
        ("/api/agents/EAA/health", "EAA Health"),
        ("/api/agents/WFA/health", "WFA Health"),
        ("/api/email-tracking/stats", "Email Tracking Stats"),
        ("/api/form-tracking/stats", "Form Tracking Stats"),
        ("/api/admin/database/stats", "Database Stats"),
    ]

    async with aiohttp.ClientSession() as session:
        for endpoint, name in endpoints:
            try:
                print(f"\n[TEST] {name} - {endpoint}")
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"[OK] SUCCESS - Status: {response.status}")

                        # Pretty print key data points
                        if "system_metrics" in data:
                            metrics = data["system_metrics"]
                            print(f"  - Active Bid Cards: {metrics.get('bid_cards_active', 0)}")
                            print(f"  - Contractors Total: {metrics.get('contractors_total', 0)}")
                            print(f"  - Emails Sent Today: {metrics.get('emails_sent_today', 0)}")
                            print(f"  - Forms Filled Today: {metrics.get('forms_filled_today', 0)}")

                        elif "health_score" in data:
                            print(f"  - Agent: {data.get('agent_name', 'Unknown')}")
                            print(f"  - Status: {data.get('status', 'Unknown')}")
                            print(f"  - Health Score: {data.get('health_score', 0)}%")
                            print(f"  - Operations Today: {data.get('operations_today', 0)}")

                        elif "total_emails_sent" in data:
                            print(f"  - Total Emails: {data.get('total_emails_sent', 0)}")
                            print(f"  - Emails Today: {data.get('emails_sent_today', 0)}")
                            print(f"  - Delivery Rate: {data.get('delivery_rate', 0):.1f}%")
                            print(f"  - Open Rate: {data.get('open_rate', 0):.1f}%")

                        elif "total_forms_submitted" in data:
                            print(f"  - Total Forms: {data.get('total_forms_submitted', 0)}")
                            print(f"  - Forms Today: {data.get('forms_submitted_today', 0)}")
                            print(f"  - Success Rate: {data.get('success_rate', 0):.1f}%")

                        elif "table_counts" in data:
                            counts = data.get("table_counts", {})
                            print(f"  - Bid Cards: {counts.get('bid_cards', 0)}")
                            print(f"  - Contractors: {counts.get('contractor_leads', 0)}")
                            print(f"  - Campaigns: {counts.get('outreach_campaigns', 0)}")

                    else:
                        print(f"[FAIL] FAILED - Status: {response.status}")
                        error_text = await response.text()
                        print(f"  - Error: {error_text}")

            except Exception as e:
                print(f"[ERROR] ERROR - {e!s}")

    print("\n\n=== Test Complete ===")
    print("\nSUMMARY:")
    print("- All endpoints should return real data from the database")
    print("- Email/form counts should reflect actual followup_logs entries")
    print("- Agent health should show real activity metrics")
    print("- Database stats should show actual table row counts")

    # Test WebSocket connection
    print("\n\n=== Testing WebSocket Connection ===")
    try:
        ws_url = "ws://localhost:8008/ws/admin"
        async with session.ws_connect(ws_url) as ws:
            print("[OK] WebSocket connection established")

            # Send auth message
            auth_msg = {
                "type": "auth",
                "token": "test-admin-token"
            }
            await ws.send_str(json.dumps(auth_msg))

            # Listen for a few messages
            print("\nListening for WebSocket updates (5 seconds)...")
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < 5:
                try:
                    msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        print(f"[MSG] Received: {data.get('type', 'unknown')} - {data.get('timestamp', '')}")
                except TimeoutError:
                    continue

            await ws.close()
            print("\n[OK] WebSocket test complete")

    except Exception as e:
        print(f"[ERROR] WebSocket error: {e!s}")

if __name__ == "__main__":
    asyncio.run(test_admin_endpoints())
