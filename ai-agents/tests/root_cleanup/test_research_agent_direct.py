"""
Test the research agent directly to see if it works
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.research_based_agent import ResearchBasedCoIAAgent

async def test_research_agent():
    """Test research agent directly"""
    
    print("TESTING RESEARCH AGENT DIRECTLY")
    print("=" * 50)
    
    try:
        # Initialize research agent
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("ERROR: No ANTHROPIC_API_KEY found")
            return
            
        agent = ResearchBasedCoIAAgent(api_key)
        print("SUCCESS: Research agent initialized")
        
        # Test with the exact message the research node sends
        message = "Research company: Turf Grass Artificial Solutions"
        session_id = "test_research_direct"
        
        print(f"\nSending message: {message}")
        print(f"Session ID: {session_id}")
        
        # Call the agent
        result = await agent.process_message(
            session_id=session_id,
            user_message=message,
            context={"company_name": "Turf Grass Artificial Solutions"}
        )
        
        print(f"\nRESULT:")
        print(f"Response: {result.get('response', 'No response')[:200]}...")
        print(f"Stage: {result.get('stage')}")
        print(f"Research Data Available: {bool(result.get('research_data'))}")
        
        if result.get('profile_progress'):
            progress = result['profile_progress']
            print(f"Completeness: {progress.get('completeness', 0)}%")
            collected = progress.get('collectedData', {})
            print(f"Collected Data Keys: {list(collected.keys())}")
            
            # Show some key data
            if collected.get('phone'):
                print(f"  Phone: {collected['phone']}")
            if collected.get('email'):
                print(f"  Email: {collected['email']}")
            if collected.get('service_areas'):
                print(f"  Service Areas: {collected['service_areas']}")
        
        print("\nANALYSIS:")
        if result.get('research_data'):
            print("SUCCESS: Research worked - data was returned")
        else:
            print("FAILED: Research failed - no data returned")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_research_agent())