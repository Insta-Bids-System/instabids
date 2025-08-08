#!/usr/bin/env python3
"""
Test proper profile creation and persistence
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

import agents.coia.unified_graph as ug_module
fixed_checkpointer = MemorySaver(serde=MessageAwareSerializer())

async def test_proper_profile_creation():
    """Test memory persistence with proper profile handling"""
    print("="*70)
    print("PROPER PROFILE CREATION TEST")
    print("="*70)
    
    try:
        app = await ug_module.create_unified_coia_system(checkpointer=fixed_checkpointer)
        
        contractor_id = "proper_test_contractor"
        config = {"configurable": {"thread_id": f"chat_{contractor_id}"}}
        
        # CONVERSATION 1: Normal profile creation through extraction
        print("\n[CONVERSATION 1] Normal profile creation...")
        
        from agents.coia.unified_state import create_initial_state
        
        state1 = create_initial_state(
            session_id="proper_session_1",
            interface="chat",
            contractor_lead_id=contractor_id
        ).to_langgraph_state()
        
        state1["messages"] = [HumanMessage(content="Hi! I'm ProperTest Roofing. We've been in business for 18 years in Chicago and specialize in storm damage repairs.")]
        
        result1 = await app.ainvoke(state1, config)
        profile1 = result1.get("contractor_profile", {})
        
        print(f"Profile after conversation 1:")
        print(f"  Company: {profile1.get('company_name')}")
        print(f"  Years: {profile1.get('years_in_business')}")
        print(f"  Trade: {profile1.get('primary_trade')}")
        
        # Verify it's saved correctly
        saved_state1 = await app.aget_state(config)
        saved_profile1 = saved_state1.values.get("contractor_profile", {})
        print(f"Saved profile:")
        print(f"  Company: {saved_profile1.get('company_name')}")
        print(f"  Years: {saved_profile1.get('years_in_business')}")
        print(f"  Trade: {saved_profile1.get('primary_trade')}")
        
        # CONVERSATION 2: Using invoke_coia_chat instead of direct ainvoke
        print("\n[CONVERSATION 2] Using invoke_coia_chat...")
        
        response2 = await ug_module.invoke_coia_chat(
            app=app,
            user_message="What's my company name and how many years have I been in business?",
            contractor_lead_id=contractor_id,
            session_id="proper_session_2"
        )
        
        # Check the state after invoke_coia_chat
        state2 = await app.aget_state(config)
        profile2 = state2.values.get("contractor_profile", {})
        
        print(f"Profile after invoke_coia_chat:")
        print(f"  Company: {profile2.get('company_name')}")
        print(f"  Years: {profile2.get('years_in_business')}")
        print(f"  Trade: {profile2.get('primary_trade')}")
        
        messages2 = state2.values.get("messages", [])
        if messages2:
            last_message = messages2[-1]
            print(f"Response: {last_message.content[:100]}...")
        
        # ANALYSIS
        print(f"\n[ANALYSIS]")
        company1 = profile1.get('company_name')
        company2 = profile2.get('company_name') 
        years1 = profile1.get('years_in_business')
        years2 = profile2.get('years_in_business')
        
        print(f"Company name: '{company1}' -> '{company2}'")
        print(f"Years in business: {years1} -> {years2}")
        
        company_persisted = company1 == company2 and company1 is not None
        years_persisted = years1 == years2 and years1 is not None
        
        if company_persisted and years_persisted:
            print("[SUCCESS] Profile data persisted correctly!")
            return True
        else:
            print("[FAILURE] Profile data lost during memory persistence")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_proper_profile_creation())
    print(f"\nRESULT: {'SUCCESS' if success else 'FAILED'}")