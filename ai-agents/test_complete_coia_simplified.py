"""
SIMPLIFIED COMPLETE COIA TEST - Real API calls without unicode issues
"""
import requests
import json
import time
from config.service_urls import get_backend_url

def test_complete_workflow():
    base_url = f"{get_backend_url()}/api/coia/landing"
    contractor_lead_id = f"test-{int(time.time())}"
    
    print("COMPLETE COIA WORKFLOW TEST")
    print("=" * 60)
    
    stages = [
        {
            "name": "Stage 1: Initial Contact",
            "message": "Hi, I'm Justin from JM Holiday Lighting. We install Christmas lights in South Florida.",
            "expected": ["Pompano Beach", "jmholidaylighting.com", "research"]
        },
        {
            "name": "Stage 2: Research Confirmation", 
            "message": "Yes, that's correct! Can you research more details about my business?",
            "expected": ["comprehensive", "detailed", "gathering"]
        },
        {
            "name": "Stage 3: Profile Building",
            "message": "Tell me what information you found and what else you need to know.",
            "expected": ["profile", "questions", "business"]
        },
        {
            "name": "Stage 4: InstaBids Value",
            "message": "How can InstaBids help my business grow?",
            "expected": ["InstaBids", "projects", "homeowners"]
        },
        {
            "name": "Stage 5: Account Creation",
            "message": "I want to create an account and start bidding on projects.",
            "expected": ["account", "signup", "contractor"]
        }
    ]
    
    results = []
    
    for i, stage in enumerate(stages, 1):
        print(f"\n{stage['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(base_url, json={
                "message": stage["message"],
                "contractor_lead_id": contractor_lead_id,
                "session_id": f"session-{i}"
            }, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                
                # Check expected keywords (without printing full response to avoid unicode)
                found_keywords = []
                for keyword in stage["expected"]:
                    if keyword.lower() in ai_response.lower():
                        found_keywords.append(keyword)
                
                print(f"API Response: {response.status_code} OK")
                print(f"Response length: {len(ai_response)} characters")
                print(f"Keywords found: {found_keywords}")
                print(f"Research completed: {data.get('research_completed', False)}")
                print(f"Contractor created: {data.get('contractor_created', False)}")
                
                # Store result
                results.append({
                    "stage": stage["name"],
                    "success": len(found_keywords) > 0,
                    "keywords_found": found_keywords,
                    "data": data
                })
                
            else:
                print(f"API ERROR: {response.status_code}")
                results.append({
                    "stage": stage["name"],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"Exception: {e}")
            results.append({
                "stage": stage["name"],
                "success": False,
                "error": str(e)
            })
        
        time.sleep(2)  # Brief pause between stages
    
    # Final analysis
    print("\n" + "=" * 60)
    print("FINAL ANALYSIS")
    print("=" * 60)
    
    successful_stages = [r for r in results if r.get("success", False)]
    print(f"Successful stages: {len(successful_stages)}/5")
    print(f"Success rate: {len(successful_stages)/5*100:.1f}%")
    
    print(f"\nDETAILED RESULTS:")
    for result in results:
        status = "PASS" if result.get("success", False) else "FAIL"
        print(f"  {result['stage']}: {status}")
        if "keywords_found" in result:
            print(f"    Keywords: {result['keywords_found']}")
        if "error" in result:
            print(f"    Error: {result['error']}")
    
    # Check final state
    final_data = results[-1].get("data", {}) if results else {}
    contractor_profile = final_data.get("contractor_profile", {})
    
    print(f"\nFINAL STATE:")
    print(f"  Contractor profile fields: {len(contractor_profile)}")
    print(f"  Company name: {contractor_profile.get('company_name', 'Not found')}")
    print(f"  Research completed: {final_data.get('research_completed', False)}")
    print(f"  Contractor created: {final_data.get('contractor_created', False)}")
    
    return len(successful_stages) == 5

if __name__ == "__main__":
    success = test_complete_workflow()
    
    print(f"\n" + "=" * 60)
    if success:
        print("RESULT: COMPLETE SUCCESS - All stages working!")
    else:
        print("RESULT: WORKFLOW INCOMPLETE - Some stages failed")
    print("=" * 60)