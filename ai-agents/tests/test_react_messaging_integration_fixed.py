"""
Test React Messaging Components Integration
Tests that React components use API endpoints correctly for content filtering
"""

import asyncio
import time
import uuid

import requests
from playwright.async_api import async_playwright


# Test configuration
API_BASE_URL = "http://localhost:8008"
FRONTEND_URL = "http://localhost:3000"  # Adjust to your frontend port

async def test_messaging_with_contact_filtering():
    """Test that messages with contact info get filtered through API"""

    # First, let's create a test conversation via API
    print("\n1. Creating test conversation via API...")

    # Use proper UUIDs
    bid_card_id = str(uuid.uuid4())

    # Create message with contact info
    message_data = {
        "bid_card_id": bid_card_id,
        "content": "Hi, my phone is 555-1234 and email is test@email.com",
        "sender_type": "homeowner",
        "sender_id": str(uuid.uuid4())
    }

    # Send via API (should filter contact info)
    api_response = requests.post(
        f"{API_BASE_URL}/api/messages/send",
        json=message_data,
        params={"user_type": "homeowner", "user_id": message_data["sender_id"]}
    )

    if api_response.status_code == 200:
        api_result = api_response.json()
        if api_result.get("success"):
            print(f"✅ API filtered content: {api_result.get('filtered_content', 'N/A')}")
            print(f"   Content was filtered: {api_result.get('content_filtered', False)}")
            print(f"   Message ID: {api_result.get('message_id', 'N/A')}")
        else:
            print(f"❌ API returned success=false: {api_result.get('error', 'Unknown error')}")
            return
    else:
        print(f"❌ API error: {api_response.status_code}")
        print(api_response.json())
        return

    # Now test via Playwright to see if frontend uses API
    print("\n2. Testing frontend integration...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))

        # Navigate to messaging interface
        await page.goto(f"{FRONTEND_URL}/messages")

        # Wait for page to load
        await page.wait_for_load_state("networkidle")

        # Check if messaging interface loaded
        try:
            await page.wait_for_selector("[data-testid='message-input']", timeout=5000)
            print("✅ Messaging interface loaded")
        except:
            print("❌ Messaging interface not found")
            # Try alternative selectors
            try:
                # Look for any input field that might be for messaging
                input_field = await page.query_selector("input[type='text'], textarea")
                if input_field:
                    print("✅ Found input field (not using data-testid)")
                else:
                    print("❌ No input field found")
            except:
                pass

            # Take screenshot for debugging
            await page.screenshot(path="messaging_interface_error.png")
            print("Screenshot saved as messaging_interface_error.png")

        # Listen for network requests to see if API is called
        api_calls = []

        def handle_request(request):
            if "/api/" in request.url:
                api_calls.append({
                    "url": request.url,
                    "method": request.method,
                    "time": time.time()
                })
                print(f"API Request: {request.method} {request.url}")

        page.on("request", handle_request)

        # Try to find and use any message input
        input_selectors = [
            "[data-testid='message-input']",
            "textarea",
            "input[type='text']",
            "[placeholder*='message']",
            "[placeholder*='Message']",
            "[aria-label*='message']"
        ]

        message_input = None
        for selector in input_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    message_input = element
                    print(f"Found input using selector: {selector}")
                    break
            except:
                continue

        if message_input:
            # Type message with contact info
            await message_input.fill("Call me at 555-9876 or email john@example.com")

            # Look for send button
            send_selectors = [
                "[data-testid='send-message-button']",
                "button[type='submit']",
                "button:has-text('Send')",
                "button:has-text('send')",
                "[aria-label*='send']"
            ]

            send_button = None
            for selector in send_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        send_button = element
                        print(f"Found send button using selector: {selector}")
                        break
                except:
                    continue

            if send_button:
                # Send message
                await send_button.click()

                # Wait for potential API call
                await page.wait_for_timeout(2000)

                # Check if message API was called
                message_api_called = any("/api/messages" in call["url"] for call in api_calls)

                if message_api_called:
                    print("✅ Frontend correctly uses API endpoint")
                    relevant_calls = [call for call in api_calls if "/api/messages" in call["url"]]
                    for call in relevant_calls:
                        print(f"   - {call['method']} {call['url']}")
                else:
                    print("❌ Frontend bypasses API - using Supabase directly!")
                    print("   This means NO content filtering is happening!")

                    # Check if Supabase was called instead
                    supabase_calls = [call for call in api_calls if "supabase" in call["url"]]
                    if supabase_calls:
                        print("   Detected direct Supabase calls:")
                        for call in supabase_calls:
                            print(f"   - {call['method']} {call['url']}")
            else:
                print("❌ Could not find send button")
        else:
            print("❌ Could not find message input field")

        # Take screenshot of final state
        await page.screenshot(path="messaging_test_result.png")
        print("\nScreenshot saved as messaging_test_result.png")

        await browser.close()

async def check_frontend_running():
    """Quick check if frontend is running"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        return response.status_code < 500
    except:
        return False

def main():
    """Run all integration tests"""

    print("=" * 60)
    print("React Messaging Components Integration Test")
    print("=" * 60)

    # Check if frontend is running
    print("\nChecking if frontend is running...")
    if asyncio.run(check_frontend_running()):
        print("✅ Frontend is accessible")
    else:
        print("❌ Frontend not running on port 3000")
        print("   Please ensure the React app is running")
        return

    # Run tests
    asyncio.run(test_messaging_with_contact_filtering())

    print("\n" + "=" * 60)
    print("Integration Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
