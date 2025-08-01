#!/usr/bin/env python3
"""
Fix storage bucket configuration using service role
"""

import os
from database_simple import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def fix_storage_bucket():
    """Fix the project-images bucket configuration"""
    print("Fixing storage bucket configuration...")
    
    try:
        # List existing buckets
        buckets = db.client.storage.list_buckets()
        bucket_names = [b.name for b in buckets] if buckets else []
        print(f"Existing buckets: {bucket_names}")
        
        # Check if project-images exists
        if 'project-images' not in bucket_names:
            print("Creating project-images bucket...")
            # Create the bucket with public access
            db.client.storage.create_bucket('project-images', options={'public': True})
            print("✅ Created project-images bucket with public access")
        else:
            print("Bucket already exists, updating settings...")
            # Update bucket to ensure it's public
            try:
                # First, let's test by uploading a simple test file
                test_data = b"test"
                test_path = "test/test.txt"
                
                # Try to upload
                response = db.client.storage.from_('project-images').upload(
                    test_path,
                    test_data,
                    {"content-type": "text/plain", "upsert": True}
                )
                
                print("✅ Test upload successful!")
                
                # Clean up test file
                db.client.storage.from_('project-images').remove([test_path])
                
            except Exception as e:
                print(f"❌ Test upload failed: {e}")
                print("\nThis usually means RLS policies need to be configured.")
                
        print("\n" + "="*50)
        print("NEXT STEPS:")
        print("="*50)
        print("\n1. Go to Supabase Dashboard")
        print("2. Navigate to Authentication > Policies")
        print("3. Click on storage.objects table")
        print("4. Create these policies:\n")
        
        print("POLICY 1 - Public Read:")
        print("  - Name: Allow public read access to project-images")
        print("  - Target: SELECT")
        print("  - Check: bucket_id = 'project-images'")
        print("")
        
        print("POLICY 2 - Service Insert:")
        print("  - Name: Allow service role to insert")
        print("  - Target: INSERT")
        print("  - Check: bucket_id = 'project-images'")
        print("")
        
        print("Or run the SQL file: fix_storage_rls_policies.sql")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_storage_bucket()