#!/usr/bin/env python3
"""
Test contractor creation without password fields
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coia.tools import COIATools
from database_simple import db

async def test_contractor_creation():
    """Test creating a contractor without password fields"""
    print("\n=== Testing Contractor Creation (No Password Fields) ===\n")
    
    # Initialize tools
    tools = COIATools()
    
    # Test contractor profile
    test_profile = {
        "company_name": "Test Contractor LLC",
        "email": "test@contractor.com",
        "phone": "(555) 123-4567",
        "contact_name": "John Test",
        "address": "123 Test St",
        "city": "Fort Lauderdale",
        "state": "FL",
        "zip_code": "33301",
        "website": "https://testcontractor.com",
        "specialties": ["Plumbing", "HVAC"],
        "years_in_business": 10,
        "estimated_employees": "10-25",
        "service_areas": ["Fort Lauderdale", "Miami", "Boca Raton"],
        "insurance_verified": True,
        "license_verified": True,
        "bonded": True,
        "rating": 4.8,
        "review_count": 125
    }
    
    print("Creating contractor with profile:")
    print(f"  Company: {test_profile['company_name']}")
    print(f"  Email: {test_profile['email']}")
    print(f"  Phone: {test_profile['phone']}")
    
    try:
        # Create contractor account
        result = await tools.create_contractor_account(test_profile)
        
        if result.get("success"):
            contractor_id = result.get("account", {}).get("id")
            print(f"\n[SUCCESS] Contractor created with ID: {contractor_id}")
            
            # Verify in database
            print("\nVerifying in database...")
            contractor = db.client.table("contractors").select("*").eq("id", contractor_id).execute()
            
            if contractor.data:
                print("[SUCCESS] Contractor found in database!")
                print(f"  Company: {contractor.data[0].get('company_name')}")
                print(f"  Email: {contractor.data[0].get('email')}")
                print(f"  Tier: {contractor.data[0].get('tier')}")
                print(f"  Status: {contractor.data[0].get('availability_status')}")
                
                # Check that no password fields exist
                if 'password' in contractor.data[0] or 'temporary_password' in contractor.data[0]:
                    print("\n[ERROR] Password fields found in database!")
                else:
                    print("\n[VERIFIED] No password fields in database")
            else:
                print("[ERROR] Contractor not found in database")
        else:
            print(f"\n[ERROR] Failed to create contractor: {result.get('error')}")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_contractor_creation())