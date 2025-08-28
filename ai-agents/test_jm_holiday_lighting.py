#!/usr/bin/env python3
"""
Test COIA with JM Holiday Lighting to prove database save works
"""

import asyncio
import sys
import os
sys.path.append('.')

async def test_jm_holiday_lighting():
    print("Testing COIA with JM Holiday Lighting in South Florida...")
    print("-" * 60)
    
    from agents.coia.tools import COIATools
    
    # Test data for JM Holiday Lighting
    company_name = "JM Holiday Lighting"
    
    # Mock Google data for a holiday lighting company
    google_data = {
        "success": True,
        "company_name": company_name,
        "phone": "(954) 555-8888",
        "address": "456 Holiday Way, Boca Raton, FL 33432",
        "website": "https://jmholidaylighting.com",
        "rating": 4.8,
        "review_count": 42,
        "place_id": "jm_holiday_place_id"
    }
    
    # Mock web data  
    web_data = {
        "extracted_info": {
            "services": ["Holiday Lighting Installation", "Christmas Lights", "Event Lighting"],
            "years_in_business": 5,
            "employees": 8,
            "business_description": "Professional holiday lighting installation in South Florida",
            "contact_methods": {
                "emails": ["info@jmholidaylighting.com"],
                "phones": ["(954) 555-8888"]
            }
        }
    }
    
    # Mock license data
    license_data = {
        "licenses": [{
            "number": "FL789012",
            "state": "FL"
        }]
    }
    
    print(f"1. Building profile for: {company_name}")
    print("-" * 60)
    
    # Test the tools
    async with COIATools() as tools:
        profile = await tools.build_contractor_profile(
            company_name=company_name,
            google_data=google_data,
            web_data=web_data,
            license_data=license_data
        )
        
        print(f"   Profile completeness: {profile.get('completeness_score', 0):.1f}%")
        print(f"   Data completeness: {profile.get('data_completeness', 0):.1f}%")
        print(f"   Lead score: {profile.get('lead_score', 0):.1f}")
        
        if profile.get('database_saved'):
            print(f"\n2. DATABASE SAVE SUCCESS!")
            print(f"   Contractor ID: {profile.get('contractor_lead_id')}")
            print(f"   Saved at: {profile.get('saved_at')}")
            
            # Verify with database query
            print(f"\n3. Verifying in database...")
            print("-" * 60)
            try:
                from database_simple import db
                contractor_id = profile.get('contractor_lead_id')
                
                # Query contractor_leads table
                result = db.client.table("contractor_leads").select("*").eq("id", contractor_id).execute()
                
                if result.data:
                    saved_record = result.data[0]
                    print(f"   FOUND IN DATABASE!")
                    print(f"   - Company: {saved_record.get('company_name')}")
                    print(f"   - Phone: {saved_record.get('phone')}")
                    print(f"   - Email: {saved_record.get('email')}")
                    print(f"   - Website: {saved_record.get('website')}")
                    print(f"   - Address: {saved_record.get('address')}")
                    print(f"   - City: {saved_record.get('city')}")
                    print(f"   - State: {saved_record.get('state')}")
                    print(f"   - Rating: {saved_record.get('rating')}")
                    print(f"   - Review Count: {saved_record.get('review_count')}")
                    print(f"   - Specialties: {saved_record.get('specialties')}")
                    print(f"   - Years in Business: {saved_record.get('years_in_business')}")
                    print(f"   - License Number: {saved_record.get('license_number')}")
                    print(f"   - License Verified: {saved_record.get('license_verified')}")
                    print(f"   - Data Completeness: {saved_record.get('data_completeness')}%")
                    print(f"   - Lead Score: {saved_record.get('lead_score')}")
                    print(f"   - Source: {saved_record.get('source')}")
                    print(f"   - Created At: {saved_record.get('created_at')}")
                    
                    # Count how many fields are filled
                    filled_fields = len([k for k, v in saved_record.items() 
                                        if v is not None and v != '' and v != [] and v != {}])
                    print(f"\n   TOTAL FILLED FIELDS: {filled_fields} out of 49")
                    
                    return True
                else:
                    print(f"   ERROR: Not found in database!")
                    return False
                    
            except Exception as e:
                print(f"   Database verification error: {e}")
                return False
        else:
            print(f"\n   DATABASE SAVE FAILED!")
            if profile.get('database_error'):
                print(f"   Error: {profile.get('database_error')}")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("COIA DATABASE SAVE VERIFICATION TEST")
    print("Testing with: JM Holiday Lighting in South Florida")
    print("=" * 60)
    print()
    
    success = asyncio.run(test_jm_holiday_lighting())
    
    print("\n" + "=" * 60)
    if success:
        print("TEST PASSED: JM Holiday Lighting was saved to database!")
        print("The database save functionality is CONFIRMED WORKING!")
    else:
        print("TEST FAILED: Database save not working")
    print("=" * 60)