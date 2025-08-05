"""
Test React Messaging Components Integration
Tests that React components use API endpoints correctly for content filtering
"""

import asyncio
import time

import requests
from playwright.async_api import async_playwright


# Test configuration
API_BASE_URL = "http://localhost:8008"
FRONTEND_URL = "http://localhost:3000"  # Adjust to your frontend port

async def test_messaging_with_contact_filtering():
    """Test that messages with contact info get filtered through API"""

    # First, let's create a test conversation via API
    print("\n1. Creating test conversation via API...")

    # Create message with contact info
    message_data = {
        "bid_card_id": "test-bid-123",
        "content": "Hi, my phone is 555-1234 and email is test@email.com",
        "sender_type": "homeowner",
        "sender_id": "test-homeowner-123"
    }

    # Send via API (should filter contact info)
    api_response = requests.post(
        f"{API_BASE_URL}/api/messages/send",
        json=message_data,
        params={"user_type": "homeowner", "user_id": "test-homeowner-123"}
    )

    if api_response.status_code == 200:
        api_result = api_response.json()
        print(f"✅ API filtered content: {api_result['data']['filtered_content']}")
        print(f"   Content was filtered: {api_result['data']['content_filtered']}")
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
            # Take screenshot for debugging
            await page.screenshot(path="messaging_interface_error.png")
            await browser.close()
            return

        # Type message with contact info
        message_input = page.locator("[data-testid='message-input']")
        await message_input.fill("Call me at 555-9876 or email john@example.com")

        # Listen for network requests to see if API is called
        api_called = False
        filtered_response = None

        def handle_response(response):
            nonlocal api_called, filtered_response
            if "/api/messages" in response.url:
                api_called = True
                print(f"✅ API endpoint called: {response.url}")
                # Try to get response body
                try:
                    body = response.json()
                    if body and "data" in body:
                        filtered_response = body["data"].get("filtered_content")
                except:
                    pass

        page.on("response", handle_response)

        # Send message
        send_button = page.locator("[data-testid='send-message-button']")
        await send_button.click()

        # Wait a bit for request to complete
        await page.wait_for_timeout(2000)

        # Check results
        if api_called:
            print("✅ Frontend correctly uses API endpoint")
            if filtered_response:
                print(f"✅ Filtered content received: {filtered_response}")
        else:
            print("❌ Frontend bypasses API - using Supabase directly!")
            print("   This means NO content filtering is happening!")

        # Check if message appears in UI
        messages = await page.locator("[data-testid='message-content']").all()
        if messages:
            last_message = await messages[-1].text_content()
            print(f"\n3. Message displayed in UI: {last_message}")

            if "555-9876" in last_message or "john@example.com" in last_message:
                print("❌ CRITICAL: Contact info visible in UI - filtering not working!")
            else:
                print("✅ Contact info properly filtered in UI")

        # Take screenshot of final state
        await page.screenshot(path="messaging_test_result.png")

        await browser.close()

async def test_conversation_list_api_usage():
    """Test if ConversationList uses API to fetch conversations"""

    print("\n\nTesting ConversationList component...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Track API calls
        api_endpoints_called = []

        def track_requests(request):
            if "/api/" in request.url:
                api_endpoints_called.append(request.url)
                print(f"API Request: {request.url}")

        page.on("request", track_requests)

        # Navigate to messages page
        await page.goto(f"{FRONTEND_URL}/messages")
        await page.wait_for_load_state("networkidle")

        # Wait for conversations to load
        await page.wait_for_timeout(3000)

        # Check what endpoints were called
        print("\nAPI Endpoints called:")
        for endpoint in api_endpoints_called:
            print(f"  - {endpoint}")

        # Check if correct API endpoint was used
        conversation_api_called = any("/api/messages/conversations" in url for url in api_endpoints_called)

        if conversation_api_called:
            print("✅ ConversationList uses API endpoint")
        else:
            print("❌ ConversationList bypasses API - using Supabase directly!")

        await browser.close()

async def test_message_thread_api_usage():
    """Test if MessageThread uses API to fetch messages"""

    print("\n\nTesting MessageThread component...")

    # First create a conversation with messages
    conversation_id = "test-conv-" + str(int(time.time()))

    # Create some test messages via API
    for i in range(3):
        message_data = {
            "bid_card_id": "test-bid-123",
            "content": f"Test message {i+1}",
            "sender_type": "homeowner" if i % 2 == 0 else "contractor",
            "sender_id": "test-user-123",
            "conversation_id": conversation_id
        }

        requests.post(
            f"{API_BASE_URL}/api/messages/send",
            json=message_data,
            params={"user_type": message_data["sender_type"], "user_id": "test-user-123"}
        )

    print(f"Created test conversation: {conversation_id}")

    # Now test frontend
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Track API calls
        message_api_called = False

        def check_message_api(request):
            nonlocal message_api_called
            if f"/api/messages/conversation/{conversation_id}" in request.url:
                message_api_called = True
                print(f"✅ Correct API called: {request.url}")

        page.on("request", check_message_api)

        # Navigate directly to conversation
        await page.goto(f"{FRONTEND_URL}/messages/{conversation_id}")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        if message_api_called:
            print("✅ MessageThread uses API to fetch messages")
        else:
            print("❌ MessageThread bypasses API - using Supabase directly!")

        await browser.close()

def main():
    """Run all integration tests"""

    print("=" * 60)
    print("React Messaging Components Integration Test")
    print("=" * 60)

    # Run tests
    asyncio.run(test_messaging_with_contact_filtering())
    asyncio.run(test_conversation_list_api_usage())
    asyncio.run(test_message_thread_api_usage())

    print("\n" + "=" * 60)
    print("Integration Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
