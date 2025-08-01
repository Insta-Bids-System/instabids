#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_simple import SupabaseDB
import json
from datetime import datetime

def sync_potential_contractors_to_leads():
    """
    Sync all potential_contractors records to contractor_leads table
    to fix foreign key constraint violations
    """
    print("SYNCING POTENTIAL CONTRACTORS TO CONTRACTOR LEADS")
    print("=" * 60)
    
    db = SupabaseDB()
    supabase = db.client
    
    # First, get all potential contractors
    print("\n1. Fetching all potential contractors...")
    potential_result = supabase.table('potential_contractors').select('*').execute()
    
    if not potential_result.data:
        print("ERROR: No potential contractors found")
        return False
        
    contractors = potential_result.data
    print(f"Found {len(contractors)} potential contractors")
    
    # Check which ones already exist in contractor_leads
    print("\n2. Checking existing contractor_leads...")
    leads_result = supabase.table('contractor_leads').select('id').execute()
    existing_lead_ids = set([lead['id'] for lead in leads_result.data]) if leads_result.data else set()
    print(f"Found {len(existing_lead_ids)} existing contractor leads")
    
    # Find contractors that need to be synced
    contractors_to_sync = []
    for contractor in contractors:
        if contractor['id'] not in existing_lead_ids:
            contractors_to_sync.append(contractor)
    
    print(f"Need to sync {len(contractors_to_sync)} contractors")
    
    if not contractors_to_sync:
        print("All contractors already synced!")
        return True
    
    # Create contractor_leads records for missing contractors
    print("\n3. Creating contractor_leads records...")
    
    leads_to_insert = []
    for contractor in contractors_to_sync:
        lead_record = {
            'id': contractor['id'],  # Use same ID
            'source': 'manual',
            'company_name': contractor.get('company_name'),
            'contact_name': contractor.get('contact_name'),
            'email': contractor['email'],
            'phone': contractor.get('phone'),
            'website': contractor.get('website'),
            'address': contractor.get('address'),
            'city': contractor.get('city'),
            'state': contractor.get('state'),
            'zip_code': contractor.get('zip_code'),
            'specialties': contractor.get('specialties', []),
            'years_in_business': contractor.get('years_in_business'),
            'license_number': contractor.get('license_number'),
            'insurance_verified': contractor.get('insurance_verified'),
            'bonded': contractor.get('bonded'),
            'lead_status': contractor.get('lead_status', 'new'),
            'created_at': contractor.get('created_at'),
            'updated_at': contractor.get('updated_at')
        }
        leads_to_insert.append(lead_record)
        
        print(f"  {contractor.get('company_name', 'Unknown')} ({contractor['email']})")
    
    # Insert in batches to avoid timeout
    batch_size = 50
    total_inserted = 0
    
    for i in range(0, len(leads_to_insert), batch_size):
        batch = leads_to_insert[i:i+batch_size]
        try:
            result = supabase.table('contractor_leads').insert(batch).execute()
            if result.data:
                total_inserted += len(result.data)
                print(f"  SUCCESS: Inserted batch {i//batch_size + 1}: {len(result.data)} records")
            else:
                print(f"  ERROR: Failed to insert batch {i//batch_size + 1}")
        except Exception as e:
            print(f"  ERROR: Error inserting batch {i//batch_size + 1}: {e}")
            continue
    
    print(f"\n4. SYNC COMPLETE!")
    print(f"   Total contractors synced: {total_inserted}")
    
    # Verify the specific contractor causing the error exists now
    target_id = 'e3748954-efc0-486e-bf79-0f898fc5d8a2'
    check_result = supabase.table('contractor_leads').select('id, company_name, email').eq('id', target_id).execute()
    
    if check_result.data:
        contractor = check_result.data[0]
        print(f"\nVERIFIED: Target contractor {target_id} now exists:")
        print(f"   Company: {contractor['company_name']}")
        print(f"   Email: {contractor['email']}")
    else:
        print(f"\nWARNING: Target contractor {target_id} still not found!")
        
    return total_inserted > 0

if __name__ == "__main__":
    success = sync_potential_contractors_to_leads()
    if success:
        print("\nSYNC SUCCESSFUL - Ready to test campaign flow!")
    else:
        print("\nSYNC FAILED - Check errors above")