#!/usr/bin/env python3
"""
Direct test of memory with fixed checkpointer
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
        return json.dumps(obj, default=self._serialize_message, indent=2)
    
    def loads_typed(self, data):
        return json.loads(data, object_hook=self._deserialize_message)
    
    def _serialize_message(self, obj):
        if isinstance(obj, BaseMessage):
            return {
                "__langchain_type": obj.__class__.__name__,
                "content": obj.content,
                "additional_kwargs": getattr(obj, 'additional_kwargs', {}),
                "response_metadata": getattr(obj, 'response_metadata', {})
            }
        elif hasattr(obj, '__dict__'):
            # For other objects, serialize their dict
            return {f"__{obj.__class__.__name__}": obj.__dict__}
        return str(obj)
    
    def _deserialize_message(self, obj):
        if isinstance(obj, dict) and "__langchain_type" in obj:
            msg_type = obj["__langchain_type"]
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

# Directly patch the checkpointer creation in unified graph
import agents.coia.unified_graph as ug_module

# Create our fixed checkpointer
fixed_checkpointer = MemorySaver(serde=MessageAwareSerializer())

# Replace the MemorySaver calls directly 
original_create_system = ug_module.create_unified_coia_system

async def create_fixed_coia_system():
    """Create COIA system with our fixed checkpointer"""
    return await original_create_system(checkpointer=fixed_checkpointer)

# Monkey patch
ug_module.create_unified_coia_system = create_fixed_coia_system

async def test_direct_memory_fix():
    """Test memory with direct checkpointer fix"""
    print("======================================================================")
    print("DIRECT MEMORY FIX TEST")
    print("Testing with directly injected fixed checkpointer") 
    print("======================================================================")
    
    try:
        # Create system with our fixed checkpointer
        print("\n[SETUP] Creating COIA system with directly injected fixed checkpointer...")
        app = await create_fixed_coia_system()
        print("COIA system created with message-aware serialization")
        
        contractor_id = "direct_fix_contractor"
        thread_id = f"chat_{contractor_id}"
        
        # CONVERSATION 1: Create profile
        print(f"\n[CONVERSATION 1] Creating contractor profile...")
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Create initial state manually
        from agents.coia.unified_state import UnifiedCoIAState, create_initial_state
        from langchain_core.messages import HumanMessage
        
        initial_state = create_initial_state(
            session_id="test_session_1",
            interface="chat", 
            contractor_lead_id=contractor_id
        ).to_langgraph_state()
        
        initial_state["messages"] = [HumanMessage(content="Hi! I'm DirectFix Roofing from Miami. We've been in business for 20 years and specialize in hurricane damage repairs.")]
        
        print("Invoking COIA with fixed checkpointer...")
        result1 = await app.ainvoke(initial_state, config)
        
        # Extract profile and response 
        profile1 = result1.get("contractor_profile", {})
        messages1 = result1.get("messages", [])
        response1 = messages1[-1].content if messages1 else "No response"
        
        print(f"Profile created: {json.dumps({k: v for k, v in profile1.items() if v}, indent=2)}")
        print(f"Response: {response1[:100]}...")
        
        # CONVERSATION 2: Test memory
        print(f"\n[CONVERSATION 2] Testing memory...")
        
        # For conversation 2, just add a new message to existing state
        new_message = HumanMessage(content="What's my company name and how long have I been in business?")
        
        result2 = await app.ainvoke({"messages": [new_message]}, config)
        
        profile2 = result2.get("contractor_profile", {}) 
        messages2 = result2.get("messages", [])
        response2 = messages2[-1].content if messages2 else "No response"
        
        print(f"Remembered profile: {json.dumps({k: v for k, v in profile2.items() if v}, indent=2)}")
        print(f"Memory response: {response2}")
        
        # ANALYSIS
        print("\n" + "="*70)
        print("DIRECT FIX ANALYSIS") 
        print("="*70)
        
        company_works = profile2.get('company_name') == 'DirectFix Roofing'
        years_works = profile2.get('years_in_business') == 20
        location_works = 'Miami' in str(profile2.get('service_areas', []))
        
        print(f"Company name persisted: {'PASS' if company_works else 'FAIL'}")
        print(f"Years in business persisted: {'PASS' if years_works else 'FAIL'}")
        print(f"Location persisted: {'PASS' if location_works else 'FAIL'}")
        
        if company_works and years_works:
            print("\n[SUCCESS] Direct checkpointer fix works!")
        else:
            print("\n[FAILURE] Still having memory issues")
            
        return company_works and years_works
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct_memory_fix())
    print(f"\nFINAL RESULT: {'SUCCESS' if success else 'FAILED'}")