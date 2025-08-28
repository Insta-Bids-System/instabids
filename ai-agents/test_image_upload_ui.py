#!/usr/bin/env python3
"""
TEST IMAGE UPLOAD THROUGH CHAT UI
Tests image upload functionality in the InstaBids chat system
"""

import asyncio
import requests
import base64
import uuid
import os
from PIL import Image, ImageDraw, ImageFont
import io
from config.service_urls import get_backend_url

class ImageUploadTester:
    def __init__(self):
        self.base_url = get_backend_url()
        self.user_id = str(uuid.uuid4())
        self.contractor_id = str(uuid.uuid4())
        self.bid_card_id = str(uuid.uuid4())
        
    def create_test_image_with_contact_info(self):
        """Create a test image containing contact information"""
        
        # Create a simple image with contact info
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use default font, fallback if not available
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Add text with contact information
        text_lines = [
            "Premium Kitchen Remodeling",
            "Call us: (407) 555-1234",
            "Email: contact@kitchenpro.com", 
            "Visit: www.premiumkitchens.com",
            "Licensed & Insured"
        ]
        
        y_offset = 50
        for line in text_lines:
            draw.text((20, y_offset), line, fill='black', font=font)
            y_offset += 40
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def test_image_upload_api(self):
        """Test image upload through intelligent messaging API"""
        
        print("IMAGE UPLOAD THROUGH CHAT UI TEST")
        print("=" * 50)
        
        # Create test image
        print("Creating test image with contact information...")
        image_data = self.create_test_image_with_contact_info()
        print(f"  Image size: {len(image_data)} bytes")
        
        # Test the send-with-image endpoint
        url = f"{self.base_url}/api/intelligent-messages/send-with-image"
        
        files = {
            'image': ('contact_info.png', image_data, 'image/png')
        }
        
        data = {
            'content': 'Here is my business card with contact information',
            'sender_type': 'contractor',
            'sender_id': self.contractor_id,
            'bid_card_id': self.bid_card_id,
            'conversation_id': None,
            'target_contractor_id': None
        }
        
        try:
            print("Uploading image through chat API...")
            response = requests.post(url, files=files, data=data, timeout=30)
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Upload Success: {result.get('success', False)}")
                print(f"Message Approved: {result.get('approved', False)}")
                print(f"Agent Decision: {result.get('agent_decision', 'unknown')}")
                print(f"Threats Detected: {result.get('threats_detected', [])}")
                
                # Check image analysis
                image_analysis = result.get('image_analysis', {})
                if image_analysis:
                    print("\nIMAGE ANALYSIS RESULTS:")
                    print(f"  Contact Info Detected: {image_analysis.get('contact_info_detected', 'unknown')}")
                    print(f"  Confidence: {image_analysis.get('confidence', 0.0)}")
                    print(f"  Explanation: {image_analysis.get('explanation', 'none')}")
                    
                    phones = image_analysis.get('phones', [])
                    emails = image_analysis.get('emails', [])
                    if phones:
                        print(f"  Phones Found: {phones}")
                    if emails:
                        print(f"  Emails Found: {emails}")
                
                # Test result assessment
                contact_detected = image_analysis.get('contact_info_detected', False)
                message_blocked = not result.get('approved', True)
                
                print("\nTEST ASSESSMENT:")
                if contact_detected and message_blocked:
                    print("  ✅ SUCCESS: Image contact detection working!")
                    print("  ✅ Contact info detected in image")
                    print("  ✅ Message correctly blocked")
                    return True
                elif contact_detected and not message_blocked:
                    print("  ⚠️ PARTIAL: Contact detected but message not blocked")
                    return False
                else:
                    print("  ❌ ISSUE: Contact info not detected in image")
                    return False
            
            else:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_legitimate_image_upload(self):
        """Test legitimate image upload (no contact info)"""
        
        print("\nLEGITIMATE IMAGE UPLOAD TEST")
        print("=" * 40)
        
        # Create legitimate image
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            
        draw.text((50, 100), "Kitchen Design Ideas", fill='darkblue', font=font)
        draw.text((50, 150), "Modern Cabinets", fill='darkblue', font=font)
        draw.text((50, 200), "Granite Countertops", fill='darkblue', font=font)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        image_data = img_bytes.getvalue()
        
        # Test upload
        url = f"{self.base_url}/api/intelligent-messages/send-with-image"
        
        files = {
            'image': ('design_ideas.png', image_data, 'image/png')
        }
        
        data = {
            'content': 'Here are some design ideas for your kitchen project',
            'sender_type': 'contractor',
            'sender_id': self.contractor_id,
            'bid_card_id': self.bid_card_id
        }
        
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                approved = result.get('approved', False)
                
                print(f"Upload Success: {result.get('success', False)}")
                print(f"Message Approved: {approved}")
                
                if approved:
                    print("  ✅ SUCCESS: Legitimate image correctly approved")
                    return True
                else:
                    print("  ❌ ISSUE: Legitimate image wrongly blocked")
                    return False
            else:
                print(f"HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return False

def main():
    """Run image upload tests"""
    
    tester = ImageUploadTester()
    
    # Test 1: Image with contact info (should be blocked)
    contact_test_passed = tester.test_image_upload_api()
    
    # Test 2: Legitimate image (should be approved)
    legitimate_test_passed = tester.test_legitimate_image_upload()
    
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    print(f"Contact Info Detection: {'PASS' if contact_test_passed else 'FAIL'}")
    print(f"Legitimate Image Upload: {'PASS' if legitimate_test_passed else 'FAIL'}")
    
    overall_success = contact_test_passed and legitimate_test_passed
    
    if overall_success:
        print("\n🎉 IMAGE UPLOAD SYSTEM FULLY OPERATIONAL!")
        print("✅ Contact info detection working in images")
        print("✅ Legitimate images correctly processed")
        print("✅ Chat UI image upload ready for production")
    else:
        print("\n⚠️ Image upload system needs configuration")
        if not contact_test_passed:
            print("❌ Contact info detection needs attention")
        if not legitimate_test_passed:
            print("❌ Legitimate image processing needs fixing")
    
    return overall_success

if __name__ == "__main__":
    main()