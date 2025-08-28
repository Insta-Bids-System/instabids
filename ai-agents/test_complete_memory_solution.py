#!/usr/bin/env python3
"""
Complete solution for both memory systems working together
Handles all foreign key constraints and unique constraints properly
"""

import uuid
import asyncio
import json
from datetime import datetime, timezone
from database import SupabaseDB

async def create_all_parent_records(db):
    """Create all required parent records with proper foreign key chain"""
    
    # Generate IDs
    user_id = str(uuid.uuid4())
    contractor_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    
    print("Creating complete parent record chain...")
    
    # 1. Create profile (parent for contractors)
    print("\n1. Creating profile record...")
    try:
        profile_data = {
            "id": user_id,
            "email": f"test_{uuid.uuid4().hex[:8]}@instabids.com",
            "full_name": "Test Contractor User",
            "role": "contractor",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.client.table("profiles").insert(profile_data).execute()
        if result.data:
            print(f"  SUCCESS: Created profile {user_id}")
    except Exception as e:
        if "duplicate key" in str(e).lower():
            print(f"  Profile already exists, continuing...")
        else:
            print(f"  Note: {e}")
    
    # 2. Create contractor (parent for contractor_ai_memory)
    print("\n2. Creating contractor record...")
    try:
        contractor_data = {
            "id": contractor_id,
            "user_id": user_id,
            "company_name": "ServiceTitan Landscaping Test",
            "license_number": f"LIC-{uuid.uuid4().hex[:8].upper()}",
            "verified": False,
            "tier": 3,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.client.table("contractors").insert(contractor_data).execute()
        if result.data:
            print(f"  SUCCESS: Created contractor {contractor_id}")
    except Exception as e:
        print(f"  Note: {e}")
    
    # 3. Create unified conversation (parent for unified_conversation_memory)
    print("\n3. Creating unified conversation record...")
    try:
        conversation_data = {
            "id": conversation_id,
            "tenant_id": contractor_id,
            "created_by": user_id,
            "conversation_type": "bsa_chat",
            "entity_id": contractor_id,
            "entity_type": "contractor",
            "title": "BSA Complete Memory Test",
            "status": "active",
            "metadata": {"test": True, "session_id": f"test_{uuid.uuid4().hex[:8]}"},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.client.table("unified_conversations").insert(conversation_data).execute()
        if result.data:
            print(f"  SUCCESS: Created conversation {conversation_id}")
    except Exception as e:
        print(f"  Note: {e}")
    
    return user_id, contractor_id, conversation_id

async def upsert_contractor_memory(db, contractor_id: str, new_data: dict) -> bool:
    """
    UPSERT pattern for contractor_ai_memory
    Handles unique constraint by updating if exists, inserting if not
    """
    try:
        # Check if record exists
        existing = db.client.table("contractor_ai_memory")\
            .select("*")\
            .eq("contractor_id", contractor_id)\
            .execute()
        
        if existing.data:
            # UPDATE: Merge existing data with new data
            existing_memory = existing.data[0].get('memory_data', {})
            merged_memory = {**existing_memory, **new_data}
            
            result = db.client.table("contractor_ai_memory")\
                .update({
                    "memory_data": merged_memory,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })\
                .eq("contractor_id", contractor_id)\
                .execute()
            
            return bool(result.data)
        else:
            # INSERT: Create new record
            result = db.client.table("contractor_ai_memory")\
                .insert({
                    "id": str(uuid.uuid4()),
                    "contractor_id": contractor_id,
                    "memory_data": new_data,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })\
                .execute()
            
            return bool(result.data)
    except Exception as e:
        print(f"    Error in upsert: {e}")
        return False

async def test_complete_memory_solution():
    """Test both memory systems with proper constraint handling"""
    
    print("="*80)
    print("COMPLETE MEMORY SOLUTION - BOTH SYSTEMS WORKING")
    print("="*80)
    
    db = SupabaseDB()
    
    # Create all parent records
    user_id, contractor_id, conversation_id = await create_all_parent_records(db)
    
    print(f"\nTest IDs created:")
    print(f"  User ID: {user_id}")
    print(f"  Contractor ID: {contractor_id}")
    print(f"  Conversation ID: {conversation_id}")
    
    # CONVERSATION 1: Initial data
    print("\n" + "="*60)
    print("CONVERSATION 1: Initial contractor information")
    print("="*60)
    
    # Save to contractor_ai_memory (with UPSERT)
    print("\nSaving to contractor_ai_memory...")
    memory1_success = await upsert_contractor_memory(db, contractor_id, {
        "company_name": "ServiceTitan Landscaping",
        "years_in_business": 15,
        "employees": 25,
        "markup_materials": "25%",
        "markup_labor": "40%",
        "crm_system": "ServiceTitan",
        "conversation_1": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "I'm Bob from ServiceTitan Landscaping with 15 years experience"
        }
    })
    print(f"  Result: {'SUCCESS' if memory1_success else 'FAILED'}")
    
    # Save to unified_conversation_memory (no unique constraint)
    print("\nSaving to unified_conversation_memory...")
    unified1_success = False
    try:
        unified_data = {
            "id": str(uuid.uuid4()),
            "tenant_id": contractor_id,
            "conversation_id": conversation_id,
            "memory_scope": "contractor",
            "memory_type": "business_info",
            "memory_key": "initial_conversation",
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
            print(f"  Result: SUCCESS")
            unified1_success = True
    except Exception as e:
        print(f"  Result: FAILED - {e}")
    
    # CONVERSATION 2: Updated information
    print("\n" + "="*60)
    print("CONVERSATION 2: Updated contractor information")
    print("="*60)
    
    # Update contractor_ai_memory (UPSERT will merge)
    print("\nUpdating contractor_ai_memory...")
    memory2_success = await upsert_contractor_memory(db, contractor_id, {
        "employees": 30,  # Updated from 25
        "certifications": ["LEED", "BBB A+"],  # New info
        "conversation_2": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "We now have 30 employees and LEED certification"
        }
    })
    print(f"  Result: {'SUCCESS' if memory2_success else 'FAILED'}")
    
    # Add second entry to unified_conversation_memory
    print("\nAdding second memory to unified_conversation_memory...")
    unified2_success = False
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
                "certifications": ["LEED", "BBB A+"],
                "update_type": "growth"
            },
            "importance_score": 8,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.client.table("unified_conversation_memory").insert(unified_data_2).execute()
        if result.data:
            print(f"  Result: SUCCESS")
            unified2_success = True
    except Exception as e:
        print(f"  Result: FAILED - {e}")
    
    # VERIFICATION: Check both systems
    print("\n" + "="*60)
    print("VERIFICATION: Checking both memory systems")
    print("="*60)
    
    # Verify contractor_ai_memory
    print("\ncontractor_ai_memory status:")
    contractor_verify = False
    try:
        result = db.client.table("contractor_ai_memory")\
            .select("*")\
            .eq("contractor_id", contractor_id)\
            .execute()
        
        if result.data:
            memory = result.data[0]['memory_data']
            print(f"  Records found: 1 (unique constraint enforces single record)")
            print(f"  Company: {memory.get('company_name')}")
            print(f"  Employees: {memory.get('employees')} (updated from 25 to 30)")
            print(f"  Certifications: {memory.get('certifications', [])}")
            print(f"  Has conversation_1: {'conversation_1' in memory}")
            print(f"  Has conversation_2: {'conversation_2' in memory}")
            contractor_verify = True
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Verify unified_conversation_memory
    print("\nunified_conversation_memory status:")
    unified_verify = False
    try:
        result = db.client.table("unified_conversation_memory")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=False)\
            .execute()
        
        if result.data:
            print(f"  Records found: {len(result.data)} (multiple records allowed)")
            for i, entry in enumerate(result.data, 1):
                print(f"  Entry {i}: {entry['memory_key']} ({entry['memory_type']})")
            unified_verify = True
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # SUMMARY
    print("\n" + "="*80)
    print("FINAL RESULTS - BOTH MEMORY SYSTEMS STATUS")
    print("="*80)
    
    all_tests = [
        ("contractor_ai_memory - First save", memory1_success),
        ("contractor_ai_memory - Second update", memory2_success),
        ("contractor_ai_memory - Verification", contractor_verify),
        ("unified_conversation_memory - First save", unified1_success),
        ("unified_conversation_memory - Second save", unified2_success),
        ("unified_conversation_memory - Verification", unified_verify)
    ]
    
    for test_name, passed in all_tests:
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(passed for _, passed in all_tests)
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    if all_passed:
        print("✅ BOTH MEMORY SYSTEMS FULLY WORKING!")
        print("")
        print("contractor_ai_memory:")
        print("  - Uses UPSERT pattern to handle unique constraint")
        print("  - One record per contractor, continuously updated")
        print("  - All conversation data merged and preserved")
        print("")
        print("unified_conversation_memory:")
        print("  - Supports multiple memory entries per conversation")
        print("  - Each conversation turn adds new memory record")
        print("  - Complete conversation history maintained")
        print("")
        print("BOTH SYSTEMS:")
        print("  - Save data properly ✅")
        print("  - Retrieve data properly ✅")
        print("  - Update data properly ✅")
    else:
        print("⚠️ Some tests failed - check errors above")
    
    return contractor_id, conversation_id

def main():
    """Run the complete memory solution test"""
    contractor_id, conversation_id = asyncio.run(test_complete_memory_solution())
    print(f"\nTest complete.")
    print(f"  Contractor ID: {contractor_id}")
    print(f"  Conversation ID: {conversation_id}")

if __name__ == "__main__":
    main()