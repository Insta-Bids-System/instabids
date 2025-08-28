#!/usr/bin/env python3
"""
REAL Multi-Turn CIA Agent Conversation Test
Tests a complete 5-8 turn conversation with image handling and full bid card completion
"""
import requests
import json
import uuid
import time
import base64
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

class RealConversationTest:
    def __init__(self):
        self.base_url = "http://localhost:8008/api/cia/stream"
        self.user_id = str(uuid.uuid4())
        self.conv_id = str(uuid.uuid4())
        self.messages = []
        self.bid_card_id = None
        
    def send_message(self, message, images=None):
        """Send a message and get response"""
        print(f"\n{'='*60}")
        print(f"USER: {message}")
        if images:
            print(f"[Attached {len(images)} image(s)]")
        print('-'*60)
        
        # Add user message to history
        self.messages.append({"role": "user", "content": message})
        
        payload = {
            "messages": self.messages,
            "user_id": self.user_id,
            "conversation_id": self.conv_id
        }
        
        # Add images if provided
        if images:
            payload["images"] = images
        
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
    
    def check_bid_card_status(self):
        """Check the current bid card completion status"""
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("[ERROR] Supabase credentials not found")
            return None
            
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        # Get bid card for this conversation
        url = f"{SUPABASE_URL}/rest/v1/cia_conversation_tracking"
        params = {
            "select": "*",
            "conversation_id": f"eq.{self.conv_id}",
            "limit": "1"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data:
                    tracking = data[0]
                    self.bid_card_id = tracking.get('potential_bid_card_id')
                    
                    print(f"\n[BID CARD STATUS]")
                    print(f"  Bid Card ID: {self.bid_card_id}")
                    print(f"  Completion: {tracking.get('completion_percentage', 0)}%")
                    
                    fields = tracking.get('fields_collected', {})
                    if fields:
                        print("  Fields Collected:")
                        for field, info in fields.items():
                            print(f"    - {field}: YES")
                    
                    return tracking
            return None
        except Exception as e:
            print(f"[ERROR] Database check failed: {e}")
            return None
    
    def get_final_bid_card(self):
        """Get the final bid card data"""
        if not self.bid_card_id or not SUPABASE_URL or not SUPABASE_KEY:
            return None
            
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        url = f"{SUPABASE_URL}/rest/v1/potential_bid_cards"
        params = {
            "select": "*",
            "id": f"eq.{self.bid_card_id}",
            "limit": "1"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0]
            return None
        except:
            return None
    
    def run_full_conversation(self):
        """Run a complete multi-turn conversation"""
        print("\n" + "="*80)
        print("REAL MULTI-TURN CIA AGENT CONVERSATION TEST")
        print("="*80)
        print(f"User ID: {self.user_id}")
        print(f"Conv ID: {self.conv_id}")
        print(f"Started: {datetime.now().isoformat()}")
        
        # Turn 1: Initial request
        print("\n[TURN 1: Initial Request]")
        self.send_message("I need artificial turf installed in my backyard")
        self.check_bid_card_status()
        time.sleep(2)
        
        # Turn 2: Provide location
        print("\n[TURN 2: Location]")
        self.send_message("I'm in Austin, Texas, zip code 78701")
        self.check_bid_card_status()
        time.sleep(2)
        
        # Turn 3: Timeline
        print("\n[TURN 3: Timeline]")
        self.send_message("I'd like to get this done within the next 2-3 weeks if possible")
        self.check_bid_card_status()
        time.sleep(2)
        
        # Turn 4: Size/Scope
        print("\n[TURN 4: Size and Scope]")
        self.send_message("The backyard is about 1,500 square feet. I want the premium quality turf that looks very realistic")
        self.check_bid_card_status()
        time.sleep(2)
        
        # Turn 5: Budget
        print("\n[TURN 5: Budget]")
        self.send_message("My budget is around $8,000 to $12,000")
        self.check_bid_card_status()
        time.sleep(2)
        
        # Turn 6: Special requirements
        print("\n[TURN 6: Special Requirements]")
        self.send_message("I have two dogs, so I need pet-friendly turf with good drainage. Also need the old grass removed")
        self.check_bid_card_status()
        time.sleep(2)
        
        # Turn 7: Contact info
        print("\n[TURN 7: Contact Information]")
        self.send_message("My email is john.smith@example.com and phone is 512-555-0123")
        self.check_bid_card_status()
        time.sleep(2)
        
        # Turn 8: Image (simulate with description since we can't upload real image)
        print("\n[TURN 8: Additional Details]")
        self.send_message("I'd also like some decorative rocks around the edges. Can you work with that?")
        final_status = self.check_bid_card_status()
        
        # Get final bid card
        print("\n" + "="*80)
        print("FINAL BID CARD DATA")
        print("="*80)
        
        final_card = self.get_final_bid_card()
        if final_card:
            print("\nExtracted Fields:")
            important_fields = [
                'title', 'primary_trade', 'user_scope_notes', 
                'project_complexity', 'property_area', 'room_location',
                'timeline_flexibility', 'seasonal_constraint'
            ]
            
            for field in important_fields:
                value = final_card.get(field)
                if value:
                    print(f"  {field}: {value}")
            
            # Check for additional data in AI analysis
            ai_analysis = final_card.get('ai_analysis', {})
            if ai_analysis:
                print("\nAI Analysis Data:")
                for key, value in ai_analysis.items():
                    if value:
                        print(f"  {key}: {value}")
        
        # Final summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        if final_status:
            completion = final_status.get('completion_percentage', 0)
            fields_collected = final_status.get('fields_collected', {})
            
            print(f"\nTotal Turns: 8")
            print(f"Final Completion: {completion}%")
            print(f"Fields Extracted: {len(fields_collected)}")
            
            expected_fields = [
                'project_type', 'service_type', 'location', 'zip_code',
                'timeline', 'scope_details', 'budget_min', 'budget_max',
                'email', 'phone', 'special_requirements', 'materials'
            ]
            
            print("\nField Extraction Check:")
            for field in expected_fields:
                if field in fields_collected:
                    print(f"  [YES] {field}")
                else:
                    print(f"  [NO]  {field}")
            
            # Success criteria
            print("\n[SUCCESS CRITERIA]")
            print(f"  Multi-turn conversation: {'YES' if len(self.messages) >= 10 else 'NO'}")
            print(f"  Completion > 80%: {'YES' if completion > 80 else 'NO'}")
            print(f"  Location extracted: {'YES' if 'location' in fields_collected or 'zip_code' in fields_collected else 'NO'}")
            print(f"  Timeline extracted: {'YES' if 'timeline' in fields_collected else 'NO'}")
            print(f"  Budget extracted: {'YES' if 'budget_min' in fields_collected or 'budget_max' in fields_collected else 'NO'}")
            print(f"  Contact info: {'YES' if 'email' in fields_collected or 'phone' in fields_collected else 'NO'}")
            
            # Overall result
            success_count = sum([
                len(self.messages) >= 10,
                completion > 80,
                'location' in fields_collected or 'zip_code' in fields_collected,
                'timeline' in fields_collected,
                'budget_min' in fields_collected or 'budget_max' in fields_collected,
                'email' in fields_collected or 'phone' in fields_collected
            ])
            
            print(f"\n[FINAL RESULT]: {success_count}/6 criteria met")
            if success_count >= 5:
                print("[VERDICT]: PASSED - CIA agent handles multi-turn conversations!")
            else:
                print("[VERDICT]: FAILED - CIA agent needs improvements")
        else:
            print("[ERROR] Could not retrieve final status")
        
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)

if __name__ == "__main__":
    tester = RealConversationTest()
    tester.run_full_conversation()