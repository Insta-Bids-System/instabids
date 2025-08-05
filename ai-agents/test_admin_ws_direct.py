#!/usr/bin/env python3
"""Test admin WebSocket directly"""

import asyncio
import json

import websockets


async def test_admin_ws():
    uri = "ws://localhost:8008/api/admin/ws/admin"

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to admin WebSocket")

            # Should receive test message immediately
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"Received initial message: {message}")
            except TimeoutError:
                print("No initial message received in 2 seconds")

            # Try to send auth message
            auth_msg = {
                "type": "auth",
                "session_id": "test-session"
            }
            await websocket.send(json.dumps(auth_msg))
            print(f"Sent auth: {auth_msg}")

            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"Received response: {response}")
            except TimeoutError:
                print("No response received in 2 seconds")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_admin_ws())
