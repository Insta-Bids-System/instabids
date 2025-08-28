#!/usr/bin/env python3
"""
Test complete photo upload flow with property creation
"""

import requests
import json
import base64
from config.service_urls import get_backend_url

def create_homeowner_and_property():
    """Create a test homeowner and property first"""
    print("1. Creating test homeowner...")
    
    # Create homeowner via Supabase
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    from supabase import create_client, Client
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Create homeowner
        homeowner_data = {
            "id": "test-homeowner-123",
            "user_id": "test-user-12345", 
            "full_name": "Test Homeowner",
            "email": "test@example.com"
        }
        
        homeowner_result = supabase.table("homeowners").upsert(homeowner_data).execute()
        print(f"   Homeowner created: {homeowner_result.data}")
        
        # Create property
        property_data = {
            "id": "test-property-123",
            "user_id": "test-user-12345",
            "name": "Test Living Room Property",
            "address": "123 Test St, Test City",
            "property_type": "single_family",
            "metadata": {}
        }
        
        property_result = supabase.table("properties").upsert(property_data).execute()
        print(f"   Property created: {property_result.data}")
        
        return True
        
    except Exception as e:
        print(f"   ERROR creating homeowner/property: {e}")
        return False

def test_photo_upload_with_real_property():
    """Test photo upload with real property"""
    print("\n2. Testing photo upload...")
    
    # Create minimal valid JPEG
    jpg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    files = {
        'file': ('living_room_broken_blinds.jpg', jpg_header, 'image/jpeg')
    }
    
    data = {
        'photo_type': 'documentation'
    }
    
    try:
        response = requests.post(
            f'{get_backend_url()}/api/properties/test-property-123/photos/upload?user_id=test-user-12345',
            files=files,
            data=data,
            timeout=60
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   SUCCESS! Photo uploaded!")
            print(f"   AI Description: {result.get('ai_description')}")
            
            # Check if using real AI
            ai_classification = result.get('ai_classification', {})
            description = ai_classification.get('description', '')
            
            if 'temporarily unavailable' in description:
                print("   ❌ STILL USING FALLBACK - OpenAI not working in property API")
                return False
            else:
                print("   ✅ USING REAL OPENAI - AI analysis working!")
                print(f"   Room detected: {result.get('room_classified')}")
                print(f"   Assets detected: {result.get('detected_assets')}")
                return True
                
        else:
            print(f"   ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing complete photo upload flow with real OpenAI API...")
    
    # Step 1: Create homeowner and property
    if create_homeowner_and_property():
        # Step 2: Test photo upload
        if test_photo_upload_with_real_property():
            print("\n🎉 SUCCESS: Real OpenAI API working in property system!")
        else:
            print("\n💔 FAILURE: Still using fallback instead of real OpenAI")
    else:
        print("\n💔 FAILURE: Could not create test property")