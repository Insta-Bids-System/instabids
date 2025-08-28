#!/usr/bin/env python3
"""
Test the Fixed Contractor System
Verify that the COIA research functionality is now working
"""

import asyncio
import os
from agents.coia.openai_gpt5_agent import initialize_openai_gpt5_coia

async def test_contractor_system():
    """Test that contractor research is no longer returning 'under development'"""
    
    print("TESTING FIXED CONTRACTOR SYSTEM")
    print("="*50)
    
    try:
        # Initialize COIA with OpenAI key
        openai_key = os.getenv("OPENAI_API_KEY") 
        if not openai_key:
            print("NO OPENAI API KEY - Cannot test")
            return False
        
        print(f"OK OpenAI API Key found: {openai_key[:20]}...")
        
        # Initialize COIA agent
        coia = initialize_openai_gpt5_coia(openai_key)
        print("OK COIA Agent initialized")
        
        # Test contractor message that should trigger research
        test_message = "I do artificial turf installation in South Florida, zip code 33442. I'll take projects within 40 miles."
        print(f"Test Message: {test_message}")
        
        # Process the message
        print("Processing message...")
        result = await coia.process_message(
            session_id="test_fixed_system",
            user_message=test_message
        )
        
        # Check the response
        response_text = result.get("response", result.get("message", ""))
        print(f"COIA Response: {response_text[:200]}...")
        
        # Verify it's NOT the old "under development" message
        if "under development" in response_text:
            print("ERROR: STILL SHOWING 'UNDER DEVELOPMENT' - Fix didn't work")
            return False
        elif "Error" in response_text:
            print(f"ERROR in system: {response_text}")
            return False
        elif "found" in response_text and "projects" in response_text:
            print("SUCCESS: Research functionality is now working!")
            print(f"   Projects found: {result.get('projects_found', 'Unknown')}")
            return True
        else:
            print("Unexpected response - system may be working differently than expected")
            print(f"   Full response: {response_text}")
            return False
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_contractor_system())
    
    if result:
        print("\nCONTRACTOR SYSTEM FIXED AND WORKING!")
        print("The 90% functional system is now 100% operational.")
    else:
        print("\nSYSTEM STILL HAS ISSUES")
        print("Further debugging required.")