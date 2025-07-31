#!/usr/bin/env python3
"""
Demonstrate CIA conversation patterns with different user personas
"""

import time
from datetime import datetime

def print_conversation_turn(turn_num, user_name, user_message, agent_response, response_time, phase, ready_for_jaa, collected_info):
    """Print a conversation turn with all details"""
    print(f"\n{'='*80}")
    print(f"TURN {turn_num} - {datetime.now().strftime('%I:%M:%S %p')}")
    print(f"{'='*80}")
    print(f"\nUSER ({user_name}): {user_message}")
    print(f"\nCIA AGENT: {agent_response}")
    print(f"\n[Response Time: {response_time} seconds]")
    print(f"[Phase: {phase}]") 
    print(f"[Ready for JAA: {ready_for_jaa}]")
    if collected_info:
        print(f"[Collected: {', '.join(collected_info)}]")

def demonstrate_conversations():
    """Demonstrate different conversation styles with CIA"""
    
    print("CIA MULTI-TURN CONVERSATION DEMONSTRATION")
    print("=" * 80)
    print("Showing different user personas and how CIA adapts")
    print("=" * 80)
    
    # CONVERSATION 1: Direct Professional
    print(f"\n{'='*80}")
    print("PERSONA 1: Sarah Chen - Busy Tech Executive")
    print("Profile: Direct, time-conscious, clear about needs")
    print(f"{'='*80}")
    
    conversation1 = [
        {
            "user": "Hi, I need someone to fix my garage door. It's making grinding noises.",
            "agent": "Hi there! I'm Alex from InstaBids, and I'd be happy to help you get that garage door fixed. Those grinding noises can definitely be concerning - nobody wants to get stuck with a door that won't open!\n\nLet me ask a few quick questions to make sure we connect you with the right repair specialists:\n\nFirst, is the door still opening and closing despite the grinding noise, or has it stopped working entirely? And how long has this been going on?\n\nAlso, what's your zip code? This helps us find contractors who service your area and can get to you quickly.\n\nThe great thing about InstaBids is we don't charge contractors for leads like other platforms do, so they can offer you better prices - typically 10-20% less than you'd find elsewhere.",
            "time": 11.2,
            "phase": "details",
            "ready": False,
            "collected": []
        },
        {
            "user": "I'm in Austin, TX 78704. It's a double garage door, probably 10 years old. Still works but the noise is awful.",
            "agent": "Perfect, Austin 78704 - great area! And good that it's still functioning, that usually means we caught it before major damage.\n\nA 10-year-old double garage door making grinding noises is often due to worn rollers, dry tracks, or spring issues. The good news is these are typically straightforward repairs.\n\nA couple more quick questions:\n- When does the grinding happen - throughout the entire opening/closing cycle, or just at certain points?\n- Do you have a budget in mind for the repair? This helps me connect you with contractors in the right range.\n- How urgently do you need this fixed? Can it wait a few days or do you need someone ASAP?",
            "time": 9.8,
            "phase": "budget",
            "ready": False,
            "collected": ["location_zip", "project_type"]
        },
        {
            "user": "Throughout the cycle. Budget around $500-800. Need it this week - I work from home and it's disruptive.",
            "agent": "Ah, that makes total sense - grinding noises during work calls would drive anyone crazy! The good news is that most garage door repairs fall well within your $500-800 budget, and getting it done this week is definitely doable.\n\nSince you work from home, our contractors can usually work around your schedule. Many can even give you a heads up about the noisiest parts of the repair so you can plan calls accordingly.\n\nWould you be able to snap a quick photo of the tracks/rollers on one side? This helps contractors diagnose remotely and often bring the right parts on the first visit.\n\nAlso, what's the best way for contractors to reach you - phone, email, or text?",
            "time": 10.3,
            "phase": "contact",
            "ready": True,
            "collected": ["location_zip", "project_type", "budget_min", "budget_max", "urgency_level"]
        },
        {
            "user": "Email works best. sarah.chen@techcorp.com. I'll skip the photos - just need someone reliable.",
            "agent": "Perfect! I completely understand - you need this handled efficiently.\n\nHere's what happens next:\n- I'll get your project to our network of garage door specialists in Austin 78704\n- You'll receive emails from 3-4 qualified contractors (usually within 2-4 hours)\n- They'll provide quotes and availability for this week\n- You choose who you're most comfortable with\n\nTo summarize:\n- Double garage door repair (grinding noise throughout cycle)\n- Budget: $500-800\n- Timeline: This week\n- Location: Austin 78704\n- Contact: sarah.chen@techcorp.com\n\nI'll mark this as urgent so contractors with immediate availability prioritize reaching out. Anything else I should know?",
            "time": 11.5,
            "phase": "ready",
            "ready": True,
            "collected": ["location_zip", "project_type", "budget_min", "budget_max", "urgency_level", "email"]
        }
    ]
    
    for i, turn in enumerate(conversation1, 1):
        print_conversation_turn(
            i, 
            "Sarah Chen",
            turn["user"],
            turn["agent"],
            turn["time"],
            turn["phase"],
            turn["ready"],
            turn["collected"]
        )
        time.sleep(0.5)
    
    # CONVERSATION 2: Anxious First-Timer
    print(f"\n\n{'='*80}")
    print("PERSONA 2: Maria Rodriguez - Anxious First-Time Homeowner")
    print("Profile: Uncertain, needs reassurance, worried about costs")
    print(f"{'='*80}")
    
    conversation2 = [
        {
            "user": "Hi... I think I have a problem with my roof? I'm not really sure.",
            "agent": "Hi there! I'm Alex from InstaBids, and I'm here to help you figure out what's going on with your roof. Don't worry - we'll work through this together!\n\nRoof issues can definitely be stressful, especially when you're not sure what you're dealing with. Let me ask you a few questions to help us understand the situation:\n\nWhat made you think there might be a problem? Are you seeing:\n- Water stains on your ceiling?\n- Missing or damaged shingles?\n- Leaks when it rains?\n- Or something else?\n\nThere's no such thing as a silly concern when it comes to your home, so feel free to describe whatever you've noticed!",
            "time": 12.1,
            "phase": "details",
            "ready": False,
            "collected": []
        },
        {
            "user": "There's a water stain on my bedroom ceiling and it's getting bigger when it rains. This is my first house and I don't know what to do.",
            "agent": "I completely understand how overwhelming this must feel, especially as a first-time homeowner! The good news is you're doing exactly the right thing by addressing this now.\n\nA water stain that grows when it rains definitely indicates a leak, but many roof leaks are actually quite fixable. You've caught it early, which is great - that usually means less damage and lower repair costs.\n\nLet me help you through this step by step:\n\n1. First, where are you located? (Just need your zip code)\n2. Do you know approximately how old your roof is?\n3. Is the stain directly below the attic, or is there another floor above?\n\nAnd please don't worry - I'll explain everything clearly and make sure you understand your options. That's what we're here for!",
            "time": 13.5,
            "phase": "details",
            "ready": False,
            "collected": ["project_type", "urgency_reason"]
        },
        {
            "user": "Phoenix, AZ 85016. The house is 15 years old so I guess the roof is too? It's right below the attic.",
            "agent": "Perfect, that helps a lot! Phoenix 85016 - and yes, a 15-year-old roof in Arizona is actually pretty common for starting to need some attention. The intense sun here can be tough on roofing materials.\n\nThe fact that it's right below the attic is actually good news - that usually makes repairs more straightforward since roofers can access it easily.\n\nHere's what I want you to know:\n- In Phoenix, most roof repairs for issues like this range from $300-1,500\n- Full replacements are much more (we're talking $8,000+), but that's usually not needed for a single leak\n- Most contractors can temporarily patch it quickly, then do permanent repairs\n\nTwo important questions:\n1. Do you have a budget in mind, even a rough idea? This helps me match you with the right contractors\n2. Has the leak caused any damage inside beyond the stain? (Dripping water, soggy drywall, etc.)\n\nAnd remember - every homeowner goes through this. You're handling it perfectly by getting help before it gets worse!",
            "time": 14.2,
            "phase": "budget",
            "ready": False,
            "collected": ["project_type", "urgency_reason", "location_zip", "property_details"]
        }
    ]
    
    for i, turn in enumerate(conversation2, 1):
        print_conversation_turn(
            i,
            "Maria Rodriguez",
            turn["user"],
            turn["agent"],
            turn["time"],
            turn["phase"],
            turn["ready"],
            turn["collected"]
        )
        time.sleep(0.5)
    
    # ANALYSIS SUMMARY
    print(f"\n\n{'='*80}")
    print("CONVERSATION ANALYSIS")
    print(f"{'='*80}")
    
    print("\nKEY OBSERVATIONS:")
    print("\n1. RESPONSE TIME PATTERNS:")
    print("   - Initial responses: 11-14 seconds (include introduction)")
    print("   - Follow-up responses: 9-13 seconds")
    print("   - Complex explanations: 13-14 seconds")
    
    print("\n2. ADAPTATION TO USER STYLE:")
    print("   - Professional (Sarah): Direct, efficient, bullet points")
    print("   - Anxious (Maria): Reassuring, educational, step-by-step")
    
    print("\n3. INFORMATION GATHERING PHASES:")
    print("   - Phase 1 (details): Project type, basic situation")
    print("   - Phase 2 (budget): Location, urgency, budget range")
    print("   - Phase 3 (contact): Contact preferences, final details")
    print("   - Phase 4 (ready): Confirmation, ready for JAA")
    
    print("\n4. INSTABIDS VALUE PROPS MENTIONED:")
    print("   - 10-20% cost savings (no lead fees)")
    print("   - Quick contractor connections")
    print("   - Multiple quotes for comparison")
    print("   - Education and guidance")
    
    print("\n5. CONVERSATION LENGTH:")
    print("   - Efficient users: 3-4 turns to ready")
    print("   - Anxious users: 5-6 turns to ready")
    print("   - Average time: 3-5 minutes total")

if __name__ == "__main__":
    demonstrate_conversations()