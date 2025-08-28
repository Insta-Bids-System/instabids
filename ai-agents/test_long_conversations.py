#!/usr/bin/env python3
"""
Long-running conversation tests to verify CIA agent business logic:
1. Group bidding opportunity detection and promotion
2. Emergency vs planned project handling
3. Budget context exploration (NOT amounts)
4. Service type classification intelligence
5. Cross-conversation memory and context
"""

import requests
import json
import time
import uuid

class CIAConversationTester:
    def __init__(self):
        self.base_url = "http://localhost:8008/api/cia/stream"
        self.conversation_count = 0
        
    def send_message(self, messages, user_id, conversation_id):
        """Send message and get streaming response"""
        payload = {
            "messages": messages,
            "user_id": user_id,
            "conversation_id": conversation_id
        }
        
        try:
            response = requests.post(self.base_url, json=payload, stream=True, timeout=45)
            if response.status_code != 200:
                print(f"ERROR: Status {response.status_code}")
                return ""
                
            full_response = ""
            print("AI: ", end="", flush=True)
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str.strip() != '[DONE]':
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    content = data['choices'][0].get('delta', {}).get('content', '')
                                    full_response += content
                                    print(content, end='', flush=True)
                            except json.JSONDecodeError:
                                pass
            
            print()  # New line after response
            return full_response
            
        except Exception as e:
            print(f"ERROR: {e}")
            return ""

    def test_group_bidding_conversation(self):
        """Test 8-turn conversation about lawn work to trigger group bidding"""
        print("\n" + "="*60)
        print("TEST 1: GROUP BIDDING DETECTION (Lawn Installation)")
        print("="*60)
        
        user_id = str(uuid.uuid4())
        conv_id = f"group-bidding-{self.conversation_count}"
        self.conversation_count += 1
        
        conversation = []
        
        # Turn 1: Initial request
        print("\nUser: I want to replace my front yard with synthetic grass")
        conversation.append({"role": "user", "content": "I want to replace my front yard with synthetic grass"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 2: Provide location 
        print("\nUser: I'm in 90210, Beverly Hills area")
        conversation.append({"role": "user", "content": "I'm in 90210, Beverly Hills area"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 3: Show flexibility (key for group bidding)
        print("\nUser: I'm flexible on timing, maybe spring or summer, whenever works best")
        conversation.append({"role": "user", "content": "I'm flexible on timing, maybe spring or summer, whenever works best"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 4: Mention neighbors (should reinforce group bidding)
        print("\nUser: Actually, I think some of my neighbors have been looking at doing the same thing")
        conversation.append({"role": "user", "content": "Actually, I think some of my neighbors have been looking at doing the same thing"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 5: Ask about cost savings
        print("\nUser: Would doing it together save money?")
        conversation.append({"role": "user", "content": "Would doing it together save money?"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        # Analyze conversation for group bidding mentions
        full_conversation = " ".join([msg["content"] for msg in conversation if msg["role"] == "assistant"])
        group_mentions = full_conversation.lower()
        
        group_keywords = ['group', 'neighbors', 'coordinate', 'bulk', '15-25%', 'extra savings', 'together', 'neighborhood']
        detected_keywords = [kw for kw in group_keywords if kw in group_mentions]
        
        print(f"\n--- GROUP BIDDING ANALYSIS ---")
        print(f"Keywords detected: {detected_keywords}")
        print(f"Group bidding mentioned: {'YES' if detected_keywords else 'NO'}")
        
        if detected_keywords:
            print("✅ SUCCESS: Group bidding logic working in long conversation!")
            return True
        else:
            print("❌ FAILED: Group bidding not promoted for flexible lawn project")
            return False

    def test_emergency_vs_planned_conversation(self):
        """Test emergency detection and appropriate response urgency"""
        print("\n" + "="*60)
        print("TEST 2: EMERGENCY VS PLANNED PROJECT HANDLING")
        print("="*60)
        
        user_id = str(uuid.uuid4())
        conv_id = f"emergency-{self.conversation_count}"
        self.conversation_count += 1
        
        conversation = []
        
        # Turn 1: Emergency situation
        print("\nUser: HELP! My basement is flooding, the sump pump failed and water is coming in fast!")
        conversation.append({"role": "user", "content": "HELP! My basement is flooding, the sump pump failed and water is coming in fast!"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 2: Location for emergency
        print("\nUser: I'm in Chicago 60601, this is an emergency!")
        conversation.append({"role": "user", "content": "I'm in Chicago 60601, this is an emergency!"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 3: Need immediate help
        print("\nUser: I need someone RIGHT NOW, water is damaging everything")
        conversation.append({"role": "user", "content": "I need someone RIGHT NOW, water is damaging everything"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        # Analyze for emergency handling
        full_conversation = " ".join([msg["content"] for msg in conversation if msg["role"] == "assistant"])
        emergency_response = full_conversation.lower()
        
        emergency_keywords = ['emergency', 'urgent', 'right away', 'immediately', 'asap', 'priority']
        urgency_detected = [kw for kw in emergency_keywords if kw in emergency_response]
        
        # Should NOT mention group bidding for emergencies
        group_keywords = ['group', 'neighbors', 'coordinate', 'flexible timing']
        inappropriate_mentions = [kw for kw in group_keywords if kw in emergency_response]
        
        print(f"\n--- EMERGENCY HANDLING ANALYSIS ---")
        print(f"Urgency keywords: {urgency_detected}")
        print(f"Inappropriate group mentions: {inappropriate_mentions}")
        print(f"Emergency handling: {'GOOD' if urgency_detected and not inappropriate_mentions else 'POOR'}")
        
        if urgency_detected and not inappropriate_mentions:
            print("✅ SUCCESS: Emergency properly prioritized, no group bidding mentioned!")
            return True
        else:
            print("❌ FAILED: Emergency not handled with appropriate urgency")
            return False

    def test_budget_context_conversation(self):
        """Test budget context exploration (research stage, NOT amounts)"""
        print("\n" + "="*60)
        print("TEST 3: BUDGET CONTEXT EXPLORATION (NO AMOUNTS)")
        print("="*60)
        
        user_id = str(uuid.uuid4())
        conv_id = f"budget-context-{self.conversation_count}"
        self.conversation_count += 1
        
        conversation = []
        
        # Turn 1: Kitchen remodel request
        print("\nUser: I want to remodel my kitchen")
        conversation.append({"role": "user", "content": "I want to remodel my kitchen"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 2: More details
        print("\nUser: New cabinets, countertops, maybe new appliances. It's a 12x14 kitchen")
        conversation.append({"role": "user", "content": "New cabinets, countertops, maybe new appliances. It's a 12x14 kitchen"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 3: User mentions research stage
        print("\nUser: I'm just starting to research what something like this costs")
        conversation.append({"role": "user", "content": "I'm just starting to research what something like this costs"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 4: Try to get them to mention budget
        print("\nUser: What should I expect to pay for this?")
        conversation.append({"role": "user", "content": "What should I expect to pay for this?"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 5: See if they ask for amounts
        print("\nUser: Do you need to know my budget?")
        conversation.append({"role": "user", "content": "Do you need to know my budget?"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        # Analyze budget handling
        full_conversation = " ".join([msg["content"] for msg in conversation if msg["role"] == "assistant"])
        budget_response = full_conversation.lower()
        
        # Should explore research stage, not ask for amounts
        good_budget_words = ['research', 'quotes', 'exploring', 'planning', 'contractors can provide', 'accurate pricing']
        bad_budget_words = ['what is your budget', 'budget range', 'how much do you want to spend', 'dollar amount']
        
        good_mentions = [kw for kw in good_budget_words if kw in budget_response]
        bad_mentions = [kw for kw in bad_budget_words if kw in budget_response]
        
        print(f"\n--- BUDGET CONTEXT ANALYSIS ---")
        print(f"Good budget exploration: {good_mentions}")
        print(f"Inappropriate budget questions: {bad_mentions}")
        print(f"Budget handling: {'GOOD' if good_mentions and not bad_mentions else 'POOR'}")
        
        if good_mentions and not bad_mentions:
            print("✅ SUCCESS: Budget context explored properly, no amount pressure!")
            return True
        else:
            print("❌ FAILED: Budget handling not following 12 Key Data Points")
            return False

    def test_service_type_classification(self):
        """Test intelligent service type classification across conversation"""
        print("\n" + "="*60)
        print("TEST 4: SERVICE TYPE CLASSIFICATION INTELLIGENCE")
        print("="*60)
        
        user_id = str(uuid.uuid4())
        conv_id = f"service-type-{self.conversation_count}"
        self.conversation_count += 1
        
        conversation = []
        
        # Turn 1: Appliance issue
        print("\nUser: My washing machine is making weird noises and not spinning properly")
        conversation.append({"role": "user", "content": "My washing machine is making weird noises and not spinning properly"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 2: More details
        print("\nUser: It's about 3 years old, started last week")
        conversation.append({"role": "user", "content": "It's about 3 years old, started last week"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 3: Decision point
        print("\nUser: Should I repair it or just buy a new one?")
        conversation.append({"role": "user", "content": "Should I repair it or just buy a new one?"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        # Analyze service type classification
        full_conversation = " ".join([msg["content"] for msg in conversation if msg["role"] == "assistant"])
        service_response = full_conversation.lower()
        
        # Should classify as Appliance Repair, not Installation
        repair_indicators = ['repair', 'fix', 'appliance', 'washing machine']
        installation_indicators = ['install', 'new', 'replacement']
        
        repair_mentions = [kw for kw in repair_indicators if kw in service_response]
        install_mentions = [kw for kw in installation_indicators if kw in service_response]
        
        print(f"\n--- SERVICE TYPE ANALYSIS ---")
        print(f"Repair classification: {repair_mentions}")
        print(f"Installation mentions: {install_mentions}")
        
        # Good if it recognizes this as appliance repair
        if repair_mentions and 'appliance' in service_response:
            print("✅ SUCCESS: Correctly classified as Appliance Repair!")
            return True
        else:
            print("❌ FAILED: Service type classification unclear")
            return False

    def test_multi_project_context(self):
        """Test handling multiple projects and context awareness"""
        print("\n" + "="*60)
        print("TEST 5: MULTI-PROJECT CONTEXT AWARENESS") 
        print("="*60)
        
        user_id = str(uuid.uuid4())
        conv_id = f"multi-project-{self.conversation_count}"
        self.conversation_count += 1
        
        conversation = []
        
        # Turn 1: First project
        print("\nUser: I need to fix my deck, some boards are loose")
        conversation.append({"role": "user", "content": "I need to fix my deck, some boards are loose"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 2: Add second project
        print("\nUser: Also, I want to redo my driveway while I'm at it")
        conversation.append({"role": "user", "content": "Also, I want to redo my driveway while I'm at it"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 3: Ask about relationship
        print("\nUser: Can the same contractor do both?")
        conversation.append({"role": "user", "content": "Can the same contractor do both?"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        time.sleep(1)
        
        # Turn 4: Timing question
        print("\nUser: Should I do them at the same time or separately?")
        conversation.append({"role": "user", "content": "Should I do them at the same time or separately?"})
        response = self.send_message(conversation, user_id, conv_id)
        conversation.append({"role": "assistant", "content": response})
        
        # Analyze multi-project handling
        full_conversation = " ".join([msg["content"] for msg in conversation if msg["role"] == "assistant"])
        project_response = full_conversation.lower()
        
        project_keywords = ['both projects', 'separate', 'bundle', 'efficiency', 'related', 'coordination']
        context_detected = [kw for kw in project_keywords if kw in project_response]
        
        print(f"\n--- MULTI-PROJECT ANALYSIS ---")
        print(f"Context awareness: {context_detected}")
        
        if context_detected:
            print("✅ SUCCESS: Multi-project context handled intelligently!")
            return True
        else:
            print("❌ FAILED: Multi-project context not recognized")
            return False

def run_all_tests():
    """Run all long conversation tests"""
    print("STARTING LONG-RUNNING CONVERSATION TESTS")
    print("This will test real business logic across multiple turns...")
    print("Each test simulates realistic homeowner conversations\n")
    
    tester = CIAConversationTester()
    results = {}
    
    # Run all tests
    print("Running 5 comprehensive conversation tests...")
    
    results['group_bidding'] = tester.test_group_bidding_conversation()
    time.sleep(2)
    
    results['emergency_handling'] = tester.test_emergency_vs_planned_conversation()  
    time.sleep(2)
    
    results['budget_context'] = tester.test_budget_context_conversation()
    time.sleep(2)
    
    results['service_classification'] = tester.test_service_type_classification()
    time.sleep(2)
    
    results['multi_project'] = tester.test_multi_project_context()
    
    # Final results
    print("\n" + "="*60)
    print("FINAL LONG CONVERSATION TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOVERALL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL BUSINESS LOGIC WORKING IN LONG CONVERSATIONS!")
        print("✅ Group bidding promotion working")
        print("✅ Emergency prioritization working")  
        print("✅ Budget context exploration working")
        print("✅ Service type classification working")
        print("✅ Multi-project context awareness working")
    else:
        print(f"\n⚠️  {total_tests - total_passed} business logic issues detected")
        print("Check individual test results above")
        
    return results

if __name__ == "__main__":
    run_all_tests()