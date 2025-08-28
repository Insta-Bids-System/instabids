"""
Direct test of OpenAI Vision API
"""

import os
from openai import OpenAI

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Error: OPENAI_API_KEY not found")
    exit(1)

client = OpenAI(api_key=openai_api_key)

# Test with a simple base64 image (1x1 red pixel)
REAL_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

try:
    print("Testing OpenAI Vision API directly...")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What do you see in this image? Please describe it briefly."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{REAL_IMAGE_BASE64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    result_text = response.choices[0].message.content
    print(f"\nOpenAI Vision Response:\n{result_text}")
    print("\n[SUCCESS] OpenAI Vision API is working!")
    
except Exception as e:
    print(f"\n[ERROR] OpenAI Vision API Error: {e}")
    print(f"Error type: {type(e).__name__}")
    
    if "401" in str(e) or "invalid_api_key" in str(e):
        print("\n[CRITICAL] The OpenAI API key is invalid or expired!")
        print("Please update the OPENAI_API_KEY environment variable with a valid key.")
        print("You can get a key from: https://platform.openai.com/account/api-keys")