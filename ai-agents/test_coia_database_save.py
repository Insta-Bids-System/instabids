#!/usr/bin/env python3
"""
Test COIA database save functionality directly
"""
import sys
from datetime import datetime

# Fix Windows Unicode
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def test_direct_database_save():
    print("🔧 TESTING DIRECT DATABASE SAVE")
    
    try:
        from database_simple import db
        print("   ✅ Database connection imported successfully")
        
        # Test data similar to what COIA would create
        test_contractor_data = {
            "company_name": f"DirectTestCorp_{int(datetime.now().timestamp())}",
            "contact_name": "Direct Test",
            "email": "directtest@example.com",
            "phone": "555-123-4567",
            "website": "https://directtest.com",
            "specialties": ["Kitchen Remodeling", "Bathroom Renovation"],
            "city": "Miami",
            "state": "FL",
            "source": "COIA Direct Test",
            "lead_status": "qualified",
            "discovered_at": datetime.now().isoformat()
        }
        
        print(f"   🎯 Company: {test_contractor_data['company_name']}")
        
        # Attempt database save
        result = db.client.table("contractor_leads").insert(test_contractor_data).execute()
        
        if result.data:
            contractor_id = result.data[0]['id']
            print(f"   ✅ Successfully saved contractor: ID {contractor_id}")
            
            # Verify it was saved by reading it back
            verify_result = db.client.table("contractor_leads").select("*").eq("id", contractor_id).execute()
            if verify_result.data:
                saved_contractor = verify_result.data[0]
                print(f"   ✅ Verification successful: {saved_contractor.get('company_name')}")
                return True, test_contractor_data['company_name']
            else:
                print("   ❌ Verification failed - could not read back saved data")
                return False, None
        else:
            print("   ❌ Database insert returned no data")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Database save failed: {e}")
        print(f"   🔍 Error type: {type(e).__name__}")
        return False, None

def main():
    print("🎯 COIA DATABASE SAVE TEST")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    print("=" * 50)
    
    success, company_name = test_direct_database_save()
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    if success:
        print("✅ Database save working correctly")
        print(f"   Company saved: {company_name}")
        print("🎉 COIA database integration is FUNCTIONAL")
    else:
        print("❌ Database save failed")
        print("⚠️ COIA database integration needs debugging")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)