"""
Test AsyncIO Fix for COIA DeepAgents
Tests that _run_async properly handles both sync and async contexts
"""

import asyncio
import sys
import os

# Add ai-agents directory to path
sys.path.insert(0, 'C:/Users/Not John Or Justin/Documents/instabids/ai-agents')

from agents.coia.deepagents_tools import _run_async

async def sample_async_func():
    """Sample async function that returns after a short delay"""
    await asyncio.sleep(0.1)
    return {"test": "success", "value": 42}

def test_from_sync():
    """Test calling async function from sync context"""
    print("Testing from sync context...")
    try:
        result = _run_async(sample_async_func)
        assert result["test"] == "success"
        assert result["value"] == 42
        print("[PASSED] Test from sync context: SUCCESS")
        return True
    except Exception as e:
        print(f"[FAILED] Test from sync context: ERROR - {e}")
        return False

async def test_from_async():
    """Test calling async function from async context (the problematic case)"""
    print("Testing from async context (the fix)...")
    try:
        result = _run_async(sample_async_func)
        assert result["test"] == "success"
        assert result["value"] == 42
        print("[PASSED] Test from async context: PASSED")
        return True
    except Exception as e:
        print(f"[FAILED] Test from async context: FAILED - {e}")
        return False

async def test_nested_async():
    """Test calling from deeply nested async context"""
    print("Testing from nested async context...")
    try:
        async def inner_async():
            return _run_async(sample_async_func)
        
        result = await inner_async()
        assert result["test"] == "success"
        assert result["value"] == 42
        print("[PASSED] Test from nested async context: PASSED")
        return True
    except Exception as e:
        print(f"[FAILED] Test from nested async context: FAILED - {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("COIA AsyncIO Fix Test Suite")
    print("=" * 60)
    
    # Test 1: From sync context
    test1_pass = test_from_sync()
    
    # Test 2: From async context (the problematic case we fixed)
    test2_pass = asyncio.run(test_from_async())
    
    # Test 3: From nested async context
    test3_pass = asyncio.run(test_nested_async())
    
    print("=" * 60)
    if test1_pass and test2_pass and test3_pass:
        print("[PASSED] ALL ASYNCIO TESTS PASSED!")
        print("The fix successfully handles both sync and async contexts")
    else:
        print("[FAILED] Some tests failed - check output above")
    print("=" * 60)