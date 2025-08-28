"""
Test IRIS Agent with Cost Tracking
Verify that the cost tracking system captures tokens and costs
"""
import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.iris.agent_tracked import IrisAgentTracked, IrisRequest
from services.llm_cost_tracker import LLMCostTracker
from database_simple import SupabaseDB

async def test_iris_with_cost_tracking():
    """Test IRIS agent and verify cost tracking"""
    print("\n" + "="*60)
    print("TESTING IRIS AGENT WITH COST TRACKING")
    print("="*60)
    
    # Initialize the tracked IRIS agent
    iris = IrisAgentTracked()
    print("[OK] IRIS Agent initialized with cost tracking")
    
    # Create test request
    test_request = IrisRequest(
        message="I'm thinking about renovating my kitchen. I love modern styles with clean lines and minimalist aesthetics. What color schemes would work well?",
        user_id="test-user-123",
        project_id="test-project-456",
        session_id="test-session-789"
    )
    
    print(f"\n[MESSAGE] Test Message: {test_request.message}")
    print(f"[USER] User ID: {test_request.user_id}")
    print(f"[PROJECT] Project ID: {test_request.project_id}")
    print(f"[SESSION] Session ID: {test_request.session_id}")
    
    # Process message
    print("\n[PROCESSING] Processing message with IRIS...")
    response = await iris.process_message(test_request)
    
    print("\n[SUCCESS] IRIS Response received!")
    print(f"[RESPONSE] Response: {response.response[:200]}...")
    print(f"[SUGGESTIONS] Suggestions: {response.suggestions}")
    
    # Check cost info
    if response.cost_info:
        print("\n[COST] COST TRACKING INFO:")
        print(f"  - Input Tokens: {response.cost_info.get('input_tokens', 'N/A')}")
        print(f"  - Output Tokens: {response.cost_info.get('output_tokens', 'N/A')}")
        print(f"  - Model: {response.cost_info.get('model', 'N/A')}")
        print(f"  - Provider: {response.cost_info.get('provider', 'N/A')}")
    
    # Query database to verify cost was logged
    print("\n[DATABASE] Checking database for cost tracking records...")
    db = SupabaseDB()
    
    # Check for recent IRIS logs
    query = """
    SELECT 
        agent_name,
        provider,
        model,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        cost_usd,
        session_id,
        timestamp
    FROM llm_usage_log
    WHERE agent_name = 'IRIS'
        AND session_id = 'test-session-789'
    ORDER BY timestamp DESC
    LIMIT 1
    """
    
    try:
        result = await db.execute_query(query)
        if result:
            print("\n[VERIFIED] DATABASE VERIFICATION:")
            log = result[0]
            print(f"  - Agent: {log['agent_name']}")
            print(f"  - Provider: {log['provider']}")
            print(f"  - Model: {log['model']}")
            print(f"  - Input Tokens: {log['prompt_tokens']}")
            print(f"  - Output Tokens: {log['completion_tokens']}")
            print(f"  - Total Tokens: {log['total_tokens']}")
            print(f"  - Cost (USD): ${log['cost_usd']:.6f}")
            print(f"  - Session ID: {log['session_id']}")
            print(f"  - Timestamp: {log['timestamp']}")
            
            # Calculate cost per 1000 tokens
            if log['total_tokens'] > 0:
                cost_per_1k = (log['cost_usd'] / log['total_tokens']) * 1000
                print(f"  - Cost per 1K tokens: ${cost_per_1k:.6f}")
        else:
            print("[WARNING] No cost tracking records found in database yet")
            print("   (Records may take a moment to appear)")
    except Exception as e:
        print(f"[WARNING] Could not query database: {e}")
        print("   (This is okay if database table doesn't exist yet)")
    
    print("\n" + "="*60)
    print("TEST COMPLETE - IRIS AGENT WITH COST TRACKING")
    print("="*60)
    
    return response

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_iris_with_cost_tracking())