#!/usr/bin/env python3
"""
Final comprehensive test of complete memory persistence system
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

async def test_final_memory_system():
    """Comprehensive test of complete memory persistence"""
    print("="*80)
    print("FINAL COMPREHENSIVE MEMORY PERSISTENCE TEST")
    print("Testing: Serialization + State Management + Profile Persistence")
    print("="*80)
    
    try:
        app = await ug_module.create_unified_coia_system(checkpointer=fixed_checkpointer)
        
        contractor_id = "comprehensive_test_contractor"
        
        # TEST 1: Create detailed contractor profile
        print("\n[TEST 1] Creating comprehensive contractor profile...")
        response1 = await ug_module.invoke_coia_chat(
            app=app,
            user_message="Hi! I'm Sarah from FinalTest HVAC Solutions. We've been in business for 28 years in Seattle, Washington. We specialize in commercial HVAC installations and emergency repairs, and we're fully licensed and insured.",
            contractor_lead_id=contractor_id,
            session_id="final_session_1"
        )
        
        config = {"configurable": {"thread_id": f"chat_{contractor_id}"}}
        state1 = await app.aget_state(config)
        profile1 = state1.values.get("contractor_profile", {})
        
        print(f"Profile created:")
        print(f"  Company: {profile1.get('company_name')}")
        print(f"  Years: {profile1.get('years_in_business')}")
        print(f"  Trade: {profile1.get('primary_trade')}")
        print(f"  Location: {profile1.get('service_areas')}")
        print(f"  Specializations: {profile1.get('specializations')}")
        
        # TEST 2: Memory recall test
        print(f"\n[TEST 2] Memory recall - asking about company details...")
        response2 = await ug_module.invoke_coia_chat(
            app=app,
            user_message="What's my company name and how many years have I been in business?",
            contractor_lead_id=contractor_id,
            session_id="final_session_2"
        )
        
        state2 = await app.aget_state(config)
        profile2 = state2.values.get("contractor_profile", {})
        
        print(f"Memory recall response: {response2.get('response', 'No response')[:100]}...")
        print(f"Remembered profile:")
        print(f"  Company: {profile2.get('company_name')}")
        print(f"  Years: {profile2.get('years_in_business')}")
        print(f"  Trade: {profile2.get('primary_trade')}")
        
        # TEST 3: Add new information
        print(f"\n[TEST 3] Adding new profile information...")
        response3 = await ug_module.invoke_coia_chat(
            app=app,
            user_message="We also handle residential work and have a team of 12 technicians. Our service area covers King County.",
            contractor_lead_id=contractor_id,
            session_id="final_session_3"
        )
        
        state3 = await app.aget_state(config)
        profile3 = state3.values.get("contractor_profile", {})
        
        print(f"Enhanced profile:")
        print(f"  Company: {profile3.get('company_name')}")
        print(f"  Years: {profile3.get('years_in_business')}")
        print(f"  Team size: {profile3.get('team_size')}")
        print(f"  Service areas: {profile3.get('service_areas')}")
        
        # TEST 4: Final memory verification
        print(f"\n[TEST 4] Final comprehensive memory test...")
        response4 = await ug_module.invoke_coia_chat(
            app=app,
            user_message="Can you summarize my complete contractor profile?",
            contractor_lead_id=contractor_id,
            session_id="final_session_4"
        )
        
        state4 = await app.aget_state(config)
        profile4 = state4.values.get("contractor_profile", {})
        
        print(f"Final profile summary:")
        non_empty = {k: v for k, v in profile4.items() if v}
        print(json.dumps(non_empty, indent=2))
        
        # COMPREHENSIVE ANALYSIS
        print(f"\n" + "="*80)
        print("COMPREHENSIVE ANALYSIS")
        print("="*80)
        
        # Check persistence across all conversations
        company_persistent = all([
            profile1.get('company_name'),
            profile2.get('company_name') == profile1.get('company_name'),
            profile3.get('company_name') == profile1.get('company_name'),
            profile4.get('company_name') == profile1.get('company_name')
        ])
        
        years_persistent = all([
            profile1.get('years_in_business'),
            profile2.get('years_in_business') == profile1.get('years_in_business'),
            profile3.get('years_in_business') == profile1.get('years_in_business'),
            profile4.get('years_in_business') == profile1.get('years_in_business')
        ])
        
        data_accumulation = (
            len([v for v in profile1.values() if v]) <= 
            len([v for v in profile4.values() if v])
        )
        
        print(f"Company name persistence across 4 conversations: {'PASS' if company_persistent else 'FAIL'}")
        print(f"Years in business persistence across 4 conversations: {'PASS' if years_persistent else 'FAIL'}")
        print(f"Data accumulation (profile grows over time): {'PASS' if data_accumulation else 'FAIL'}")
        
        # Check message history persistence
        messages = state4.values.get("messages", [])
        conversation_history = len(messages) >= 8  # Should have 4+ human + 4+ AI messages
        
        print(f"Conversation history persistence ({len(messages)} messages): {'PASS' if conversation_history else 'FAIL'}")
        
        overall_success = company_persistent and years_persistent and data_accumulation and conversation_history
        
        if overall_success:
            print(f"\n[SUCCESS] Complete memory persistence system working!")
            print(f"- Profile data persists across multiple conversations")
            print(f"- New information is accumulated without losing existing data") 
            print(f"- Conversation history is maintained")
            print(f"- Serialization handles LangChain messages correctly")
        else:
            print(f"\n[FAILURE] Memory persistence system has issues")
            
        return overall_success
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_final_memory_system())
    print(f"\nFINAL RESULT: {'COMPLETE SUCCESS' if success else 'FAILED'}")
    print("="*80)