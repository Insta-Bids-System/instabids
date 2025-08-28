#!/usr/bin/env python3
"""
SIMPLE IMAGE UPLOAD TEST
Tests image upload functionality without Unicode issues
"""

import requests
import base64
import uuid
import json
from PIL import Image, ImageDraw, ImageFont
import io
from config.service_urls import get_backend_url

def create_test_image_with_contact_info():
    """Create test image with contact info"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Add contact information text
    text_lines = [
        "Premium Kitchen Remodeling",
        "Call us: (407) 555-1234",
        "Email: contact@kitchenpro.com", 
        "Visit: www.premiumkitchens.com"
    ]
    
    y_offset = 50
    for line in text_lines:
        draw.text((20, y_offset), line, fill='black', font=font)
        y_offset += 40
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_image_upload():
    """Test image upload through API"""
    
    print("IMAGE UPLOAD TEST")
    print("=" * 50)
    
    base_url = get_backend_url()
    user_id = str(uuid.uuid4())
    contractor_id = str(uuid.uuid4())
    bid_card_id = str(uuid.uuid4())
    
    # Create test image
    print("Creating test image with contact information...")
    image_data = create_test_image_with_contact_info()
    print(f"Image size: {len(image_data)} bytes")
    
    # Test the API endpoint
    url = f"{base_url}/api/intelligent-messages/send-with-image"
    
    files = {
        'image': ('contact_info.png', image_data, 'image/png')
    }
    
    data = {
        'content': 'Here is my business card with contact information',
        'sender_type': 'contractor',
        'sender_id': contractor_id,
        'bid_card_id': bid_card_id,
        'conversation_id': '',
        'target_contractor_id': ''
    }
    
    try:
        print("Sending image upload request...")
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response received successfully")
            print(f"Response keys: {list(result.keys())}")
            
            success = result.get('success', False)
            approved = result.get('approved', False)
            agent_decision = result.get('agent_decision', 'unknown')
            threats = result.get('threats_detected', [])
            
            print(f"Success: {success}")
            print(f"Approved: {approved}")
            print(f"Agent Decision: {agent_decision}")
            print(f"Threats: {threats}")
            
            # Check for image analysis
            image_analysis = result.get('image_analysis', {})
            if image_analysis:
                print("\nImage Analysis Results:")
                contact_detected = image_analysis.get('contact_info_detected', False)
                confidence = image_analysis.get('confidence', 0.0)
                explanation = image_analysis.get('explanation', '')
                phones = image_analysis.get('phones', [])
                emails = image_analysis.get('emails', [])
                
                print(f"  Contact Info Detected: {contact_detected}")
                print(f"  Confidence: {confidence}")
                print(f"  Explanation: {explanation}")
                if phones:
                    print(f"  Phones: {phones}")
                if emails:
                    print(f"  Emails: {emails}")
                
                # Assessment
                if contact_detected:
                    print("\nSUCCESS: Contact info detected in image!")
                    if not approved:
                        print("SUCCESS: Message correctly blocked due to contact info")
                        return True
                    else:
                        print("ISSUE: Contact detected but message not blocked")
                        return False
                else:
                    print("\nISSUE: Contact info not detected in image")
                    return False
            else:
                print("\nNo image analysis results found")
                return False
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during request: {e}")
        return False

def main():
    """Run the test"""
    result = test_image_upload()
    
    print("\n" + "=" * 50)
    print("FINAL RESULT")
    print("=" * 50)
    
    if result:
        print("PASS: Image upload with contact detection working!")
    else:
        print("FAIL: Image upload system needs attention")
    
    return result

if __name__ == "__main__":
    main()