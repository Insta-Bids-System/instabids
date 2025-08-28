"""
FULL PIPELINE INVESTIGATION
==========================

Test the complete COIA pipeline to see what's actually happening:
1. Google API ✅ (already confirmed working)
2. Tavily website scraping 
3. Profile field completion
4. Bid card UI presentation

This will show us exactly where the pipeline breaks down.
"""

import requests
import json
import time
from config.service_urls import get_backend_url

BACKEND_URL = get_backend_url()

def test_pipeline_stages():
    """Test each stage of the pipeline individually"""
    
    print("FULL PIPELINE INVESTIGATION")
    print("=" * 50)
    
    # Generate unique session
    import uuid
    contractor_lead_id = f"landing-{str(uuid.uuid4())[:8]}"
    print(f"Using contractor_lead_id: {contractor_lead_id}")
    
    # Stage 1: Initial contact with detailed company info
    print("\nSTAGE 1: Initial Contact with Rich Company Data")
    print("-" * 50)
    
    stage1_data = {
        "message": "Hi, I'm John Smith from TurfGrass Artificial Solutions. We're based in Miami and specialize in artificial grass installation, landscape design, and outdoor lighting. We've been in business for 15 years with 12 employees. Our website is tropicalturf.com and we're licensed and insured. I'd like to join your platform to find more commercial and residential projects.",
        "session_id": contractor_lead_id,
        "contractor_lead_id": contractor_lead_id
    }
    
    print("Sending rich company data...")
    response1 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage1_data)
    
    if response1.status_code != 200:
        print(f"STAGE 1 FAILED: {response1.status_code}")
        return False
        
    result1 = response1.json()
    response_text = result1.get('response', '')
    print(f"Response length: {len(response_text)} characters")
    
    # Check what was extracted
    extracted_data = [
        'turfgrass' in response_text.lower(),
        'artificial' in response_text.lower(),
        'miami' in response_text.lower(),
        'tropicalturf.com' in response_text.lower(),
        '15 years' in response_text.lower() or 'fifteen' in response_text.lower(),
        '12 employees' in response_text.lower() or 'twelve' in response_text.lower()
    ]
    
    extraction_score = sum(extracted_data)
    print(f"Data extraction: {extraction_score}/6 items captured")
    
    # Stage 2: Research trigger - check what tools are called
    print("\nSTAGE 2: Research Trigger - Tool Investigation")
    print("-" * 50)
    
    stage2_data = {
        "message": "Yes, that's all correct! Please research my company website and gather all the information you can to complete my contractor profile. I want to make sure you have everything for my account.",
        "session_id": contractor_lead_id,
        "contractor_lead_id": contractor_lead_id
    }
    
    print("Triggering comprehensive research...")
    start_time = time.time()
    response2 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage2_data)
    research_time = time.time() - start_time
    
    print(f"Research took: {research_time:.2f} seconds")
    
    if response2.status_code != 200:
        print(f"STAGE 2 FAILED: {response2.status_code}")
        return False
        
    result2 = response2.json()
    response_text = result2.get('response', '')
    
    # Check for research indicators
    research_indicators = [
        'google' in response_text.lower(),
        'website' in response_text.lower(),
        'research' in response_text.lower(),
        'found' in response_text.lower(),
        'information' in response_text.lower(),
        'profile' in response_text.lower()
    ]
    
    research_score = sum(research_indicators)
    print(f"Research indicators: {research_score}/6 found")
    
    # Check for specific website data that should be scraped
    website_data = [
        'address' in response_text.lower(),
        'phone' in response_text.lower() or 'contact' in response_text.lower(),
        'email' in response_text.lower(),
        'services' in response_text.lower(),
        'projects' in response_text.lower() or 'portfolio' in response_text.lower(),
        'testimonials' in response_text.lower() or 'reviews' in response_text.lower(),
        'certifications' in response_text.lower() or 'license' in response_text.lower(),
        'years' in response_text.lower() or 'experience' in response_text.lower()
    ]
    
    website_score = sum(website_data)
    print(f"Website data extracted: {website_score}/8 fields")
    print(f"   Address: {'YES' if website_data[0] else 'NO'}")
    print(f"   Contact: {'YES' if website_data[1] else 'NO'}")
    print(f"   Email: {'YES' if website_data[2] else 'NO'}")
    print(f"   Services: {'YES' if website_data[3] else 'NO'}")
    print(f"   Portfolio: {'YES' if website_data[4] else 'NO'}")
    print(f"   Reviews: {'YES' if website_data[5] else 'NO'}")
    print(f"   Licenses: {'YES' if website_data[6] else 'NO'}")
    print(f"   Experience: {'YES' if website_data[7] else 'NO'}")
    
    # Stage 3: Profile completion check
    print("\nSTAGE 3: Profile Completion Analysis")
    print("-" * 50)
    
    stage3_data = {
        "message": "Great! Now show me my complete contractor profile with all the information you've gathered.",
        "session_id": contractor_lead_id,
        "contractor_lead_id": contractor_lead_id
    }
    
    print("Requesting profile summary...")
    response3 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage3_data)
    
    if response3.status_code != 200:
        print(f"STAGE 3 FAILED: {response3.status_code}")
        return False
        
    result3 = response3.json()
    response_text = result3.get('response', '')
    
    # Check profile completeness (66 contractor fields mentioned in the code)
    profile_fields = [
        'company' in response_text.lower(),
        'location' in response_text.lower() or 'address' in response_text.lower(),
        'phone' in response_text.lower(),
        'email' in response_text.lower(),
        'website' in response_text.lower(),
        'services' in response_text.lower(),
        'specialties' in response_text.lower() or 'specializations' in response_text.lower(),
        'license' in response_text.lower() or 'certifications' in response_text.lower(),
        'insurance' in response_text.lower(),
        'employees' in response_text.lower() or 'team' in response_text.lower(),
        'years' in response_text.lower() or 'experience' in response_text.lower(),
        'reviews' in response_text.lower() or 'rating' in response_text.lower()
    ]
    
    profile_score = sum(profile_fields)
    print(f"Profile completeness: {profile_score}/12 major fields")
    
    # Stage 4: Bid card presentation
    print("\nSTAGE 4: Bid Card UI Presentation")
    print("-" * 50)
    
    stage4_data = {
        "message": "Perfect! Now show me some relevant projects I can bid on.",
        "session_id": contractor_lead_id,
        "contractor_lead_id": contractor_lead_id
    }
    
    print("Requesting bid cards...")
    response4 = requests.post(f"{BACKEND_URL}/api/coia/landing", json=stage4_data)
    
    if response4.status_code != 200:
        print(f"STAGE 4 FAILED: {response4.status_code}")
        return False
        
    result4 = response4.json()
    response_text = result4.get('response', '')
    
    # Check for actual bid card UI elements
    ui_elements = [
        '**' in response_text,  # Bold formatting for titles
        'project' in response_text.lower(),
        '$' in response_text or 'budget' in response_text.lower(),
        'timeline' in response_text.lower() or 'deadline' in response_text.lower(),
        'location' in response_text.lower(),
        'bid' in response_text.lower(),
        'details' in response_text.lower(),
        'more' in response_text.lower()
    ]
    
    ui_score = sum(ui_elements)
    print(f"UI presentation elements: {ui_score}/8 found")
    print(f"   Formatted titles: {'YES' if ui_elements[0] else 'NO'}")
    print(f"   Project info: {'YES' if ui_elements[1] else 'NO'}")
    print(f"   Budget info: {'YES' if ui_elements[2] else 'NO'}")
    print(f"   Timeline info: {'YES' if ui_elements[3] else 'NO'}")
    print(f"   Location info: {'YES' if ui_elements[4] else 'NO'}")
    print(f"   Bid actions: {'YES' if ui_elements[5] else 'NO'}")
    print(f"   Detail links: {'YES' if ui_elements[6] else 'NO'}")
    print(f"   Navigation: {'YES' if ui_elements[7] else 'NO'}")
    
    # FINAL ANALYSIS
    print("\n" + "=" * 50)
    print("PIPELINE ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"Stage 1 - Data Extraction: {extraction_score}/6 fields")
    print(f"Stage 2 - Website Research: {website_score}/8 fields")
    print(f"Stage 3 - Profile Completion: {profile_score}/12 fields")
    print(f"Stage 4 - Bid Card UI: {ui_score}/8 elements")
    
    # Calculate where the pipeline breaks down
    stage_scores = [extraction_score/6, website_score/8, profile_score/12, ui_score/8]
    
    print(f"\nPERCENTAGE COMPLETION:")
    print(f"Data Extraction: {stage_scores[0]*100:.0f}%")
    print(f"Website Research: {stage_scores[1]*100:.0f}%")
    print(f"Profile Completion: {stage_scores[2]*100:.0f}%")  
    print(f"Bid Card UI: {stage_scores[3]*100:.0f}%")
    
    # Identify the bottleneck
    min_score_idx = stage_scores.index(min(stage_scores))
    stage_names = ["Data Extraction", "Website Research", "Profile Completion", "Bid Card UI"]
    
    print(f"\nBOTTLENECK IDENTIFIED: {stage_names[min_score_idx]} ({stage_scores[min_score_idx]*100:.0f}%)")
    
    if min(stage_scores) < 0.5:
        print("CRITICAL ISSUE: Pipeline failing at this stage")
    elif min(stage_scores) < 0.7:
        print("MODERATE ISSUE: Pipeline partially working")
    else:
        print("PIPELINE MOSTLY FUNCTIONAL: Minor optimization needed")
    
    return min(stage_scores) >= 0.5

if __name__ == "__main__":
    success = test_pipeline_stages()
    exit(0 if success else 1)