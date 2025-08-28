"""
REAL COIA CONVERSATION TEST
Testing actual multi-turn conversation with a real contractor
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY', '')
os.environ['USE_TAVILY'] = 'true'
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', '')

async def test_real_coia_conversation():
    print("=" * 80)
    print("REAL COIA CONVERSATION TEST")
    print("Testing actual multi-turn conversation with real contractor")
    print("=" * 80)
    
    # Test with a REAL contractor we know exists
    test_messages = [
        "Hi, I'm from JM Holiday Lighting in Florida. We do Christmas light installation and holiday decorating services.",
        "We've been in business for about 8 years and specialize in residential holiday lighting.",
        "I'm interested in finding new projects and getting more customers through your platform."
    ]
    
    try:
        # Import the actual COIA agent
        from agents.coia.unified_graph import create_coia_graph
        from agents.coia.unified_state import UnifiedCoIAState
        
        print("CREATING COIA AGENT...")
        graph = create_coia_graph()
        
        # Initialize conversation state
        initial_state = UnifiedCoIAState(
            messages=[],
            company_name=None,
            location=None,
            current_stage="extraction"
        )
        
        print("STARTING MULTI-TURN CONVERSATION...")
        print()
        
        for i, message in enumerate(test_messages, 1):
            print(f"TURN {i}: USER MESSAGE")
            print(f"User: {message}")
            print()
            
            # Add user message to state
            from langchain_core.messages import HumanMessage
            initial_state["messages"].append(HumanMessage(content=message))
            
            print(f"TURN {i}: COIA PROCESSING...")
            
            # Run the graph
            result = await graph.ainvoke(initial_state)
            
            # Get the response
            if result.get("messages"):
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(f"COIA: {last_message.content}")
                else:
                    print(f"COIA: {last_message}")
            
            # Show extracted data
            print(f"\nEXTRACTED DATA AFTER TURN {i}:")
            print(f"  Company: {result.get('company_name', 'None')}")
            print(f"  Location: {result.get('location', 'None')}")
            print(f"  Stage: {result.get('current_stage', 'None')}")
            print(f"  Services: {result.get('services', 'None')}")
            print(f"  Years in Business: {result.get('years_in_business', 'None')}")
            
            # Update state for next turn
            initial_state = result
            print("-" * 60)
            print()
    
    except Exception as e:
        print(f"ERROR in conversation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_coia_conversation())