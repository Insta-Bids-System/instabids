#!/usr/bin/env python3
"""
Test script to verify COIA contractor profile database save fix
"""

import asyncio
import sys
import os
sys.path.append('.')

async def test_contractor_profile_database_save():
    """Test the fixed build_contractor_profile function saves to database"""
    print("Testing COIA contractor profile database save fix...")
    
    from agents.coia.tools import COIATools
    
    # Test data
    company_name = "Turf Grass Artificial Solutions"
    
    # Mock Google data
    google_data = {
        "success": True,
        "company_name": company_name,
        "phone": "(555) 123-4567",
        "address": "123 Turf Way, Fort Lauderdale, FL 33301",
        "website": "https://turfgrassartificial.com",
        "rating": 4.5,
        "review_count": 15,
        "place_id": "test_place_id"
    }
    
    # Mock web data  
    web_data = {
        "extracted_info": {
            "services": ["Artificial Turf Installation", "Landscaping", "Hardscaping"],
            "years_in_business": 8,
            "employees": 5,
            "contact_form_url": "https://turfgrassartificial.com/contact",
            "certifications": ["Licensed Contractor"],
            "business_description": "Professional artificial turf installation in South Florida",
            "contact_methods": {
                "emails": ["info@turfgrassartificial.com"],
                "phones": ["(555) 123-4567"]
            },
            "social_media_links": {
                "facebook_url": "https://facebook.com/turfgrassartificial"
            }
        }
    }
    
    # Mock license data
    license_data = {
        "licenses": [{
            "number": "FL123456",
            "state": "FL"
        }]
    }
    
    print(f"Testing contractor profile building and database save for: {company_name}")
    
    # Test the tools
    async with COIATools() as tools:
        
        print("\n1. Building contractor profile...")
        profile = await tools.build_contractor_profile(
            company_name=company_name,
            google_data=google_data,
            web_data=web_data,
            license_data=license_data
        )
        
        print(f"   - Profile completeness: {profile.get('completeness_score', 0):.1f}%")
        print(f"   - Data completeness: {profile.get('data_completeness', 0):.1f}%")
        print(f"   - Lead score: {profile.get('lead_score', 0):.1f}")
        print(f"   - Data sources: {', '.join(profile.get('data_sources', []))}")
        
        # Check database save
        if profile.get('database_saved'):
            print(f"\n✅ DATABASE SAVE SUCCESS!")
            print(f"   - Contractor ID: {profile.get('contractor_lead_id')}")
            print(f"   - Saved at: {profile.get('saved_at')}")
            print(f"   - Discovery source: coia_research")
            
            # Verify data was actually saved by querying the database
            print(f"\n2. Verifying database record...")
            try:
                from database_simple import db
                contractor_id = profile.get('contractor_lead_id')
                
                # Query contractor_leads table
                result = db.client.table("contractor_leads").select("*").eq("id", contractor_id).execute()
                
                if result.data:
                    saved_record = result.data[0]
                    print(f"   ✅ Found saved record in contractor_leads table")
                    print(f"   - Company name: {saved_record.get('company_name')}")
                    print(f"   - Phone: {saved_record.get('phone')}")
                    print(f"   - Email: {saved_record.get('email')}")
                    print(f"   - Website: {saved_record.get('website')}")
                    print(f"   - Specialties: {saved_record.get('specialties')}")
                    print(f"   - Completeness score: {saved_record.get('completeness_score')}")
                    print(f"   - Discovery source: {saved_record.get('discovery_source')}")
                    
                    # Verify the profile data is complete
                    total_fields = len([k for k, v in saved_record.items() if v is not None and v != '' and v != []])
                    print(f"   - Total filled fields: {total_fields}")
                    
                    return True
                else:
                    print(f"   ❌ No record found in database for ID: {contractor_id}")
                    return False
                    
            except Exception as db_error:
                print(f"   ❌ Database verification error: {db_error}")
                return False
                
        else:
            print(f"\n❌ DATABASE SAVE FAILED!")
            if profile.get('database_error'):
                print(f"   - Error: {profile.get('database_error')}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_contractor_profile_database_save())
    
    if success:
        print(f"\n🎉 TEST PASSED: Contractor profile database save is working!")
    else:
        print(f"\n💥 TEST FAILED: Database save needs debugging")