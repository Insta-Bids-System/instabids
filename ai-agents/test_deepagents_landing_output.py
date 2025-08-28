#!/usr/bin/env python3
"""Test what DeepAgents landing actually returns"""

import json
from agents.coia.landing_deepagent import get_agent

def test_deepagents_output():
    """Test the actual DeepAgents landing output structure"""
    
    # Get the landing agent
    agent = get_agent()
    
    # Test input
    test_input = {
        "messages": [{"role": "user", "content": "Test Company LLC in Miami"}],
        "context": {}
    }
    
    print("Testing DeepAgents landing with input:")
    print(json.dumps(test_input, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Invoke the agent
    result = agent.invoke(test_input)
    
    # Analyze the result
    print("Result type:", type(result))
    print("\nResult keys:", list(result.keys()) if isinstance(result, dict) else "Not a dict")
    
    if isinstance(result, dict):
        # Check messages
        if "messages" in result:
            print(f"\nMessages: {len(result['messages'])} messages")
            last_msg = result['messages'][-1] if result['messages'] else None
            if last_msg:
                print(f"Last message type: {type(last_msg).__name__}")
                if hasattr(last_msg, 'content'):
                    print(f"Last message preview: {last_msg.content[:200]}...")
        
        # Check for other expected fields
        expected_fields = [
            "contractor_profile", "profile_completeness", "research_completed",
            "company_name", "contractor_created", "files", "todos"
        ]
        
        print("\nExpected fields check:")
        for field in expected_fields:
            if field in result:
                print(f"  ✓ {field}: {type(result[field]).__name__}")
            else:
                print(f"  ✗ {field}: NOT FOUND")
        
        # Show any unexpected fields
        unexpected = set(result.keys()) - set(expected_fields) - {"messages"}
        if unexpected:
            print(f"\nUnexpected fields found: {unexpected}")
    
    return result

if __name__ == "__main__":
    try:
        result = test_deepagents_output()
        print("\n✅ Test completed!")
        print("\nFull result structure:")
        print(json.dumps({k: str(v)[:100] for k, v in result.items()}, indent=2))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()