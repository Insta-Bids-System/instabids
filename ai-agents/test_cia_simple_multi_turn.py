#!/usr/bin/env python3
"""
Simple 3-turn conversation test for CIA agent
Tests basic context maintenance
"""
import requests
import json
import uuid
import time
from datetime import datetime

class SimpleConversationTest:
    def __init__(self):
        self.base_url = "http://localhost:8008/api/cia/stream"
        self.user_id = str(uuid.uuid4())
        self.conv_id = str(uuid.uuid4())
        self.messages = []
        
    def send_message(self, message):
        """Send a message and get response"""
        print(f"\n{'='*60}")
        print(f"USER: {message}")
        print('-'*60)
        
        # Add user message to history
        self.messages.append({"role": "user", "content": message})
        
        payload = {
            "messages": self.messages,
            "user_id": self.user_id,
            "conversation_id": self.conv_id
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=30, stream=True)
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            if data_str != '[DONE]':
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and data['choices']:
                                        content = data['choices'][0].get('delta', {}).get('content', '')
                                        full_response += content
                                except:
                                    pass
                
                # Add assistant response to history
                self.messages.append({"role": "assistant", "content": full_response})
                
                print(f"CIA: {full_response}")
                return full_response
            else:
                print(f"[ERROR] HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return None
    
    def run_test(self):
        """Run a simple 3-turn conversation"""
        print("\n" + "="*80)
        print("SIMPLE 3-TURN CONVERSATION TEST")
        print("="*80)
        print(f"User ID: {self.user_id}")
        print(f"Conv ID: {self.conv_id}")
        
        # Turn 1: Initial request
        print("\n[TURN 1]")
        self.send_message("I need artificial turf installed")
        time.sleep(2)
        
        # Turn 2: Add location
        print("\n[TURN 2]")
        self.send_message("I'm in Austin, Texas")
        time.sleep(2)
        
        # Turn 3: Confirm context is maintained
        print("\n[TURN 3]")
        response = self.send_message("What project did I mention I need help with?")
        
        # Check if agent remembers
        print("\n" + "="*80)
        print("TEST RESULT")
        print("="*80)
        
        if response and "turf" in response.lower():
            print("[SUCCESS] Agent maintained context - remembers artificial turf")
        else:
            print("[FAILED] Agent lost context - doesn't remember artificial turf")
        
        print("\nTotal messages in conversation:", len(self.messages))

if __name__ == "__main__":
    tester = SimpleConversationTest()
    tester.run_test()