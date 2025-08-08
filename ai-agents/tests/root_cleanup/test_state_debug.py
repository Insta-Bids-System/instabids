#!/usr/bin/env python3
"""
Debug state persistence in COIA system
"""
import asyncio
import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath('.'))

# Set up logging
logging.basicConfig(level=logging.WARNING)

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class MessageAwareSerializer:
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

# Direct setup
import agents.coia.unified_graph as ug_module
fixed_checkpointer = MemorySaver(serde=MessageAwareSerializer())

async def debug_state_persistence():
    """Debug what's happening to state between conversations"""
    print("="*70)
    print("STATE PERSISTENCE DEBUG")
    print("="*70)
    
    try:
        app = await ug_module.create_unified_coia_system(checkpointer=fixed_checkpointer)
        
        thread_id = "debug_contractor"
        config = {"configurable": {"thread_id": f"chat_{thread_id}"}}
        
        print(f"\n[STEP 1] Initial state check...")
        initial_state = await app.aget_state(config)
        print(f"Initial state exists: {bool(initial_state.values)}")
        
        # CONVERSATION 1
        print(f"\n[STEP 2] First conversation - creating profile...")
        from agents.coia.unified_state import create_initial_state
        
        state1 = create_initial_state(
            session_id="debug_session",
            interface="chat",
            contractor_lead_id=thread_id
        ).to_langgraph_state()
        
        state1["messages"] = [HumanMessage(content="Hi! I'm StateDebug Plumbing. We've been in business for 25 years in Denver.")]
        
        result1 = await app.ainvoke(state1, config)
        profile1 = result1.get("contractor_profile", {})
        
        print(f"After conversation 1:")
        print(f"  Profile created: {json.dumps({k: v for k, v in profile1.items() if v}, indent=4)}")
        
        # Check saved state
        saved_state1 = await app.aget_state(config)
        saved_profile1 = saved_state1.values.get("contractor_profile", {})
        print(f"  Saved profile: {json.dumps({k: v for k, v in saved_profile1.items() if v}, indent=4)}")
        
        # CONVERSATION 2 
        print(f"\n[STEP 3] Second conversation - testing memory...")
        
        # Get current state first
        current_state = await app.aget_state(config)
        print(f"Current state before conversation 2:")
        print(f"  Has messages: {len(current_state.values.get('messages', []))}")
        print(f"  Has profile: {bool(current_state.values.get('contractor_profile'))}")
        
        # Add just new message to existing state 
        result2 = await app.ainvoke({"messages": [HumanMessage(content="What's my company name?")]}, config)
        profile2 = result2.get("contractor_profile", {})
        
        print(f"After conversation 2:")
        print(f"  Profile in result: {json.dumps({k: v for k, v in profile2.items() if v}, indent=4)}")
        
        # Check final saved state
        saved_state2 = await app.aget_state(config)
        saved_profile2 = saved_state2.values.get("contractor_profile", {})
        print(f"  Final saved profile: {json.dumps({k: v for k, v in saved_profile2.items() if v}, indent=4)}")
        
        # ANALYSIS
        print(f"\n[ANALYSIS]")
        name1 = profile1.get('company_name', 'NONE')
        name2 = profile2.get('company_name', 'NONE') 
        years1 = profile1.get('years_in_business', 'NONE')
        years2 = profile2.get('years_in_business', 'NONE')
        
        print(f"Company name: {name1} -> {name2}")
        print(f"Years in business: {years1} -> {years2}")
        
        if name1 != 'NONE' and name2 == 'NONE':
            print("❌ PROFILE DATA LOST between conversations")
        elif name1 == name2 and years1 == years2:
            print("✅ PROFILE DATA PERSISTED correctly")
        else:
            print("⚠️  PROFILE DATA PARTIALLY PERSISTED")
            
        return name1 != 'NONE' and name2 != 'NONE'
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_state_persistence())
    print(f"\nFINAL: {'SUCCESS' if success else 'FAILED'}")