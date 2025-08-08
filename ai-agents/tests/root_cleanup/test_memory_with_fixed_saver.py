#!/usr/bin/env python3
"""
Test memory persistence with properly serialized checkpointer
"""
import asyncio
import os
import sys
import json
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class MessageAwareSerializer:
    """Custom serializer that can handle LangChain messages"""
    
    def dumps_typed(self, obj):
        return json.dumps(obj, default=self._serialize_message)
    
    def loads_typed(self, data):
        return json.loads(data, object_hook=self._deserialize_message)
    
    def _serialize_message(self, obj):
        if isinstance(obj, BaseMessage):
            return {
                "__type": obj.__class__.__name__,
                "content": obj.content,
                "additional_kwargs": getattr(obj, 'additional_kwargs', {}),
                "response_metadata": getattr(obj, 'response_metadata', {})
            }
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    def _deserialize_message(self, obj):
        if isinstance(obj, dict) and "__type" in obj:
            msg_type = obj["__type"]
            if msg_type == "HumanMessage":
                return HumanMessage(
                    content=obj["content"],
                    additional_kwargs=obj.get("additional_kwargs", {}),
                    response_metadata=obj.get("response_metadata", {})
                )
            elif msg_type == "AIMessage":
                return AIMessage(
                    content=obj["content"],
                    additional_kwargs=obj.get("additional_kwargs", {}),
                    response_metadata=obj.get("response_metadata", {})
                )
        return obj

class FixedMemorySaver(MemorySaver):
    """MemorySaver with proper message serialization"""
    
    def __init__(self):
        super().__init__(serde=MessageAwareSerializer())

from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

async def test_memory_with_fixed_saver():
    """Test memory with fixed serialization"""
    print("======================================================================")
    print("MEMORY TEST WITH FIXED SERIALIZATION")
    print("Testing message-aware checkpointer")
    print("======================================================================")
    
    # Monkey patch to use our fixed checkpointer
    import agents.coia.unified_graph as graph_module
    original_memory_saver = graph_module.MemorySaver
    graph_module.MemorySaver = FixedMemorySaver
    
    try:
        # Create COIA system with fixed checkpointer
        print("\n[SETUP] Creating COIA system with fixed checkpointer...")
        app = await create_unified_coia_system()
        print("COIA system created - using fixed message serialization")
        
        contractor_id = "serialization_test_contractor"
        
        # CONVERSATION 1: Create profile
        print(f"\n[CONVERSATION 1] Creating contractor profile...")
        response1 = await invoke_coia_chat(
            app=app,
            user_message="Hi! I'm Sarah from SerializeTest Plumbing. We've been in business for 15 years, based in Austin, Texas. We specialize in emergency plumbing repairs and bathroom renovations.",
            contractor_lead_id=contractor_id,
            session_id="test_session_1"
        )
        
        # Extract profile from state 
        config = {"configurable": {"thread_id": f"chat_{contractor_id}"}}
        state = await app.aget_state(config)
        profile1 = state.values.get("contractor_profile", {})
        
        print(f"Profile created: {json.dumps({k: v for k, v in profile1.items() if v}, indent=2)}")
        print(f"Response: {response1['response'][:100]}...")
        
        # CONVERSATION 2: Test memory 
        print(f"\n[CONVERSATION 2] Testing memory recall...")
        response2 = await invoke_coia_chat(
            app=app,
            user_message="What's my company name and how many years have I been in business?",
            contractor_lead_id=contractor_id,
            session_id="test_session_2"
        )
        
        # Check remembered profile
        state2 = await app.aget_state(config)
        profile2 = state2.values.get("contractor_profile", {})
        
        print(f"Remembered profile: {json.dumps({k: v for k, v in profile2.items() if v}, indent=2)}")
        print(f"Memory response: {response2['response']}")
        
        # ANALYSIS
        print("\n" + "="*70)
        print("SERIALIZATION ANALYSIS")
        print("="*70)
        
        company_works = profile2.get('company_name') == 'SerializeTest Plumbing'
        years_works = profile2.get('years_in_business') == 15
        location_works = 'Austin' in str(profile2.get('service_areas', []))
        
        print(f"Company name persisted: {'PASS' if company_works else 'FAIL'}")
        print(f"Years in business persisted: {'PASS' if years_works else 'FAIL'}")
        print(f"Service area persisted: {'PASS' if location_works else 'FAIL'}")
        
        if company_works and years_works and location_works:
            print("\n[SUCCESS] SERIALIZATION FIX SUCCESSFUL!")
            print("Memory persistence now works with message-aware serializer")
        else:
            print(f"\n[FAILURE] SERIALIZATION STILL HAS ISSUES")
            print("Need to investigate further")
            
        return company_works and years_works and location_works
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore original
        graph_module.MemorySaver = original_memory_saver

if __name__ == "__main__":
    success = asyncio.run(test_memory_with_fixed_saver())
    print(f"\nFINAL RESULT: {'SUCCESS' if success else 'FAILED'}")