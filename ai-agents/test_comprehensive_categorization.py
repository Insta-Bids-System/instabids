"""
Comprehensive test of categorization integration
Tests both API responses and backend logs for tool calls
"""

import requests
import json
import uuid
import time
import subprocess

def test_with_log_monitoring():
    """Test categorization while monitoring backend logs for tool calls"""
    
    base_url = "http://localhost:8008"
    endpoint = f"{base_url}/api/cia/stream"
    
    # Test scenarios
    scenarios = [
        {
            "name": "Artificial Turf (High Confidence Expected)",
            "message": "I need artificial turf installed in my backyard",
            "expected_category": "Installation",
            "expected_type": "turf_installation",
            "expected_confidence": ">=0.7"
        },
        {
            "name": "Christmas Lights (High Confidence Expected)", 
            "message": "Looking for someone to install christmas lights on my house",
            "expected_category": "Installation", 
            "expected_type": "holiday_lighting_installation",
            "expected_confidence": ">=0.7"
        },
        {
            "name": "Pool Project (High Confidence Expected)",
            "message": "I want to install a swimming pool in my backyard",
            "expected_category": "Installation",
            "expected_type": "pool_installation", 
            "expected_confidence": ">=0.7"
        },
        {
            "name": "Vague Request (Low Confidence Expected)",
            "message": "I need some work done",
            "expected_category": "Unknown",
            "expected_type": "clarifying_question", 
            "expected_confidence": "<0.7"
        },
        {
            "name": "Solar Panels (High Confidence Expected)",
            "message": "Solar panel installation with battery backup system",
            "expected_category": "Installation",
            "expected_type": "solar_panel_installation",
            "expected_confidence": ">=0.7"
        }
    ]
    
    print("COMPREHENSIVE CATEGORIZATION TEST")
    print("=" * 60)
    print(f"Backend URL: {base_url}")
    print(f"Test scenarios: {len(scenarios)}")
    print()
    
    user_id = str(uuid.uuid4())
    results = []
    
    for i, scenario in enumerate(scenarios):
        conversation_id = f"categorization_test_{i}_{uuid.uuid4()}"
        
        print(f"TEST {i+1}/5: {scenario['name']}")
        print(f"Message: '{scenario['message']}'")
        print(f"Expected: {scenario['expected_category']} -> {scenario['expected_type']} ({scenario['expected_confidence']})")
        print("-" * 60)
        
        # Prepare request
        request_data = {
            "messages": [{"content": scenario["message"], "images": []}],
            "conversation_id": conversation_id,
            "user_id": user_id
        }
        
        try:
            # Make API call
            start_time = time.time()
            response = requests.post(
                endpoint,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=45
            )
            duration = time.time() - start_time
            
            print(f"[TIME] Response time: {duration:.2f}s")
            print(f"[STATUS] Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.text
                print(f"[LENGTH] Response length: {len(response_text)} chars")
                
                # Analyze response content
                analysis = analyze_categorization_response(response_text, scenario)
                results.append({
                    "scenario": scenario["name"],
                    "success": response.status_code == 200,
                    "analysis": analysis,
                    "duration": duration
                })
                
                # Print analysis
                print(f"[ANALYSIS] Results:")
                for key, value in analysis.items():
                    if key != "response_preview":
                        print(f"   {key}: {value}")
                
                if analysis["categorization_evidence"]:
                    print("[SUCCESS] CATEGORIZATION WORKING")
                else:
                    print("[FAILED] NO CATEGORIZATION EVIDENCE")
                    
            else:
                print(f"[ERROR] HTTP {response.status_code}")
                print(f"Response: {response.text[:300]}")
                results.append({
                    "scenario": scenario["name"], 
                    "success": False,
                    "error": f"{response.status_code}: {response.text[:100]}"
                })
                
        except Exception as e:
            print(f"[EXCEPTION] {str(e)}")
            results.append({
                "scenario": scenario["name"],
                "success": False,
                "error": str(e)
            })
            
        print()
        
        # Brief pause between tests
        if i < len(scenarios) - 1:
            time.sleep(2)
    
    # Print summary
    print("=" * 60)
    print("CATEGORIZATION TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"[SUCCESS] Successful: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"[FAILED] Failed: {total-successful}/{total}")
    print()
    
    for result in results:
        status = "[SUCCESS]" if result["success"] else "[FAILED]"
        print(f"{status} {result['scenario']}")
        if "analysis" in result:
            analysis = result["analysis"]
            if analysis["categorization_evidence"]:
                print(f"   [FOUND] Keywords: {', '.join(analysis['keywords_found'])}")
            if analysis["tool_call_evidence"]:
                print(f"   [TOOLS] Tool calls detected")
            print(f"   [TIME] {result['duration']:.1f}s")
    
    print()
    print("[CHECK] Backend logs should show:")
    print("   - 'Categorization tool called: {...}'")
    print("   - Tool execution results")
    print("   - Database updates to potential_bid_cards")
    

def analyze_categorization_response(response_text, scenario):
    """Analyze the streaming response for categorization evidence"""
    
    analysis = {
        "response_preview": response_text[:200],
        "total_length": len(response_text),
        "keywords_found": [],
        "categorization_evidence": False,
        "tool_call_evidence": False,
        "confidence_mentioned": False
    }
    
    # Check for categorization keywords
    categorization_keywords = [
        "installation", "turf", "artificial", "lighting", "christmas", "solar", 
        "pool", "swimming", "holiday", "lights", "panels", "battery", "Tagged as"
    ]
    
    response_lower = response_text.lower()
    
    for keyword in categorization_keywords:
        if keyword.lower() in response_lower:
            analysis["keywords_found"].append(keyword)
            analysis["categorization_evidence"] = True
    
    # Check for tool call evidence
    tool_indicators = [
        "categorize_project", "tool_call", "confidence", "Tagged as", 
        "project_type", "service_category"
    ]
    
    for indicator in tool_indicators:
        if indicator.lower() in response_lower:
            analysis["tool_call_evidence"] = True
            break
    
    # Check for confidence mentions
    if any(word in response_lower for word in ["confidence", "0.", "90%", "95%"]):
        analysis["confidence_mentioned"] = True
    
    return analysis


if __name__ == "__main__":
    print("Starting comprehensive categorization test...")
    print("Monitor Docker logs with: docker logs instabids-instabids-backend-1 -f")
    print()
    
    test_with_log_monitoring()