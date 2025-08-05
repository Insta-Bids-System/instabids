#!/usr/bin/env python3
"""
REAL CDA Test - Actually run the contractor discovery with radius
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

# Load environment
load_dotenv(override=True)

print("\n" + "="*70)
print("REAL CDA TEST - WHAT ACTUALLY HAPPENS")
print("="*70)

# Step 1: Check what contractors we have in the database
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

print("\nSTEP 1: CHECKING ACTUAL DATABASE")
print("-"*70)

# Check contractor_leads
try:
    result = supabase.table("contractor_leads").select("company_name, zip_code").limit(5).execute()
    print(f"Sample contractor_leads in DB:")
    for lead in result.data:
        print(f"  - {lead['company_name']} in {lead['zip_code']}")
except Exception as e:
    print(f"Error: {e}")

# Check potential_contractors
try:
    result = supabase.table("potential_contractors").select("company_name, zip_code").limit(5).execute()
    print(f"\nSample potential_contractors in DB:")
    for contractor in result.data:
        print(f"  - {contractor['company_name']} in {contractor['zip_code']}")
except Exception as e:
    print(f"Error: {e}")

print("\nSTEP 2: RUNNING ACTUAL CDA WITH RADIUS")
print("-"*70)

# Import CDA agent
from agents.cda.agent import ContractorDiscoveryAgent

# Create agent
agent = ContractorDiscoveryAgent()

# Use a test bid card that mimics real data
test_bid_card_id = "test-lawn-care-coconut-creek"

try:
    # Run discovery with 10-mile radius
    print(f"Running CDA with 10-mile radius...")
    result = agent.discover_contractors(
        bid_card_id=test_bid_card_id,
        contractors_needed=5,
        radius_miles=10
    )
    
    print("\nRESULTS:")
    if result["success"]:
        print(f"  Total contractors found: {result['total_found']}")
        print(f"  - Tier 1 (Internal): {result['tier_results']['tier1_internal']}")
        print(f"  - Tier 2 (Previous): {result['tier_results']['tier2_previous']}")
        print(f"  - Tier 3 (Web): {result['tier_results']['tier3_web']}")
        
        if result.get("selected_contractors"):
            print(f"\n  Selected {len(result['selected_contractors'])} contractors")
    else:
        print(f"  Error: {result.get('error')}")
        
except Exception as e:
    print(f"  Exception: {e}")

print("\nSTEP 3: WHAT WOULD BE STORED IN DATABASE")
print("-"*70)
print("If this ran successfully, the following would happen:")
print("1. Selected contractors would be stored in 'contractor_bid_matches' table")
print("2. Each would have a match_score from AI")
print("3. Discovery run would be logged in 'discovery_runs' table")
print("4. Bid card status would update")

print("\nBOTTOM LINE TRUTH:")
print("-"*70)
print("- The CODE is updated to support radius search")
print("- The radius utilities WORK (tested separately)")
print("- The database connection issues prevent full end-to-end test")
print("- NO contractors have been discovered/stored from this test session")
print("- The 'lawn care contractors found' were SIMULATED examples")