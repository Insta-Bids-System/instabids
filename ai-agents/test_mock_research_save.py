#!/usr/bin/env python3
"""
Test research save with mock data (no actual API calls)
"""

import asyncio
import sys
import os
sys.path.append('.')

async def test_mock_research_save():
    print("Testing research save with mock data (no API calls)...")
    
    from agents.coia.tools import COIATools
    
    # Test company
    company_name = "Elite Plumbing Services Miami"
    
    # Mock Google Places data (simulating successful API response)
    mock_google_data = {
        "success": True,
        "company_name": company_name,
        "phone": "(305) 555-9999",
        "address": "789 Ocean Drive, Miami Beach, FL 33139",
        "website": "https://eliteplumbingmiami.com",
        "rating": 4.7,
        "review_count": 28,
        "place_id": "mock_place_id_elite_plumbing"
    }
    
    # Mock web scraping data
    mock_web_data = {
        "extracted_info": {
            "services": ["Emergency Plumbing", "Water Heater Installation", "Drain Cleaning", "Leak Detection"],
            "years_in_business": 12,
            "employees": 15,
            "business_description": "Elite Plumbing Services - Miami's trusted plumbing experts since 2013",
            "contact_methods": {
                "emails": ["service@eliteplumbingmiami.com"],
                "phones": ["(305) 555-9999"]
            },
            "certifications": ["Licensed & Insured", "BBB Accredited"],
            "social_media_links": {
                "facebook_url": "https://facebook.com/eliteplumbingmiami",
                "instagram_url": "https://instagram.com/eliteplumbing"
            }
        }
    }
    
    # Mock license data
    mock_license_data = {
        "licenses": [{
            "number": "FL345678",
            "state": "FL"
        }]
    }
    
    print(f"Company: {company_name}")
    print("-" * 60)
    
    # Test the profile builder with database save
    async with COIATools() as tools:
        print("Building contractor profile with mock data...")
        
        profile = await tools.build_contractor_profile(
            company_name=company_name,
            google_data=mock_google_data,
            web_data=mock_web_data,
            license_data=mock_license_data
        )
        
        print(f"Profile completeness: {profile.get('completeness_score', 0):.1f}%")
        print(f"Data completeness: {profile.get('data_completeness', 0):.1f}%")
        print(f"Lead score: {profile.get('lead_score', 0):.1f}")
        
        # Check database save
        if profile.get('database_saved'):
            print(f"\n✅ DATABASE SAVE SUCCESS!")
            print(f"Contractor Lead ID: {profile.get('contractor_lead_id')}")
            print(f"Saved at: {profile.get('saved_at')}")
            
            # Verify in database
            from database_simple import db
            contractor_id = profile.get('contractor_lead_id')
            
            result = db.client.table("contractor_leads").select("*").eq("id", contractor_id).execute()
            
            if result.data:
                record = result.data[0]
                print(f"\n✅ VERIFIED IN DATABASE!")
                print(f"Company: {record.get('company_name')}")
                print(f"Phone: {record.get('phone')}")
                print(f"Email: {record.get('email')}")
                print(f"Website: {record.get('website')}")
                print(f"Address: {record.get('address')}")
                print(f"City: {record.get('city')}")
                print(f"Rating: {record.get('rating')}")
                print(f"Specialties: {record.get('specialties')}")
                print(f"Years in business: {record.get('years_in_business')}")
                print(f"License: {record.get('license_number')}")
                print(f"Data completeness: {record.get('data_completeness')}%")
                
                # Count filled fields
                filled = len([k for k, v in record.items() if v is not None and v != '' and v != [] and v != {}])
                print(f"\nTotal filled fields: {filled} out of 49")
                
                return True
            else:
                print(f"❌ NOT FOUND in database")
                return False
        else:
            print(f"❌ DATABASE SAVE FAILED!")
            if profile.get('database_error'):
                print(f"Error: {profile.get('database_error')}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_mock_research_save())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Database save working with mock data!")
    else:
        print("❌ TEST FAILED: Database save not working")
    print("=" * 60)