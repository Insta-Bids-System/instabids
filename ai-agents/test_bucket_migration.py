#!/usr/bin/env python3
"""
Test the complete bucket migration workflow
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from scripts.migrate_base64_to_buckets import Base64ToBucketMigration
from database_simple import db

async def test_migration():
    """Test the migration workflow"""
    print("=" * 60)
    print("TESTING BUCKET MIGRATION")
    print("=" * 60)
    
    # Check current state
    print("\n1. CHECKING CURRENT STATE...")
    property_photos = db.client.table("property_photos")\
        .select("id, photo_url")\
        .like("photo_url", "data:image%")\
        .limit(1)\
        .execute()
    
    if property_photos.data:
        print(f"[SUCCESS] Found base64 image to migrate: ID {property_photos.data[0]['id']}")
        print(f"   Size: {len(property_photos.data[0]['photo_url'])} bytes")
    else:
        print("[ERROR] No base64 images found to migrate")
        return
    
    # Run migration for just one image as a test
    print("\n2. RUNNING MIGRATION FOR ONE IMAGE...")
    migration = Base64ToBucketMigration()
    
    # Create buckets
    if not await migration.create_buckets_if_needed():
        print("[ERROR] Failed to create buckets")
        return
    
    # Test migrating just the first image
    test_photo = property_photos.data[0]
    print(f"\n3. MIGRATING TEST IMAGE {test_photo['id']}...")
    
    try:
        # Extract base64 data
        base64_url = test_photo['photo_url']
        if ',' in base64_url:
            base64_data = base64_url.split(',')[1]
        else:
            base64_data = base64_url
        
        # Upload to bucket
        storage_result = await migration.storage_service.upload_base64_image(
            base64_string=base64_data,
            bucket_name="property-photos",
            path_prefix="test/migration",
            filename="test_migration.jpg"
        )
        
        print(f"[SUCCESS] Successfully uploaded to bucket!")
        print(f"   Original URL: {storage_result['original_url']}")
        print(f"   Thumbnail URL: {storage_result.get('thumbnail_url', 'Not generated')}")
        print(f"   File ID: {storage_result['file_id']}")
        
        # Update database record
        print("\n4. UPDATING DATABASE RECORD...")
        update_result = db.client.table("property_photos")\
            .update({
                "photo_url": storage_result["original_url"],
                "thumbnail_url": storage_result.get("thumbnail_url")
            })\
            .eq("id", test_photo['id'])\
            .execute()
        
        if update_result.data:
            print(f"[SUCCESS] Database updated successfully!")
        
        # Verify the change
        print("\n5. VERIFYING MIGRATION...")
        verify_result = db.client.table("property_photos")\
            .select("id, photo_url")\
            .eq("id", test_photo['id'])\
            .execute()
        
        if verify_result.data:
            new_url = verify_result.data[0]['photo_url']
            if new_url.startswith('https://'):
                print(f"[SUCCESS] MIGRATION SUCCESSFUL!")
                print(f"   Image now stored at: {new_url}")
                print(f"   Database size reduced by: {len(test_photo['photo_url'])} bytes")
            else:
                print(f"[ERROR] Migration failed - still using base64")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_migration())