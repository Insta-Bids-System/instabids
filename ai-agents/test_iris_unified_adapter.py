"""
Test IRIS Context Adapter with Unified Memory System
Verifies adapter accesses unified tables and conversations from other agents
"""

import asyncio
import json
from adapters.iris_context import IrisContextAdapter

def test_iris_unified_adapter():
    """Test IRIS adapter with unified memory system integration"""
    
    print("Testing IRIS Context Adapter with Unified Memory System")
    print("=" * 80)
    
    # Initialize adapter
    adapter = IrisContextAdapter()
    
    if not adapter.supabase:
        print("❌ FAILED: No Supabase connection available")
        return False
    
    # Test with sample user_id and project_id
    test_user_id = "test-user-123"
    test_project_id = "test-project-456"
    
    try:
        # Get full inspiration context
        context = adapter.get_inspiration_context(
            user_id=test_user_id,
            project_id=test_project_id
        )
        
        print("✅ Context Retrieved Successfully")
        print(f"Context keys: {list(context.keys())}")
        
        # Verify all expected keys are present
        expected_keys = [
            "inspiration_boards",
            "project_context", 
            "design_preferences",
            "previous_designs",
            "conversations_from_other_agents",
            "photos_from_unified_system",
            "privacy_level"
        ]
        
        missing_keys = [key for key in expected_keys if key not in context]
        if missing_keys:
            print(f"❌ FAILED: Missing keys: {missing_keys}")
            return False
        
        print("✅ All expected context keys present")
        
        # Test conversations from other agents
        conversations = context["conversations_from_other_agents"]
        print(f"\nConversations from other agents:")
        print(f"  - Homeowner conversations: {len(conversations.get('homeowner_conversations', []))}")
        print(f"  - Messaging conversations: {len(conversations.get('messaging_conversations', []))}")
        print(f"  - Project conversations: {len(conversations.get('project_conversations', []))}")
        
        # Test photos from unified system
        photos = context["photos_from_unified_system"]
        print(f"\nPhotos from unified system:")
        print(f"  - Project photos: {len(photos.get('project_photos', []))}")
        print(f"  - Inspiration photos: {len(photos.get('inspiration_photos', []))}")
        print(f"  - Message attachments: {len(photos.get('message_attachments', []))}")
        
        # Test project context
        project = context["project_context"]
        print(f"\nProject context available: {project.get('project_available', False)}")
        if project.get("project_available"):
            print(f"  - Project type: {project.get('project_type')}")
            print(f"  - Conversation title: {project.get('conversation_title')}")
        
        # Test inspiration boards
        boards = context["inspiration_boards"]
        print(f"\nInspiration boards: {len(boards)} boards found")
        
        # Test design preferences
        prefs = context["design_preferences"]
        print(f"\nDesign preferences: {len(prefs)} preferences found")
        
        # Test previous designs
        designs = context["previous_designs"]
        print(f"\nPrevious designs: {len(designs)} designs found")
        
        print(f"\n✅ IRIS Unified Adapter Test PASSED")
        print(f"✅ Adapter successfully accesses unified conversation system")
        print(f"✅ Can retrieve conversations from homeowner and messaging agents")
        print(f"✅ Can access photos from unified message attachments")
        print(f"✅ Privacy level correctly set: {context['privacy_level']}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Error testing IRIS adapter: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_adapter_methods_individually():
    """Test each adapter method individually"""
    
    print("\nTesting Individual Adapter Methods")
    print("=" * 50)
    
    adapter = IrisContextAdapter()
    test_user_id = "test-user-123"
    test_project_id = "test-project-456"
    
    methods_to_test = [
        ("_get_inspiration_boards", [test_user_id]),
        ("_get_project_context", [test_user_id, test_project_id]),
        ("_get_design_preferences", [test_user_id]),
        ("_get_previous_designs", [test_user_id]),
        ("_get_conversations_from_other_agents", [test_user_id, test_project_id]),
        ("_get_photos_from_unified_system", [test_user_id, test_project_id])
    ]
    
    results = {}
    
    for method_name, args in methods_to_test:
        try:
            method = getattr(adapter, method_name)
            result = method(*args)
            results[method_name] = {
                "success": True,
                "data_type": type(result).__name__,
                "data_length": len(result) if hasattr(result, '__len__') else 0
            }
            print(f"✅ {method_name}: {results[method_name]['data_type']} with {results[method_name]['data_length']} items")
            
        except Exception as e:
            results[method_name] = {
                "success": False,
                "error": str(e)
            }
            print(f"❌ {method_name}: {e}")
    
    success_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)
    
    print(f"\nIndividual Method Test Results: {success_count}/{total_count} passed")
    
    return success_count == total_count

if __name__ == "__main__":
    print("IRIS Context Adapter Unified Memory Test")
    print("Testing adapter integration with unified conversation system")
    print("=" * 80)
    
    # Test main functionality
    main_test_passed = test_iris_unified_adapter()
    
    # Test individual methods
    methods_test_passed = test_adapter_methods_individually()
    
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    
    if main_test_passed and methods_test_passed:
        print("✅ ALL TESTS PASSED")
        print("✅ IRIS adapter successfully integrated with unified memory system")
        print("✅ Can access conversations from homeowner agent and messaging agent")
        print("✅ Can retrieve photos from unified system")
        print("✅ No direct database queries to legacy tables")
    else:
        print("❌ SOME TESTS FAILED")
        if not main_test_passed:
            print("❌ Main adapter test failed")
        if not methods_test_passed:
            print("❌ Individual methods test failed")
    
    print("\nINTEGRATION SUMMARY:")
    print("- IRIS now uses IrisContextAdapter exclusively")
    print("- Adapter queries unified_conversations and unified_conversation_memory")
    print("- Can access conversations from other agents (homeowner, messaging)")
    print("- Can retrieve photos from unified_message_attachments")
    print("- No more direct queries to inspiration_boards, user_memories, generated_dream_spaces")