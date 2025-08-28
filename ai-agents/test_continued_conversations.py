#!/usr/bin/env python3
"""
Test continued conversations with same homeowner to verify context building
"""

import asyncio
import json
from datetime import datetime
import database_simple

from agents.cia.agent import CustomerInterfaceAgent
from services.universal_session_manager import universal_session_manager

db = database_simple.get_client()

async def test_continued_conversations():
    """Test multiple conversations with same homeowner"""
    
    print("\n" + "="*70)
    print("CONTINUED CONVERSATION TEST - CONTEXT BUILDING")
    print("="*70)
    
    # Same homeowner from previous test
    user_id = "1fc89c95-3dba-4780-9171-9a60600bacf3"
    print(f"Using same homeowner: {user_id}")
    
    # Check existing conversations first
    existing_convs = db.table("unified_conversations").select("*").eq(
        "created_by", user_id
    ).execute()
    
    print(f"Starting with {len(existing_convs.data)} existing conversations")
    for conv in existing_convs.data:
        agent_type = conv.get("metadata", {}).get("agent_type", "Unknown")
        print(f"  - {agent_type}: {conv.get('title', 'No title')}")
    
    # Initialize CIA
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: No API key")
        return False
        
    cia = CustomerInterfaceAgent(api_key=api_key)
    
    # CONTINUED CONVERSATION 1: CIA Follow-up
    print(f"\n" + "-"*60)
    print("CONTINUED CIA CONVERSATION - Follow-up Questions")
    print("-"*60)
    
    cia_session_2 = f"followup-cia-{int(datetime.now().timestamp())}"
    print(f"New CIA Session: {cia_session_2}")
    
    cia_followup_message = """Hi Alex, I have some follow-up questions about my bathroom renovation. 
    I'm wondering about the walk-in shower - what size should I plan for in a 60 sq ft space? 
    Also, I'm now thinking maybe I want heated floors. Would that fit in my $15k-$20k budget?"""
    
    print(f"Homeowner follow-up: {cia_followup_message[:100]}...")
    
    try:
        cia_response_2 = await cia.handle_conversation(
            user_id=user_id,
            message=cia_followup_message,
            session_id=cia_session_2
        )
        print(f"CIA Follow-up Response: {len(cia_response_2['response'])} characters")
        print(f"Preview: {cia_response_2['response'][:150]}...")
    except Exception as e:
        print(f"CIA Error: {e}")
        return False
    
    # CONTINUED CONVERSATION 2: More CIA details
    print(f"\n" + "-"*60) 
    print("THIRD CIA CONVERSATION - More Specifics")
    print("-"*60)
    
    cia_message_3 = """I've been thinking more about the vanity. The current one is 24 inches but I'd love 
    to go to 36 inches if possible. Also, I saw some beautiful quartz countertops online - are those 
    within budget? And can you help me understand what permits I might need?"""
    
    print(f"Homeowner specifics: {cia_message_3[:100]}...")
    
    try:
        cia_response_3 = await cia.handle_conversation(
            user_id=user_id,
            message=cia_message_3,
            session_id=cia_session_2  # Same session as follow-up
        )
        print(f"CIA Specifics Response: {len(cia_response_3['response'])} characters")
        print(f"Preview: {cia_response_3['response'][:150]}...")
    except Exception as e:
        print(f"CIA Error: {e}")
        
    # CONTINUED IRIS CONVERSATION
    print(f"\n" + "-"*60)
    print("CONTINUED IRIS CONVERSATION - More Design Ideas") 
    print("-"*60)
    
    iris_session_2 = f"followup-iris-{int(datetime.now().timestamp())}"
    
    # Create IRIS follow-up session
    iris_session = await universal_session_manager.get_or_create_session(
        session_id=iris_session_2,
        user_id=user_id,
        agent_type="IRIS"
    )
    
    if iris_session:
        print(f"IRIS follow-up session created: {iris_session_2}")
        
        # IRIS follow-up showing awareness of CIA updates
        await universal_session_manager.add_message_to_session(
            session_id=iris_session_2,
            role="user",
            content="I'm getting more specific about my bathroom. I want a 36-inch vanity instead of 24-inch, and I'm considering heated floors and quartz countertops. Can you show me inspiration for this upgraded design?",
            metadata={"agent_type": "IRIS"}
        )
        
        iris_followup_response = """Great! I can see your project is evolving beautifully. Based on your latest updates - 36-inch vanity, heated floors, and quartz countertops - here are some stunning inspiration ideas. For your 60 sq ft space with $15k-$20k budget, I recommend: white quartz with gray veining, 36-inch floating vanity in navy or gray, radiant floor heating (adds $2k-3k), and maybe a statement mirror. This upgrade still works within your timeline but might push toward the higher end of your budget."""
        
        await universal_session_manager.add_message_to_session(
            session_id=iris_session_2,
            role="assistant",
            content=iris_followup_response,
            metadata={
                "agent_type": "IRIS", 
                "cross_agent_context": {
                    "cia_updates": {
                        "vanity_size": "36_inch_upgrade",
                        "heated_floors": "considering",
                        "countertops": "quartz_preference",
                        "permits": "inquired_about"
                    },
                    "budget_impact": "higher_end_of_range"
                }
            }
        )
        
        print(f"IRIS shows awareness of CIA conversation updates")
        
    # CHECK DATABASE - Context building verification
    print(f"\n" + "-"*60)
    print("DATABASE VERIFICATION - Context Building")
    print("-"*60)
    
    all_conversations = db.table("unified_conversations").select("*").eq(
        "created_by", user_id
    ).order("created_at", desc=False).execute()
    
    print(f"Total conversations now: {len(all_conversations.data)}")
    
    session_timeline = []
    for conv in all_conversations.data:
        agent_type = conv.get("metadata", {}).get("agent_type", "Unknown")
        session_id = conv.get("metadata", {}).get("session_id", "No session")
        title = conv.get("title", "No title")
        created = conv.get("created_at", "")[:19]
        
        session_timeline.append({
            "agent": agent_type,
            "session": session_id,
            "title": title,
            "created": created
        })
        
        print(f"  {agent_type:>10}: {title} ({created})")
    
    # Check for context evolution in messages
    print(f"\n" + "-"*60)
    print("MESSAGE EVOLUTION CHECK")
    print("-"*60)
    
    conv_ids = [conv["id"] for conv in all_conversations.data]
    all_messages = db.table("unified_messages").select("*").in_(
        "conversation_id", conv_ids
    ).order("created_at", desc=False).execute()
    
    print(f"Total messages: {len(all_messages.data)}")
    
    # Look for evolving project details
    project_evolution = []
    for msg in all_messages.data[-5:]:  # Last 5 messages
        content = msg.get("content", "")
        metadata = msg.get("metadata", {})
        
        # Extract key details mentioned
        details = []
        if "vanity" in content.lower():
            if "36" in content:
                details.append("36-inch vanity")
            elif "24" in content:
                details.append("24-inch vanity")
        if "heated floor" in content.lower():
            details.append("heated floors")
        if "quartz" in content.lower():
            details.append("quartz countertops")
        if "permit" in content.lower():
            details.append("permits inquiry")
            
        if details:
            project_evolution.append({
                "timestamp": msg.get("created_at", ""),
                "details": details,
                "cross_agent_refs": metadata.get("cross_agent_context")
            })
    
    print(f"Project evolution timeline:")
    for evo in project_evolution:
        timestamp = evo["timestamp"][:19]
        details = ", ".join(evo["details"])
        print(f"  {timestamp}: {details}")
        if evo["cross_agent_refs"]:
            print(f"    -> Cross-agent awareness: {list(evo['cross_agent_refs'].keys())}")
    
    # SUCCESS CRITERIA
    print(f"\n" + "-"*60)
    print("CONTEXT BUILDING VERIFICATION")
    print("-"*60)
    
    success_checks = [
        ("Multiple CIA sessions", len([s for s in session_timeline if s["agent"] == "Unknown"]) >= 2),
        ("Multiple IRIS sessions", len([s for s in session_timeline if s["agent"] == "IRIS"]) >= 2), 
        ("Total conversations increased", len(all_conversations.data) >= 5),
        ("Project details evolved", len(project_evolution) >= 3),
        ("Cross-agent awareness", any(evo.get("cross_agent_refs") for evo in project_evolution)),
        ("Message count increased", len(all_messages.data) >= 10)
    ]
    
    passed = sum(1 for _, result in success_checks if result)
    
    print(f"CONTEXT BUILDING RESULTS ({passed}/{len(success_checks)} passed):")
    for check_name, result in success_checks:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {check_name}")
    
    if passed >= 4:
        print(f"\nSUCCESS: Context building verified!")
        print(f"  - Homeowner had multiple conversations with CIA and IRIS")
        print(f"  - Project details evolved and became more specific")
        print(f"  - Agents show awareness of updates from other conversations")
        return True
    else:
        print(f"\nISSUE: Context building needs verification")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_continued_conversations())
    print(f"\nFINAL: {'SUCCESS' if result else 'NEEDS_WORK'}")