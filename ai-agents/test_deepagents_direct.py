"""Test DeepAgents directly to see what it returns"""
import os
os.environ["USE_DEEPAGENTS_LANDING"] = "true"

from agents.coia.landing_deepagent import get_agent

def test_deepagents_direct():
    """Test the DeepAgents agent directly"""
    
    # Get the agent
    agent = get_agent()
    print(f"Got agent: {type(agent)}")
    
    # Create input matching DeepAgentState structure
    test_input = {
        "messages": [
            {
                "role": "user",
                "content": "I'm Solar Green Solutions, a solar panel installation company in Orlando, Florida"
            }
        ]
    }
    
    print("Sending to DeepAgents...")
    print(f"Input: {test_input}")
    print("-" * 50)
    
    try:
        # Invoke the agent
        result = agent.invoke(test_input)
        
        print(f"DeepAgents returned!")
        print(f"Result type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"Result keys: {result.keys()}")
            
            # Check messages
            if 'messages' in result:
                print(f"\nMessages: {len(result['messages'])} messages")
                for i, msg in enumerate(result['messages'][-3:]):  # Last 3 messages
                    print(f"\n  Message {i}:")
                    if hasattr(msg, 'content'):
                        print(f"    Type: {type(msg).__name__}")
                        print(f"    Content: {str(msg.content)[:200]}...")
                    elif isinstance(msg, dict):
                        print(f"    Dict: {msg}")
            
            # Check todos
            if 'todos' in result:
                print(f"\nTodos found: {len(result.get('todos', []))} todos")
                for todo in result.get('todos', [])[:3]:
                    print(f"  - {todo}")
            
            # Check files  
            if 'files' in result:
                print(f"\nFiles found: {result['files']}")
            
            # Any other keys
            other_keys = [k for k in result.keys() if k not in ['messages', 'todos', 'files']]
            if other_keys:
                print(f"\nOther keys: {other_keys}")
        else:
            print(f"Unexpected result type: {result}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing DeepAgents direct invocation...")
    test_deepagents_direct()