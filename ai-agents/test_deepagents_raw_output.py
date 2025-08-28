"""Test to understand what DeepAgents actually returns"""
import asyncio
import os
os.environ["USE_DEEPAGENTS_LANDING"] = "true"

from agents.coia.landing_deepagent import process_landing_message

async def test_deepagents_raw():
    """Test what DeepAgents actually returns without any adapters"""
    
    # Simple test message
    test_request = {
        "user_id": "test-deepagents-raw",
        "session_id": "session-deepagents-raw",
        "message": "I'm a solar panel installation company in Orlando, Florida"
    }
    
    print("🔍 Testing DeepAgents raw output...")
    print(f"Request: {test_request}")
    print("-" * 50)
    
    try:
        # Call the DeepAgents implementation directly
        result = await process_landing_message(test_request)
        
        print(f"✅ DeepAgents returned successfully!")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            # Check messages
            if 'messages' in result:
                print(f"\n📧 Messages: {len(result['messages'])} messages")
                for i, msg in enumerate(result['messages'][:3]):  # First 3 messages
                    print(f"  Message {i}: {type(msg)}")
                    if hasattr(msg, 'content'):
                        print(f"    Content preview: {str(msg.content)[:100]}...")
                    elif isinstance(msg, dict):
                        print(f"    Dict keys: {msg.keys()}")
            
            # Check todos
            if 'todos' in result:
                print(f"\n📝 Todos: {result['todos']}")
            
            # Check files
            if 'files' in result:
                print(f"\n📁 Files: {result['files']}")
                
            # Check other keys
            other_keys = [k for k in result.keys() if k not in ['messages', 'todos', 'files']]
            if other_keys:
                print(f"\n🔑 Other keys: {other_keys}")
                for key in other_keys:
                    value = result[key]
                    if isinstance(value, (str, int, float, bool, type(None))):
                        print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {type(value)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deepagents_raw())