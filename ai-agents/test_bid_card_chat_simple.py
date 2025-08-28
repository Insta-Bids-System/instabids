#!/usr/bin/env python3
"""
BID CARD CHAT INTEGRATION TEST (Simple Version)
Tests intelligent messaging system in actual homeowner-contractor chat environment
"""

import requests
import json
import uuid
from datetime import datetime
from config.service_urls import get_backend_url

class BidCardChatTest:
    def __init__(self):
        self.base_url = get_backend_url()
        self.user_id = str(uuid.uuid4())
        self.contractor_id = str(uuid.uuid4())
        self.bid_card_id = str(uuid.uuid4())
        
    def run_test(self):
        """Run comprehensive bid card chat integration test"""
        
        print("BID CARD CHAT INTEGRATION TEST")
        print("=" * 60)
        print(f"Testing intelligent messaging in REAL bid card chat environment")
        print(f"Homeowner ID: {self.user_id}")
        print(f"Contractor ID: {self.contractor_id}")
        print(f"Bid Card ID: {self.bid_card_id}")
        print()
        
        # Test 1: Homeowner sending contact info
        print("TEST 1: Homeowner message with contact info")
        homeowner_result = self.test_homeowner_contact()
        print()
        
        # Test 2: Contractor sending contact info
        print("TEST 2: Contractor message with contact info")
        contractor_result = self.test_contractor_contact()
        print()
        
        # Test 3: Legitimate communication
        print("TEST 3: Legitimate project communication")
        legitimate_result = self.test_legitimate_message()
        print()
        
        # Final results
        print("FINAL INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"Homeowner Contact Blocking: {'PASS' if homeowner_result else 'FAIL'}")
        print(f"Contractor Contact Blocking: {'PASS' if contractor_result else 'FAIL'}")
        print(f"Legitimate Communication: {'PASS' if legitimate_result else 'FAIL'}")
        
        all_passed = homeowner_result and contractor_result and legitimate_result
        
        print()
        if all_passed:
            print("SUCCESS: Intelligent messaging FULLY INTEGRATED in bid card chat!")
            print("Contact information blocking works in real homeowner-contractor chat")
            print("System ready for production use")
        else:
            print("PARTIAL SUCCESS: Some integration issues found")
            
        return all_passed
    
    def test_homeowner_contact(self):
        """Test homeowner sending contact info through bid card chat"""
        
        print("  Testing: 'My cell is 407-555-1234, call me directly'")
        
        payload = {
            "content": "Hi! I love your work. My cell is 407-555-1234, please call me directly to discuss pricing. My email is homeowner@gmail.com",
            "sender_type": "homeowner",
            "sender_id": self.user_id,
            "bid_card_id": self.bid_card_id,
            "recipient_id": self.contractor_id
        }
        
        try:
            # Use the actual bid card messaging endpoint
            response = requests.post(
                f"{self.base_url}/api/bid-cards/messages", 
                json=payload, 
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"    Status: {response.status_code}")
                print(f"    Message Approved: {result.get('approved', False)}")
                
                intelligent_result = result.get('intelligent_result', {})
                print(f"    Agent Decision: {intelligent_result.get('agent_decision', 'unknown')}")
                print(f"    Threats Detected: {intelligent_result.get('threats_detected', [])}")
                
                # Should be blocked due to contact info
                blocked = not result.get('approved', True)
                if blocked:
                    print("  SUCCESS: Homeowner contact info correctly blocked")
                    return True
                else:
                    print("  FAILED: Homeowner contact info not blocked")
                    return False
            else:
                print(f"  HTTP Error: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_contractor_contact(self):
        """Test contractor sending contact info through bid card chat"""
        
        print("  Testing: contractor message with phone and website")
        
        payload = {
            "content": "I can do your kitchen! Check out my website at testkitchens.com or text me at 321-555-9876. Here's my email: contractor@business.com",
            "sender_type": "contractor",
            "sender_id": self.contractor_id,
            "bid_card_id": self.bid_card_id,
            "recipient_id": self.user_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/bid-cards/messages", 
                json=payload, 
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"    Status: {response.status_code}")
                print(f"    Message Approved: {result.get('approved', False)}")
                
                intelligent_result = result.get('intelligent_result', {})
                print(f"    Agent Decision: {intelligent_result.get('agent_decision', 'unknown')}")
                print(f"    Threats Detected: {intelligent_result.get('threats_detected', [])}")
                
                # Should be blocked due to contact info
                blocked = not result.get('approved', True)
                if blocked:
                    print("  SUCCESS: Contractor contact info correctly blocked")
                    return True
                else:
                    print("  FAILED: Contractor contact info not blocked")
                    return False
            else:
                print(f"  HTTP Error: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_legitimate_message(self):
        """Test legitimate project communication passes through"""
        
        print("  Testing: legitimate project discussion")
        
        payload = {
            "content": "I can install your kitchen cabinets for $18,000. Timeline would be 3-4 weeks. Do you prefer oak, maple, or cherry wood? I can also upgrade countertops.",
            "sender_type": "contractor",
            "sender_id": self.contractor_id,
            "bid_card_id": self.bid_card_id,
            "recipient_id": self.user_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/bid-cards/messages", 
                json=payload, 
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"    Status: {response.status_code}")
                print(f"    Message Approved: {result.get('approved', True)}")
                
                intelligent_result = result.get('intelligent_result', {})
                print(f"    Agent Decision: {intelligent_result.get('agent_decision', 'unknown')}")
                print(f"    Threats Detected: {intelligent_result.get('threats_detected', [])}")
                
                # Should be approved - legitimate project discussion
                approved = result.get('approved', False)
                if approved:
                    print("  SUCCESS: Legitimate communication correctly approved")
                    return True
                else:
                    print("  FAILED: Legitimate communication wrongly blocked")
                    return False
            else:
                print(f"  HTTP Error: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Error: {e}")
            return False

def main():
    """Run the bid card chat integration test"""
    
    test = BidCardChatTest()
    success = test.run_test()
    
    print("\n" + "=" * 60)
    if success:
        print("FINAL RESULT: INTELLIGENT MESSAGING FULLY INTEGRATED!")
        print("System tested in REAL homeowner-contractor bid card chat environment")  
        print("Contact information blocking confirmed working")
        print("READY FOR PRODUCTION USE!")
    else:
        print("FINAL RESULT: Integration issues found")
        print("Some components need debugging")
    
    return success

if __name__ == "__main__":
    main()