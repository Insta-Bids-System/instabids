"""
Direct test of account creation functionality
This bypasses the conversation flow and tests the account creation directly
"""

import asyncio
import requests
from config.service_urls import get_backend_url

async def test_direct_account_creation():
    """Test account creation directly through COIA tools"""
    print("\n" + "="*80)
    print("DIRECT ACCOUNT CREATION TEST")
    print("="*80)
    
    # Test contractor profile data (what would be gathered from conversation)
    contractor_profile = {
        "company_name": "JM Holiday Lighting",
        "email": "justin@jmholidaylighting.com", 
        "phone": "(954) 555-0123",
        "address": "Fort Lauderdale, Florida 33301",
        "primary_trade": "electrical",
        "years_in_business": 8,
        "specializations": ["holiday_lighting", "christmas_lighting", "residential", "commercial"],
        "service_areas": ["Broward County", "Palm Beach County"],
        "license_verified": True,
        "insurance_verified": True,
        "team_size": "small",
        "minimum_project_size": 500,
        "preferred_project_types": ["holiday_lighting"]
    }
    
    print("[TEST] Testing account creation with profile:")
    for key, value in contractor_profile.items():
        print(f"  {key}: {value}")
    
    try:
        # Import and test the COIA tools directly
        import sys
        sys.path.append("agents/coia")
        from tools import coia_tools
        
        print("\n[TEST] Creating account directly through COIA tools...")
        
        async with coia_tools as tools:
            account_result = await tools.create_contractor_account(contractor_profile)
            
            if account_result.get("success"):
                account = account_result["account"]
                print("\n[SUCCESS] Account created successfully!")
                print(f"  Company: {account['company_name']}")
                print(f"  Username: {account['username']}")
                print(f"  Email: {account['email']}")
                print(f"  Password: {account['password']}")
                print(f"  Status: {account['availability_status']}")
                print(f"  Tier: {account['tier']}")
                
                # Now verify in database
                print("\n[TEST] Verifying account exists in database...")
                response = requests.get(f"{get_backend_url()}/api/contractor-management/contractors")
                
                if response.status_code == 200:
                    contractors = response.json().get('contractors', [])
                    found = False
                    for contractor in contractors:
                        if contractor.get('company_name') == 'JM Holiday Lighting':
                            print(f"[SUCCESS] Found contractor in database!")
                            print(f"  Database ID: {contractor.get('id')}")
                            print(f"  Company: {contractor.get('company_name')}")
                            print(f"  Email: {contractor.get('email')}")
                            print(f"  Phone: {contractor.get('phone')}")
                            found = True
                            break
                    
                    if not found:
                        print("[WARNING] Contractor not found in database API")
                    
                    return account
                else:
                    print(f"[ERROR] Database check failed: {response.text}")
            else:
                print(f"[ERROR] Account creation failed: {account_result}")
                return None
    
    except Exception as e:
        print(f"[ERROR] Direct account creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run the direct account creation test"""
    account = await test_direct_account_creation()
    
    if account:
        print(f"\n[CHRISTMAS TREE] SUCCESS! JM Holiday Lighting account created:")
        print(f"  Username: {account['username']}")
        print(f"  Password: {account['password']}")
        print(f"  Email: {account['email']}")
    else:
        print(f"\n[ERROR] Account creation test failed")

if __name__ == "__main__":
    asyncio.run(main())