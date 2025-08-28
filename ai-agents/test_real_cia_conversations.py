#!/usr/bin/env python3
"""
REAL CIA Agent Multi-Turn Conversation Testing
Tests actual CIA agent with natural conversation flows (NO artificial limits)
"""

import requests
import json
import time
from typing import List, Dict, Any
import uuid
from datetime import datetime
from config.service_urls import get_backend_url

class CIAConversationTester:
    def __init__(self):
        self.base_url = get_backend_url()
        self.session_data = {}  # Track conversation data
        
    def stream_to_cia(self, messages: List[Dict], conversation_id: str, user_id: str) -> Dict[str, Any]:
        """Send message to CIA agent and get complete response"""
        url = f"{self.base_url}/api/cia/stream"
        
        payload = {
            "messages": messages,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "max_tokens": 1000,
            "model_preference": "gpt-4o"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(url, json=payload, headers=headers, 
                                   stream=True, timeout=30)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": time.time() - start_time
                }
            
            # Parse SSE stream
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data_part = line_text[6:]  # Remove 'data: '
                        if data_part.strip() == '[DONE]':
                            break
                        try:
                            chunk_data = json.loads(data_part)
                            # Handle OpenAI streaming format
                            if 'choices' in chunk_data and chunk_data['choices']:
                                delta = chunk_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    full_response += delta['content']
                        except json.JSONDecodeError:
                            continue
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": True,
                "content": full_response.strip(),
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    def run_natural_conversation(self, persona_name: str, initial_message: str, 
                                follow_up_messages: List[str]) -> Dict[str, Any]:
        """Run a complete natural conversation with a persona"""
        
        conversation_id = f"test-{persona_name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:8]}"
        user_id = f"test-user-{persona_name.lower().replace(' ', '-')}"
        
        print(f"\n{'='*60}")
        print(f"TESTING PERSONA: {persona_name}")
        print(f"Conversation ID: {conversation_id}")
        print(f"User ID: {user_id}")
        print(f"{'='*60}")
        
        conversation_history = []
        full_dialogue = []
        
        # Start conversation
        messages = [{"role": "user", "content": initial_message}]
        
        print(f"\n[TURN 1] USER: {initial_message}")
        
        response_data = self.stream_to_cia(messages, conversation_id, user_id)
        
        if not response_data["success"]:
            print(f"FAILED: {response_data['error']}")
            return {
                "persona": persona_name,
                "success": False,
                "error": response_data["error"],
                "dialogue": full_dialogue
            }
        
        cia_response = response_data["content"]
        response_time = response_data["response_time"]
        
        print(f"[TURN 1] CIA ({response_time:.2f}s): {cia_response[:200]}{'...' if len(cia_response) > 200 else ''}")
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": initial_message})
        conversation_history.append({"role": "assistant", "content": cia_response})
        
        full_dialogue.append({
            "turn": 1,
            "user_message": initial_message,
            "cia_response": cia_response,
            "response_time": response_time,
            "timestamp": response_data["timestamp"]
        })
        
        # Continue with follow-up messages
        for turn_num, follow_up in enumerate(follow_up_messages, 2):
            print(f"\n[TURN {turn_num}] USER: {follow_up}")
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": follow_up})
            
            # Send entire conversation history to maintain context
            response_data = self.stream_to_cia(conversation_history, conversation_id, user_id)
            
            if not response_data["success"]:
                print(f"FAILED ON TURN {turn_num}: {response_data['error']}")
                full_dialogue.append({
                    "turn": turn_num,
                    "user_message": follow_up,
                    "cia_response": f"ERROR: {response_data['error']}",
                    "response_time": response_data["response_time"],
                    "timestamp": response_data.get("timestamp", "")
                })
                continue
            
            cia_response = response_data["content"]
            response_time = response_data["response_time"]
            
            print(f"[TURN {turn_num}] CIA ({response_time:.2f}s): {cia_response[:200]}{'...' if len(cia_response) > 200 else ''}")
            
            # Add CIA response to history
            conversation_history.append({"role": "assistant", "content": cia_response})
            
            full_dialogue.append({
                "turn": turn_num,
                "user_message": follow_up,
                "cia_response": cia_response,
                "response_time": response_time,
                "timestamp": response_data["timestamp"]
            })
            
            # Small delay between turns for natural conversation flow
            time.sleep(1)
        
        # Analyze conversation
        total_turns = len(full_dialogue)
        avg_response_time = sum(d["response_time"] for d in full_dialogue) / len(full_dialogue)
        
        # Look for triggers
        triggers_detected = self.analyze_triggers(full_dialogue)
        
        print(f"\nCONVERSATION SUMMARY:")
        print(f"   Total Turns: {total_turns}")
        print(f"   Avg Response Time: {avg_response_time:.2f}s")
        print(f"   Triggers Detected: {', '.join(triggers_detected) if triggers_detected else 'None'}")
        
        return {
            "persona": persona_name,
            "conversation_id": conversation_id,
            "success": True,
            "dialogue": full_dialogue,
            "total_turns": total_turns,
            "avg_response_time": avg_response_time,
            "triggers_detected": triggers_detected
        }
    
    def analyze_triggers(self, dialogue: List[Dict]) -> List[str]:
        """Analyze conversation for trigger patterns"""
        triggers = []
        
        for turn in dialogue:
            response = turn["cia_response"].lower()
            
            # Look for common triggers
            if "bid card" in response or "project card" in response:
                triggers.append("bid_card_mention")
            if "budget" in response and ("what's" in response or "range" in response):
                triggers.append("budget_inquiry")
            if "timeline" in response or "when do you" in response:
                triggers.append("timeline_assessment")
            if "contractor" in response and ("find" in response or "connect" in response):
                triggers.append("contractor_matching")
            if "group bidding" in response or "save money" in response:
                triggers.append("group_bidding_mention")
            if "emergency" in response or "urgent" in response:
                triggers.append("emergency_handling")
            if "value" in response and ("delivering" in response or "proposition" in response):
                triggers.append("value_proposition")
        
        return list(set(triggers))  # Remove duplicates

def main():
    """Run comprehensive CIA conversation testing"""
    tester = CIAConversationTester()
    
    print("STARTING REAL CIA CONVERSATION TESTING")
    print("Testing natural conversation flows with NO artificial limits")
    print("Each conversation will run until natural completion")
    
    # Define persona test cases with natural follow-up flows
    personas = [
        {
            "name": "Price Conscious Budget Seeker",
            "initial": "I need bathroom work but I'm on a tight budget, only $5000",
            "follow_ups": [
                "That sounds expensive. What if I do some of the work myself?",
                "Can you find contractors who work with tight budgets?",
                "How do I know I'm getting a fair price?",
                "What's the minimum I absolutely need to spend?",
                "Are there ways to save money on this project?"
            ]
        },
        {
            "name": "Emergency Urgent Repair",
            "initial": "HELP! My roof is leaking and it's raining!",
            "follow_ups": [
                "It's getting worse! Water is dripping into my living room!",
                "How quickly can you get someone here?",
                "I don't care about cost right now, I just need help",
                "Should I be doing anything to minimize damage?",
                "What if this happens again?"
            ]
        },
        {
            "name": "Curious InstaBids Browser",
            "initial": "What exactly is InstaBids and how is it different from Angie's List?",
            "follow_ups": [
                "How do you make money?",
                "What kind of contractors do you work with?",
                "Is this going to cost me anything?",
                "How do I know the contractors are good?",
                "What happens after I get quotes?"
            ]
        }
    ]
    
    all_results = []
    
    for persona in personas:
        result = tester.run_natural_conversation(
            persona["name"],
            persona["initial"],
            persona["follow_ups"]
        )
        all_results.append(result)
        
        # Brief pause between personas
        time.sleep(2)
    
    # Print final summary
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS")
    print(f"{'='*60}")
    
    for result in all_results:
        if result["success"]:
            print(f"\nSUCCESS: {result['persona']}")
            print(f"   Turns: {result['total_turns']}")
            print(f"   Avg Response Time: {result['avg_response_time']:.2f}s")
            print(f"   Triggers: {', '.join(result['triggers_detected']) if result['triggers_detected'] else 'None'}")
        else:
            print(f"\nFAILED: {result['persona']}: {result.get('error', 'Unknown error')}")
    
    print(f"\nTesting completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()