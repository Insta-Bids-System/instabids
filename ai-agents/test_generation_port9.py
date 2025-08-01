"""
Test DALL-E generation on port 8009
"""
import requests
import json
import time

def test_generation():
    print("Testing DALL-E generation endpoint on port 8009...")
    
    # Wait a moment for server to start
    time.sleep(3)
    
    payload = {
        "board_id": "26cf972b-83e4-484c-98b6-a5d1a4affee3",
        "ideal_image_id": "115f9265-e462-458f-a159-568790fc6941",
        "current_image_id": "5d46e708-3f0c-4985-9617-68afd8e2892b",
        "user_preferences": "Modern industrial kitchen with exposed brick accent wall"
    }
    
    try:
        response = requests.post(
            "http://localhost:8009/api/image-generation/generate-dream-space",
            json=payload,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Generated image URL:", result.get('generated_image_url'))
            print("Generation ID:", result.get('generation_id'))
            print("Prompt:", result.get('prompt_used')[:100] + "...")
            return True
        else:
            print("Error:", response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("Connection error - server not running on port 8009")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_generation()