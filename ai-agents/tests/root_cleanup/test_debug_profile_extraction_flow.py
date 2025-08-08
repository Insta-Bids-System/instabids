#!/usr/bin/env python3
"""
Debug the exact profile extraction flow during conversation
"""
import asyncio
import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath('.'))

# Enable more detailed logging to see what's happening
logging.basicConfig(level=logging.INFO)

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class MessageAwareSerializer:
    def dumps_typed(self, obj):
        return json.dumps(obj, default=self._serialize_message)
    
    def loads_typed(self, data):
        return json.loads(data, object_hook=self._deserialize_message)
    
    def _serialize_message(self, obj):
        if isinstance(obj, BaseMessage):
            return {"__langchain_type": obj.__class__.__name__, "content": obj.content}
        return str(obj)
    
    def _deserialize_message(self, obj):
        if isinstance(obj, dict) and "__langchain_type" in obj:
            msg_type = obj["__langchain_type"]
            if msg_type == "HumanMessage":
                return HumanMessage(content=obj["content"])
            elif msg_type == "AIMessage":
                return AIMessage(content=obj["content"])
        return obj

# Patch the conversation node to add debugging
import agents.coia.langgraph_nodes as nodes_module

original_conversation_node = nodes_module.conversation_node

async def debug_conversation_node(state):
    print(f"\n[DEBUG] conversation_node called")
    
    profile_in_state = state.get("contractor_profile", "NOT_FOUND")
    print(f"[DEBUG] INPUT profile: {type(profile_in_state)}")
    if isinstance(profile_in_state, dict):
        non_empty = {k: v for k, v in profile_in_state.items() if v}
        print(f"[DEBUG] INPUT profile contents: {json.dumps(non_empty, indent=2) if non_empty else 'EMPTY DICT'}")
    
    # Patch the _smart_profile_extraction to see what it's doing
    import agents.coia.langgraph_nodes as nodes
    
    # Find the ConversationNode instance to patch its method
    original_extraction = None
    for attr_name in dir(nodes):
        attr = getattr(nodes, attr_name)
        if hasattr(attr, '_smart_profile_extraction'):
            original_extraction = attr._smart_profile_extraction
            
            def debug_extraction(self, user_message, current_profile):
                print(f"[DEBUG] _smart_profile_extraction called:")
                print(f"[DEBUG]   user_message: '{user_message}'")
                print(f"[DEBUG]   current_profile input: {json.dumps({k: v for k, v in current_profile.items() if v}, indent=2) if current_profile else 'NONE'}")
                
                result = original_extraction(user_message, current_profile)
                
                print(f"[DEBUG]   extraction result: {json.dumps({k: v for k, v in result.items() if v}, indent=2) if result else 'NONE'}")
                return result
            
            attr._smart_profile_extraction = debug_extraction
            break
    
    # Call original method
    result = await original_conversation_node(state)
    
    profile_in_result = result.get("contractor_profile", "NOT_FOUND")  
    print(f"[DEBUG] OUTPUT profile: {type(profile_in_result)}")
    if isinstance(profile_in_result, dict):
        non_empty_result = {k: v for k, v in profile_in_result.items() if v}
        print(f"[DEBUG] OUTPUT profile contents: {json.dumps(non_empty_result, indent=2) if non_empty_result else 'EMPTY DICT'}")
    
    return result

# Monkey patch
nodes_module.conversation_node = debug_conversation_node

import agents.coia.unified_graph as ug_module
fixed_checkpointer = MemorySaver(serde=MessageAwareSerializer())

async def debug_profile_extraction_flow():
    """Debug what happens to profile during conversation processing"""
    print("="*70)
    print("DEBUG PROFILE EXTRACTION FLOW")
    print("="*70)
    
    try:
        app = await ug_module.create_unified_coia_system(checkpointer=fixed_checkpointer)
        
        contractor_id = "debug_flow_contractor"
        config = {"configurable": {"thread_id": f"chat_{contractor_id}"}}
        
        # STEP 1: Create profile with direct ainvoke
        print("\n[STEP 1] Creating profile with direct ainvoke...")
        
        from agents.coia.unified_state import create_initial_state
        
        state1 = create_initial_state(
            session_id="debug_session_1",
            interface="chat",
            contractor_lead_id=contractor_id
        ).to_langgraph_state()
        
        state1["messages"] = [HumanMessage(content="Hi! I'm DebugFlow Electric. We've been in business for 22 years in Boston.")]
        
        result1 = await app.ainvoke(state1, config)
        profile1 = result1.get("contractor_profile", {})
        
        print(f"[STEP 1] Profile created: {json.dumps({k: v for k, v in profile1.items() if v}, indent=2)}")
        
        # Check saved state
        saved_state1 = await app.aget_state(config)
        saved_profile1 = saved_state1.values.get("contractor_profile", {})
        print(f"[STEP 1] Saved profile: {json.dumps({k: v for k, v in saved_profile1.items() if v}, indent=2)}")
        
        # STEP 2: Use invoke_coia_chat (this is where the problem happens)
        print(f"\n[STEP 2] Using invoke_coia_chat - this should trigger the debug logging...")
        
        response2 = await ug_module.invoke_coia_chat(
            app=app,
            user_message="What's my company name?",
            contractor_lead_id=contractor_id,
            session_id="debug_session_2"
        )
        
        # Check result
        state2 = await app.aget_state(config)
        profile2 = state2.values.get("contractor_profile", {})
        
        print(f"[STEP 2] Profile after invoke_coia_chat: {json.dumps({k: v for k, v in profile2.items() if v}, indent=2)}")
        
        # ANALYSIS
        company1 = profile1.get('company_name')
        company2 = profile2.get('company_name')
        
        print(f"\n[ANALYSIS] Company name: '{company1}' -> '{company2}'")
        
        if company1 and not company2:
            print("[PROBLEM CONFIRMED] Profile data lost in invoke_coia_chat flow")
        elif company1 and company2:
            print("[SUCCESS] Profile data preserved")
        
        return bool(company1 and company2)
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_profile_extraction_flow())
    print(f"\nRESULT: {'SUCCESS' if success else 'FAILED'}")