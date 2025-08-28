#!/usr/bin/env python3
"""
Simple test for COIA contractor profile database save
"""

import asyncio
import sys
import os
sys.path.append('.')

async def test_database_save():
    print("Testing COIA contractor profile database save...")
    
    from agents.coia.tools import COIATools
    
    # Test data
    company_name = "Turf Grass Artificial Solutions"
    
    # Mock simple data
    google_data = {
        "success": True,
        "company_name": company_name,
        "phone": "(555) 123-4567",
        "address": "123 Turf Way, Fort Lauderdale, FL 33301",
        "rating": 4.5,
        "review_count": 15
    }
    
    web_data = {
        "extracted_info": {
            "services": ["Artificial Turf Installation"],
            "years_in_business": 8
        }
    }
    
    license_data = None
    
    print(f"Building profile for: {company_name}")
    
    # Test the tools
    async with COIATools() as tools:
        profile = await tools.build_contractor_profile(
            company_name=company_name,
            google_data=google_data,
            web_data=web_data,
            license_data=license_data
        )
        
        print(f"Profile completeness: {profile.get('completeness_score', 0):.1f}%")
        print(f"Data completeness: {profile.get('data_completeness', 0):.1f}%")
        
        if profile.get('database_saved'):
            print("DATABASE SAVE SUCCESS!")
            print(f"Contractor ID: {profile.get('contractor_lead_id')}")
            
            # Verify with database query
            try:
                from database_simple import db
                contractor_id = profile.get('contractor_lead_id')
                
                result = db.client.table("contractor_leads").select("company_name, phone, email, specialties, data_completeness").eq("id", contractor_id).execute()
                
                if result.data:
                    saved_record = result.data[0]
                    print("VERIFICATION SUCCESS - Found in database:")
                    print(f"  Company: {saved_record.get('company_name')}")
                    print(f"  Phone: {saved_record.get('phone')}")
                    print(f"  Specialties: {saved_record.get('specialties')}")
                    print(f"  Completeness: {saved_record.get('data_completeness')}")
                    return True
                else:
                    print("VERIFICATION FAILED - Not found in database")
                    return False
                    
            except Exception as e:
                print(f"Verification error: {e}")
                return False
        else:
            print("DATABASE SAVE FAILED!")
            if profile.get('database_error'):
                print(f"Error: {profile.get('database_error')}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_database_save())
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")