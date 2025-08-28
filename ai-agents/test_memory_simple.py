#!/usr/bin/env python3
"""
Simple test to isolate what's breaking in the memory system
"""
import asyncio
import sys
import os
import time
from config.service_urls import get_backend_url

# Add project root to path
sys.path.append(os.path.dirname(__file__))

async def test_contractor_context_adapter():
    """Test ContractorContextAdapter to see what queries it makes"""
    print("Testing ContractorContextAdapter...")
    
    try:
        from adapters.contractor_context import ContractorContextAdapter
        
        adapter = ContractorContextAdapter()
        contractor_id = "22222222-2222-2222-2222-222222222222"
        session_id = "test-session-123"
        
        print(f"Loading context for contractor: {contractor_id}")
        start_time = time.time()
        
        # This is what my fix is calling - and what's causing the slowdown
        context = adapter.get_contractor_context(contractor_id, session_id)
        
        end_time = time.time()
        print(f"Adapter took: {end_time - start_time:.2f} seconds")
        
        # Show what we got
        print(f"Context keys: {list(context.keys())}")
        
        conv_history = context.get("conversation_history", [])
        print(f"Conversation history: {len(conv_history)} conversations")
        
        return True
        
    except Exception as e:
        print(f"ContractorContextAdapter failed: {e}")
        return False

async def test_http_api():
    """Test HTTP conversation API"""
    print("\nTesting HTTP conversation API...")
    
    try:
        import aiohttp
        
        contractor_id = "22222222-2222-2222-2222-222222222222"
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(ff"{get_backend_url()}/api/conversations/user/{contractor_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    end_time = time.time()
                    print(f"HTTP API took: {end_time - start_time:.2f} seconds")
                    
                    conversations = data.get("conversations", [])
                    print(f"Found {len(conversations)} conversations")
                    return True
                else:
                    print(f"HTTP API returned status: {response.status}")
                    return False
        
    except Exception as e:
        print(f"HTTP API failed: {e}")
        return False

async def main():
    """Run tests to identify the problem"""
    print("Memory system diagnosis")
    print("=" * 40)
    
    # Test both approaches
    adapter_works = await test_contractor_context_adapter()
    http_works = await test_http_api()
    
    print("\n" + "=" * 40)
    print("RESULTS:")
    print(f"ContractorContextAdapter: {'WORKS' if adapter_works else 'BROKEN'}")
    print(f"HTTP conversation API: {'WORKS' if http_works else 'BROKEN'}")
    
    if not adapter_works:
        print("\nPROBLEM: ContractorContextAdapter is too slow/broken")
        print("SOLUTION: Use HTTP API approach instead")
    elif adapter_works:
        print(f"\nContractorContextAdapter works but might be slow")

if __name__ == "__main__":
    asyncio.run(main())