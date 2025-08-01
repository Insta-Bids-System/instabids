#!/usr/bin/env python3
"""
Test storage upload after bucket is created
"""

import os
import base64
from database_simple import db
from dotenv import load_dotenv
from datetime import datetime
import uuid

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_storage_upload():
    """Test uploading to storage bucket"""
    print("Testing Supabase Storage upload...")
    
    try:
        # Create a simple test image (1x1 red pixel)
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4AWP4/5+hHgAF/wJ/4u7yWgAAAABJRU5ErkJggg=="
        )
        
        # Generate unique filename
        test_user_id = "test-user-123"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{test_user_id}/test_{timestamp}.png"
        
        print(f"Attempting to upload: {file_name}")
        
        # Try to upload
        response = db.client.storage.from_('project-images').upload(
            file_name,
            test_image_data,
            {"content-type": "image/png"}
        )
        
        print("✅ Upload successful!")
        
        # Get public URL
        public_url = db.client.storage.from_('project-images').get_public_url(file_name)
        print(f"✅ Public URL: {public_url}")
        
        # Try to read it back
        print("\nTesting public access...")
        import requests
        r = requests.get(public_url)
        if r.status_code == 200:
            print("✅ Public access works!")
        else:
            print(f"❌ Public access failed: {r.status_code}")
            
        # Clean up
        print("\nCleaning up test file...")
        db.client.storage.from_('project-images').remove([file_name])
        print("✅ Test file removed")
        
        print("\n" + "="*50)
        print("SUCCESS! Storage is properly configured!")
        print("="*50)
        print("\nThe CIA agent can now upload images without token limits.")
        print("Images will be stored as URLs instead of base64.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n" + "="*50)
        print("STORAGE NOT CONFIGURED!")
        print("="*50)
        print("\nPlease follow the setup guide:")
        print("1. Go to Supabase Dashboard > Storage")
        print("2. Create 'project-images' bucket (make it PUBLIC)")
        print("3. Set up the RLS policies as described in SUPABASE_STORAGE_SETUP_GUIDE.md")

if __name__ == "__main__":
    test_storage_upload()