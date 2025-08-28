"""
Test the categorization tool integration with CIA agent
"""

import asyncio
import os
import uuid
from agents.cia.agent import CustomerInterfaceAgent

async def test_categorization_scenarios():
    """Test the 5 required scenarios"""
    
    # Initialize CIA agent
    cia = CustomerInterfaceAgent()
    
    # Test user ID and session IDs for each scenario
    user_id = str(uuid.uuid4())
    
    test_scenarios = [
        {
            "name": "Artificial Turf (High Confidence)",
            "message": "I need artificial turf installed in my backyard",
            "expected": "Should categorize as Installation, turf_installation with high confidence"
        },
        {
            "name": "Christmas Lights (High Confidence)", 
            "message": "Looking for someone to install christmas lights",
            "expected": "Should categorize as Installation, holiday_lighting_installation with high confidence"
        },
        {
            "name": "Pool and Hot Tub (High Confidence)",
            "message": "Want to put in a pool and hot tub", 
            "expected": "Should categorize as Installation, multi_trade with high confidence"
        },
        {
            "name": "Vague Request (Low Confidence)",
            "message": "Need some work done on my house",
            "expected": "Should ask clarifying question due to low confidence"
        },
        {
            "name": "Solar Panel (High Confidence)",
            "message": "Solar panel installation with battery backup",
            "expected": "Should categorize as Installation, solar_panel_installation with high confidence"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios):
        session_id = f"test_session_{i + 1}"
        
        print(f"\n{'='*50}")
        print(f"TEST {i+1}: {scenario['name']}")
        print(f"Message: '{scenario['message']}'")
        print(f"Expected: {scenario['expected']}")
        print(f"{'='*50}")
        
        try:
            # Call the CIA agent
            response = await cia.handle_conversation(
                user_id=user_id,
                message=scenario['message'],
                session_id=session_id
            )
            
            # Extract results
            result = {
                "scenario": scenario['name'],
                "message": scenario['message'],
                "response": response.get("response", ""),
                "bid_card_id": response.get("bid_card_id"),
                "completion_percentage": response.get("completion_percentage", 0),
                "extracted_data": response.get("extracted_data", {}),
                "success": True
            }
            
            print(f"SUCCESS: {scenario['name']}")
            print(f"Response: {result['response'][:200]}...")
            print(f"Completion: {result['completion_percentage']}%")
            print(f"Bid Card ID: {result['bid_card_id']}")
            
            results.append(result)
            
        except Exception as e:
            print(f"ERROR: {scenario['name']}")
            print(f"Error: {str(e)}")
            
            results.append({
                "scenario": scenario['name'],
                "message": scenario['message'],
                "error": str(e),
                "success": False
            })
    
    # Summary Report
    print(f"\n{'='*60}")
    print("CATEGORIZATION INTEGRATION TEST RESULTS")
    print(f"{'='*60}")
    
    successful = len([r for r in results if r.get("success", False)])
    print(f"Successful Tests: {successful}/5")
    print(f"Failed Tests: {5 - successful}/5")
    
    # Detailed Analysis
    for result in results:
        if result.get("success"):
            print(f"\n{result['scenario']}:")
            print(f"   Completion: {result.get('completion_percentage', 0)}%")
            print(f"   Response: {result['response'][:100]}...")
        else:
            print(f"\n{result['scenario']}: {result.get('error', 'Unknown error')}")
    
    # Check for categorization evidence
    print(f"\n{'='*40}")
    print("CATEGORIZATION ANALYSIS:")
    print(f"{'='*40}")
    
    for result in results:
        if result.get("success"):
            response_text = result.get("response", "").lower()
            
            # Look for categorization indicators
            categorization_found = False
            confidence_found = False
            
            if any(word in response_text for word in ["tagged", "installation", "repair", "renovation"]):
                categorization_found = True
            
            if any(phrase in response_text for phrase in ["confidence", "0.", "clarifying question"]):
                confidence_found = True
            
            print(f"\n{result['scenario']}:")
            print(f"   Categorization Evidence: {'YES' if categorization_found else 'NO'}")
            print(f"   Confidence System: {'YES' if confidence_found else 'NO'}")
    
    return results

if __name__ == "__main__":
    print("Testing CIA Agent + Categorization Tool Integration")
    print("Testing 5 scenarios to verify categorization works...")
    
    results = asyncio.run(test_categorization_scenarios())
    
    print(f"\nTest Complete!")
    print(f"Check results above for categorization tool integration success.")