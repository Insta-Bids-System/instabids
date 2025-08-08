#!/usr/bin/env python3
"""
Debug how LangGraph handles partial state updates
"""
import asyncio
import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath('.'))
logging.basicConfig(level=logging.WARNING)

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class MessageAwareSerializer:
    def dumps_typed(self, obj):
        return json.dumps(obj, default=self._serialize_message)
    
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
        return str(obj)
    
    def _deserialize_message(self, obj):
        if isinstance(obj, dict) and "__langchain_type" in obj:
            msg_type = obj["__langchain_type"]
            if msg_type == "HumanMessage":
                return HumanMessage(content=obj["content"])
            elif msg_type == "AIMessage":
                return AIMessage(content=obj["content"])
        return obj

import agents.coia.unified_graph as ug_module
fixed_checkpointer = MemorySaver(serde=MessageAwareSerializer())

async def test_state_update_behavior():
    """Test exactly how state updates work in LangGraph"""
    print("="*70)
    print("STATE UPDATE BEHAVIOR DEBUG")  
    print("="*70)
    
    try:
        app = await ug_module.create_unified_coia_system(checkpointer=fixed_checkpointer)
        
        thread_id = "update_test_contractor"
        config = {"configurable": {"thread_id": f"chat_{thread_id}"}}
        
        # SETUP: Create initial state with profile
        print("\n[SETUP] Creating initial state with profile...")
        from agents.coia.unified_state import create_initial_state
        
        initial_state = create_initial_state(
            session_id="setup_session",
            interface="chat", 
            contractor_lead_id=thread_id
        ).to_langgraph_state()
        
        # Add profile data manually to test
        initial_state["contractor_profile"] = {
            "primary_trade": "Electrician",
            "years_in_business": 30,
            "company_name": "Test Electric Co",
            "completeness": 0.3
        }
        initial_state["messages"] = [HumanMessage(content="Initial setup message")]
        
        result_setup = await app.ainvoke(initial_state, config)
        setup_profile = result_setup.get("contractor_profile", {})
        print(f"Setup result profile: {json.dumps(setup_profile, indent=2)}")
        
        # Check what was saved
        saved_state = await app.aget_state(config)
        saved_profile = saved_state.values.get("contractor_profile", {})
        print(f"Saved profile after setup: {json.dumps(saved_profile, indent=2)}")
        
        # TEST 1: Full state update
        print(f"\n[TEST 1] Full state update...")
        
        # Get current state and add message
        current_state = await app.aget_state(config)
        full_update = current_state.values.copy()
        full_update["messages"] = current_state.values.get("messages", []) + [HumanMessage(content="Full update test")]
        
        result_full = await app.ainvoke(full_update, config)
        full_profile = result_full.get("contractor_profile", {})
        print(f"Full update result: {json.dumps(full_profile, indent=2)}")
        
        # TEST 2: Partial state update (what we were doing)
        print(f"\n[TEST 2] Partial state update...")
        
        result_partial = await app.ainvoke({"messages": [HumanMessage(content="Partial update test")]}, config)
        partial_profile = result_partial.get("contractor_profile", {})
        print(f"Partial update result: {json.dumps(partial_profile, indent=2)}")
        
        # ANALYSIS
        print(f"\n[ANALYSIS]")
        setup_name = setup_profile.get('company_name')
        full_name = full_profile.get('company_name') 
        partial_name = partial_profile.get('company_name')
        
        print(f"Company name through updates:")
        print(f"  Setup: {setup_name}")
        print(f"  Full update: {full_name}")  
        print(f"  Partial update: {partial_name}")
        
        if setup_name and full_name == setup_name and partial_name != setup_name:
            print("ISSUE IDENTIFIED: Partial updates lose profile data")
            return False
        elif setup_name and full_name == setup_name and partial_name == setup_name:
            print("SUCCESS: Both update methods preserve profile")
            return True
        else:
            print("UNCLEAR: Other issue with profile handling")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_state_update_behavior())
    print(f"\nFINAL: {'SUCCESS' if success else 'FAILED'}")