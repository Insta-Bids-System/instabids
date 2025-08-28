"""
REAL COIA PERFORMANCE TEST - Expose the actual issues
This test will show the real performance and functionality problems
"""

import requests
import time
import json

def test_coia_real_performance():
    """Test real COIA performance with detailed timing"""
    print("="*80)
    print("REAL COIA PERFORMANCE TEST - EXPOSING ACTUAL ISSUES")
    print("="*80)
    
    base_url = "http://localhost:8008"
    session_id = f"real-test-{int(time.time())}"
    
    # Track all timings
    turn_timings = []
    total_start = time.time()
    
    def send_message_with_timing(message, turn_num):
        print(f"\n--- TURN {turn_num} ---")
        print(f"SENDING: {message}")
        
        payload = {
            "message": message,
            "session_id": session_id
        }
        
        # Measure precise timing
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/api/coia/landing", 
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract just the first 200 chars of response to avoid Unicode issues
                response_text = result.get('response', '')
                if len(response_text) > 200:
                    response_text = response_text[:200] + "..."
                
                print(f"TIME: {response_time:.2f}s")
                print(f"RESPONSE: {response_text}")
                
                # Check for background processing indicators
                background_active = 'research' in response_text.lower() or 'finding' in response_text.lower()
                
                turn_timings.append({
                    "turn": turn_num,
                    "time": response_time,
                    "success": True,
                    "background_processing": background_active,
                    "contractor_lead_id": result.get("contractor_lead_id"),
                    "response_length": len(result.get('response', ''))
                })
                
                return result
            else:
                error_time = time.time() - start_time
                print(f"ERROR {response.status_code} in {error_time:.2f}s: {response.text}")
                turn_timings.append({
                    "turn": turn_num,
                    "time": error_time,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                return None
                
        except requests.exceptions.Timeout:
            timeout_time = time.time() - start_time
            print(f"TIMEOUT after {timeout_time:.2f}s - System too slow!")
            turn_timings.append({
                "turn": turn_num,
                "time": timeout_time,
                "success": False,
                "error": "TIMEOUT"
            })
            return None
            
        except Exception as e:
            error_time = time.time() - start_time
            print(f"EXCEPTION in {error_time:.2f}s: {str(e)}")
            turn_timings.append({
                "turn": turn_num,
                "time": error_time,
                "success": False,
                "error": str(e)
            })
            return None
    
    # Run multiple turns to test real conversation flow
    conversations = [
        "I am JM Holiday Lighting, a professional holiday lighting contractor in South Florida",
        "We specialize in residential and commercial holiday light installation",
        "We have been in business for 8 years and serve Miami-Dade, Broward, and Palm Beach counties",
        "Our team can handle projects from $500 residential to $50000 commercial installations", 
        "We are fully licensed and insured with a 4.8 star Google rating",
        "We typically book 2-3 months out during peak holiday season",
        "Our portfolio includes luxury homes in Coral Gables and major shopping centers",
        "We offer both temporary holiday displays and permanent LED lighting systems",
        "What kind of projects do you have available for holiday lighting contractors?",
        "Can you show me homeowners who need holiday lighting in South Florida?"
    ]
    
    print(f"Starting {len(conversations)}-turn conversation test...")
    print(f"Each turn has 30 second timeout")
    
    # Execute conversation
    for i, message in enumerate(conversations, 1):
        result = send_message_with_timing(message, i)
        
        if not result:
            print(f"CONVERSATION FAILED AT TURN {i}")
            break
            
        # Brief pause between turns
        time.sleep(0.5)
    
    total_time = time.time() - total_start
    
    # Analyze results
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    
    successful_turns = [t for t in turn_timings if t["success"]]
    failed_turns = [t for t in turn_timings if not t["success"]]
    
    print(f"TOTAL CONVERSATION TIME: {total_time:.2f} seconds")
    print(f"SUCCESSFUL TURNS: {len(successful_turns)}/{len(turn_timings)}")
    print(f"FAILED TURNS: {len(failed_turns)}")
    
    if successful_turns:
        avg_response_time = sum(t["time"] for t in successful_turns) / len(successful_turns)
        max_response_time = max(t["time"] for t in successful_turns)
        min_response_time = min(t["time"] for t in successful_turns)
        
        print(f"AVERAGE RESPONSE TIME: {avg_response_time:.2f} seconds")
        print(f"FASTEST RESPONSE: {min_response_time:.2f} seconds")
        print(f"SLOWEST RESPONSE: {max_response_time:.2f} seconds")
        
        # Check if any responses were acceptably fast
        fast_responses = [t for t in successful_turns if t["time"] < 2.0]
        print(f"FAST RESPONSES (<2s): {len(fast_responses)}/{len(successful_turns)}")
        
        # Check for background processing indicators
        background_turns = [t for t in successful_turns if t.get("background_processing")]
        print(f"BACKGROUND PROCESSING DETECTED: {len(background_turns)} turns")
        
        # Check for contractor lead IDs
        contractor_ids = [t.get("contractor_lead_id") for t in successful_turns if t.get("contractor_lead_id")]
        print(f"CONTRACTOR LEAD IDS GENERATED: {len(set(contractor_ids))}")
    
    # Show detailed timing breakdown
    print(f"\nDETAILED TIMING BREAKDOWN:")
    for timing in turn_timings:
        status = "SUCCESS" if timing["success"] else "FAILED"
        error_info = f" ({timing.get('error', '')})" if not timing["success"] else ""
        print(f"Turn {timing['turn']}: {timing['time']:.2f}s - {status}{error_info}")
    
    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)
    
    if len(successful_turns) >= 8:
        print("SUCCESS: Multi-turn conversation completed")
    elif len(successful_turns) >= 5:
        print("PARTIAL: Some conversation flow working")
    else:
        print("FAILED: Conversation flow broken")
    
    if successful_turns and avg_response_time < 3.0:
        print("SUCCESS: Response times acceptable")
    else:
        print("FAILED: Response times too slow")
    
    if len(failed_turns) == 0:
        print("SUCCESS: No system failures")
    else:
        print(f"FAILED: {len(failed_turns)} system failures detected")
    
    # Overall success rate
    success_rate = len(successful_turns) / len(turn_timings) * 100 if turn_timings else 0
    print(f"\nOVERALL SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 90 and (not successful_turns or avg_response_time < 3.0):
        print("SYSTEM STATUS: FULLY FUNCTIONAL")
        return True
    elif success_rate >= 70:
        print("SYSTEM STATUS: PARTIALLY FUNCTIONAL")
        return False
    else:
        print("SYSTEM STATUS: BROKEN")
        return False

if __name__ == "__main__":
    success = test_coia_real_performance()
    exit(0 if success else 1)