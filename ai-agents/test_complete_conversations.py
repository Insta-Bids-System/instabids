#!/usr/bin/env python3
"""
Complete Multi-Turn Conversation Testing
Captures full dialogue, timing, flow analysis, and bid card progression
"""

import asyncio
import json
import time
import aiohttp
from datetime import datetime
from config.service_urls import get_backend_url

class ConversationTester:
    def __init__(self):
        self.base_url = get_backend_url()
    
    async def send_message(self, session_id, message):
        """Send message and capture full response with timing"""
        start_time = time.time()
        
        payload = {
            "messages": [{"role": "user", "content": message}],
            "conversation_id": session_id,
            "user_id": f"user-{session_id}",
            "max_tokens": 800,
            "model_preference": "gpt-5"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/cia/stream",
                    json=payload,
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        return f"ERROR {response.status}: {error_text}", 0
                    
                    full_response = ""
                    
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
                                pass
                    
                    latency = (time.time() - start_time) * 1000
                    return full_response, latency
                    
        except Exception as e:
            return f"EXCEPTION: {str(e)}", 0

    def analyze_response(self, response):
        """Analyze response for key behaviors and triggers"""
        analysis = {
            "triggers": [],
            "behaviors": [],
            "bid_card_progress": False,
            "education_provided": False,
            "questions_asked": [],
            "tone": "neutral"
        }
        
        response_lower = response.lower()
        
        # Check for triggers
        if "$400 billion" in response_lower or "corporate" in response_lower:
            analysis["triggers"].append("mission_education")
            analysis["education_provided"] = True
            
        if "10-20%" in response_lower or "save" in response_lower:
            analysis["triggers"].append("value_proposition")
            
        if "emergency" in response_lower or "urgent" in response_lower:
            analysis["triggers"].append("timeline_assessment")
            
        if "tier" in response_lower or "handyman" in response_lower or "owner-operator" in response_lower:
            analysis["triggers"].append("contractor_tier")
            
        if "group bidding" in response_lower or "15-25%" in response_lower:
            analysis["triggers"].append("group_bidding")
            
        if "bid card" in response_lower or "project summary" in response_lower:
            analysis["triggers"].append("bid_card_mention")
            analysis["bid_card_progress"] = True
            
        if "sign up" in response_lower or "create account" in response_lower:
            analysis["triggers"].append("signup_prompt")
        
        # Detect questions being asked
        questions = [line.strip() for line in response.split('\n') if '?' in line]
        analysis["questions_asked"] = questions[:3]  # Top 3 questions
        
        # Detect tone
        if "!" in response or "revolutionary" in response_lower or "excited" in response_lower:
            analysis["tone"] = "enthusiastic"
        elif "help" in response_lower and "understand" in response_lower:
            analysis["tone"] = "helpful"
        elif "sorry" in response_lower or "apologize" in response_lower:
            analysis["tone"] = "apologetic"
        
        return analysis

    async def run_persona_conversation(self, persona_name, messages):
        """Run complete multi-turn conversation for one persona"""
        session_id = f"persona-{persona_name}-{int(time.time())}"
        
        print(f"\n{'='*80}")
        print(f"COMPLETE CONVERSATION: {persona_name.upper()} PERSONA")
        print(f"Session: {session_id}")
        print(f"{'='*80}")
        
        conversation_log = []
        total_time = 0
        
        for turn, message in enumerate(messages, 1):
            print(f"\n[TURN {turn}] USER: {message}")
            
            response, latency = await self.send_message(session_id, message)
            analysis = self.analyze_response(response)
            total_time += latency
            
            print(f"[RESPONSE] ({latency:.0f}ms):")
            print(f"{response}")
            print(f"\n[ANALYSIS]")
            print(f"  Triggers: {', '.join(analysis['triggers']) if analysis['triggers'] else 'None'}")
            print(f"  Tone: {analysis['tone']}")
            print(f"  Questions Asked: {len(analysis['questions_asked'])}")
            if analysis['questions_asked']:
                for q in analysis['questions_asked']:
                    print(f"    - {q}")
            print(f"  Education Provided: {'Yes' if analysis['education_provided'] else 'No'}")
            print(f"  Bid Card Progress: {'Yes' if analysis['bid_card_progress'] else 'No'}")
            
            conversation_log.append({
                "turn": turn,
                "user_message": message,
                "response": response,
                "latency_ms": latency,
                "analysis": analysis
            })
            
            # Wait between turns to simulate real conversation
            await asyncio.sleep(2)
        
        # Final summary
        print(f"\n{'='*80}")
        print(f"CONVERSATION SUMMARY: {persona_name.upper()}")
        print(f"{'='*80}")
        print(f"Total Turns: {len(messages)}")
        print(f"Total Time: {total_time:.0f}ms")
        print(f"Avg Response Time: {total_time/len(messages):.0f}ms")
        
        # Analyze conversation flow
        all_triggers = []
        bid_card_mentioned = False
        education_count = 0
        
        for log in conversation_log:
            all_triggers.extend(log["analysis"]["triggers"])
            if log["analysis"]["bid_card_progress"]:
                bid_card_mentioned = True
            if log["analysis"]["education_provided"]:
                education_count += 1
        
        unique_triggers = list(set(all_triggers))
        
        print(f"Unique Triggers Hit: {', '.join(unique_triggers) if unique_triggers else 'None'}")
        print(f"Education Turns: {education_count}/{len(messages)}")
        print(f"Bid Card Mentioned: {'Yes' if bid_card_mentioned else 'No'}")
        
        return conversation_log

async def main():
    """Run complete conversation tests"""
    
    tester = ConversationTester()
    
    # Define persona conversation flows - 8-10 turns each with realistic progression
    personas = {
        "PRICE_CONSCIOUS": [
            "Hi, I need some work done but I'm on a tight budget",
            "It's a bathroom remodel but I can only spend about $5000", 
            "How much can I really save with InstaBids compared to other sites?",
            "What if I'm flexible on timing? Can I save even more?",
            "Tell me more about this group bidding thing",
            "How do I know the contractors are legitimate for such low prices?",
            "What information do you need from me to get started?",
            "Ok show me what the bid card would look like for my bathroom project"
        ],
        
        "URGENT_REPAIR": [
            "HELP! My roof is leaking and it's raining!",
            "I need someone TODAY to fix this leak",
            "How fast can you actually get contractors to respond?",
            "I don't care about the cost right now, I just need it fixed",
            "Do you have emergency contractors available?",
            "What do they need to know about the leak?",
            "How do I make sure they come out today?",
            "Create the emergency bid card right now please"
        ],
        
        "CURIOUS_BROWSER": [
            "What exactly is InstaBids?",
            "How is this different from Angie's List or HomeAdvisor?",
            "Tell me more about this local economy thing you mentioned",
            "So contractors really bid for free? What's the catch?",
            "Can you really handle complex projects without a general contractor?",
            "What kind of projects can you help with?",
            "How does this AI memory thing work?",
            "I'm interested but want to understand more before committing",
            "Show me an example of how this would work for a kitchen renovation"
        ]
    }
    
    print("COMPLETE MULTI-TURN CONVERSATION ANALYSIS")
    print("Testing 3 personas with 8-9 turns each")
    print("Capturing full dialogue, timing, and behavioral analysis")
    
    # Run each persona conversation
    for persona_name, messages in personas.items():
        await tester.run_persona_conversation(persona_name, messages)
        await asyncio.sleep(5)  # Pause between personas
    
    print(f"\n{'='*80}")
    print("ALL PERSONA CONVERSATIONS COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(main())