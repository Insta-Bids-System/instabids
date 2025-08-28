"""
Test TurfGrass Artificial Solutions account creation directly
"""

import asyncio
import requests

async def test_turfgrass_account_creation():
    """Test account creation for TurfGrass directly through COIA tools"""
    print("\n" + "="*80)
    print("TURFGRASS ARTIFICIAL SOLUTIONS ACCOUNT CREATION TEST")
    print("="*80)
    
    # TurfGrass contractor profile data
    contractor_profile = {
        "company_name": "TurfGrass Artificial Solutions",
        "email": "info@turfgrassartificialsolutions.com",
        "phone": "(561) 555-0199",
        "address": "Boca Raton, Florida 33431",
        "primary_trade": "landscaping",
        "years_in_business": 12,
        "specializations": ["artificial_turf", "synthetic_grass", "landscaping", "sports_fields"],
        "service_areas": ["Palm Beach County", "Broward County", "Miami-Dade County"],
        "license_verified": True,
        "insurance_verified": True,
        "team_size": "medium",
        "minimum_project_size": 1000,
        "preferred_project_types": ["artificial_turf", "residential_landscaping"]
    }
    
    print("[TEST] Testing TurfGrass account creation with profile:")
    for key, value in contractor_profile.items():
        print(f"  {key}: {value}")
    
    try:
        # Import and test the COIA tools directly
        import sys
        sys.path.append("agents/coia")
        from tools import coia_tools
        
        print("\n[TEST] Creating TurfGrass account directly through COIA tools...")
        
        async with coia_tools as tools:
            account_result = await tools.create_contractor_account(contractor_profile)
            
            if account_result.get("success"):
                account = account_result["account"]
                print("\n[SUCCESS] TurfGrass account created successfully!")
                print(f"  Company: {account['company_name']}")
                print(f"  Username: {account['username']}")
                print(f"  Email: {account['email']}")
                print(f"  Password: {account['password']}")
                print(f"  Status: {account['availability_status']}")
                print(f"  Tier: {account['tier']}")
                
                return account
            else:
                print(f"[ERROR] TurfGrass account creation failed: {account_result}")
                return None
    
    except Exception as e:
        print(f"[ERROR] TurfGrass account creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run the TurfGrass account creation test"""
    account = await test_turfgrass_account_creation()
    
    if account:
        print(f"\n[SUCCESS] TurfGrass Artificial Solutions account created!")
        print(f"  Username: {account['username']}")
        print(f"  Password: {account['password']}")
        print(f"  Email: {account['email']}")
    else:
        print(f"\n[ERROR] TurfGrass account creation test failed")

if __name__ == "__main__":
    asyncio.run(main())