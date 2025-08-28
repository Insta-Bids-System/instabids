#!/usr/bin/env python3
"""
Direct OpenAI Image Analysis Test
Tests the exact API call that should work
"""

import asyncio
import base64
import json
from openai import AsyncOpenAI
from pathlib import Path

# Load API key the same way as the agent
from dotenv import load_dotenv
import os

load_dotenv()

# Force load the correct OpenAI key from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                correct_api_key = line.split('=', 1)[1].strip()
                break
else:
    correct_api_key = os.getenv("OPENAI_API_KEY")

openai_client = AsyncOpenAI(api_key=correct_api_key)

async def test_image_api():
    """Test direct OpenAI image analysis API call"""
    
    # Load the fake bid image
    image_path = Path("C:/Users/NOTJOH~1/AppData/Local/Temp/playwright-mcp-output/2025-08-08T05-55-47.931Z/fake-bid-with-contact-info.png")
    
    if not image_path.exists():
        print("ERROR: Image not found")
        return False
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    print(f"TESTING: Direct OpenAI image analysis...")
    print(f"API KEY: {correct_api_key[:10]}..." if correct_api_key else "NO API KEY")
    print(f"IMAGE SIZE: {len(image_data)} base64 chars")
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Analyze images for contact information. Return JSON format with contact_info_detected (boolean) and details."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyze this image for any contact information like phone numbers, emails, addresses. Return results in JSON format."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                ]}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        print(f"\nSUCCESS: OpenAI API responded")
        print(f"RESPONSE: {result}")
        
        # Parse JSON response
        parsed = json.loads(result)
        contact_detected = parsed.get('contact_info_detected', False)
        
        print(f"\nCONTACT INFO DETECTED: {contact_detected}")
        if contact_detected:
            print("TEST RESULT: PASSED - Image analysis working correctly")
        else:
            print("TEST RESULT: FAILED - Did not detect contact info in image")
        
        return contact_detected
        
    except Exception as e:
        print(f"\nERROR: OpenAI API call failed")
        print(f"ERROR DETAILS: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_image_api())
    
    if result:
        print("\nFINAL: Image analysis API is WORKING and detects contact info")
    else:
        print("\nFINAL: Image analysis API is BROKEN or not detecting contact info")