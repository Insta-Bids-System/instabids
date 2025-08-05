#!/usr/bin/env python3
"""
REAL CDA TEST - Create actual bid card and run discovery
NO AUTHENTICATION REQUIRED - Everything works without API keys
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import json

sys.path.append(os.path.dirname(__file__))

# Load environment
load_dotenv(override=True)

print("\n" + "="*70)
print("REAL CDA TEST - ACTUAL DATABASE OPERATIONS")
print("="*70)

# Connect to Supabase
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

print("\nSTEP 1: CREATE REAL BID CARD")
print("-"*70)

# Create a real bid card
bid_card_data = {
    "bid_card_number": f"BC-REALTEST-{int(datetime.now().timestamp())}",
    "project_type": "lawn care",
    "urgency_level": "week",
    "location_city": "Coconut Creek",
    "location_state": "FL",
    "location_zip": "33066",
    "budget_min": 100,
    "budget_max": 200,
    "bid_document": {
        "project_overview": {
            "description": "Need monthly lawn care service for my home. Looking for reliable contractors in the area."
        },
        "budget_information": {
            "budget_min": 100,
            "budget_max": 200,
            "notes": "Monthly service"
        },
        "timeline": {
            "urgency_level": "standard",
            "start_date": "ASAP"
        }
    },
    "contractor_count_needed": 5,
    "status": "generated",
    "created_at": datetime.now().isoformat()
}

try:
    # Insert the bid card
    result = supabase.table("bid_cards").insert(bid_card_data).execute()
    if result.data:
        bid_card_id = result.data[0]["id"]
        print(f"[SUCCESS] Created bid card: {bid_card_data['bid_card_number']}")
        print(f"  ID: {bid_card_id}")
        print(f"  Project: {bid_card_data['project_type']}")
        print(f"  Location: {bid_card_data['location_city']}, {bid_card_data['location_state']}")
    else:
        print("Failed to create bid card")
        sys.exit(1)
except Exception as e:
    print(f"Error creating bid card: {e}")
    sys.exit(1)

print("\nSTEP 2: ADD SAMPLE CONTRACTORS TO DATABASE")
print("-"*70)

# Add some sample contractors if they don't exist
sample_contractors = [
    {
        "company_name": "Green Thumb Lawn Care",
        "zip_code": "33066",
        "city": "Coconut Creek",
        "state": "FL",
        "phone": "(954) 555-0001",
        "email": "contact@greenthumb.com",
        "website": "https://greenthumb.com",
        "google_rating": 4.8,
        "google_review_count": 127,
        "specialties": ["lawn care", "landscaping"],
        "created_at": datetime.now().isoformat()
    },
    {
        "company_name": "Sunshine Lawn Services",
        "zip_code": "33067",  # Nearby zip
        "city": "Pompano Beach",
        "state": "FL",
        "phone": "(954) 555-0002",
        "email": "info@sunshinelawn.com",
        "website": "https://sunshinelawn.com",
        "google_rating": 4.6,
        "google_review_count": 89,
        "specialties": ["lawn care", "tree trimming"],
        "created_at": datetime.now().isoformat()
    },
    {
        "company_name": "Premium Lawn Masters",
        "zip_code": "33064",  # Within radius
        "city": "Parkland",
        "state": "FL", 
        "phone": "(954) 555-0003",
        "email": "service@lawnmasters.com",
        "website": "https://lawnmasters.com",
        "google_rating": 4.9,
        "google_review_count": 203,
        "specialties": ["lawn care", "pest control"],
        "created_at": datetime.now().isoformat()
    }
]

# Insert into potential_contractors table
contractor_ids = []
for contractor in sample_contractors:
    try:
        # Check if already exists
        existing = supabase.table("potential_contractors")\
            .select("id")\
            .eq("company_name", contractor["company_name"])\
            .execute()
        
        if not existing.data:
            result = supabase.table("potential_contractors").insert(contractor).execute()
            if result.data:
                contractor_ids.append(result.data[0]["id"])
                print(f"[OK] Added contractor: {contractor['company_name']} ({contractor['zip_code']})")
        else:
            contractor_ids.append(existing.data[0]["id"])
            print(f"  Contractor exists: {contractor['company_name']}")
    except Exception as e:
        print(f"  Error adding contractor: {e}")

print("\nSTEP 3: RUN CDA WITH RADIUS SEARCH")
print("-"*70)

# Import and run CDA
from agents.cda.agent import ContractorDiscoveryAgent

agent = ContractorDiscoveryAgent()

try:
    # Run discovery with 15-mile radius
    print(f"Running CDA for bid card {bid_card_id} with 15-mile radius...")
    result = agent.discover_contractors(
        bid_card_id=bid_card_id,
        contractors_needed=3,
        radius_miles=15
    )
    
    if result["success"]:
        print("\n[OK] DISCOVERY SUCCESSFUL!")
        print(f"  Total contractors found: {result['total_found']}")
        print(f"  - Tier 1 (Internal): {result['tier_results']['tier1_internal']}")
        print(f"  - Tier 2 (Previous): {result['tier_results']['tier2_previous']}")
        print(f"  - Tier 3 (Web): {result['tier_results']['tier3_web']}")
        
        if result.get("selected_contractors"):
            print(f"\n  Selected {len(result['selected_contractors'])} contractors:")
            for contractor in result["selected_contractors"]:
                print(f"    - {contractor.get('company_name', 'Unknown')}")
                print(f"      Score: {contractor.get('match_score', 0)}")
                print(f"      Location: {contractor.get('city', 'Unknown')}, {contractor.get('state', '')} {contractor.get('zip_code', '')}")
                print(f"      Rating: {contractor.get('google_rating', 'N/A')} ({contractor.get('google_review_count', 0)} reviews)")
    else:
        print(f"\n[FAIL] Discovery failed: {result.get('error')}")
        
except Exception as e:
    print(f"\n[FAIL] Exception during discovery: {e}")
    import traceback
    traceback.print_exc()

print("\nSTEP 4: VERIFY DATABASE STORAGE")
print("-"*70)

# Check if contractors were stored
try:
    # Check contractor_bid_matches table
    matches = supabase.table("contractor_bid_matches")\
        .select("*")\
        .eq("bid_card_id", bid_card_id)\
        .execute()
    
    if matches.data:
        print(f"[OK] Found {len(matches.data)} contractor matches stored:")
        for match in matches.data:
            print(f"  - {match.get('company_name')} (Score: {match.get('match_score')})")
    else:
        print("  No contractor matches stored (table may not exist)")
        
    # Check discovery_runs
    runs = supabase.table("discovery_runs")\
        .select("*")\
        .eq("bid_card_id", bid_card_id)\
        .execute()
    
    if runs.data:
        print(f"\n[OK] Discovery run logged: {runs.data[0]['id']}")
    else:
        print("\n  No discovery run logged")
        
except Exception as e:
    print(f"  Error checking storage: {e}")

print("\n" + "="*70)
print("TEST COMPLETE - CHECK DATABASE FOR RESULTS")
print("="*70)
print(f"Bid Card ID: {bid_card_id}")
print(f"Bid Card Number: {bid_card_data['bid_card_number']}")
print("\nYou can verify in Supabase:")
print("1. Check bid_cards table for the new bid card")
print("2. Check potential_contractors for the test contractors")
print("3. Check contractor_bid_matches for selected contractors (if table exists)")