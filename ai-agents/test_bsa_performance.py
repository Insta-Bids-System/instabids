"""
BSA Performance Test - Verify 2-5 second response times
Tests the optimized BSA with singleton, caching, and smart routing
"""

import asyncio
import time
import sys
import os

# Add project to path
sys.path.insert(0, r'C:\Users\Not John Or Justin\Documents\instabids\ai-agents')

from agents.bsa.bsa_deepagents import bsa_deepagent_stream


async def test_bsa_performance():
    print('=== BSA PERFORMANCE TEST ===')
    print('Testing optimized BSA with singleton, caching, and smart routing...')
    print()
    
    # Test configuration
    contractor_id = '87f93fbd-151d-4f17-9311-70ef9ba5256f'
    session_id = 'perf-test-001'
    
    # Test 1: Simple bid search (should use only bid-search subagent)
    print('TEST 1: Simple bid search request')
    print('Message: "show me available turf projects near me"')
    start = time.time()
    
    response_text = ''
    try:
        async for chunk in bsa_deepagent_stream(
            contractor_id=contractor_id,
            message='show me available turf projects near me',
            session_id=session_id,
            conversation_history=[]
        ):
            if 'choices' in chunk and chunk['choices']:
                content = chunk['choices'][0].get('delta', {}).get('content', '')
                response_text += content
            if chunk.get('done'):
                break
    except Exception as e:
        print(f'Error: {e}')
        response_text = f'Error: {e}'
    
    elapsed1 = time.time() - start
    print(f'Response time: {elapsed1:.2f} seconds')
    print(f'Response length: {len(response_text)} chars')
    
    # Test 2: Follow-up message (should use cached context)
    print()
    print('TEST 2: Follow-up message (testing cache)')
    print('Message: "what about projects within 50 miles?"')
    start = time.time()
    
    response_text = ''
    try:
        async for chunk in bsa_deepagent_stream(
            contractor_id=contractor_id,
            message='what about projects within 50 miles?',
            session_id=session_id,
            conversation_history=[
                {'role': 'user', 'content': 'show me available turf projects near me'},
                {'role': 'assistant', 'content': 'Here are the available projects...'}
            ]
        ):
            if 'choices' in chunk and chunk['choices']:
                content = chunk['choices'][0].get('delta', {}).get('content', '')
                response_text += content
            if chunk.get('done'):
                break
    except Exception as e:
        print(f'Error: {e}')
        response_text = f'Error: {e}'
    
    elapsed2 = time.time() - start
    print(f'Response time: {elapsed2:.2f} seconds')
    print(f'Response length: {len(response_text)} chars')
    
    # Test 3: Market research request (should route to different subagent)
    print()
    print('TEST 3: Market research request')
    print('Message: "what are typical prices for turf installation?"')
    start = time.time()
    
    response_text = ''
    try:
        async for chunk in bsa_deepagent_stream(
            contractor_id=contractor_id,
            message='what are typical prices for turf installation?',
            session_id=session_id,
            conversation_history=[]
        ):
            if 'choices' in chunk and chunk['choices']:
                content = chunk['choices'][0].get('delta', {}).get('content', '')
                response_text += content
            if chunk.get('done'):
                break
    except Exception as e:
        print(f'Error: {e}')
        response_text = f'Error: {e}'
    
    elapsed3 = time.time() - start
    print(f'Response time: {elapsed3:.2f} seconds')
    print(f'Response length: {len(response_text)} chars')
    
    # Performance summary
    print()
    print('=== PERFORMANCE SUMMARY ===')
    avg_time = (elapsed1 + elapsed2 + elapsed3) / 3
    print(f'Average response time: {avg_time:.2f} seconds')
    print(f'Target: 2-5 seconds')
    
    if avg_time <= 5.0:
        print('✅ SUCCESS: Target achieved!')
    elif avg_time <= 10.0:
        print('⚠️ PARTIAL: Better than before but not at target')
    else:
        print('❌ FAILED: Still too slow')
    
    print()
    print('Individual test results:')
    print(f'  Test 1 (bid search): {elapsed1:.2f}s - {"✅ PASS" if elapsed1 <= 5 else "❌ FAIL"}')
    print(f'  Test 2 (cached follow-up): {elapsed2:.2f}s - {"✅ PASS" if elapsed2 <= 5 else "❌ FAIL"}')
    print(f'  Test 3 (market research): {elapsed3:.2f}s - {"✅ PASS" if elapsed3 <= 5 else "❌ FAIL"}')


if __name__ == '__main__':
    print('Starting BSA Performance Test...')
    print('=' * 50)
    asyncio.run(test_bsa_performance())
    print('=' * 50)
    print('Test complete!')