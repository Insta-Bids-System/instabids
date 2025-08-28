#!/usr/bin/env python3
"""
Test OpenAI vision API in isolation to confirm it works
"""

import os
import base64
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_vision():
    """Test OpenAI vision with a simple image"""
    print("Testing OpenAI Vision API directly...")
    
    # Load environment
    load_dotenv(override=True)
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"API Key loaded: {openai_key[:20]}...{openai_key[-10:]}")
    
    client = OpenAI(api_key=openai_key)
    
    # Create a simple test image - a red square
    # This is a minimal valid PNG image
    png_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==")
    png_base64 = base64.b64encode(png_data).decode('utf-8')
    image_url = f"data:image/png;base64,{png_base64}"
    
    print(f"Test image created: {len(image_url)} characters")
    
    # Test with the exact same prompt the property API uses
    property_analysis_prompt = """
    You are analyzing a photo for PROPERTY DOCUMENTATION purposes (not design inspiration).
    This is someone's ACTUAL property that they want to document and manage.

    Analyze this photo and return a JSON response with:
    {
        "description": "Detailed description of what you see",
        "room_type": "kitchen|bathroom|bedroom|living_room|dining_room|exterior|garage|basement|laundry|office|other",
        "room_confidence": 0.95,
        "detected_assets": [
            {
                "type": "appliance|fixture|system|finish|furniture",
                "category": "refrigerator|stove|sink|cabinet|countertop|flooring|paint|lighting|window|door",
                "name": "Test Asset",
                "brand": "Unknown",
                "color": "color description",
                "condition": "excellent|good|fair|poor|needs_repair",
                "estimated_age": "new|recent|mature|old"
            }
        ],
        "detected_issues": [],
        "maintenance_opportunities": [],
        "improvement_suggestions": [],
        "safety_concerns": []
    }

    Focus on: Current condition, asset inventory, maintenance needs, and improvement opportunities.
    Be specific about brands, models, conditions, and any issues you can detect.
    """
    
    try:
        # Test different models to see what's available
        models_to_test = [
            "chatgpt-4o-latest",
            "gpt-4o-2024-11-20", 
            "gpt-4o",
            "gpt-4-vision-preview"
        ]
        
        for model in models_to_test:
            print(f"\nTesting model: {model}")
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": property_analysis_prompt},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ],
                    max_tokens=500
                )
                
                print(f"SUCCESS with {model}!")
                print(f"Response: {response.choices[0].message.content[:200]}...")
                print(f"Model used: {response.model}")
                
                # This is the working model - return it
                return model, response.choices[0].message.content
                
            except Exception as e:
                print(f"FAILED with {model}: {e}")
                continue
                
        print("No models worked!")
        return None, None
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None, None

if __name__ == "__main__":
    working_model, response = test_openai_vision()
    if working_model:
        print(f"\n SUCCESS! Working model: {working_model}")
        print("User should be getting REAL AI analysis, not fallback!")
    else:
        print("\n FAILURE! No OpenAI models are working")