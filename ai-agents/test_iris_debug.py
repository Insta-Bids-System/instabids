#!/usr/bin/env python3
"""
Debug Unified IRIS Agent
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.iris_unified_agent import UnifiedIrisAgent

async def test_iris_agent():
    """Test the unified IRIS agent directly"""
    print("Testing UnifiedIrisAgent directly...")
    
    try:
        # Initialize agent
        agent = UnifiedIrisAgent()
        print("PASS - Agent initialized successfully")
        
        # Test context retrieval
        print("Testing context retrieval...")
        user_id = "550e8400-e29b-41d4-a716-446655440001"
        session_id = f"test_{user_id}"
        
        context = agent.get_complete_context(user_id, session_id)
        print(f"PASS - Context retrieved: {list(context.keys())}")
        
        # Check each context component
        inspiration = context.get('inspiration', {})
        property_data = context.get('property', {})
        trade_projects = context.get('trade_projects', {})
        
        print(f"  - Inspiration boards: {len(inspiration.get('inspiration_boards', []))}")
        print(f"  - Properties: {len(property_data.get('properties', []))}")
        print(f"  - Property photos: {len(property_data.get('property_photos', []))}")
        print(f"  - Trade projects: {trade_projects.get('total_trade_projects', 0)}")
        
        # Test reasoning
        print("Testing intent analysis...")
        message = "I need help with electrical work"
        reasoning = agent.analyze_context_and_intent(message, context)
        print(f"PASS - Intent detected: {reasoning.get('user_intent', 'unknown')}")
        print(f"  - Confidence: {reasoning.get('confidence', 0):.1%}")
        print(f"  - Suggested actions: {reasoning.get('suggested_actions', [])}")
        
        # Test tools
        print("Testing available tools...")
        available_tools = agent.determine_available_tools(context, reasoning)
        print(f"PASS - Available tools: {available_tools}")
        
        print("\nAll direct tests passed! The issue might be in the API layer.")
        return True
        
    except Exception as e:
        print(f"FAIL - Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_iris_agent())
    if success:
        print("\nPASS - Direct agent testing successful")
    else:
        print("\nFAIL - Direct agent testing failed")