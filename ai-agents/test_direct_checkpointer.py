"""
Direct test of the MCP Supabase checkpointer to see if it's working
"""
import asyncio
import json

async def test_direct_checkpointer():
    """Test the checkpointer directly without going through the API"""
    try:
        from agents.coia.mcp_supabase_checkpointer import create_mcp_supabase_checkpointer
        
        print("Creating MCP Supabase checkpointer...")
        checkpointer = await create_mcp_supabase_checkpointer()
        print("Checkpointer created successfully!")
        
        # Test saving a simple checkpoint
        config = {
            "configurable": {
                "thread_id": "direct-test-thread",
                "checkpoint_ns": "test_namespace",
                "checkpoint_id": "test-checkpoint-123"
            }
        }
        
        # Create a simple checkpoint
        from langgraph.checkpoint.base import CheckpointMetadata
        checkpoint = {
            "id": "test-checkpoint-123",
            "messages": [{"role": "user", "content": "test message"}],
            "thread_id": "direct-test-thread"
        }
        
        metadata = CheckpointMetadata(
            source="test",
            step=1,
            writes={"test": "data"}
        )
        
        print("Attempting to save checkpoint...")
        result = await checkpointer.aput(config, checkpoint, metadata, {})
        print(f"Save result: {result}")
        
        # Try to retrieve the checkpoint
        print("Attempting to retrieve checkpoint...")
        retrieved = await checkpointer.aget_tuple(config)
        print(f"Retrieved: {retrieved}")
        
        return True
        
    except Exception as e:
        print(f"Error testing checkpointer: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_mcp_function():
    """Test if the MCP function can be called directly"""
    try:
        print("Testing direct MCP function call...")
        result = await mcp__supabase__execute_sql(
            project_id="xrhgrthdcaymxuqcgrmj",
            query="SELECT 'hello' as test_message"
        )
        print(f"MCP function works: {result}")
        return True
    except Exception as e:
        print(f"MCP function error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing MCP Supabase Checkpointer Directly")
    print("=" * 50)
    
    # Test MCP function first
    asyncio.run(check_mcp_function())
    
    print("\nTesting checkpointer...")
    success = asyncio.run(test_direct_checkpointer())
    
    if success:
        print("\nSUCCESS: Direct checkpointer test passed!")
    else:
        print("\nFAILURE: Direct checkpointer test failed!")