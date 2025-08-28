#!/usr/bin/env python3
"""
Simple Image Analysis Test - No Unicode Issues
Tests the GPT-4o powered image analysis on fake bid document
"""

import asyncio
import base64
import json
from pathlib import Path
from agents.intelligent_messaging_agent import process_intelligent_message

async def test_image_analysis_simple():
    """Test image analysis on fake bid document with contact info"""
    
    # Load the fake bid image
    image_path = Path("C:/Users/NOTJOH~1/AppData/Local/Temp/playwright-mcp-output/2025-08-08T05-55-47.931Z/fake-bid-with-contact-info.png")
    
    if not image_path.exists():
        print("ERROR: Image not found at expected path")
        return
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    print("TESTING: Image analysis on fake bid document...")
    print(f"INFO: Image size: {len(image_data)} characters (base64)")
    
    try:
        # Test the full message processing with image
        result = await process_intelligent_message(
            content="Here's my detailed bid proposal for your kitchen project",
            sender_type="contractor", 
            sender_id="test-contractor",
            bid_card_id="test-bid-card",
            image_data=image_data
        )
        
        print("\nRESULTS: IMAGE ANALYSIS COMPLETED")
        print(f"DECISION: {result.get('agent_decision', 'unknown')}")
        print(f"APPROVED: {result.get('approved', False)}")
        print(f"THREATS: {result.get('threats_detected', [])}")
        print(f"CONFIDENCE: {result.get('confidence_score', 0)}")
        print(f"FILTERED: {result.get('filtered_content', '')}")
        
        # Count agent comments without printing them (avoid Unicode issues)
        comment_count = len(result.get('agent_comments', []))
        print(f"COMMENTS: {comment_count} agent comments created")
        
        # Show contact info detection status
        contact_detected = 'contact_info' in result.get('threats_detected', [])
        print(f"CONTACT INFO DETECTED: {contact_detected}")
        
        return result
        
    except Exception as e:
        print(f"ERROR: Image analysis failed - {e}")
        return None

if __name__ == "__main__":
    result = asyncio.run(test_image_analysis_simple())
    
    if result:
        contact_detected = 'contact_info' in result.get('threats_detected', [])
        test_result = "PASSED" if contact_detected else "FAILED"
        print(f"\nTEST RESULT: {test_result}")
        print(f"SUMMARY: GPT-4o {'successfully detected' if contact_detected else 'failed to detect'} contact information in image")
    else:
        print("\nTEST RESULT: FAILED")
        print("SUMMARY: Image analysis test could not complete")