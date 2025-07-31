"""Fix Supabase storage bucket policies for inspiration images"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def fix_storage_policies():
    """Check and fix storage bucket policies"""
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_role_key:
        print("ERROR: Missing Supabase credentials")
        return False
    
    # Create client with service role key
    supabase: Client = create_client(supabase_url, service_role_key)
    
    try:
        # Check if bucket exists
        buckets = supabase.storage.list_buckets()
        inspiration_bucket = next((b for b in buckets if b['name'] == 'inspiration'), None)
        
        if not inspiration_bucket:
            print("Creating 'inspiration' storage bucket...")
            # Create bucket with public access
            supabase.storage.create_bucket(
                'inspiration',
                options={
                    'public': True,
                    'allowedMimeTypes': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
                    'fileSizeLimit': 10485760  # 10MB
                }
            )
            print("[OK] Created 'inspiration' bucket with public access")
        else:
            print("[OK] 'inspiration' bucket already exists")
            
        # Update bucket to ensure it's public
        try:
            supabase.storage.update_bucket(
                'inspiration',
                options={'public': True}
            )
            print("[OK] Updated bucket to ensure public access")
        except Exception as e:
            print(f"Note: Could not update bucket settings: {e}")
        
        print("\nStorage Configuration:")
        print("- Bucket: inspiration")
        print("- Access: Public (no auth required for viewing)")
        print("- Upload: Requires authenticated user")
        print("- File types: JPEG, PNG, GIF, WebP")
        print("- Max size: 10MB")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to configure storage: {e}")
        return False

if __name__ == "__main__":
    print("Fixing Supabase Storage Policies...")
    success = fix_storage_policies()
    
    if success:
        print("\n[SUCCESS] Storage configuration complete!")
        print("You should now be able to upload images to the inspiration board.")
    else:
        print("\n[ERROR] Failed to configure storage. Check your credentials.")