#!/usr/bin/env python3

import asyncio
import json
import uuid
import time
import aiohttp
from typing import List, Dict, Any

# Mock conversation personas with multi-turn dialogue simulation
PERSONAS = {
    "PRICE_CONSCIOUS": {
        "name": "Budget-Conscious Homeowner",
        "turns": [
            "I need bathroom work but I'm on a tight budget, only $5000",
            "That sounds expensive. Are there ways to keep costs down?", 
            "What if I just do the essentials? Can you help me prioritize?",
            "Okay, can you create a bid card for basic bathroom updates under $5000?"
        ]
    },
    "QUALITY_FOCUSED": {
        "name": "Quality-Focused Homeowner", 
        "turns": [
            "I want to remodel my master bathroom with high-end materials",
            "I care more about quality than price. What's the best approach?",
            "Can you help me find contractors who specialize in luxury bathrooms?",
            "Perfect. Let's create a bid card for a premium bathroom remodel"
        ]
    },
    "URGENT_REPAIR": {
        "name": "Emergency Repair",
        "turns": [
            "HELP! My roof is leaking and it's raining!",
            "How quickly can contractors come out? This is an emergency!",
            "I need someone TODAY. Cost doesn't matter right now.",
            "Yes, please get contractors out here ASAP!"
        ]
    },
    "CURIOUS_BROWSER": {
        "name": "Information Seeker",
        "turns": [
            "What exactly is InstaBids and how is it different from Angie's List?",
            "That's interesting. How do you ensure I get quality contractors?",
            "What if I just want to explore options without committing?",
            "Let me think about it. Can you show me how the process works?"
        ]
    }
}

async def simulate_cia_response(user_message: str, turn_number: int) -> str:
    """Simulate realistic CIA responses based on conversation context"""
    
    # Mock responses that would come from a working CIA agent
    responses = {
        1: {
            "budget": "I understand you're working with a $5,000 budget for bathroom work. That's completely achievable! I can help you find contractors who specialize in cost-effective bathroom updates. Let me gather some details about your project.",
            "quality": "Excellent choice focusing on quality for your master bathroom! High-end materials and craftsmanship make a huge difference. I'd love to help you find contractors who specialize in luxury bathroom remodels.",
            "urgent": "Oh no! A leaking roof is definitely an emergency, especially with rain coming down. I'm going to prioritize getting you emergency repair contractors right away. Let me start the process immediately.",
            "curious": "Great question! InstaBids is revolutionary - we cut out the $400 billion that middlemen like Angie's List extract from local economies. Instead of paying for leads, contractors compete directly for your project."
        },
        2: {
            "budget": "Absolutely! Here are some smart ways to maximize your $5,000 budget: Focus on high-impact updates like vanity, fixtures, and paint rather than moving plumbing. Would you like me to find contractors who specialize in budget-friendly transformations?",
            "quality": "Perfect mindset! Quality contractors will use premium materials like natural stone, high-end fixtures, and superior craftsmanship. I'll find contractors who have portfolios of luxury work. What's your timeline for this project?", 
            "urgent": "I'm treating this as a priority emergency. I'll target contractors who offer same-day emergency services. Are you able to be there to meet them, or do you need someone who can work with a key/access?",
            "curious": "Unlike other platforms, we use AI to intelligently match you with contractors based on your specific needs. We also group similar projects together so you get 15-25% savings through our group bidding system."
        },
        3: {
            "budget": "Smart approach! Let's prioritize: 1) Fix any functional issues first, 2) Update vanity/mirror for biggest visual impact, 3) New fixtures and paint. This keeps you in budget while maximizing transformation.",
            "quality": "Excellent! I'll find contractors who source from premium suppliers and have experience with high-end finishes. Many of our quality-focused contractors offer design consultation as part of their service.",
            "urgent": "I'm reaching out to our emergency response contractors now. Most can be on-site within 2-4 hours. I'm also looking for contractors who can provide temporary weather protection while planning permanent repairs.",
            "curious": "Exactly! Think of it as 'trying before buying.' I can show you our process by creating a sample project exploration. You'll see how contractors respond, their approach, and pricing without any commitment."
        },
        4: {
            "budget": "Perfect! I'm creating a bid card for 'Budget-Friendly Bathroom Update - $5,000 Maximum' focusing on essentials and high-impact changes. I'll target contractors who specialize in cost-effective renovations.",
            "quality": "Wonderful! I'm creating a premium bathroom remodel bid card emphasizing luxury materials and craftsmanship. I'll target our top-tier contractors who have extensive portfolios of high-end work.",
            "urgent": "I've created an EMERGENCY roof repair bid card with same-day service requirements. I'm reaching out to contractors who offer emergency response and can provide immediate weather protection.",
            "curious": "Great idea! I'll create a sample exploration for a typical home improvement project so you can see exactly how our process works - from initial matching through contractor responses and selection."
        }
    }
    
    # Determine response type based on message content
    message_lower = user_message.lower()
    if "budget" in message_lower or "$5000" in message_lower or "tight" in message_lower or "cheap" in message_lower:
        response_type = "budget"
    elif "quality" in message_lower or "high-end" in message_lower or "luxury" in message_lower or "premium" in message_lower:
        response_type = "quality" 
    elif "emergency" in message_lower or "urgent" in message_lower or "help" in message_lower or "leak" in message_lower:
        response_type = "urgent"
    else:
        response_type = "curious"
    
    # Get appropriate response for turn
    turn_responses = responses.get(turn_number, responses[4])  # Default to final turn
    return turn_responses.get(response_type, turn_responses["curious"])

async def run_mock_conversation(persona_key: str, persona_data: dict) -> dict:
    """Run a complete mock conversation for one persona"""
    
    print(f"\n{'='*60}")
    print(f"TESTING PERSONA: {persona_data['name']}")
    print('='*60)
    
    conversation_results = {
        "persona": persona_key,
        "name": persona_data["name"],
        "turns": [],
        "total_time": 0,
        "success": True,
        "triggers_detected": []
    }
    
    conversation_start = time.time()
    
    for turn_num, user_message in enumerate(persona_data["turns"], 1):
        turn_start = time.time()
        
        print(f"\n[Turn {turn_num}] User: {user_message}")
        
        # Simulate CIA response (this would normally come from the API)
        cia_response = await simulate_cia_response(user_message, turn_num)
        
        turn_time = time.time() - turn_start
        
        print(f"[Turn {turn_num}] CIA: {cia_response}")
        print(f"⏱️  Response time: {turn_time:.2f}s")
        
        # Analyze response for triggers
        triggers = []
        if "bid card" in cia_response.lower():
            triggers.append("bid_card_creation")
        if "$400 billion" in cia_response:
            triggers.append("mission_education")
        if "15-25%" in cia_response or "group bidding" in cia_response:
            triggers.append("group_bidding")
        if "emergency" in cia_response.lower() or "priority" in cia_response.lower():
            triggers.append("urgency_recognition")
        
        conversation_results["triggers_detected"].extend(triggers)
        
        conversation_results["turns"].append({
            "turn_number": turn_num,
            "user_message": user_message,
            "cia_response": cia_response,
            "response_time": turn_time,
            "triggers": triggers
        })
        
        # Small delay between turns
        await asyncio.sleep(0.5)
    
    conversation_results["total_time"] = time.time() - conversation_start
    
    print(f"\n📊 CONVERSATION SUMMARY:")
    print(f"   Total turns: {len(conversation_results['turns'])}")
    print(f"   Total time: {conversation_results['total_time']:.2f}s")
    print(f"   Triggers detected: {', '.join(set(conversation_results['triggers_detected']))}")
    
    return conversation_results

async def run_all_mock_conversations():
    """Run mock conversations for all personas to demonstrate the test flow"""
    
    print("🎭 MOCK CIA CONVERSATION TESTING")
    print("This simulates what the real conversations would look like")
    print("=" * 80)
    
    all_results = []
    
    for persona_key, persona_data in PERSONAS.items():
        try:
            results = await run_mock_conversation(persona_key, persona_data)
            all_results.append(results)
        except Exception as e:
            print(f"❌ Error testing {persona_key}: {e}")
    
    # Summary report
    print(f"\n{'='*80}")
    print("📋 TESTING SUMMARY REPORT")
    print('='*80)
    
    for result in all_results:
        print(f"\n✅ {result['name']}:")
        print(f"   Turns completed: {len(result['turns'])}/4")
        print(f"   Total time: {result['total_time']:.2f}s")
        print(f"   Average response time: {sum(t['response_time'] for t in result['turns'])/len(result['turns']):.2f}s")
        
        unique_triggers = set(result['triggers_detected'])
        print(f"   Key behaviors: {', '.join(unique_triggers) if unique_triggers else 'None detected'}")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Fix OpenAI API key to enable real CIA testing")
    print("2. Run actual API calls with these conversation flows")
    print("3. Compare real vs mock results for accuracy")
    print("4. Document any gaps in conversation handling")

if __name__ == "__main__":
    asyncio.run(run_all_mock_conversations())