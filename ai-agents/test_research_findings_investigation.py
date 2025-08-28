"""
Investigate why research_findings is null despite research_completed being True
"""
import requests
import json
from config.service_urls import get_backend_url

def test_research_findings():
    """Test research findings data flow"""
    
    print("\n" + "="*80)
    print("INVESTIGATING RESEARCH FINDINGS ISSUE")
    print("="*80)
    
    # Use a fresh session to avoid any cached state
    test_data = {
        "message": "Hello, I'm with JM Holiday Lighting, we install christmas lights in South Florida",
        "contractor_id": "research-investigation",
        "session_id": "investigation-session-789"
    }
    
    url = f"{get_backend_url()}/api/coia/landing"
    
    print("\nStep 1: Company extraction with location hint")
    print("Company: JM Holiday Lighting")
    print("Location: South Florida") 
    print("Expected: Should trigger Google Places research")
    
    try:
        # Make the request
        response = requests.post(url, json=test_data, timeout=300)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"[SUCCESS] Response received")
            print(f"Response type: {type(data)}")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Check key fields
            research_completed = data.get("research_completed")
            research_findings = data.get("research_findings")
            company_name = data.get("company_name") or data.get("contractor_profile", {}).get("company_name")
            current_mode = data.get("current_mode")
            
            print("\n" + "="*60)
            print("STATE ANALYSIS")
            print("="*60)
            print(f"company_name: {company_name}")
            print(f"current_mode: {current_mode}")
            print(f"research_completed: {research_completed}")
            print(f"research_findings: {research_findings}")
            print(f"research_findings type: {type(research_findings)}")
            
            # Check contractor profile
            contractor_profile = data.get("contractor_profile", {})
            print(f"\ncontractor_profile keys: {list(contractor_profile.keys())}")
            print(f"profile completeness: {data.get('profile_completeness')}")
            
            # Analyze the issue
            print("\n" + "="*60)
            print("ISSUE ANALYSIS")
            print("="*60)
            
            if research_completed and research_findings is None:
                print("❌ CONFIRMED ISSUE: research_completed=True but research_findings=null")
                print("   This suggests either:")
                print("   1. Research node ran but hit an exception")
                print("   2. research_findings was overwritten by another node")
                print("   3. State persistence issue between nodes")
                print("   4. Wrong research node is running")
                
                # Check if company name was extracted
                if company_name:
                    print(f"   ✅ Company extraction worked: '{company_name}'")
                    print("   ❌ But research data is missing")
                else:
                    print("   ❌ Company extraction also failed")
                    
            elif research_completed and research_findings:
                print("✅ SUCCESS: Both research_completed and research_findings are present")
                print(f"   Research status: {research_findings.get('status')}")
                print(f"   Company analyzed: {research_findings.get('company_analyzed')}")
                
            elif not research_completed:
                print("ℹ️  Research not completed yet - this may be expected for first turn")
                
            else:
                print("🤔 Unexpected state combination")
            
            # Test follow-up to see if research triggers
            if company_name and not research_completed:
                print("\n" + "="*60)
                print("TESTING FOLLOW-UP TO TRIGGER RESEARCH")
                print("="*60)
                
                followup_data = {
                    "message": "Can you research our business and find our location details?",
                    "contractor_lead_id": data.get("contractor_lead_id"),
                    "session_id": "investigation-session-789"
                }
                
                print("Making follow-up request to trigger research...")
                followup_response = requests.post(url, json=followup_data, timeout=300)
                
                if followup_response.status_code == 200:
                    followup_data = followup_response.json()
                    followup_research_completed = followup_data.get("research_completed")
                    followup_research_findings = followup_data.get("research_findings")
                    
                    print(f"Follow-up research_completed: {followup_research_completed}")
                    print(f"Follow-up research_findings: {followup_research_findings}")
                    
                    if followup_research_completed and followup_research_findings:
                        print("✅ Research triggered successfully on follow-up")
                        return followup_research_findings
                    else:
                        print("❌ Research still not working on follow-up")
                        
            return research_findings
                
        else:
            print(f"[ERROR] Request failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return None

if __name__ == "__main__":
    result = test_research_findings()
    if result:
        print(f"\n✅ INVESTIGATION SUCCESS: Research findings found")
        print(f"Research status: {result.get('status')}")
    else:
        print(f"\n❌ INVESTIGATION RESULT: Research findings missing or null")