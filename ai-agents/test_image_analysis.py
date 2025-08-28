#!/usr/bin/env python3
"""
Test Image Analysis for Contact Information Detection
Tests the GPT-4o powered image analysis on fake bid document
"""

import asyncio
import base64
import json
from pathlib import Path
from agents.intelligent_messaging_agent import process_intelligent_message

async def test_image_analysis():
    """Test image analysis on fake bid document with contact info"""
    
    # Load the fake bid image
    image_path = Path("C:/Users/NOTJOH~1/AppData/Local/Temp/playwright-mcp-output/2025-08-08T05-55-47.931Z/fake-bid-with-contact-info.png")
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    print(f"[IMAGE] Testing image analysis on fake bid document...")
    print(f"[INFO] Image size: {len(image_data)} characters (base64)")
    
    try:
        # Test the full message processing with image
        result = await process_intelligent_message(
            content="Here's my detailed bid proposal for your kitchen project",
            sender_type="contractor", 
            sender_id="test-contractor",
            bid_card_id="test-bid-card",
            image_data=image_data
        )
        
        print(f"\n[RESULTS] IMAGE ANALYSIS RESULTS:")
        print(f"[DECISION] Agent Decision: {result.get('agent_decision', 'unknown')}")
        print(f"[APPROVED] Approved: {result.get('approved', False)}")
        print(f"[THREATS] Threats Found: {result.get('threats_detected', [])}")
        print(f"[CONFIDENCE] Confidence Score: {result.get('confidence_score', 0)}")
        print(f"[FILTERED] Filtered Content: {result.get('filtered_content', '')}")
        
        if result.get('agent_comments'):
            print(f"\n[COMMENTS] AGENT COMMENTS:")
            for comment in result['agent_comments']:
                print(f"  - {comment.get('content', '')}")
        
        if result.get('image_analysis'):
            print(f"\n[IMAGE-AI] IMAGE ANALYSIS:")
            print(f"  {result['image_analysis']}")
            
        return result
        
    except Exception as e:
        print(f"❌ Error during image analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_image_analysis())
    
    if result:
        print(f"\n✅ Image analysis completed successfully!")
        print(f"📈 Test Result: {'PASSED' if result.get('contact_info_detected') else 'FAILED'}")
    else:
        print(f"\n❌ Image analysis test failed!")