#!/usr/bin/env python3
"""
Test Image Upload through API
Tests image analysis via the send-with-image endpoint
"""

import requests
import uuid
from config.service_urls import get_backend_url

def test_image_upload_api():
    """Test image upload through API"""
    
    print("INTELLIGENT MESSAGING - IMAGE UPLOAD API TEST")
    print("=" * 50)
    
    # Try to test image upload
    try:
        # Use the test image with contact information
        image_path = r"C:\Users\NOTJOH~1\AppData\Local\Temp\playwright-mcp-output\2025-08-08T05-55-47.931Z\fake-bid-with-contact-info.png"
        
        with open(image_path, "rb") as f:
            files = {"image": ("test-bid.png", f, "image/png")}
            data = {
                "content": "Here's my detailed bid proposal with all pricing",
                "sender_type": "contractor", 
                "sender_id": str(uuid.uuid4()),
                "bid_card_id": str(uuid.uuid4())
            }
            
            print("Uploading image with embedded contact information...")
            print(f"Content: '{data['content']}'")
            print("Image: fake-bid-with-contact-info.png (contains phone and email)")
            print()
            
            response = requests.post(
                f"{get_backend_url()}/api/intelligent-messages/send-with-image", 
                files=files, 
                data=data, 
                timeout=90
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"Success: {result.get('success', False)}")
                print(f"Approved: {result.get('approved', 'unknown')}")
                print(f"Agent Decision: {result.get('agent_decision', 'unknown')}")
                print(f"Threats Detected: {result.get('threats_detected', [])}")
                print(f"Confidence Score: {result.get('confidence_score', 0)}")
                print(f"Image Analysis: {result.get('image_analysis', {})}")
                
                if result.get('image_analysis'):
                    img_analysis = result.get('image_analysis', {})
                    print(f"Contact Info in Image: {img_analysis.get('contact_info_detected', False)}")
                    print(f"Phones Found: {img_analysis.get('phones', [])}")
                    print(f"Emails Found: {img_analysis.get('emails', [])}")
                
                # Check if image contact info was properly blocked
                contact_blocked = not result.get('approved') and 'contact_info' in str(result.get('threats_detected', []))
                
                if contact_blocked:
                    print("\nSUCCESS: Image contact info correctly blocked!")
                else:
                    print("\nWARNING: Image contact info may not have been blocked")
                    
            else:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except FileNotFoundError:
        print("ERROR: Test image not found")
        print("Expected path: C:\\Users\\NOTJOH~1\\AppData\\Local\\Temp\\playwright-mcp-output\\2025-08-08T05-55-47.931Z\\fake-bid-with-contact-info.png")
        
    except Exception as e:
        print(f"ERROR: {e}")
    
    print(f"\n" + "=" * 50)
    print("IMAGE UPLOAD API TEST COMPLETE")

if __name__ == "__main__":
    test_image_upload_api()