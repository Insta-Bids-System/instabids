"""
Comprehensive CIA Agent Testing with Multiple Personas
Tests real multi-turn conversations with various homeowner types
Captures all dialogue, response times, and behavioral patterns
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os
import sys
from config.service_urls import get_backend_url

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test personas with realistic conversation flows
PERSONAS = [
    {
        "name": "Price Conscious Budget Seeker",
        "id": "price_conscious_01",
        "initial_message": "I need to remodel my bathroom but I'm on a really tight budget. How much do these things usually cost?",
        "characteristics": [
            "Asks about costs frequently",
            "Worried about hidden fees",
            "Comparison shops",
            "Needs reassurance about value"
        ],
        "conversation_prompts": [
            "But what about all the fees? I've heard contractors charge extra for everything",
            "Can I really save money compared to using Angie's List or HomeAdvisor?",
            "What if I just want a basic update, nothing fancy?",
            "How do I know the contractors won't overcharge me?",
            "Is there a way to get multiple bids to compare prices?",
            "What about payment plans or financing?",
            "Do you charge homeowners anything?",
            "How much do contractors pay you?",
            "What if the project goes over budget?",
            "Can I set a maximum budget that contractors have to work within?"
        ]
    },
    {
        "name": "Quality Focused Professional",
        "id": "quality_focused_01",
        "initial_message": "I'm looking to do a high-end kitchen renovation. I want top quality work and materials.",
        "characteristics": [
            "Values expertise and credentials",
            "Asks about contractor qualifications",
            "Wants premium materials",
            "Timeline flexible for quality"
        ],
        "conversation_prompts": [
            "How do you vet the contractors? Are they licensed and insured?",
            "I want someone who specializes in luxury kitchens, not just any contractor",
            "What about warranties and guarantees on the work?",
            "Can I see examples of their previous high-end projects?",
            "Do you have contractors who work with specific designer brands?",
            "How do you ensure quality control?",
            "What if I'm not satisfied with the work?",
            "Can contractors provide references?",
            "Do you have any master craftsmen or award-winning contractors?",
            "I'd rather pay more for someone really experienced"
        ]
    },
    {
        "name": "Emergency Urgent Repair",
        "id": "urgent_repair_01",
        "initial_message": "My water heater just burst and flooded my basement! I need help immediately!",
        "characteristics": [
            "Extremely time sensitive",
            "Stressed and anxious",
            "Needs immediate response",
            "Less price sensitive due to urgency"
        ],
        "conversation_prompts": [
            "Can someone come TODAY? Water is everywhere!",
            "I can't wait days for bids, I need this fixed NOW",
            "Do you have emergency contractors available?",
            "What's the fastest you can get someone here?",
            "I don't care about the cost, I just need this fixed",
            "My insurance company needs estimates ASAP",
            "Can contractors do emergency temporary fixes?",
            "Do you work with restoration companies?",
            "The damage is getting worse every hour",
            "Please, I really need help fast!"
        ]
    },
    {
        "name": "Curious InstaBids Browser",
        "id": "curious_browser_01",
        "initial_message": "I saw an ad for InstaBids. How exactly does this work?",
        "characteristics": [
            "Information gathering mode",
            "Asks about the platform",
            "Compares to competitors",
            "Not ready to commit"
        ],
        "conversation_prompts": [
            "So you're like Angie's List but different how?",
            "Why should I use InstaBids instead of just googling contractors?",
            "What makes you different from HomeAdvisor?",
            "Do I have to commit to anything?",
            "Can I just get information without contractors calling me?",
            "How do you make money if it's free for homeowners?",
            "Is this a new company? How long have you been around?",
            "What cities do you operate in?",
            "Can I think about it and come back later?",
            "Do you have an app or is it just a website?"
        ]
    },
    {
        "name": "Skeptical Veteran Homeowner",
        "id": "skeptical_veteran_01",
        "initial_message": "I've been burned by contractors before. Why should I trust your platform?",
        "characteristics": [
            "Had bad experiences",
            "Very cautious",
            "Asks tough questions",
            "Needs trust building"
        ],
        "conversation_prompts": [
            "I've had contractors ghost me after taking deposits. How do you prevent that?",
            "HomeAdvisor sent me terrible contractors. You're probably the same.",
            "This sounds too good to be true. What's the catch?",
            "How do I know these aren't just random contractors paying you for leads?",
            "What legal recourse do I have if something goes wrong?",
            "Do you actually verify licenses or just take their word?",
            "I bet you sell my information to telemarketers",
            "Contractors always lowball then add charges. How is this different?",
            "Why should I believe you're any better than the others?",
            "I'll probably just hire my neighbor's cousin instead"
        ]
    },
    {
        "name": "Tech Savvy Millennial",
        "id": "tech_savvy_01",
        "initial_message": "Hey! I want to convert my garage into a home office/gaming setup. Can you help?",
        "characteristics": [
            "Comfortable with technology",
            "Wants modern solutions",
            "Values efficiency",
            "Expects instant responses"
        ],
        "conversation_prompts": [
            "Can I do everything through the app?",
            "Do contractors send digital quotes or do I need paper?",
            "Can I video chat with contractors before hiring?",
            "Is there a way to track the project progress online?",
            "Do you integrate with smart home systems?",
            "Can I pay electronically?",
            "Is there a contractor rating system like Uber?",
            "How quickly do contractors usually respond?",
            "Can I schedule everything online?",
            "Do you have 3D design tools or AR previews?"
        ]
    },
    {
        "name": "Elderly Cautious Planner",
        "id": "elderly_cautious_01",
        "initial_message": "My daughter says I should update my house to age in place. I don't know where to start.",
        "characteristics": [
            "Needs gentle guidance",
            "Worried about being taken advantage of",
            "Prefers phone/in-person",
            "Needs simple explanations"
        ],
        "conversation_prompts": [
            "I'm not very good with computers. Do I have to do this online?",
            "Can someone help me understand what I need?",
            "I'm worried about contractors taking advantage of seniors",
            "My daughter wants to be involved. Can she help me?",
            "I need grab bars and ramps. Do you have specialists for that?",
            "Will contractors pressure me to buy things I don't need?",
            "Can I get references from other seniors who've used your service?",
            "I prefer to pay by check. Is that okay?",
            "How do I know if the price is fair?",
            "I need someone patient who can explain things clearly"
        ]
    },
    {
        "name": "Investor Property Flipper",
        "id": "investor_flipper_01",
        "initial_message": "I just bought a property to flip. Need full renovation, kitchen, 3 baths, flooring. What's your contractor network like?",
        "characteristics": [
            "Business minded",
            "Volume potential",
            "ROI focused",
            "Wants bulk deals"
        ],
        "conversation_prompts": [
            "I do 10-15 flips a year. Do you have volume discounts?",
            "What's the typical markup contractors charge through your platform?",
            "Can I work with the same crew on multiple properties?",
            "How fast can contractors typically turn around a full renovation?",
            "Do you have contractors who understand investment properties?",
            "What about commercial properties?",
            "Can I get preferred rates as a repeat customer?",
            "Do contractors offer investor pricing?",
            "How do you handle multiple simultaneous projects?",
            "What's your coverage in different markets?"
        ]
    }
]

class CIATestRunner:
    def __init__(self):
        self.base_url = get_backend_url()
        self.results = []
        self.session = None
        self.conversation_histories = {}  # Track full conversation histories
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def send_message(self, thread_id: str, message: str, turn_number: int) -> Dict[str, Any]:
        """Send a message to CIA and capture response with timing"""
        
        print(f"\n  Turn {turn_number} - User: {message[:100]}{'...' if len(message) > 100 else ''}")
        
        url = f"{self.base_url}/api/cia/stream"
        
        # Build messages history
        if thread_id not in self.conversation_histories:
            self.conversation_histories[thread_id] = []
        
        # Add current message to history
        self.conversation_histories[thread_id].append({"role": "user", "content": message})
        
        # Send full conversation history
        payload = {
            "messages": self.conversation_histories[thread_id].copy(),
            "conversation_id": thread_id,
            "user_id": f"test_user_{thread_id}"
        }
        
        start_time = time.time()
        response_text = ""
        trigger_detected = None
        error = None
        
        try:
            async with self.session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status != 200:
                    error = f"HTTP {response.status}: {await response.text()}"
                    print(f"    ERROR: {error}")
                    return {
                        "turn": turn_number,
                        "user_message": message,
                        "response": None,
                        "error": error,
                        "latency": time.time() - start_time,
                        "trigger": None
                    }
                
                # Process SSE stream
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if chunk.get('type') == 'content':
                                response_text += chunk.get('content', '')
                            elif chunk.get('type') == 'trigger':
                                trigger_detected = chunk.get('trigger')
                        except json.JSONDecodeError:
                            continue
                            
        except asyncio.TimeoutError:
            error = "Timeout after 120 seconds"
            print(f"    ERROR: {error}")
        except Exception as e:
            error = str(e)
            print(f"    ERROR: {error}")
            
        latency = time.time() - start_time
        
        # Add assistant response to history if successful
        if response_text and thread_id in self.conversation_histories:
            self.conversation_histories[thread_id].append({"role": "assistant", "content": response_text})
        
        # Print response preview
        if response_text:
            print(f"    CIA ({latency:.2f}s): {response_text[:150]}{'...' if len(response_text) > 150 else ''}")
            if trigger_detected:
                print(f"    TRIGGER: {trigger_detected}")
        
        return {
            "turn": turn_number,
            "user_message": message,
            "response": response_text,
            "error": error,
            "latency": latency,
            "trigger": trigger_detected
        }
        
    async def test_persona(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """Run a complete multi-turn conversation with a persona"""
        
        print(f"\n{'='*80}")
        print(f"Testing Persona: {persona['name']}")
        print(f"ID: {persona['id']}")
        print(f"Characteristics: {', '.join(persona['characteristics'])}")
        print(f"{'='*80}")
        
        thread_id = f"test_{persona['id']}_{int(time.time())}"
        conversation_history = []
        total_latency = 0
        triggers_detected = []
        bid_card_mentioned = False
        signup_prompted = False
        
        # Initial message
        turn = await self.send_message(thread_id, persona['initial_message'], 1)
        conversation_history.append(turn)
        total_latency += turn['latency']
        
        if turn['trigger']:
            triggers_detected.append((1, turn['trigger']))
            
        # Check for bid card or signup mentions
        if turn['response'] and 'bid card' in turn['response'].lower():
            bid_card_mentioned = True
        if turn['response'] and any(word in turn['response'].lower() for word in ['sign up', 'get started', 'create account']):
            signup_prompted = True
            
        # Continue conversation with persona-specific prompts
        for i, prompt in enumerate(persona['conversation_prompts'], start=2):
            # Add some variation - sometimes respond to what CIA said
            if conversation_history[-1]['response'] and i % 3 == 0:
                # Occasionally acknowledge and pivot
                acknowledgment = "That's interesting. " if i % 2 == 0 else "I see. "
                message = acknowledgment + prompt
            else:
                message = prompt
                
            turn = await self.send_message(thread_id, message, i)
            conversation_history.append(turn)
            total_latency += turn['latency']
            
            if turn['trigger']:
                triggers_detected.append((i, turn['trigger']))
                
            # Check for bid card or signup mentions
            if turn['response'] and 'bid card' in turn['response'].lower():
                bid_card_mentioned = True
            if turn['response'] and any(word in turn['response'].lower() for word in ['sign up', 'get started', 'create account']):
                signup_prompted = True
                
            # Stop if we hit an error
            if turn['error']:
                print(f"\n  Stopping due to error at turn {i}")
                break
                
            # Natural conversation flow - sometimes end early if we've covered everything
            if i >= 8 and bid_card_mentioned and signup_prompted:
                print(f"\n  Natural conversation end at turn {i} (key topics covered)")
                break
                
        # Generate summary
        successful_turns = len([t for t in conversation_history if t['response']])
        failed_turns = len([t for t in conversation_history if t['error']])
        avg_latency = total_latency / len(conversation_history) if conversation_history else 0
        
        print(f"\n{'-'*60}")
        print(f"CONVERSATION SUMMARY:")
        print(f"  Total Turns: {len(conversation_history)}")
        print(f"  Successful: {successful_turns}")
        print(f"  Failed: {failed_turns}")
        print(f"  Average Latency: {avg_latency:.2f}s")
        print(f"  Total Time: {total_latency:.2f}s")
        print(f"  Bid Card Mentioned: {'Yes' if bid_card_mentioned else 'No'}")
        print(f"  Signup Prompted: {'Yes' if signup_prompted else 'No'}")
        print(f"  Triggers Detected: {len(triggers_detected)}")
        if triggers_detected:
            for turn_num, trigger in triggers_detected:
                print(f"    Turn {turn_num}: {trigger}")
        
        return {
            "persona": persona['name'],
            "persona_id": persona['id'],
            "thread_id": thread_id,
            "conversation": conversation_history,
            "summary": {
                "total_turns": len(conversation_history),
                "successful_turns": successful_turns,
                "failed_turns": failed_turns,
                "avg_latency": avg_latency,
                "total_time": total_latency,
                "bid_card_mentioned": bid_card_mentioned,
                "signup_prompted": signup_prompted,
                "triggers": triggers_detected
            }
        }
        
    async def run_all_tests(self):
        """Run tests for all personas"""
        
        print("\n" + "="*80)
        print("COMPREHENSIVE CIA AGENT TESTING")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing {len(PERSONAS)} personas with unlimited conversation turns")
        print("="*80)
        
        for persona in PERSONAS:
            result = await self.test_persona(persona)
            self.results.append(result)
            
            # Brief pause between personas
            print(f"\n  Waiting 2 seconds before next persona...")
            await asyncio.sleep(2)
            
        # Generate final report
        self.generate_report()
        
    def generate_report(self):
        """Generate comprehensive test report"""
        
        print("\n" + "="*80)
        print("FINAL TEST REPORT")
        print("="*80)
        
        # Overall statistics
        total_turns = sum(r['summary']['total_turns'] for r in self.results)
        total_successful = sum(r['summary']['successful_turns'] for r in self.results)
        total_failed = sum(r['summary']['failed_turns'] for r in self.results)
        total_time = sum(r['summary']['total_time'] for r in self.results)
        
        print(f"\nOVERALL STATISTICS:")
        print(f"  Personas Tested: {len(self.results)}")
        print(f"  Total Conversation Turns: {total_turns}")
        print(f"  Successful Responses: {total_successful}")
        print(f"  Failed Responses: {total_failed}")
        print(f"  Total Test Time: {total_time:.2f}s")
        print(f"  Success Rate: {(total_successful/total_turns*100):.1f}%")
        
        # Per-persona analysis
        print(f"\nPER-PERSONA ANALYSIS:")
        for result in self.results:
            print(f"\n  {result['persona']}:")
            s = result['summary']
            print(f"    Turns: {s['total_turns']} (Success: {s['successful_turns']}, Fail: {s['failed_turns']})")
            print(f"    Avg Response Time: {s['avg_latency']:.2f}s")
            print(f"    Bid Card Mentioned: {'Yes' if s['bid_card_mentioned'] else 'No'}")
            print(f"    Signup Prompted: {'Yes' if s['signup_prompted'] else 'No'}")
            print(f"    Triggers: {', '.join([t[1] for t in s['triggers']]) if s['triggers'] else 'None'}")
            
        # Behavioral patterns
        print(f"\nBEHAVIORAL PATTERNS:")
        bid_card_rate = sum(1 for r in self.results if r['summary']['bid_card_mentioned']) / len(self.results) * 100
        signup_rate = sum(1 for r in self.results if r['summary']['signup_prompted']) / len(self.results) * 100
        
        print(f"  Bid Card Mention Rate: {bid_card_rate:.1f}%")
        print(f"  Signup Prompt Rate: {signup_rate:.1f}%")
        
        # Response time analysis
        all_latencies = []
        for result in self.results:
            for turn in result['conversation']:
                if turn['response']:
                    all_latencies.append(turn['latency'])
                    
        if all_latencies:
            avg_latency = sum(all_latencies) / len(all_latencies)
            min_latency = min(all_latencies)
            max_latency = max(all_latencies)
            
            print(f"\nRESPONSE TIME ANALYSIS:")
            print(f"  Average: {avg_latency:.2f}s")
            print(f"  Minimum: {min_latency:.2f}s")
            print(f"  Maximum: {max_latency:.2f}s")
            
        # Save detailed results to file
        report_file = f"cia_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "personas_tested": len(self.results),
                "total_turns": total_turns,
                "results": self.results
            }, f, indent=2)
            
        print(f"\nDetailed results saved to: {report_file}")
        print("="*80)

async def main():
    """Main test execution"""
    async with CIATestRunner() as runner:
        await runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())