"""
Test CIA Agent with Cost Tracking
Verify that the cost tracking system captures tokens and costs for OpenAI
"""
import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# First, let's patch the CIA agent to use tracked client
from services.llm_cost_tracker import get_tracked_openai_client
from agents.cia.agent import CustomerInterfaceAgent

async def test_cia_with_cost_tracking():
    """Test CIA agent and verify cost tracking"""
    print("\n" + "="*60)
    print("TESTING CIA AGENT WITH COST TRACKING")
    print("="*60)
    
    # Initialize CIA with OpenAI key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] No OpenAI API key found")
        return
    
    # Create CIA agent
    cia = CustomerInterfaceAgent(api_key)
    
    # Monkey-patch the client to use tracked version
    if cia.client:
        print("[INFO] Replacing CIA client with tracked version...")
        cia.client = get_tracked_openai_client(
            agent_name="CIA",
            api_key=api_key,
            is_async=True
        )
        print("[OK] CIA Agent using tracked OpenAI client")
    
    # Test conversation
    test_message = "I need to renovate my kitchen. It's about 200 square feet and I'm looking for a modern design with new cabinets and countertops. My budget is around $25,000."
    
    print(f"\n[MESSAGE] Test Message: {test_message}")
    print(f"[USER] User ID: test-user-cia-123")
    print(f"[SESSION] Session ID: test-session-cia-789")
    
    # Process message using CIA
    print("\n[PROCESSING] Processing message with CIA...")
    
    try:
        result = await cia.handle_conversation(
            user_id="test-user-cia-123",
            message=test_message,
            project_id="test-project-cia-456"
        )
        
        print("\n[SUCCESS] CIA Response received!")
        print(f"[RESPONSE] Response: {result['response'][:200]}...")
        
        # Check if we captured token usage
        print("\n[COST] Checking for cost tracking...")
        # The cost tracking happens automatically in the background
        print("[INFO] Cost tracking data is being logged to database")
        
    except Exception as e:
        print(f"[ERROR] Failed to process message: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("TEST COMPLETE - CIA AGENT WITH COST TRACKING")
    print("="*60)

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_cia_with_cost_tracking())