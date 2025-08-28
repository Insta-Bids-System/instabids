#!/usr/bin/env python3
"""
Debug Contact Information Detection
Test why contact info isn't being detected properly
"""

import asyncio
from agents.intelligent_messaging_agent import GPT5SecurityAnalyzer

async def test_contact_detection_debug():
    """Debug contact detection issues"""
    
    print("Debugging Contact Information Detection...")
    print("=" * 50)
    
    analyzer = GPT5SecurityAnalyzer()
    
    # Test with obvious contact information
    test_content = "Hi! My email is john@contractor.com and my phone is 555-123-4567. Please contact me directly to discuss the project."
    
    print(f"Testing content: '{test_content}'")
    print("-" * 50)
    
    try:
        result = await analyzer.analyze_message_security(
            content=test_content,
            sender_type="contractor",
            project_context={"project_type": "kitchen renovation", "budget_min": 10000, "budget_max": 20000},
            conversation_history=[]
        )
        
        print("GPT Analysis Result:")
        print(f"- Threats Detected: {result.get('threats_detected', [])}")
        print(f"- Confidence Score: {result.get('confidence_score', 0)}")
        print(f"- Recommended Action: {result.get('recommended_action', 'unknown')}")
        print(f"- Explanation: {result.get('explanation', 'none')}")
        
        if result.get('alternative_message'):
            print(f"- Alternative Message: {result.get('alternative_message')}")
        
        # Test the fallback system too
        print("\n" + "=" * 50)
        print("Testing Fallback Analysis...")
        
        fallback_result = analyzer._fallback_analysis(test_content)
        print("Fallback Analysis Result:")
        print(f"- Threats Detected: {fallback_result.get('threats_detected', [])}")
        print(f"- Confidence Score: {fallback_result.get('confidence_score', 0)}")
        print(f"- Recommended Action: {fallback_result.get('recommended_action', 'unknown')}")
        
    except Exception as e:
        print(f"Error in analysis: {e}")
        
        # Test fallback directly
        print("\nTesting fallback analysis directly...")
        fallback_result = analyzer._fallback_analysis(test_content)
        print("Fallback Analysis Result:")
        print(f"- Threats Detected: {fallback_result.get('threats_detected', [])}")
        print(f"- Confidence Score: {fallback_result.get('confidence_score', 0)}")
        print(f"- Recommended Action: {fallback_result.get('recommended_action', 'unknown')}")

if __name__ == "__main__":
    asyncio.run(test_contact_detection_debug())