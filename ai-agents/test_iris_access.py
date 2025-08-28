"""Test IRIS access to boards and bid cards"""

import requests
import json
from datetime import datetime
from config.service_urls import get_backend_url

BASE_URL = get_backend_url()
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"

def test_iris_access():
    """Test what IRIS has access to"""
    
    print("\n=== TESTING IRIS ACCESS TO BOARDS AND BID CARDS ===\n")
    
    session_id = f"access_test_{int(datetime.now().timestamp())}"
    
    # Ask IRIS about its capabilities
    response = requests.post(
        f"{BASE_URL}/api/iris/unified-chat",
        json={
            "user_id": TEST_USER_ID,
            "message": "What information do you have access to about my projects and boards?",
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("IRIS Response:")
        print("-" * 50)
        print(data.get('response', 'No response'))
        
        print("\n\nContext Summary:")
        print("-" * 50)
        context = data.get('context_summary', {})
        print(f"- Inspiration Boards: {context.get('inspiration_boards', 0)}")
        print(f"- Property Photos: {context.get('property_photos', 0)}")
        print(f"- Trade Projects: {context.get('trade_projects', 0)}")
        
        print("\n\nAvailable Tools:")
        print("-" * 50)
        tools = data.get('available_tools', [])
        for tool in tools:
            print(f"- {tool}")
        
        print("\n\nReasoning:")
        print("-" * 50)
        reasoning = data.get('reasoning', {})
        print(f"- Intent: {reasoning.get('user_intent', 'unknown')}")
        print(f"- Confidence: {reasoning.get('confidence', 0) * 100:.0f}%")
        
        context_analysis = reasoning.get('context_analysis', {})
        print(f"- Has Inspiration Boards: {context_analysis.get('has_inspiration_boards', False)}")
        print(f"- Has Property Photos: {context_analysis.get('has_property_photos', False)}")
        print(f"- Has Trade Projects: {context_analysis.get('has_trade_projects', False)}")
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text[:500])

if __name__ == "__main__":
    test_iris_access()