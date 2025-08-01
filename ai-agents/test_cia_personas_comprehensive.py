"""
Comprehensive CIA Agent Persona Testing
Tests different personalities, projects, and memory persistence
"""
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cia.agent import CustomerInterfaceAgent
from datetime import datetime
import json

# Test personas with different characteristics
PERSONAS = {
    "emergency": {
        "name": "Sarah (Emergency)",
        "scenario": "Roof is leaking after storm",
        "messages": [
            "Help! My roof is leaking water into my bedroom after that storm last night",
            "It's dripping pretty badly, I have buckets catching water",
            "I'm in zip code 78704, can you help me find someone quickly?",
            "Yes I need this fixed ASAP before more rain comes"
        ],
        "expected_behavior": {
            "no_budget_push": True,  # Should NOT ask for budget in emergency
            "quick_to_essentials": True,  # Should get to core info fast
            "group_bidding": False,  # Should NOT suggest group bidding
            "urgency_recognition": True  # Should recognize emergency
        }
    },
    
    "explorer": {
        "name": "Mike (Explorer)",
        "scenario": "Just researching kitchen remodel costs",
        "messages": [
            "I'm thinking about maybe doing a kitchen remodel sometime",
            "Just trying to get an idea of what things cost these days",
            "Not in any rush, maybe next year or something",
            "What information would you need to give me a rough idea?"
        ],
        "expected_behavior": {
            "no_budget_push": True,  # Should explore stage, not push for numbers
            "educational": True,  # Should be more conversational/educational
            "group_bidding": True,  # Could mention for future planning
            "planning_focus": True  # Should focus on research/planning stage
        }
    },
    
    "group_opportunity": {
        "name": "Linda (Group Bidding)",
        "scenario": "Lawn care with flexible timing",
        "messages": [
            "I need someone for regular lawn care service",
            "My grass is getting pretty long but it's not urgent",
            "I'm in a neighborhood with lots of similar sized yards",
            "Monthly service would be ideal, starting whenever"
        ],
        "expected_behavior": {
            "no_budget_push": True,  # Should focus on value, not ask for budget
            "group_bidding": True,  # MUST mention group pricing opportunity
            "value_focus": True,  # Should emphasize 15-25% savings
            "timing_flexible": True  # Should recognize flexibility
        }
    },
    
    "budget_conscious": {
        "name": "Dave (Budget Conscious)",
        "scenario": "Mentions budget concerns naturally",
        "messages": [
            "I need to replace my water heater but money is tight",
            "The old one is making weird noises and barely heating",
            "I've been saving up but probably only have about 2 grand",
            "Is that even enough? I have no idea what these cost"
        ],
        "expected_behavior": {
            "no_budget_push": True,  # Already gave budget, don't push
            "acknowledge_budget": True,  # Should work with mentioned budget
            "value_emphasis": True,  # Should emphasize InstaBids savings
            "helpful_response": True  # Should be reassuring about budget
        }
    }
}

async def test_persona(cia, persona_key, persona_data):
    """Test CIA with a specific persona"""
    print(f"\n{'='*60}")
    print(f"TESTING PERSONA: {persona_data['name']}")
    print(f"Scenario: {persona_data['scenario']}")
    print(f"{'='*60}")
    
    # Create unique session for this persona
    user_id = f"test_user_{persona_key}_{datetime.now().timestamp()}"
    session_id = f"test_session_{persona_key}_{datetime.now().timestamp()}"
    
    results = {
        "responses": [],
        "behavior_checks": {},
        "memory_persistence": False,
        "avoided_budget_push": True
    }
    
    # Send all messages for this persona
    for i, message in enumerate(persona_data["messages"]):
        print(f"\n[Turn {i+1}] User: {message}")
        
        result = await cia.handle_conversation(
            user_id=user_id,
            message=message,
            session_id=session_id
        )
        
        response = result['response']
        print(f"[Turn {i+1}] CIA: {response[:200]}...")
        
        results["responses"].append(response)
        
        # Check for pushy budget questions
        response_lower = response.lower()
        if any(phrase in response_lower for phrase in [
            "what's your budget",
            "what is your budget", 
            "budget range",
            "how much are you looking to spend",
            "what are you hoping to spend"
        ]):
            results["avoided_budget_push"] = False
            print("❌ FAILED: Asked for budget directly!")
    
    # Analyze behavior against expectations
    all_responses = " ".join(results["responses"]).lower()
    expected = persona_data["expected_behavior"]
    
    # Check each expected behavior
    if expected.get("no_budget_push"):
        results["behavior_checks"]["no_budget_push"] = results["avoided_budget_push"]
    
    if expected.get("quick_to_essentials"):
        # Check if first response mentions getting help quickly
        quick_phrases = ["right away", "immediately", "quickly", "asap", "emergency", "urgent"]
        results["behavior_checks"]["quick_to_essentials"] = any(
            phrase in results["responses"][0].lower() for phrase in quick_phrases
        )
    
    if expected.get("group_bidding") is not None:
        # Check if group bidding was mentioned appropriately
        group_phrases = ["group", "neighbor", "bulk", "together", "15-25%", "15%", "25%"]
        mentioned = any(phrase in all_responses for phrase in group_phrases)
        results["behavior_checks"]["group_bidding_appropriate"] = (
            mentioned == expected["group_bidding"]
        )
    
    if expected.get("urgency_recognition"):
        # Check if urgency was recognized
        urgent_phrases = ["urgent", "emergency", "right away", "asap", "quickly"]
        results["behavior_checks"]["urgency_recognized"] = any(
            phrase in all_responses for phrase in urgent_phrases
        )
    
    if expected.get("educational"):
        # Check for educational/exploratory tone
        educational_phrases = ["explore", "research", "planning", "considering", "information"]
        results["behavior_checks"]["educational_approach"] = any(
            phrase in all_responses for phrase in educational_phrases
        )
    
    if expected.get("planning_focus"):
        # Check for planning stage questions
        planning_phrases = ["gotten quotes", "researching", "planning", "exploring", "stage"]
        results["behavior_checks"]["planning_focus"] = any(
            phrase in all_responses for phrase in planning_phrases
        )
    
    # Test memory persistence - send follow-up message
    print(f"\n[Memory Test] Sending follow-up after brief pause...")
    await asyncio.sleep(1)
    
    memory_result = await cia.handle_conversation(
        user_id=user_id,
        message="What were we just discussing?",
        session_id=session_id
    )
    
    memory_response = memory_result['response'].lower()
    
    # Check if key details are remembered
    if persona_key == "emergency":
        results["memory_persistence"] = "roof" in memory_response and "leak" in memory_response
    elif persona_key == "explorer":
        results["memory_persistence"] = "kitchen" in memory_response
    elif persona_key == "group_opportunity":
        results["memory_persistence"] = "lawn" in memory_response
    elif persona_key == "budget_conscious":
        results["memory_persistence"] = "water heater" in memory_response
    
    return results

async def test_multi_project_memory(cia):
    """Test memory across multiple projects for same user"""
    print(f"\n{'='*60}")
    print("TESTING MULTI-PROJECT MEMORY")
    print(f"{'='*60}")
    
    user_id = f"test_multi_project_{datetime.now().timestamp()}"
    
    # Project 1: Kitchen remodel
    print("\n[Project 1] Starting kitchen remodel discussion...")
    session1 = f"session_kitchen_{datetime.now().timestamp()}"
    
    result1 = await cia.handle_conversation(
        user_id=user_id,
        message="I want to remodel my kitchen, probably spend around 50k",
        session_id=session1
    )
    print(f"Response: {result1['response'][:150]}...")
    
    # Project 2: Lawn care (should recognize it's a different project)
    print("\n[Project 2] Starting lawn care discussion...")
    session2 = f"session_lawn_{datetime.now().timestamp()}"
    
    result2 = await cia.handle_conversation(
        user_id=user_id,
        message="I also need someone for lawn care",
        session_id=session2
    )
    
    response2 = result2['response'].lower()
    print(f"Response: {result2['response'][:150]}...")
    
    # Check if AI recognizes this is in addition to kitchen project
    multi_project_aware = any(phrase in response2 for phrase in [
        "addition to", "kitchen", "also working on", "another project", "separate"
    ])
    
    # Go back to kitchen project
    print("\n[Back to Project 1] Returning to kitchen discussion...")
    result3 = await cia.handle_conversation(
        user_id=user_id,
        message="For the kitchen, I'm thinking quartz countertops",
        session_id=session1
    )
    
    response3 = result3['response'].lower()
    
    # Check if context is maintained
    kitchen_context_maintained = "kitchen" in response3 or "50" in response3
    
    return {
        "multi_project_aware": multi_project_aware,
        "context_maintained": kitchen_context_maintained
    }

async def main():
    """Run all persona tests"""
    print("CIA AGENT COMPREHENSIVE PERSONA TESTING")
    print("="*60)
    print("Testing conversational flow and memory persistence")
    print(f"Start time: {datetime.now()}")
    
    # Initialize CIA agent
    cia = CustomerInterfaceAgent(os.getenv('ANTHROPIC_API_KEY'))
    
    # Store all results
    all_results = {}
    
    # Test each persona
    for persona_key, persona_data in PERSONAS.items():
        results = await test_persona(cia, persona_key, persona_data)
        all_results[persona_key] = results
        await asyncio.sleep(2)  # Brief pause between personas
    
    # Test multi-project memory
    multi_project_results = await test_multi_project_memory(cia)
    all_results["multi_project"] = multi_project_results
    
    # Generate summary report
    print(f"\n{'='*60}")
    print("COMPREHENSIVE TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    # Persona results
    for persona_key, results in all_results.items():
        if persona_key == "multi_project":
            continue
            
        print(f"\n{PERSONAS[persona_key]['name']}:")
        print(f"  ✓ Avoided budget push: {'✅ PASS' if results['avoided_budget_push'] else '❌ FAIL'}")
        print(f"  ✓ Memory persistence: {'✅ PASS' if results['memory_persistence'] else '❌ FAIL'}")
        
        for check, passed in results["behavior_checks"].items():
            print(f"  ✓ {check}: {'✅ PASS' if passed else '❌ FAIL'}")
    
    # Multi-project results
    print(f"\nMulti-Project Memory:")
    print(f"  ✓ Recognizes multiple projects: {'✅ PASS' if all_results['multi_project']['multi_project_aware'] else '❌ FAIL'}")
    print(f"  ✓ Maintains project context: {'✅ PASS' if all_results['multi_project']['context_maintained'] else '❌ FAIL'}")
    
    # Overall summary
    print(f"\n{'='*60}")
    print("OVERALL ASSESSMENT:")
    
    total_checks = 0
    passed_checks = 0
    
    for persona_key, results in all_results.items():
        if persona_key == "multi_project":
            total_checks += 2
            passed_checks += sum([
                results['multi_project_aware'],
                results['context_maintained']
            ])
        else:
            total_checks += 2 + len(results["behavior_checks"])
            passed_checks += sum([
                results['avoided_budget_push'],
                results['memory_persistence']
            ]) + sum(results["behavior_checks"].values())
    
    success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"Passed {passed_checks}/{total_checks} checks ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("\n✅ SUCCESS: CIA agent demonstrates improved conversational flow!")
        print("   - Avoids pushy budget questions")
        print("   - Maintains memory across turns")
        print("   - Responds appropriately to different personas")
    elif success_rate >= 60:
        print("\n⚠️  PARTIAL SUCCESS: Some improvements needed")
    else:
        print("\n❌ NEEDS WORK: Significant issues with conversational flow")
    
    # Save detailed results
    with open('test_results_cia_personas.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDetailed results saved to test_results_cia_personas.json")

if __name__ == "__main__":
    asyncio.run(main())