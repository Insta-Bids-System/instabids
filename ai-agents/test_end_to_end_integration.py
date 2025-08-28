#!/usr/bin/env python3
"""Complete end-to-end test of integrated clean CIA implementation"""

import asyncio
import aiohttp
import json
import requests

def test_opening_message():
    """Test opening message endpoint"""
    print("Testing opening message endpoint...")
    
    try:
        response = requests.get("http://localhost:8008/api/cia/opening-message")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "Alex" in data.get("message", ""):
                print("PASS: Opening message endpoint working")
                return True
            else:
                print(f"FAIL: Invalid opening message format: {data}")
                return False
        else:
            print(f"FAIL: Opening message endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Opening message test failed: {e}")
        return False

def test_conversation_history():
    """Test conversation history endpoint"""
    print("Testing conversation history endpoint...")
    
    try:
        response = requests.get("http://localhost:8008/api/cia/conversation/test-session-123")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "messages" in data:
                print("PASS: Conversation history endpoint working")
                return True
            else:
                print(f"FAIL: Invalid conversation history format: {data}")
                return False
        else:
            print(f"FAIL: Conversation history returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Conversation history test failed: {e}")
        return False

async def test_streaming_conversation():
    """Test complete streaming conversation"""
    print("Testing streaming conversation...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test conversation with extraction data
            payload = {
                'messages': [{'content': 'I need to renovate my bathroom in 10001, budget $8,000-12,000, need it done in 2 weeks', 'role': 'user'}],
                'conversation_id': 'test-e2e-conversation',
                'user_id': 'test-user-e2e'
            }
            
            async with session.post('http://localhost:8008/api/cia/stream', json=payload) as resp:
                if resp.status != 200:
                    print(f"FAIL: Streaming returned {resp.status}")
                    return False
                
                full_response = ''
                completed = False
                
                async for line in resp.content:
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            data_part = line_str[6:]
                            if data_part == '[DONE]':
                                completed = True
                                break
                            elif data_part:
                                try:
                                    chunk = json.loads(data_part)
                                    if 'choices' in chunk and chunk['choices']:
                                        content = chunk['choices'][0].get('delta', {}).get('content', '')
                                        if content:
                                            full_response += content
                                except json.JSONDecodeError:
                                    pass
                
                if not completed:
                    print("FAIL: Stream did not complete properly")
                    return False
                
                if len(full_response) < 50:
                    print(f"FAIL: Response too short: {len(full_response)} chars")
                    return False
                
                # Check for key extraction indicators
                extraction_checks = {
                    'bathroom': 'bathroom' in full_response.lower(),
                    'budget_mentioned': any(b in full_response for b in ['$8,000', '$12,000', 'budget']),
                    'urgency': any(u in full_response for u in ['weeks', '2 weeks', 'timeline']),
                    'location': '10001' in full_response
                }
                
                passed_checks = sum(extraction_checks.values())
                total_checks = len(extraction_checks)
                
                print(f"PASS: Streaming conversation completed ({len(full_response)} chars)")
                print(f"      Extraction quality: {passed_checks}/{total_checks} key details detected")
                
                for check, result in extraction_checks.items():
                    status = "PASS" if result else "WARN"
                    print(f"      {check}: {status}")
                
                return passed_checks >= total_checks * 0.5  # At least 50% extraction quality
                
    except Exception as e:
        print(f"ERROR: Streaming conversation test failed: {e}")
        return False

async def test_conversation_persistence():
    """Test that conversations are properly saved and can be retrieved"""
    print("Testing conversation persistence...")
    
    try:
        # First, have a conversation
        async with aiohttp.ClientSession() as session:
            payload = {
                'messages': [{'content': 'I want to install new flooring in my living room', 'role': 'user'}],
                'conversation_id': 'test-persistence-123',
                'user_id': 'test-user-persistence'
            }
            
            async with session.post('http://localhost:8008/api/cia/stream', json=payload) as resp:
                if resp.status != 200:
                    print(f"FAIL: Initial conversation failed: {resp.status}")
                    return False
                
                # Just consume the stream without processing
                async for line in resp.content:
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: ') and line_str[6:] == '[DONE]':
                            break
        
        # Give it a moment to save
        await asyncio.sleep(1)
        
        # Now try to retrieve the conversation
        response = requests.get("http://localhost:8008/api/cia/conversation/test-persistence-123")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and len(data.get("messages", [])) > 0:
                print("PASS: Conversation persistence working")
                return True
            else:
                print(f"FAIL: No messages found in persisted conversation: {data}")
                return False
        else:
            print(f"FAIL: Could not retrieve persisted conversation: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Conversation persistence test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run all end-to-end tests"""
    print("Starting Comprehensive End-to-End Integration Test")
    print("=" * 60)
    
    tests = []
    
    # Static endpoint tests
    tests.append(("Opening Message", test_opening_message()))
    tests.append(("Conversation History", test_conversation_history()))
    
    # Async tests
    tests.append(("Streaming Conversation", await test_streaming_conversation()))
    tests.append(("Conversation Persistence", await test_conversation_persistence()))
    
    # Analyze results
    passed = sum(1 for name, result in tests if result)
    total = len(tests)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("-" * 20)
    
    for test_name, result in tests:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\nSUCCESS: All end-to-end tests passed!")
        print("The clean CIA implementation is fully integrated and operational.")
        return True
    else:
        print(f"\nWARNING: {total-passed} test(s) failed. Check the integration.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_test())
    exit(0 if success else 1)