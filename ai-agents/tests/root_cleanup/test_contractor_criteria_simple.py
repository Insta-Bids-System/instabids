"""
TEST: Contractor Search Criteria Analysis
Purpose: Show another agent what data we store and how we match contractors to bid cards
"""
import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*80)
    print("CONTRACTOR SEARCH CRITERIA ANALYSIS")
    print("="*80)
    
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    print("\n1. CONTRACTOR PROFILE DATA WE STORE:")
    print("-" * 50)
    
    # Get sample contractor
    result = supabase.table("contractors").select("*").limit(1).execute()
    if result.data:
        contractor = result.data[0]
        print("CONTRACTOR FIELDS:")
        for key, value in contractor.items():
            if key in ['id', 'user_id', 'created_at', 'updated_at']:
                continue  # Skip system fields
            print(f"   • {key}: {value}")
    
    print("\n2. BID CARD MATCHING CRITERIA:")
    print("-" * 50)
    
    # Get sample bid card
    result = supabase.table("bid_cards").select("*").limit(1).execute()
    if result.data:
        bid_card = result.data[0]
        print("BID CARD SEARCH FIELDS:")
        matching_fields = [
            'project_type', 'location_city', 'location_state', 'location_zip',
            'budget_min', 'budget_max', 'contractor_count_needed', 
            'urgency_level', 'categories', 'complexity_score'
        ]
        for field in matching_fields:
            value = bid_card.get(field)
            if value is not None:
                print(f"   • {field}: {value}")
    
    print("\n3. MAIN SEARCH CRITERIA (5 KEY FACTORS):")
    print("-" * 50)
    print("   1. ZIP CODE + RADIUS - Location and miles willing to travel")
    print("   2. PROJECT TYPE + SPECIALTIES - Type of work and skills")  
    print("   3. COMPANY SIZE/TIER - Small (1), Medium (2), Large (3)")
    print("   4. BUDGET RANGE - Project budget compatibility")
    print("   5. URGENCY + AVAILABILITY - Timeline and contractor availability")
    
    print("\n4. DETAILED BREAKDOWN:")
    print("-" * 50)
    
    print("CONTRACTOR PROFILE KEY FIELDS:")
    print("   • service_areas: ZIP codes or cities they serve")
    print("   • specialties: Array of services (e.g., ['roofing', 'repair'])")
    print("   • tier: Company size (1=owner-operator, 2=small team, 3=large company)")
    print("   • availability_status: 'available', 'busy', 'unavailable'")
    print("   • rating: Customer rating (0-5)")
    print("   • total_jobs: Number of completed projects")
    
    print("\nBID CARD MATCHING FIELDS:")
    print("   • location_zip + location_city + location_state: Project location")
    print("   • project_type: Main category (e.g., 'roofing', 'plumbing')")
    print("   • categories: Detailed project categories array")
    print("   • budget_min + budget_max: Budget range")
    print("   • contractor_count_needed: How many contractors needed")
    print("   • urgency_level: 'emergency', 'urgent', 'standard', 'flexible'")
    
    print("\n5. MATCHING ALGORITHM LOGIC:")
    print("-" * 50)
    print("   Step 1: Filter by location (ZIP + radius)")
    print("   Step 2: Match specialties to project type")
    print("   Step 3: Check company size preference")
    print("   Step 4: Verify budget compatibility")
    print("   Step 5: Check availability for urgency level")
    
    print("\n" + "="*80)
    print("SUMMARY FOR OTHER AGENTS")
    print("="*80)
    print("The backend uses these 5 main criteria to find matching contractors:")
    print("1. LOCATION: ZIP code + travel radius (default 15 miles)")
    print("2. SPECIALTIES: Project type must match contractor specialties") 
    print("3. COMPANY SIZE: Tier 1-3 based on project complexity/budget")
    print("4. BUDGET: Contractor tier should match budget range")
    print("5. AVAILABILITY: Urgency level vs contractor availability")
    print("\nThis data is stored in 'contractors' table and matched against")
    print("'bid_cards' table using the CDA (Contractor Discovery Agent)")

if __name__ == "__main__":
    main()