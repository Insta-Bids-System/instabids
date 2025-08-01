"""
Direct test of the DALL-E generation endpoint
"""
import asyncio
import httpx
import json

async def test_dalle_generation():
    """Test DALL-E generation with real board data"""
    async with httpx.AsyncClient() as client:
        print("Testing DALL-E Dream Space Generation...")
        
        # Test the generation endpoint directly with the real board data
        payload = {
            "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3",
            "ideal_image_id": "115f9265-e462-458f-a159-568790fc6941",
            "current_image_id": "5d46e708-3f0c-4985-9617-68afd8e2892b",
            "user_preferences": "Modern industrial kitchen with exposed brick accent wall"
        }
        
        try:
            print("Sending request to generation endpoint...")
            response = await client.post(
                "http://localhost:8008/api/image-generation/generate-dream-space",
                json=payload,
                timeout=60.0
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ DALL-E Generation SUCCESS!")
                print(f"Generated image URL: {result.get('generated_image_url')}")
                print(f"Generation ID: {result.get('generation_id')}")
                print(f"Prompt used: {result.get('prompt_used')}")
                return result
            else:
                print(f"❌ Generation failed with status {response.status_code}")
                print(f"Response: {response.text}")
                
        except httpx.TimeoutException:
            print("❌ Request timed out - DALL-E generation takes time")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_dalle_generation())