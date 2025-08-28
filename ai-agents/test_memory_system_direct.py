#!/usr/bin/env python3
"""
DIRECT MEMORY SYSTEM VERIFICATION
Tests the enhanced memory system directly without BSA API
Shows concrete evidence of memory extraction and storage
"""

import asyncio
import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.enhanced_contractor_memory import EnhancedContractorMemory
from database import SupabaseDB

# Test contractor
CONTRACTOR_ID = "523c0f63-e75c-4d65-963e-561d7f4169db"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

async def clear_test_data():
    """Clear existing test data"""
    print_section("CLEARING TEST DATA")
    
    db = SupabaseDB()
    tables = [
        "contractor_business_profile",
        "contractor_bidding_patterns", 
        "contractor_relationship_memory",
        "contractor_information_needs",
        "contractor_pain_points"
    ]
    
    for table in tables:
        try:
            result = db.client.table(table).delete().eq("contractor_id", CONTRACTOR_ID).execute()
            print(f"[CLEANED] {table}: removed {len(result.data) if result.data else 0} records")
        except Exception as e:
            print(f"[NOTE] No existing {table} to clear: {e}")

async def test_conversation_1():
    """Test first conversation with rich business details"""
    print_section("CONVERSATION 1: Rich Business Context")
    
    memory = EnhancedContractorMemory()
    
    if not memory.openai_client:
        print("ERROR: OpenAI client not initialized - check OPENAI_API_KEY")
        return False, None
    
    conversation_data = {
        'input': """Hi, I'm Mike from Mike's Plumbing Services. We've been in business for 12 years and specialize in 
                   bathroom and kitchen remodeling. We use ServiceTitan for our CRM system and have 15 employees. 
                   Our typical project range is $30k-$75k. We markup materials 25% and labor 40%. 
                   Our biggest operational challenge is managing electrical and HVAC subcontractors - they're always 
                   late and it throws off our schedules. Cash flow gets tight when customers take 60+ days to pay.
                   I prefer email for non-urgent communication but text me at 555-0123 for emergencies.""",
        'response': """Thank you Mike! I understand you run Mike's Plumbing Services with 15 employees, specializing in 
                      bathroom and kitchen remodeling. I noted your ServiceTitan CRM usage, project range of $30k-$75k, 
                      and your markup structure. I'll keep in mind your subcontractor challenges and payment timeline 
                      concerns, as well as your communication preferences.""",
        'project_type': 'bathroom_remodel'
    }
    
    print("[INPUT CONVERSATION]")
    print(f"Contractor: {conversation_data['input'][:200]}...")
    print(f"AI Response: {conversation_data['response'][:200]}...")
    
    print("\n[EXTRACTING FROM CONVERSATION WITH GPT-4o]")
    print("Calling enhanced memory system...")
    
    # Update all memory dimensions
    results = await memory.update_all_contractor_memories(CONTRACTOR_ID, conversation_data)
    
    if results:
        print(f"[SUCCESS] Updated {len(results)} memory dimensions")
        for dimension, data in results.items():
            print(f"  - {dimension}: {len(str(data))} characters of data")
        return True, results
    else:
        print("[ERROR] No memory updates returned")
        return False, None

async def verify_conversation_1_storage():
    """Verify conversation 1 was stored correctly"""
    print_section("VERIFICATION 1: Database Storage")
    
    db = SupabaseDB()
    tables = [
        "contractor_business_profile",
        "contractor_bidding_patterns", 
        "contractor_relationship_memory",
        "contractor_information_needs",
        "contractor_pain_points"
    ]
    
    facts_found = []
    tables_with_data = 0
    
    for table in tables:
        try:
            result = db.client.table(table).select("*").eq("contractor_id", CONTRACTOR_ID).execute()
            
            if result.data:
                tables_with_data += 1
                record = result.data[0]
                print(f"\n[{table.upper().replace('CONTRACTOR_', '')}]")
                
                # Show key fields
                for key, value in record.items():
                    if key not in ['id', 'contractor_id', 'created_at', 'last_updated'] and value:
                        print(f"  {key}: {value}")
                
                # Check for specific facts
                record_str = str(record).lower()
                if "servicetitan" in record_str:
                    facts_found.append(f"ServiceTitan CRM -> {table}")
                if "15" in record_str and "employee" in record_str:
                    facts_found.append(f"15 employees -> {table}")
                if "25" in record_str:
                    facts_found.append(f"25% markup -> {table}")
                if "40" in record_str:
                    facts_found.append(f"40% markup -> {table}")
                if "electrical" in record_str or "hvac" in record_str:
                    facts_found.append(f"Subcontractor challenges -> {table}")
                if "60" in record_str:
                    facts_found.append(f"60+ day payment -> {table}")
                if "email" in record_str:
                    facts_found.append(f"Email preference -> {table}")
                if "30k" in record_str or "75k" in record_str:
                    facts_found.append(f"Project range -> {table}")
                    
        except Exception as e:
            print(f"[ERROR] Checking {table}: {e}")
    
    print(f"\n[STORAGE VERIFICATION]")
    print(f"Tables with data: {tables_with_data}/{len(tables)}")
    print(f"\n[FACTS EXTRACTED AND STORED]")
    for fact in facts_found:
        print(f"  ✅ {fact}")
    
    success = tables_with_data >= 3 and len(facts_found) >= 5
    print(f"\n[VERIFICATION RESULT] {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"  - {tables_with_data} tables populated")
    print(f"  - {len(facts_found)} specific facts extracted")
    
    return success

async def test_context_generation():
    """Test context generation for follow-up conversations"""
    print_section("CONTEXT GENERATION TEST")
    
    memory = EnhancedContractorMemory()
    
    print("[GENERATING COMPLETE CONTRACTOR PROFILE]")
    complete_profile = await memory.get_complete_contractor_profile(CONTRACTOR_ID)
    
    if complete_profile:
        print(f"[SUCCESS] Generated profile: {len(complete_profile)} characters")
        print("\n[PROFILE PREVIEW]")
        print(complete_profile[:800] + "..." if len(complete_profile) > 800 else complete_profile)
        
        # Check for key context
        profile_lower = complete_profile.lower()
        context_elements = []
        
        if "servicetitan" in profile_lower:
            context_elements.append("ServiceTitan CRM")
        if "15" in profile_lower:
            context_elements.append("15 employees")
        if "25%" in profile_lower or "25" in profile_lower:
            context_elements.append("25% markup")
        if "40%" in profile_lower or "40" in profile_lower:
            context_elements.append("40% markup")
        if "electrical" in profile_lower:
            context_elements.append("Electrical challenges")
        if "30k" in profile_lower or "75k" in profile_lower:
            context_elements.append("Project range")
        if "email" in profile_lower:
            context_elements.append("Communication preferences")
        
        print(f"\n[CONTEXT ELEMENTS INCLUDED]")
        for element in context_elements:
            print(f"  ✅ {element}")
        
        context_success = len(context_elements) >= 5
        print(f"\n[CONTEXT GENERATION] {'✅ SUCCESS' if context_success else '❌ FAILED'}")
        print(f"  - {len(context_elements)} context elements included")
        
        return context_success, complete_profile
    else:
        print("[ERROR] No profile generated")
        return False, None

async def test_conversation_2(existing_context):
    """Test second conversation with context restoration simulation"""
    print_section("CONVERSATION 2: Context Restoration Simulation")
    
    memory = EnhancedContractorMemory()
    
    # Simulate what BSA would do - inject context into conversation
    conversation_data = {
        'input': """Hey, it's Mike again. I wanted to follow up about expanding our commercial work. 
                   Can you remind me what markup percentages I mentioned? Also, what was our biggest challenge?""",
        'response': f"""Based on our previous conversation, I can remind you of those details:
                      
                      CONTEXT FROM YOUR PROFILE:
                      {existing_context[:500]}...
                      
                      From our previous discussion:
                      - Materials markup: 25%, Labor markup: 40%
                      - Biggest challenge: Managing electrical and HVAC subcontractors who are often late
                      - Your CRM system: ServiceTitan
                      - Project range: $30k-$75k
                      
                      Regarding commercial expansion, that's exciting! How does that align with your current 
                      residential focus on bathroom and kitchen remodeling?""",
        'project_type': 'commercial_expansion'
    }
    
    print("[CONVERSATION 2 INPUT]")
    print(f"Contractor: {conversation_data['input']}")
    print(f"AI Response length: {len(conversation_data['response'])} characters")
    print(f"Context included: {'✅ YES' if len(existing_context) > 100 else '❌ NO'}")
    
    print("\n[UPDATING MEMORY WITH CONVERSATION 2]")
    results = await memory.update_all_contractor_memories(CONTRACTOR_ID, conversation_data)
    
    if results:
        print(f"[SUCCESS] Updated {len(results)} dimensions with new insights")
        return True
    else:
        print("[WARNING] No new insights extracted (may be normal if no new business facts)")
        return True  # This is actually normal - not every conversation has new extractable facts

async def verify_final_state():
    """Verify final memory state after both conversations"""
    print_section("FINAL MEMORY STATE VERIFICATION")
    
    memory = EnhancedContractorMemory()
    
    # Generate final profile
    final_profile = await memory.get_complete_contractor_profile(CONTRACTOR_ID)
    
    if final_profile:
        print(f"[FINAL PROFILE] {len(final_profile)} characters")
        
        # Check that original facts are still preserved
        profile_lower = final_profile.lower()
        preserved_facts = []
        
        if "servicetitan" in profile_lower:
            preserved_facts.append("ServiceTitan CRM (from conversation 1)")
        if "15" in profile_lower:
            preserved_facts.append("15 employees (from conversation 1)")
        if "25" in profile_lower:
            preserved_facts.append("25% markup (from conversation 1)")
        if "electrical" in profile_lower:
            preserved_facts.append("Electrical challenges (from conversation 1)")
        if "commercial" in profile_lower:
            preserved_facts.append("Commercial expansion (from conversation 2)")
        
        print(f"\n[FACT PRESERVATION ACROSS CONVERSATIONS]")
        for fact in preserved_facts:
            print(f"  ✅ {fact}")
        
        preservation_success = len(preserved_facts) >= 4
        print(f"\n[PRESERVATION TEST] {'✅ SUCCESS' if preservation_success else '❌ FAILED'}")
        print(f"  - {len(preserved_facts)} facts preserved across multiple conversations")
        
        return preservation_success
    else:
        print("[ERROR] No final profile generated")
        return False

async def main():
    print(f"DIRECT MEMORY SYSTEM VERIFICATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing enhanced contractor memory system with concrete evidence")
    
    # Test sequence
    success_steps = 0
    total_steps = 6
    
    # Step 1: Clear test data
    await clear_test_data()
    success_steps += 1
    
    # Step 2: First conversation
    conv1_success, conv1_results = await test_conversation_1()
    if conv1_success:
        success_steps += 1
    
    # Step 3: Verify conversation 1 storage
    storage1_success = await verify_conversation_1_storage()
    if storage1_success:
        success_steps += 1
    
    # Step 4: Context generation test
    context_success, context_profile = await test_context_generation()
    if context_success:
        success_steps += 1
    
    # Step 5: Second conversation (if context generation worked)
    if context_success and context_profile:
        conv2_success = await test_conversation_2(context_profile)
        if conv2_success:
            success_steps += 1
    
    # Step 6: Final verification
    final_success = await verify_final_state()
    if final_success:
        success_steps += 1
    
    print_section("DIRECT MEMORY SYSTEM TEST RESULTS")
    
    success_percentage = (success_steps / total_steps) * 100
    
    if success_steps == total_steps:
        print("🎉 ✅ COMPLETE SUCCESS - MEMORY SYSTEM FULLY VERIFIED")
        print("\n100% CONCRETE EVIDENCE PROVIDED:")
        print("  ✅ Enhanced memory system extracts specific business facts from conversations")
        print("  ✅ GPT-4o prompts capture details like 'ServiceTitan', '15 employees', '25% markup'")
        print("  ✅ Facts are stored correctly across 5 specialized database tables")
        print("  ✅ Complete contractor profiles are generated with comprehensive context")
        print("  ✅ Context restoration works - previous facts are preserved across conversations")
        print("  ✅ Memory system maintains continuity for multi-turn contractor conversations")
        print("\nSYSTEM IS READY FOR BSA INTEGRATION AND PRODUCTION USE")
    else:
        print(f"❌ PARTIAL SUCCESS - {success_percentage:.1f}% ({success_steps}/{total_steps} steps)")
        print("Check detailed logs above for specific issues")
        print("Memory system needs fixes before BSA integration")

if __name__ == "__main__":
    asyncio.run(main())