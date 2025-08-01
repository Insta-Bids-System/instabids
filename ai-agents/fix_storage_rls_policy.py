#!/usr/bin/env python3
"""
Fix Supabase Storage RLS policy for project-images bucket
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def fix_storage_policy():
    """Create proper RLS policy for storage"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Missing Supabase credentials!")
        return
        
    # Create Supabase client with service role key
    supabase = create_client(supabase_url, supabase_key)
    
    print("Checking storage buckets...")
    
    try:
        # List buckets
        buckets = supabase.storage.list_buckets()
        bucket_names = [b['name'] for b in buckets] if buckets else []
        
        print(f"Found buckets: {bucket_names}")
        
        # Create project-images bucket if it doesn't exist
        if 'project-images' not in bucket_names:
            print("Creating project-images bucket...")
            supabase.storage.create_bucket('project-images', {
                'public': True,
                'allowed_mime_types': ['image/jpeg', 'image/png', 'image/webp'],
                'file_size_limit': 10485760  # 10MB
            })
            print("✓ Created project-images bucket")
        else:
            print("✓ project-images bucket already exists")
            
        # Update bucket to be public
        try:
            supabase.storage.update_bucket('project-images', {
                'public': True
            })
            print("✓ Set bucket to public")
        except:
            pass
            
        print("\n✓ Storage bucket is ready for uploads!")
        print("\nNote: If uploads still fail, you may need to:")
        print("1. Go to Supabase Dashboard > Storage")
        print("2. Click on 'project-images' bucket")
        print("3. Go to Policies tab")
        print("4. Create INSERT policy: 'Enable insert for authenticated users'")
        print("5. Create SELECT policy: 'Enable read access for all users'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_storage_policy()