#!/usr/bin/env python3
"""
Test script to isolate what's breaking in the memory system
"""
import asyncio
import sys
import os
import time
import logging
from config.service_urls import get_backend_url

# Add project root to path
sys.path.append(os.path.dirname(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_contractor_context_adapter():
    """Test just the ContractorContextAdapter to see what queries it makes"""
    print("Testing ContractorContextAdapter directly...")
    
    try:
        from adapters.contractor_context import ContractorContextAdapter
        
        adapter = ContractorContextAdapter()
        contractor_id = "22222222-2222-2222-2222-222222222222"
        session_id = "test-session-123"
        
        print(f"📋 Loading context for contractor: {contractor_id}")
        start_time = time.time()
        
        # This is what my fix is calling
        context = adapter.get_contractor_context(contractor_id, session_id)
        
        end_time = time.time()
        print(f"⏱️ Adapter took: {end_time - start_time:.2f} seconds")
        
        # Analyze what we got
        print(f"📊 Context keys: {list(context.keys())}")
        
        for key, value in context.items():
            if isinstance(value, list):
                print(f"  - {key}: {len(value)} items")
            elif isinstance(value, dict):
                print(f"  - {key}: {len(value)} fields")
            else:
                print(f"  - {key}: {type(value)}")
        
        # Check conversation history specifically
        conv_history = context.get("conversation_history", [])
        print(f"💬 Conversation history: {len(conv_history)} conversations")
        
        return True
        
    except Exception as e:
        print(f"❌ ContractorContextAdapter failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_simple_conversation_lookup():
    """Test just loading conversation history without all the extra data"""
    print("\nTesting simple conversation lookup...")
    
    try:
        from adapters.contractor_context import ContractorContextAdapter
        
        adapter = ContractorContextAdapter()
        contractor_id = "22222222-2222-2222-2222-222222222222"
        session_id = "test-session-123"
        
        print(f"📋 Testing just conversation history lookup...")
        start_time = time.time()
        
        # Call just the conversation history method
        conv_history = adapter._get_conversation_history(contractor_id, session_id)
        
        end_time = time.time()
        print(f"⏱️ Conversation lookup took: {end_time - start_time:.2f} seconds")
        print(f"💬 Found {len(conv_history)} conversations")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple conversation lookup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_http_conversation_api():
    """Test the original HTTP conversation API approach"""
    print("\nTesting HTTP conversation API...")
    
    try:
        import aiohttp
        
        contractor_id = "22222222-2222-2222-2222-222222222222"
        
        print(f"📋 Testing HTTP conversation API for: {contractor_id}")
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(ff"{get_backend_url()}/api/conversations/user/{contractor_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    end_time = time.time()
                    print(f"⏱️ HTTP API took: {end_time - start_time:.2f} seconds")
                    print(f"📊 Response: {data.get('success', False)}")
                    
                    conversations = data.get("conversations", [])
                    print(f"💬 Found {len(conversations)} conversations")
                    return True
                else:
                    print(f"❌ HTTP API returned status: {response.status}")
                    return False
        
    except Exception as e:
        print(f"❌ HTTP conversation API failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests to identify the problem"""
    print("Starting memory system diagnosis...")
    print("=" * 60)
    
    # Test 1: Full ContractorContextAdapter
    adapter_works = await test_contractor_context_adapter()
    
    # Test 2: Simple conversation lookup
    simple_works = await test_simple_conversation_lookup()
    
    # Test 3: HTTP API approach
    http_works = await test_http_conversation_api()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS RESULTS:")
    print(f"  ContractorContextAdapter: {'Works' if adapter_works else 'Broken'}")
    print(f"  Simple conversation lookup: {'Works' if simple_works else 'Broken'}")
    print(f"  HTTP conversation API: {'Works' if http_works else 'Broken'}")
    
    if not adapter_works:
        print("\nRECOMMENDATION: ContractorContextAdapter is the problem")
        print("   - It's making too many database queries")
        print("   - Should use HTTP API approach instead")
    elif adapter_works and not simple_works:
        print("\nRECOMMENDATION: Full context loading is slow but works")
        print("   - Could optimize by loading only conversation history")
    else:
        print("\nAll approaches work - problem might be elsewhere")


if __name__ == "__main__":
    asyncio.run(main())