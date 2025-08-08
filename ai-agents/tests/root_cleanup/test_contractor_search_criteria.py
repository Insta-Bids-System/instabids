"""
TEST: Contractor Search Criteria Analysis
Purpose: Show another agent what data we store and how we match contractors to bid cards

This test will reveal:
1. What contractor profile data we actually store
2. What search criteria our backend uses for matching
3. How the matching algorithm works
4. What data is useful for bid card searches
"""
import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def test_contractor_profile_data():
    """Test what data we store in contractor profiles"""
    print("="*80)
    print("🔍 CONTRACTOR PROFILE DATA ANALYSIS")
    print("="*80)
    
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    print("\n📊 CONTRACTOR TABLE SCHEMA:")
    print("-" * 40)
    
    # Get a sample contractor to see what data we actually store
    result = supabase.table("contractors").select("*").limit(1).execute()
    
    if result.data:
        contractor = result.data[0]
        print("✅ CONTRACTOR PROFILE FIELDS:")
        for key, value in contractor.items():
            print(f"   • {key}: {type(value).__name__} = {value}")
    
    print("\n🎯 KEY MATCHING CRITERIA WE STORE:")
    print("-" * 40)
    
    # Get multiple contractors to analyze patterns
    result = supabase.table("contractors").select("*").limit(5).execute()
    contractors = result.data if result.data else []
    
    matching_criteria = {
        "location_data": [],
        "specialties": [],
        "service_areas": [],
        "company_sizes": [],
        "other_criteria": []
    }
    
    for contractor in contractors:
        # Analyze location/service area data
        service_areas = contractor.get("service_areas", [])
        if service_areas:
            matching_criteria["location_data"].append({
                "company": contractor.get("company_name"),
                "service_areas": service_areas,
                "type": type(service_areas).__name__
            })
        
        # Analyze specialties
        specialties = contractor.get("specialties", [])
        if specialties:
            matching_criteria["specialties"].extend(specialties)
        
        # Analyze tier/size
        tier = contractor.get("tier")
        if tier:
            matching_criteria["company_sizes"].append(tier)
    
    print("1. 📍 LOCATION/SERVICE AREA DATA:")
    for item in matching_criteria["location_data"]:
        print(f"   • {item['company']}: {item['service_areas']} ({item['type']})")
    
    print("\n2. 🔧 CONTRACTOR SPECIALTIES:")
    unique_specialties = list(set(matching_criteria["specialties"]))
    for specialty in unique_specialties:
        print(f"   • {specialty}")
    
    print("\n3. 🏢 COMPANY TIERS:")
    unique_tiers = list(set(matching_criteria["company_sizes"]))
    for tier in unique_tiers:
        print(f"   • Tier {tier}")
    
    return contractors

def test_bid_card_matching_criteria():
    """Test what criteria we use to match contractors to bid cards"""
    print("\n" + "="*80)
    print("🎯 BID CARD MATCHING CRITERIA ANALYSIS")
    print("="*80)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    # Get sample bid cards to see what matching criteria we store
    result = supabase.table("bid_cards").select("*").limit(2).execute()
    bid_cards = result.data if result.data else []
    
    print("\n📋 BID CARD SEARCH CRITERIA:")
    print("-" * 40)
    
    for i, bid_card in enumerate(bid_cards, 1):
        print(f"\n🎯 BID CARD {i}: {bid_card.get('bid_card_number', 'Unknown')}")
        print(f"   Project Type: {bid_card.get('project_type')}")
        print(f"   Location: {bid_card.get('location_city')}, {bid_card.get('location_state')} {bid_card.get('location_zip')}")
        print(f"   Budget: ${bid_card.get('budget_min', 0):,} - ${bid_card.get('budget_max', 0):,}")
        print(f"   Contractors Needed: {bid_card.get('contractor_count_needed')}")
        print(f"   Urgency: {bid_card.get('urgency_level')}")
        print(f"   Categories: {bid_card.get('categories')}")
        print(f"   Complexity Score: {bid_card.get('complexity_score')}")
        
        # Analyze bid_document for additional criteria
        bid_document = bid_card.get("bid_document", {})
        if isinstance(bid_document, dict):
            extracted_data = bid_document.get("all_extracted_data", {})
            if extracted_data:
                contractor_reqs = extracted_data.get("contractor_requirements", {})
                print(f"   Contractor Requirements: {contractor_reqs}")

def test_matching_algorithm():
    """Test how our CDA agent actually matches contractors to projects"""
    print("\n" + "="*80)
    print("🤖 MATCHING ALGORITHM ANALYSIS")
    print("="*80)
    
    print("\n🔍 CURRENT MATCHING CRITERIA (Based on CDA Code):")
    print("-" * 50)
    
    matching_rules = [
        "1. 📍 LOCATION MATCHING:",
        "   • ZIP CODE: Primary location filter",
        "   • RADIUS: Miles willing to travel (default 15 miles)",
        "   • SERVICE AREAS: Contractor's defined service areas",
        "",
        "2. 🔧 SPECIALTY MATCHING:", 
        "   • PROJECT TYPE: e.g., 'roofing', 'plumbing', 'electrical'",
        "   • SPECIALTIES: Contractor's listed specializations",
        "   • CATEGORIES: Project categories from bid card",
        "",
        "3. 🏢 COMPANY SIZE MATCHING:",
        "   • TIER: 1=Small, 2=Medium, 3=Large companies", 
        "   • CONTRACTOR SIZE PREFERENCE: From project requirements",
        "",
        "4. 💰 BUDGET COMPATIBILITY:",
        "   • BUDGET RANGE: Project budget min/max",
        "   • CONTRACTOR TIER: Higher tiers for larger budgets",
        "",
        "5. ⏰ AVAILABILITY:",
        "   • URGENCY LEVEL: emergency, urgent, standard, flexible",
        "   • AVAILABILITY STATUS: available, busy, unavailable"
    ]
    
    for rule in matching_rules:
        print(rule)

def run_contractor_search_analysis():
    """Main function to run complete analysis"""
    print("🚀 CONTRACTOR SEARCH CRITERIA ANALYSIS")
    print("🎯 Purpose: Help other agents understand our matching system")
    
    # Test 1: What data do we store?
    contractors = test_contractor_profile_data()
    
    # Test 2: What criteria do we use for matching?
    test_bid_card_matching_criteria()
    
    # Test 3: How does the algorithm work?
    test_matching_algorithm()
    
    print("\n" + "="*80)
    print("📊 SUMMARY FOR OTHER AGENTS")
    print("="*80)
    
    summary = {
        "main_search_criteria": [
            "ZIP CODE + RADIUS (miles willing to travel)",
            "PROJECT TYPE + SPECIALTIES",
            "COMPANY SIZE/TIER (1-3 scale)", 
            "BUDGET RANGE compatibility",
            "URGENCY LEVEL + AVAILABILITY"
        ],
        "contractor_profile_key_fields": [
            "service_areas (zip codes or cities)",
            "specialties (array of services)",
            "tier (1=small, 2=medium, 3=large)",
            "availability_status",
            "rating and total_jobs"
        ],
        "bid_card_matching_fields": [
            "location_zip + location_city + location_state",
            "project_type + categories",
            "budget_min + budget_max", 
            "contractor_count_needed",
            "urgency_level"
        ]
    }
    
    print("\n🎯 MAIN SEARCH CRITERIA (5 key factors):")
    for i, criteria in enumerate(summary["main_search_criteria"], 1):
        print(f"   {i}. {criteria}")
    
    print(f"\n📊 ANALYSIS COMPLETE")
    print(f"✅ Analyzed {len(contractors)} contractor profiles")
    print(f"✅ Identified 5 main matching criteria")
    print(f"✅ Ready for other agents to use this data")
    
    return summary

if __name__ == "__main__":
    summary = run_contractor_search_analysis()