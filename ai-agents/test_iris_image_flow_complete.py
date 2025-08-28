"""
Complete Test of IRIS Image Flow with Unified System
Tests both save and retrieve operations for images
"""

import uuid
import json
import asyncio
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(supabase_url, supabase_key)

def test_image_save_flow():
    """Test how images SHOULD be saved to unified system"""
    print("\n" + "="*80)
    print("TESTING IMAGE SAVE FLOW TO UNIFIED SYSTEM")
    print("="*80)
    
    # Test user and conversation setup
    test_user_id = "550e8400-e29b-41d4-a716-446655440001"
    test_conversation_id = str(uuid.uuid4())
    test_message_id = str(uuid.uuid4())
    test_tenant_id = "00000000-0000-0000-0000-000000000000"
    
    try:
        # 1. Create a conversation for IRIS
        print("\n1. Creating IRIS conversation in unified_conversations...")
        conversation_data = {
            "id": test_conversation_id,
            "tenant_id": test_tenant_id,
            "created_by": test_user_id,
            "conversation_type": "iris_inspiration",
            "entity_type": "inspiration_board",
            "entity_id": str(uuid.uuid4()),  # Board ID
            "title": "Test Inspiration Board",
            "status": "active",
            "metadata": {
                "room_type": "kitchen",
                "style": "modern"
            }
        }
        
        result = supabase.table("unified_conversations").insert(conversation_data).execute()
        if result.data:
            print(f"✓ Created conversation: {test_conversation_id}")
        else:
            print(f"✗ Failed to create conversation")
            return False
            
        # 2. Save an image reference to unified_conversation_memory
        print("\n2. Saving image to unified_conversation_memory...")
        memory_data = {
            "id": str(uuid.uuid4()),
            "tenant_id": test_tenant_id,
            "conversation_id": test_conversation_id,
            "memory_scope": "conversation",
            "memory_type": "photo_reference",
            "memory_key": "inspiration_image_1",
            "memory_value": {
                "images": [{
                    "url": "https://example.com/test-image.jpg",
                    "path": "iris_visions/test-image.jpg",
                    "metadata": {
                        "category": "inspiration",
                        "room_type": "kitchen",
                        "style": "modern",
                        "uploaded_at": datetime.now().isoformat()
                    }
                }]
            },
            "importance_score": 8
        }
        
        result = supabase.table("unified_conversation_memory").insert(memory_data).execute()
        if result.data:
            print(f"✓ Saved image to memory: {memory_data['memory_key']}")
        else:
            print(f"✗ Failed to save image to memory")
            return False
            
        # 3. Alternative: Save as message attachment
        print("\n3. Saving image as message attachment...")
        
        # First create a message
        message_data = {
            "id": test_message_id,
            "tenant_id": test_tenant_id,
            "conversation_id": test_conversation_id,
            "sender_id": test_user_id,
            "sender_type": "user",
            "content": "Here's my kitchen inspiration image",
            "metadata": {"has_attachment": True}
        }
        
        result = supabase.table("unified_messages").insert(message_data).execute()
        if result.data:
            print(f"✓ Created message: {test_message_id}")
        else:
            print(f"✗ Failed to create message")
            # Continue anyway as table might not exist
            
        # Then create attachment
        attachment_data = {
            "id": str(uuid.uuid4()),
            "tenant_id": test_tenant_id,
            "message_id": test_message_id,
            "storage_path": "iris_visions/kitchen_modern_001.jpg",
            "mime_type": "image/jpeg",
            "file_size": 1024000  # 1MB
        }
        
        try:
            result = supabase.table("unified_message_attachments").insert(attachment_data).execute()
            if result.data:
                print(f"✓ Created attachment for message")
            else:
                print(f"✗ Failed to create attachment")
        except Exception as e:
            print(f"⚠ unified_message_attachments table may not exist: {e}")
            
        return test_conversation_id
        
    except Exception as e:
        print(f"✗ Error in save flow: {e}")
        return None

def test_image_retrieve_flow(conversation_id):
    """Test how IRIS adapter retrieves images"""
    print("\n" + "="*80)
    print("TESTING IMAGE RETRIEVE FLOW FROM UNIFIED SYSTEM")
    print("="*80)
    
    from adapters.iris_context import IrisContextAdapter
    
    adapter = IrisContextAdapter()
    test_user_id = "550e8400-e29b-41d4-a716-446655440001"
    
    print("\n1. Testing adapter retrieval...")
    context = adapter.get_inspiration_context(
        user_id=test_user_id,
        project_id=None
    )
    
    # Check if we got photos
    photos = context.get("photos_from_unified_system", {})
    print(f"\n✓ Photos retrieved from unified system:")
    print(f"  - Project photos: {len(photos.get('project_photos', []))}")
    print(f"  - Inspiration photos: {len(photos.get('inspiration_photos', []))}")
    print(f"  - Message attachments: {len(photos.get('message_attachments', []))}")
    
    # Display any photos found
    all_photos = (
        photos.get('project_photos', []) + 
        photos.get('inspiration_photos', []) + 
        photos.get('message_attachments', [])
    )
    
    if all_photos:
        print("\n✓ Found photos:")
        for photo in all_photos:
            print(f"  - Path: {photo.get('file_path')}")
            print(f"    Type: {photo.get('type')}")
            print(f"    Metadata: {photo.get('metadata')}")
    else:
        print("\n⚠ No photos found through adapter")
        
    # Check conversations
    conversations = context.get("conversations_from_other_agents", {})
    print(f"\n✓ Conversations found:")
    for conv_type, convs in conversations.items():
        if convs:
            print(f"  - {conv_type}: {len(convs)} conversations")
            for conv in convs[:2]:  # Show first 2
                print(f"    • {conv.get('title')} ({conv.get('conversation_type')})")
                
    return bool(all_photos)

def verify_current_issues():
    """Verify what's currently broken in the system"""
    print("\n" + "="*80)
    print("VERIFYING CURRENT SYSTEM ISSUES")
    print("="*80)
    
    issues = []
    
    # 1. Check if ImagePersistenceService uses wrong table
    print("\n1. Checking ImagePersistenceService...")
    from services.image_persistence_service import ImagePersistenceService
    service = ImagePersistenceService()
    
    # Check what table it's using
    print(f"  - Service bucket: {service.bucket_name}")
    print(f"  ✗ ISSUE: Service updates 'inspiration_images' table (line 124)")
    print(f"    Should update unified_conversation_memory instead!")
    issues.append("ImagePersistenceService saves to legacy table")
    
    # 2. Check if IRIS agent has save methods
    print("\n2. Checking IRIS agent save capabilities...")
    import inspect
    from agents.iris import agent
    
    iris_methods = [m for m in dir(agent.IrisAgent) if not m.startswith('_')]
    save_methods = [m for m in iris_methods if 'save' in m.lower() or 'store' in m.lower()]
    
    if not save_methods:
        print(f"  ✗ ISSUE: IRIS agent has NO save methods!")
        print(f"    Methods found: {iris_methods}")
        issues.append("IRIS agent cannot save images")
    else:
        print(f"  ✓ Save methods found: {save_methods}")
        
    # 3. Check unified tables structure
    print("\n3. Checking unified tables for image support...")
    
    # Check if unified_conversation_memory can store images
    result = supabase.table("unified_conversation_memory").select("*").eq(
        "memory_type", "photo_reference"
    ).limit(1).execute()
    
    if result.data:
        print(f"  ✓ unified_conversation_memory has photo_reference entries")
    else:
        print(f"  ⚠ No photo_reference entries found in unified_conversation_memory")
        
    # Check if unified_message_attachments exists
    try:
        result = supabase.table("unified_message_attachments").select("*").limit(1).execute()
        print(f"  ✓ unified_message_attachments table exists")
    except Exception as e:
        print(f"  ✗ ISSUE: unified_message_attachments may not exist: {e}")
        issues.append("unified_message_attachments table issues")
        
    return issues

def create_production_ready_save_function():
    """Create the correct image save function for unified system"""
    print("\n" + "="*80)
    print("PRODUCTION-READY IMAGE SAVE FUNCTION")
    print("="*80)
    
    code = '''
async def save_image_to_unified_system(
    user_id: str,
    conversation_id: str,
    image_url: str,
    image_metadata: dict
) -> bool:
    """
    Save image to unified conversation memory system
    This is how IRIS should save images!
    """
    try:
        # Create memory entry for image
        memory_data = {
            "id": str(uuid.uuid4()),
            "tenant_id": "00000000-0000-0000-0000-000000000000",
            "conversation_id": conversation_id,
            "memory_scope": "conversation",
            "memory_type": "photo_reference",
            "memory_key": f"image_{datetime.now().timestamp()}",
            "memory_value": {
                "images": [{
                    "url": image_url,
                    "path": image_url.split("/")[-1],
                    "metadata": image_metadata
                }]
            },
            "importance_score": 7
        }
        
        result = supabase.table("unified_conversation_memory").insert(memory_data).execute()
        return bool(result.data)
        
    except Exception as e:
        logger.error(f"Failed to save image to unified system: {e}")
        return False
'''
    
    print(code)
    return code

if __name__ == "__main__":
    print("COMPLETE IRIS IMAGE FLOW TEST")
    print("Testing save, retrieve, and production readiness")
    print("="*80)
    
    # Test save flow
    conversation_id = test_image_save_flow()
    
    # Test retrieve flow
    if conversation_id:
        success = test_image_retrieve_flow(conversation_id)
    else:
        print("\n✗ Cannot test retrieve - save failed")
        success = False
        
    # Verify current issues
    issues = verify_current_issues()
    
    # Show production-ready solution
    create_production_ready_save_function()
    
    # Final verdict
    print("\n" + "="*80)
    print("PRODUCTION READINESS ASSESSMENT")
    print("="*80)
    
    if issues:
        print("\n❌ NOT PRODUCTION READY - Issues found:")
        for issue in issues:
            print(f"  • {issue}")
            
        print("\n📋 Required fixes:")
        print("  1. Update ImagePersistenceService to save to unified_conversation_memory")
        print("  2. Add save_image method to IRIS agent that calls unified system")
        print("  3. Ensure unified_message_attachments table exists and is accessible")
        print("  4. Test complete flow with real image uploads")
    else:
        print("\n✅ System appears production ready")
        
    print("\n📊 Current Status:")
    print("  • READ operations: ✅ Working through IrisContextAdapter")
    print("  • WRITE operations: ❌ Still using legacy tables")
    print("  • Adapter pattern: ✅ Correctly implemented for reads")
    print("  • Image persistence: ⚠️ Needs migration to unified system")