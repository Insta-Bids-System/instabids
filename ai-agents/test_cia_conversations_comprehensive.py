#!/usr/bin/env python3
"""
Comprehensive CIA Agent Multi-Turn Conversation Testing
Tests different homeowner personas and conversation flows
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import aiohttp
from dataclasses import dataclass
from enum import Enum
from config.service_urls import get_backend_url

# Different homeowner personas
class HomeownerPersona(Enum):
    PRICE_CONSCIOUS = "price_conscious"
    QUALITY_FOCUSED = "quality_focused"
    URGENT_REPAIR = "urgent_repair"
    CURIOUS_BROWSER = "curious_browser"
    SKEPTICAL_VETERAN = "skeptical_veteran"
    TECH_SAVVY = "tech_savvy"
    ELDERLY_CAUTIOUS = "elderly_cautious"
    INVESTOR_MINDED = "investor_minded"

@dataclass
class ConversationTurn:
    persona: HomeownerPersona
    message: str
    response: str
    latency_ms: float
    triggers: List[str]  # What was triggered (education, bid_card, timeline_assessment, etc.)

class CIAConversationTester:
    def __init__(self):
        self.base_url = get_backend_url()
        self.conversations: Dict[HomeownerPersona, List[ConversationTurn]] = {}
        
    async def send_message(self, session_id: str, message: str, user_id: str = "test-user-001") -> tuple[str, float, List[str]]:
        """Send a message and get response with latency and trigger analysis"""
        start_time = time.time()
        
        payload = {
            "message": {"role": "user", "content": message},
            "session_id": session_id,
            "user_id": user_id,
            "images": []
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/cia/stream",
                    json=payload,
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    
                    full_response = ""
                    triggers = []
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if "choices" in data:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        full_response += delta["content"]
                            except json.JSONDecodeError:
                                continue
                    
                    # Analyze triggers in response
                    triggers = self.analyze_triggers(full_response)
                    
                    latency_ms = (time.time() - start_time) * 1000
                    return full_response, latency_ms, triggers
                    
        except Exception as e:
            print(f"Error sending message: {e}")
            return f"Error: {str(e)}", 0, []
    
    def analyze_triggers(self, response: str) -> List[str]:
        """Analyze what was triggered in the response"""
        triggers = []
        
        # Check for various triggers
        trigger_patterns = {
            "mission_education": ["$400 billion", "corporate", "local economy", "taking back"],
            "value_proposition": ["10-20%", "save", "no lead fees", "contractors pass"],
            "timeline_assessment": ["emergency", "urgent", "flexible", "timeline", "when do you need"],
            "contractor_tier": ["handyman", "owner-operator", "regional", "national", "size"],
            "group_bidding": ["group bidding", "15-25%", "additional savings", "flexible timeline"],
            "preview_bid_card": ["here's your", "project summary", "ready to activate"],
            "ai_capabilities": ["remember everything", "persistent", "photo", "multi-step"],
            "budget_inquiry": ["budget", "price range", "how much", "investment"],
            "photo_request": ["upload", "photo", "picture", "image", "show me"],
            "signup_prompt": ["create account", "sign up", "activate", "get started"]
        }
        
        response_lower = response.lower()
        for trigger_name, patterns in trigger_patterns.items():
            if any(pattern.lower() in response_lower for pattern in patterns):
                triggers.append(trigger_name)
        
        return triggers

    async def run_persona_conversation(self, persona: HomeownerPersona) -> List[ConversationTurn]:
        """Run a multi-turn conversation for a specific persona"""
        session_id = f"test-session-{persona.value}-{int(time.time())}"
        conversation = []
        
        # Get persona-specific conversation flow
        messages = self.get_persona_messages(persona)
        
        print(f"\n{'='*80}")
        print(f"Starting conversation for {persona.value.upper()} persona")
        print(f"{'='*80}")
        
        for i, message in enumerate(messages, 1):
            print(f"\n[Turn {i}] {persona.value}: {message}")
            
            response, latency, triggers = await self.send_message(session_id, message)
            
            turn = ConversationTurn(
                persona=persona,
                message=message,
                response=response,
                latency_ms=latency,
                triggers=triggers
            )
            conversation.append(turn)
            
            print(f"[CIA Response] ({latency:.0f}ms): {response[:200]}...")
            print(f"[Triggers]: {', '.join(triggers) if triggers else 'None'}")
            
            # Small delay between turns
            await asyncio.sleep(2)
        
        return conversation
    
    def get_persona_messages(self, persona: HomeownerPersona) -> List[str]:
        """Get conversation flow for each persona"""
        conversations = {
            HomeownerPersona.PRICE_CONSCIOUS: [
                "Hi, I need some work done but I'm on a tight budget",
                "It's a bathroom remodel but I can only spend about $5000",
                "How much can I really save with InstaBids?",
                "What if I'm flexible on timing? Can I save more?",
                "Ok show me what the bid card would look like"
            ],
            
            HomeownerPersona.QUALITY_FOCUSED: [
                "I'm looking for high-quality kitchen renovation",
                "I want premium materials and experienced contractors only",
                "Do you work with licensed and insured contractors?",
                "My budget is $50,000 and I want it done right",
                "What size contractor would you recommend for this?"
            ],
            
            HomeownerPersona.URGENT_REPAIR: [
                "HELP! My roof is leaking and it's raining!",
                "I need someone TODAY to fix this",
                "How fast can you get someone here?",
                "I don't care about the cost, just fix it",
                "Do you have emergency contractors?"
            ],
            
            HomeownerPersona.CURIOUS_BROWSER: [
                "What exactly is InstaBids?",
                "How is this different from Angie's List?",
                "Tell me more about the local economy thing",
                "Can you really do complex projects without a general contractor?",
                "What kind of projects can you help with?"
            ],
            
            HomeownerPersona.SKEPTICAL_VETERAN: [
                "I've been burned by contractors before",
                "How do I know these contractors are legitimate?",
                "What happens if the work isn't done right?",
                "This sounds too good to be true, what's the catch?",
                "How do you make money if contractors bid for free?"
            ],
            
            HomeownerPersona.TECH_SAVVY: [
                "I want to upload photos of my backyard for landscaping",
                "Can your AI analyze these and suggest projects?",
                "How does the persistent memory work?",
                "Can I manage multiple projects at once?",
                "Show me the tech behind this"
            ],
            
            HomeownerPersona.ELDERLY_CAUTIOUS: [
                "Hello, I need help with some home repairs",
                "I'm not very good with technology, is this complicated?",
                "I just need someone trustworthy to fix my fence",
                "Will I have to meet with lots of contractors?",
                "Can my daughter help me with this?"
            ],
            
            HomeownerPersona.INVESTOR_MINDED: [
                "I have 3 rental properties that need updating",
                "Can I get volume discounts for multiple projects?",
                "I need quick turnaround between tenants",
                "What about commercial properties?",
                "How does group bidding work exactly?"
            ]
        }
        
        return conversations.get(persona, [])
    
    async def run_all_tests(self):
        """Run all persona conversations"""
        print("\n" + "="*80)
        print("COMPREHENSIVE CIA AGENT CONVERSATION TESTING")
        print("Testing 8 different homeowner personas with multi-turn conversations")
        print("="*80)
        
        all_results = {}
        
        for persona in HomeownerPersona:
            conversation = await self.run_persona_conversation(persona)
            all_results[persona] = conversation
            
            # Longer delay between different personas
            await asyncio.sleep(5)
        
        # Generate comprehensive report
        self.generate_report(all_results)
        
        return all_results
    
    def generate_report(self, results: Dict[HomeownerPersona, List[ConversationTurn]]):
        """Generate comprehensive analysis report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE ANALYSIS REPORT")
        print("="*80)
        
        # Overall statistics
        total_turns = sum(len(conv) for conv in results.values())
        avg_latency = sum(turn.latency_ms for conv in results.values() for turn in conv) / total_turns
        
        print(f"\nOVERALL STATISTICS:")
        print(f"- Total conversations: {len(results)}")
        print(f"- Total turns: {total_turns}")
        print(f"- Average response latency: {avg_latency:.0f}ms")
        
        # Trigger frequency analysis
        trigger_counts = {}
        for conv in results.values():
            for turn in conv:
                for trigger in turn.triggers:
                    trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        print(f"\nTRIGGER FREQUENCY ANALYSIS:")
        for trigger, count in sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_turns) * 100
            print(f"- {trigger}: {count} times ({percentage:.1f}% of turns)")
        
        # Persona-specific analysis
        print(f"\nPERSONA-SPECIFIC INSIGHTS:")
        for persona, conversation in results.items():
            print(f"\n{persona.value.upper()}:")
            print(f"  Turns: {len(conversation)}")
            print(f"  Avg latency: {sum(t.latency_ms for t in conversation)/len(conversation):.0f}ms")
            
            # Most common triggers for this persona
            persona_triggers = {}
            for turn in conversation:
                for trigger in turn.triggers:
                    persona_triggers[trigger] = persona_triggers.get(trigger, 0) + 1
            
            if persona_triggers:
                top_triggers = sorted(persona_triggers.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"  Top triggers: {', '.join([f'{t[0]}({t[1]})' for t in top_triggers])}")
            
            # Check if bid card was offered
            bid_card_offered = any('preview_bid_card' in turn.triggers for turn in conversation)
            signup_prompted = any('signup_prompt' in turn.triggers for turn in conversation)
            print(f"  Bid card offered: {'Yes' if bid_card_offered else 'No'}")
            print(f"  Signup prompted: {'Yes' if signup_prompted else 'No'}")
        
        # Save detailed results to file
        self.save_detailed_results(results)
    
    def save_detailed_results(self, results: Dict[HomeownerPersona, List[ConversationTurn]]):
        """Save detailed conversation logs"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cia_conversation_analysis_{timestamp}.json"
        
        output = {
            "timestamp": timestamp,
            "conversations": {}
        }
        
        for persona, conversation in results.items():
            output["conversations"][persona.value] = [
                {
                    "turn": i + 1,
                    "user_message": turn.message,
                    "cia_response": turn.response,
                    "latency_ms": turn.latency_ms,
                    "triggers": turn.triggers
                }
                for i, turn in enumerate(conversation)
            ]
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nDetailed results saved to: {filename}")

async def main():
    tester = CIAConversationTester()
    results = await tester.run_all_tests()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())