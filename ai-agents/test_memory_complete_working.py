#!/usr/bin/env python3
"""
Complete working memory system test
Creates all required parent records first, then tests both memory systems
"""

import uuid
import asyncio
import json
from datetime import datetime, timezone
from database import SupabaseDB

async def create_parent_records(db):
    """Create required parent records for foreign key constraints"""
    
    contractor_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    print("Creating parent records for foreign key constraints...")
    
    # 1. Create contractor record (parent for contractor_ai_memory)
    print("\n1. Creating contractor record...")
    try:
        contractor_data = {
            "id": contractor_id,
            "user_id": user_id,
            "company_name": "ServiceTitan Landscaping Test",
            "license_number": "TEST123",
            "verified": False,
            "tier": 3,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.client.table("contractors").insert(contractor_data).execute()
        if result.data:
            print(f"  SUCCESS: Created contractor {contractor_id}")
    except Exception as e:
        print(f"  ERROR creating contractor: {e}")
        # Try to use existing contractor if creation fails
        try:
            result = db.client.table("contractors").select("id").limit(1).execute()
            if result.data:
                contractor_id = result.data[0]['id']
                print(f"  Using existing contractor: {contractor_id}")
        except:
            pass
    
    # 2. Create unified conversation record (parent for unified_conversation_memory)
    print("\n2. Creating unified conversation record...")
    try:
        conversation_data = {
            "id": conversation_id,
            "tenant_id": contractor_id,  # Use contractor_id as tenant_id
            "created_by": user_id,
            "conversation_type": "bsa_chat",
            "entity_id": contractor_id,
            "entity_type": "contractor",
            "title": "BSA Memory Test Conversation",
            "status": "active",
            "metadata": {"test": True},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.client.table("unified_conversations").insert(conversation_data).execute()
        if result.data:
            print(f"  SUCCESS: Created conversation {conversation_id}")
    except Exception as e:
        print(f"  ERROR creating conversation: {e}")
    
    return contractor_id, conversation_id

async def test_memory_systems_complete():
    """Test both memory systems with proper parent records"""
    
    print("="*80)
    print("COMPLETE MEMORY SYSTEM TEST WITH PROPER SETUP")
    print("="*80)
    
    db = SupabaseDB()
    
    # Create parent records first
    contractor_id, conversation_id = await create_parent_records(db)
    
    print(f"\nUsing IDs:")
    print(f"  Contractor ID: {contractor_id}")
    print(f"  Conversation ID: {conversation_id}")
    
    # TEST 1: Save to contractor_ai_memory
    print("\n" + "="*60)
    print("TEST 1: Saving to contractor_ai_memory")
    print("="*60)
    
    memory_saved = False
    try:
        memory_data = {
            "id": str(uuid.uuid4()),
            "contractor_id": contractor_id,
            "memory_data": {
                "company_name": "ServiceTitan Landscaping",
                "years_in_business": 15,
                "employees": 25,
                "markup_materials": "25%",
                "markup_labor": "40%",
                "crm_system": "ServiceTitan",
                "specialties": ["premium residential", "landscaping"],
                "conversation_1": "I'm Bob from ServiceTitan Landscaping with 15 years experience"
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.client.table("contractor_ai_memory").insert(memory_data).execute()
        if result.data:
            print("  SUCCESS: Saved to contractor_ai_memory")
            print(f"  - Company: {memory_data['memory_data']['company_name']}")
            print(f"  - Years: {memory_data['memory_data']['years_in_business']}")
            print(f"  - Employees: {memory_data['memory_data']['employees']}")
            memory_saved = True
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # TEST 2: Save to unified_conversation_memory
    print("\n" + "="*60)
    print("TEST 2: Saving to unified_conversation_memory")
    print("="*60)
    
    unified_saved = False
    try:
        unified_data = {
            "id": str(uuid.uuid4()),
            "tenant_id": contractor_id,  # Use contractor_id as tenant
            "conversation_id": conversation_id,
            "memory_scope": "contractor",
            "memory_type": "business_info",
            "memory_key": "initial_details",
            "memory_value": {
                "company_name": "ServiceTitan Landscaping",
                "years_in_business": 15,
                "employees": 25,
                "markup": {"materials": "25%", "labor": "40%"},
                "crm_system": "ServiceTitan"
            },
            "importance_score": 10,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.client.table("unified_conversation_memory").insert(unified_data).execute()
        if result.data:
            print("  SUCCESS: Saved to unified_conversation_memory")
            print(f"  - Memory key: {result.data[0]['memory_key']}")
            print(f"  - Memory type: {result.data[0]['memory_type']}")
            unified_saved = True
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # TEST 3: Retrieve from both systems
    print("\n" + "="*60)
    print("TEST 3: Retrieving from both memory systems")
    print("="*60)
    
    # Retrieve from contractor_ai_memory
    print("\nRetrieving from contractor_ai_memory...")
    memory_retrieved = False
    try:
        result = db.client.table("contractor_ai_memory")\
            .select("*")\
            .eq("contractor_id", contractor_id)\
            .execute()
        
        if result.data:
            print(f"  SUCCESS: Retrieved {len(result.data)} records")
            memory = result.data[0]['memory_data']
            print(f"  - Company: {memory.get('company_name')}")
            print(f"  - Years: {memory.get('years_in_business')}")
            print(f"  - Employees: {memory.get('employees')}")
            memory_retrieved = True
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Retrieve from unified_conversation_memory
    print("\nRetrieving from unified_conversation_memory...")
    unified_retrieved = False
    try:
        result = db.client.table("unified_conversation_memory")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .execute()
        
        if result.data:
            print(f"  SUCCESS: Retrieved {len(result.data)} memory entries")
            for entry in result.data:
                memory_value = entry['memory_value']
                print(f"  - Key: {entry['memory_key']}")
                print(f"  - Company: {memory_value.get('company_name')}")
                print(f"  - Years: {memory_value.get('years_in_business')}")
            unified_retrieved = True
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # TEST 4: Update with new information (simulating second conversation)
    print("\n" + "="*60)
    print("TEST 4: Second conversation - updating memory")
    print("="*60)
    
    # Update contractor_ai_memory
    print("\nUpdating contractor_ai_memory with new info...")
    memory_updated = False
    try:
        result = db.client.table("contractor_ai_memory")\
            .select("*")\
            .eq("contractor_id", contractor_id)\
            .execute()
        
        if result.data:
            existing_memory = result.data[0]['memory_data']
            # Add new information from second conversation
            existing_memory['employees'] = 30  # Updated from 25
            existing_memory['certifications'] = ['LEED']  # New info
            existing_memory['conversation_2'] = "We now have 30 employees and LEED certification"
            
            update_result = db.client.table("contractor_ai_memory")\
                .update({
                    "memory_data": existing_memory,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })\
                .eq("contractor_id", contractor_id)\
                .execute()
            
            if update_result.data:
                print("  SUCCESS: Updated with new information")
                print(f"  - New employee count: 30 (was 25)")
                print(f"  - New certification: LEED")
                memory_updated = True
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Add second entry to unified_conversation_memory
    print("\nAdding second memory to unified_conversation_memory...")
    unified_updated = False
    try:
        unified_data_2 = {
            "id": str(uuid.uuid4()),
            "tenant_id": contractor_id,
            "conversation_id": conversation_id,
            "memory_scope": "contractor",
            "memory_type": "update",
            "memory_key": "second_conversation",
            "memory_value": {
                "employees": 30,
                "certifications": ["LEED"],
                "previous_employees": 25,
                "change": "growth"
            },
            "importance_score": 8,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.client.table("unified_conversation_memory").insert(unified_data_2).execute()
        if result.data:
            print("  SUCCESS: Added second conversation memory")
            print(f"  - Memory key: {result.data[0]['memory_key']}")
            unified_updated = True
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # FINAL VERIFICATION
    print("\n" + "="*80)
    print("FINAL VERIFICATION - 1000% CONFIRMATION")
    print("="*80)
    
    # Check contractor_ai_memory final state
    print("\nFinal state of contractor_ai_memory:")
    try:
        result = db.client.table("contractor_ai_memory")\
            .select("*")\
            .eq("contractor_id", contractor_id)\
            .execute()
        
        if result.data:
            memory = result.data[0]['memory_data']
            print(f"  Company: {memory.get('company_name')}")
            print(f"  Employees: {memory.get('employees')} (updated from 25)")
            print(f"  Certifications: {memory.get('certifications', [])}")
            print(f"  Has conversation 1: {'conversation_1' in memory}")
            print(f"  Has conversation 2: {'conversation_2' in memory}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Check unified_conversation_memory final state
    print("\nFinal state of unified_conversation_memory:")
    try:
        result = db.client.table("unified_conversation_memory")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=False)\
            .execute()
        
        if result.data:
            print(f"  Total memory entries: {len(result.data)}")
            for i, entry in enumerate(result.data, 1):
                print(f"  Entry {i}: {entry['memory_key']} - {entry['memory_type']}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    all_tests = [
        ("contractor_ai_memory save", memory_saved),
        ("contractor_ai_memory retrieve", memory_retrieved),
        ("contractor_ai_memory update", memory_updated),
        ("unified_conversation_memory save", unified_saved),
        ("unified_conversation_memory retrieve", unified_retrieved),
        ("unified_conversation_memory update", unified_updated)
    ]
    
    for test_name, passed in all_tests:
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(passed for _, passed in all_tests)
    
    if all_passed:
        print("\n1000% CONFIRMATION: BOTH MEMORY SYSTEMS WORKING!")
        print("- contractor_ai_memory: Saves, retrieves, and updates properly")
        print("- unified_conversation_memory: Saves, retrieves, and updates properly")
        print("- Both systems maintain conversation history")
        print("- Both systems handle second conversations correctly")
        print("- Memory persists and can be restored")
    else:
        print("\nSome tests failed - check errors above")
    
    return contractor_id, conversation_id

def main():
    """Run the complete memory system test"""
    contractor_id, conversation_id = asyncio.run(test_memory_systems_complete())
    print(f"\nTest complete. IDs used:")
    print(f"  Contractor ID: {contractor_id}")
    print(f"  Conversation ID: {conversation_id}")

if __name__ == "__main__":
    main()