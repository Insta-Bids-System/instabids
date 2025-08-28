"""
Test direct CIA agent call to verify categorization tool execution
This bypasses the API route and calls the agent directly
"""

import asyncio
import sys
import os
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from agents.cia.agent import CustomerInterfaceAgent

async def test_direct_cia_categorization():
    """Test direct CIA agent call for categorization"""
    
    print("TESTING DIRECT CIA AGENT CATEGORIZATION")
    print("=" * 60)
    
    # Initialize CIA agent
    cia_agent = CustomerInterfaceAgent()
    print(f"[OK] CIA Agent initialized")
    
    # Test message that should trigger categorization
    test_message = "I need artificial turf installed in my backyard"
    user_id = "test-user-12345"
    session_id = "test-session-67890"
    
    print(f"Test message: '{test_message}'")
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")
    print()
    
    try:
        # Call the CIA agent directly
        print("[CALLING] Calling CIA agent handle_conversation...")
        result = await cia_agent.handle_conversation(
            user_id=user_id,
            message=test_message,
            session_id=session_id,
            conversation_id=None,
            project_id=None,
            images=None,
            existing_state=None
        )
        
        print(f"[SUCCESS] CIA agent responded successfully")
        print(f"Response type: {type(result)}")
        print(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        print()
        
        # Analyze the response for categorization evidence
        if isinstance(result, dict):
            response_text = result.get("response", "")
            extracted_data = result.get("extracted_data", {})
            
            print("RESPONSE ANALYSIS:")
            print("-" * 30)
            print(f"Response text: {response_text[:200]}...")
            print(f"Extracted data: {extracted_data}")
            print(f"Success: {result.get('success', False)}")
            print(f"Bid card ID: {result.get('bid_card_id', 'None')}")
            print(f"Completion %: {result.get('completion_percentage', 0)}%")
            print()
            
            # Check for categorization evidence
            categorization_indicators = [
                "Tagged as", "confidence", "Installation", 
                "turf_installation", "categorize_project"
            ]
            
            found_indicators = []
            response_lower = response_text.lower()
            
            for indicator in categorization_indicators:
                if indicator.lower() in response_lower:
                    found_indicators.append(indicator)
                    
            if found_indicators:
                print(f"[EVIDENCE] CATEGORIZATION EVIDENCE FOUND: {found_indicators}")
                
                # Look for specific Tagged output
                if "tagged as" in response_lower:
                    print("[SUCCESS] Found 'Tagged as' output - categorization tool executed!")
                    lines = response_text.split('\n')
                    for line in lines:
                        if 'tagged' in line.lower():
                            print(f"Tool output: {line.strip()}")
                else:
                    print("[PARTIAL] Found categorization keywords but no 'Tagged as' output")
            else:
                print("[FAILED] NO CATEGORIZATION EVIDENCE: Tool was not called")
                
        else:
            print(f"[ERROR] Unexpected response type: {type(result)}")
            print(f"Response: {result}")
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting direct CIA agent categorization test...")
    print()
    asyncio.run(test_direct_cia_categorization())