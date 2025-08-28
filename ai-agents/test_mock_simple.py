#!/usr/bin/env python3

import asyncio
import time

async def run_mock_persona_test():
    """Simple mock test showing what the real CIA conversation flow would look like"""
    
    print("MOCK CIA CONVERSATION TESTING")
    print("This demonstrates what we'll test once OpenAI API is fixed")
    print("=" * 60)
    
    persona = "Budget-Conscious Homeowner"
    turns = [
        "I need bathroom work but I'm on a tight budget, only $5000",
        "That sounds expensive. Are there ways to keep costs down?", 
        "What if I just do the essentials? Can you help me prioritize?",
        "Okay, can you create a bid card for basic bathroom updates under $5000?"
    ]
    
    mock_responses = [
        "I understand you're working with a $5,000 budget for bathroom work. That's completely achievable! Let me gather some details about your project.",
        "Absolutely! Focus on high-impact updates like vanity, fixtures, and paint rather than moving plumbing. This maximizes your budget.",
        "Smart approach! Let's prioritize: 1) Fix functional issues, 2) Update vanity/mirror for biggest visual impact, 3) New fixtures and paint.",
        "Perfect! I'm creating a bid card for 'Budget-Friendly Bathroom Update - $5,000 Maximum' targeting cost-effective contractors."
    ]
    
    print(f"\nTesting: {persona}")
    print("-" * 40)
    
    total_start = time.time()
    
    for i, (user_msg, cia_response) in enumerate(zip(turns, mock_responses), 1):
        turn_start = time.time()
        
        print(f"\n[Turn {i}] User: {user_msg}")
        
        # Simulate processing time
        await asyncio.sleep(0.2)
        
        turn_time = time.time() - turn_start
        
        print(f"[Turn {i}] CIA: {cia_response}")
        print(f"Response time: {turn_time:.2f}s")
        
        # Check for key triggers
        triggers = []
        if "bid card" in cia_response.lower():
            triggers.append("bid_card_creation")
        if "$5,000" in cia_response or "budget" in cia_response.lower():
            triggers.append("budget_awareness")
        if "prioritize" in cia_response.lower():
            triggers.append("guidance_provided")
        
        if triggers:
            print(f"Triggers: {', '.join(triggers)}")
    
    total_time = time.time() - total_start
    
    print(f"\nCONVERSATION COMPLETE")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average response time: {total_time/len(turns):.2f}s")
    print("\nKEY BEHAVIORS DEMONSTRATED:")
    print("- Budget awareness and sensitivity")  
    print("- Practical guidance and prioritization")
    print("- Natural progression to bid card creation")
    print("- Maintains helpful, non-pushy tone")
    
    print(f"\nNEXT STEPS:")
    print("1. Fix OpenAI API key issue")
    print("2. Test this exact conversation flow with real CIA agent")
    print("3. Run all 4 personas (Budget, Quality, Urgent, Curious)")
    print("4. Measure actual response times and conversation quality")
    print("5. Document any differences from expected behavior")

if __name__ == "__main__":
    asyncio.run(run_mock_persona_test())