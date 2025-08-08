"""
Test COIA Research Mode with Real Business Discovery
Test the complete pipeline: Message → Research Mode → Website/Google → Profile Fill
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the unified COIA system
from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_landing_page
from agents.coia.supabase_checkpointer_simple import create_supabase_checkpointer

async def test_complete_coia_research():
    """Test COIA with Turf Grass Artificial Solutions - REAL business"""
    
    print("=" * 80)
    print("TESTING COIA COMPLETE RESEARCH SYSTEM")
    print("Testing with REAL business: Turf Grass Artificial Solutions")
    print("=" * 80)
    
    try:
        # Initialize COIA system
        print("\n1. INITIALIZING COIA SYSTEM...")
        checkpointer = await create_supabase_checkpointer()
        coia_app = await create_unified_coia_system(checkpointer)
        print("✅ COIA system initialized")
        
        # Test message that should trigger research mode
        contractor_message = "Hi, I'm from Turf Grass Artificial Solutions. We're a landscaping company based in South Florida."
        session_id = f"test_research_{int(asyncio.get_event_loop().time())}"
        
        print(f"\n2. SENDING CONTRACTOR MESSAGE...")
        print(f"Message: {contractor_message}")
        print(f"Session: {session_id}")
        
        # Process through COIA landing page (unified system)
        result = await invoke_coia_landing_page(
            app=coia_app,
            user_message=contractor_message,
            session_id=session_id,
            contractor_lead_id=session_id
        )
        
        print(f"\n3. COIA PROCESSING RESULTS:")
        print(f"Current Mode: {result.get('current_mode', 'unknown')}")
        print(f"Research Completed: {result.get('research_completed', False)}")
        print(f"Website Research: {result.get('website_research_status', 'unknown')}")
        print(f"Response: {result.get('response', 'No response')[:200]}...")
        
        # Check contractor profile data
        contractor_profile = result.get("contractor_profile", {})
        print(f"\n4. EXTRACTED PROFILE DATA:")
        
        critical_fields = [
            "company_name",
            "main_service_type", 
            "business_size_category",
            "service_subtypes",
            "zip_codes",
            "website",
            "phone",
            "google_rating"
        ]
        
        for field in critical_fields:
            value = contractor_profile.get(field)
            if value:
                print(f"  ✅ {field}: {value}")
            else:
                print(f"  ❌ {field}: NOT FOUND")
        
        # Check research findings
        research_findings = result.get("research_findings", {})
        if research_findings:
            print(f"\n5. RESEARCH FINDINGS:")
            for key, value in research_findings.items():
                print(f"  {key}: {value}")
        else:
            print(f"\n5. RESEARCH FINDINGS: None found")
        
        # Test if research was actually triggered
        current_mode = result.get('current_mode')
        if current_mode == 'research':
            print(f"\n✅ SUCCESS: Research mode was triggered!")
            print("COIA detected business name and should be researching...")
        elif contractor_profile.get('website'):
            print(f"\n✅ SUCCESS: Website found in profile!")
            print(f"Website: {contractor_profile['website']}")
        else:
            print(f"\n❌ ISSUE: Research not triggered or completed")
            print(f"Current mode: {current_mode}")
        
        print(f"\n6. PROFILE COMPLETENESS:")
        completeness = result.get("profile_completeness", 0)
        print(f"Profile {completeness}% complete")
        
        if completeness >= 50:
            print("✅ Good profile completion rate")
        else:
            print("❌ Low profile completion - needs more data")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("COIA RESEARCH TEST SUMMARY")
        print(f"=" * 80)
        
        has_company = bool(contractor_profile.get("company_name"))
        has_website = bool(contractor_profile.get("website"))
        has_service_type = bool(contractor_profile.get("main_service_type"))
        has_size = bool(contractor_profile.get("business_size_category"))
        
        print(f"✅ Company Name Extracted: {has_company}")
        print(f"✅ Website Discovered: {has_website}") 
        print(f"✅ Service Type Identified: {has_service_type}")
        print(f"✅ Business Size Categorized: {has_size}")
        
        if all([has_company, has_service_type, has_size]):
            print(f"\n🎉 SUCCESS: COIA can extract critical matching fields!")
            print("Agent 2 backend can use this data for bid card matching")
        else:
            print(f"\n❌ NEEDS WORK: Missing critical fields for matching")
            print("More development needed for complete profile automation")
            
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_complete_coia_research())