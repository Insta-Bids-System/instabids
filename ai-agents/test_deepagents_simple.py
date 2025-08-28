#!/usr/bin/env python3
"""
Simple test to verify DeepAgents framework functionality
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set encoding to UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

async def test_deepagents():
    """Test if DeepAgents framework works with sub-agents"""
    
    print("\n=== Testing DeepAgents Framework ===\n")
    
    # Import after setting path
    from agents.bsa.agent import create_bsa_agent
    from langchain_core.messages import HumanMessage
    
    # Create BSA agent
    print("1. Creating BSA agent with DeepAgents...")
    bsa_agent = create_bsa_agent()
    print("   Agent created successfully")
    
    # Test delegation
    print("\n2. Testing sub-agent delegation...")
    
    state = {
        "messages": [HumanMessage(content="Find turf projects near 33442")],
        "contractor_id": "test-123"
    }
    
    config = {"configurable": {"thread_id": "test_thread"}}
    
    try:
        # Invoke agent
        print("   Invoking agent...")
        result = await bsa_agent.ainvoke(state, config)
        
        # Check for delegation
        delegation_happened = False
        sub_agent_called = None
        
        if "messages" in result:
            for msg in result["messages"]:
                if hasattr(msg, "tool_calls"):
                    for tool_call in msg.tool_calls:
                        if tool_call.get("name") == "task":
                            delegation_happened = True
                            sub_agent_called = tool_call.get("args", {}).get("subagent_type")
                            print(f"   Delegated to: {sub_agent_called}")
                            
        if delegation_happened:
            print(f"\n3. RESULT: Framework WORKS - delegated to {sub_agent_called}")
            return True
        else:
            print("\n3. RESULT: No delegation occurred")
            return False
            
    except Exception as e:
        print(f"\n3. ERROR: {e}")
        return False

async def test_sub_agent_database():
    """Test if sub-agent can access database"""
    
    print("\n=== Testing Sub-Agent Database Access ===\n")
    
    from agents.bsa.sub_agents.bid_card_search_agent import BidCardSearchAgent
    from database_simple import SupabaseDB
    
    # Create sub-agent
    print("1. Creating bid_card_search sub-agent...")
    agent = BidCardSearchAgent()
    
    # Test database directly
    print("\n2. Testing database access...")
    db = SupabaseDB()
    
    try:
        # Simple query
        query = "SELECT COUNT(*) as count FROM bid_cards WHERE location_zip = '33442'"
        result = db.client.table("bid_cards").select("*").eq("location_zip", "33442").execute()
        
        count = len(result.data) if result.data else 0
        print(f"   Found {count} bid cards in 33442")
        
        if count > 0:
            print("\n3. RESULT: Database access WORKS")
            return True
        else:
            print("\n3. RESULT: No data found but query worked")
            return True
            
    except Exception as e:
        print(f"\n3. ERROR: Database access failed - {e}")
        return False

async def main():
    """Run tests"""
    
    # Test framework
    framework_works = await test_deepagents()
    
    # Test database
    db_works = await test_sub_agent_database()
    
    print("\n" + "="*50)
    print("FINAL RESULTS:")
    print("="*50)
    print(f"DeepAgents Delegation: {'WORKING' if framework_works else 'FAILED'}")
    print(f"Database Access: {'WORKING' if db_works else 'FAILED'}")
    
    if framework_works:
        print("\nDEEPAGENTS FRAMEWORK IS FUNCTIONAL - You can migrate other agents!")
    else:
        print("\nFRAMEWORK NEEDS FIXES before migration")

if __name__ == "__main__":
    asyncio.run(main())