"""
FULL COIA SYSTEM TEST - Real Multi-turn Contractor Conversation
Tests the complete onboarding flow with JM Holiday Lighting contractor
"""

import asyncio
import requests
import json
import time
from datetime import datetime

def test_coia_conversation():
    """Run the complete multi-turn conversation test"""
    print("="*100)
    print("FULL COIA SYSTEM TEST - JM HOLIDAY LIGHTING CONTRACTOR ONBOARDING")
    print("="*100)
    
    base_url = "http://localhost:8008"
    session_id = f"test-jm-holiday-{int(time.time())}"
    conversation_log = []
    
    def send_message(message, turn_number):
        print(f"\nTURN {turn_number}: {message}")
        
        payload = {
            "message": message,
            "session_id": session_id
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/api/coia/landing", json=payload)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"COIA ({response_time:.2f}s): {result.get('response', '')}")
            
            conversation_log.append({
                "turn": turn_number,
                "response_time": response_time,
                "success": True,
                "contractor_lead_id": result.get("contractor_lead_id"),
                "company_name": result.get("company_name"),
                "response": result.get("response", "")
            })
            
            return result
        else:
            print(f"ERROR {response.status_code}: {response.text}")
            conversation_log.append({
                "turn": turn_number,
                "response_time": response_time,
                "success": False,
                "error": response.text
            })
            return None
    
    # Run the 5-turn conversation
    print("\nStarting JM Holiday Lighting onboarding conversation...")
    
    # Turn 1: Introduction
    response1 = send_message(
        "Hello, I'm JM Holiday Lighting. We're a professional holiday lighting contractor based in South Florida.",
        1
    )
    
    # Turn 2: Services
    response2 = send_message(
        "We specialize in holiday lighting installation, permanent lighting systems, and commercial displays. We serve Miami-Dade, Broward, and Palm Beach counties.",
        2
    )
    
    # Turn 3: Credentials
    response3 = send_message(
        "We've been in business for 8 years, fully licensed and insured. We have a 4.8-star rating on Google with over 150 reviews. Our website is jmholidaylighting.com",
        3
    )
    
    # Turn 4: Capacity
    response4 = send_message(
        "We can handle projects from $500 residential displays to $50,000+ commercial installations. We typically book 2-3 months out during holiday season.",
        4
    )
    
    # Turn 5: Portfolio
    response5 = send_message(
        "Our portfolio includes luxury residential properties in Coral Gables and shopping centers like Town Center at Boca Raton. We can provide references.",
        5
    )
    
    # Analysis
    print("\n" + "="*80)
    print("TEST RESULTS ANALYSIS")
    print("="*80)
    
    successful_turns = [log for log in conversation_log if log.get("success")]
    total_response_time = sum([log["response_time"] for log in successful_turns])
    avg_response_time = total_response_time / len(successful_turns) if successful_turns else 0
    
    contractor_lead_ids = [log.get("contractor_lead_id") for log in conversation_log if log.get("contractor_lead_id")]
    company_names = [log.get("company_name") for log in conversation_log if log.get("company_name")]
    
    print(f"Successful Turns: {len(successful_turns)}/5")
    print(f"Average Response Time: {avg_response_time:.2f} seconds")
    print(f"Contractor Lead IDs Generated: {len(contractor_lead_ids)}")
    print(f"Company Names Extracted: {len(set(company_names))}")
    
    if contractor_lead_ids:
        print(f"Latest Contractor ID: {contractor_lead_ids[-1]}")
    
    # Success criteria
    success_score = 0
    total_criteria = 5
    
    if len(successful_turns) >= 5:
        print("[PASS] Multi-turn conversation completed")
        success_score += 1
    else:
        print("[FAIL] Multi-turn conversation incomplete")
    
    if avg_response_time < 5:
        print("[PASS] Response times acceptable (<5s)")
        success_score += 1
    else:
        print("[FAIL] Response times too slow (>5s)")
    
    if contractor_lead_ids:
        print("[PASS] Contractor lead IDs generated")
        success_score += 1
    else:
        print("[FAIL] No contractor lead IDs generated")
    
    if "JM Holiday" in str(company_names):
        print("[PASS] Company name recognition working")
        success_score += 1
    else:
        print("[FAIL] Company name recognition failed")
    
    # Check for meaningful responses
    meaningful_responses = [log for log in conversation_log if log.get("response") and len(log["response"]) > 50]
    if len(meaningful_responses) >= 4:
        print("[PASS] Meaningful conversation responses")
        success_score += 1
    else:
        print("[FAIL] Responses too short or missing")
    
    print(f"\nOVERALL SCORE: {success_score}/{total_criteria} ({(success_score/total_criteria)*100:.1f}%)")
    
    if success_score >= 4:
        print("\n[SUCCESS] COIA system working - contractor onboarding functional!")
        return True
    else:
        print("\n[FAILED] COIA system has issues - needs attention")
        return False

if __name__ == "__main__":
    success = test_coia_conversation()
    exit(0 if success else 1)