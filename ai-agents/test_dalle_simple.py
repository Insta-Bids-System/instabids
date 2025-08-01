"""
Simple DALL-E test without database dependencies
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_dalle_simple():
    """Test DALL-E generation directly with OpenAI API"""
    print("Testing DALL-E API directly...")
    
    # Initialize OpenAI client
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("ERROR: OPENAI_API_KEY not found")
        return
    
    print(f"OpenAI API key loaded: {openai_key[:20]}...")
    
    client = OpenAI(api_key=openai_key)
    
    # Create a simple test prompt
    prompt = """
    Photorealistic kitchen transformation. Current space: compact kitchen with white cabinets 
    and limited counter space. Transform to match this ideal: modern industrial kitchen with 
    exposed brick wall and pendant lighting. Keep the exact layout and structure of the 
    current space. Professional photography quality, realistic lighting and shadows.
    """
    
    try:
        print("Generating image with DALL-E 3...")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            style="natural",
            n=1
        )
        
        generated_url = response.data[0].url
        print(f"SUCCESS! Generated image URL: {generated_url}")
        return generated_url
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    test_dalle_simple()