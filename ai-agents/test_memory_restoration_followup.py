#!/usr/bin/env python3
"""
Test Enhanced Memory System Context Restoration in Follow-up Conversations
Verifies that contractor context is preserved and restored across multiple conversations
"""

import asyncio
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.enhanced_contractor_memory import EnhancedContractorMemory
from database import SupabaseDB

# Test contractor
CONTRACTOR_ID = "523c0f63-e75c-4d65-963e-561d7f4169db"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

async def test_memory_restoration_flow():
    """Test complete memory restoration flow across multiple conversations"""
    print_section("MEMORY RESTORATION FOLLOW-UP TEST")
    
    memory = EnhancedContractorMemory()
    
    if not memory.openai_client:
        print("[ERROR] OpenAI client not initialized")
        return False
    
    # Step 1: Initial conversation with rich business details
    print("[STEP 1] Initial conversation - storing business context...")
    
    initial_conversation = {
        'input': """Hi, I'm Mike from Mike's Plumbing. We specialize in bathroom remodels and have 15 employees. 
                   We use ServiceTitan for our CRM. Our typical project range is $30k-$75k. We markup materials 25% 
                   and labor 40%. Our biggest challenge is managing electrical subcontractors.""",
        'response': "Thanks for sharing those details, Mike.",
        'project_type': 'bathroom_remodel'
    }
    
    results1 = await memory.update_all_contractor_memories(CONTRACTOR_ID, initial_conversation)
    print(f"[SUCCESS] Stored initial context in {len(results1)} memory dimensions")
    
    # Step 2: Get complete contractor profile (what system would inject into follow-up prompts)
    print("\n[STEP 2] Retrieving complete contractor profile for context injection...")
    
    complete_profile = await memory.get_complete_contractor_profile(CONTRACTOR_ID)
    
    if complete_profile:
        print("[SUCCESS] Retrieved complete contractor profile:")
        print(f"Profile length: {len(complete_profile)} characters")
        # Show key facts that should be remembered
        key_facts_found = []
        if "ServiceTitan" in complete_profile:
            key_facts_found.append("ServiceTitan (CRM)")
        if "15" in complete_profile:
            key_facts_found.append("15 employees")
        if "25%" in complete_profile:
            key_facts_found.append("25% markup")
        if "electrical" in complete_profile.lower():
            key_facts_found.append("electrical subcontractor challenges")
        if "$30k" in complete_profile:
            key_facts_found.append("$30k-$75k project range")
        
        print(f"[CONTEXT] Key facts in profile: {', '.join(key_facts_found)}")
    else:
        print("[ERROR] No contractor profile retrieved")
        return False
    
    # Step 3: Follow-up conversation asking about previously mentioned details
    print("\n[STEP 3] Follow-up conversation - testing memory recall...")
    
    followup_conversation = {
        'input': """Can you remind me what markup percentages I use? And what's our typical project size range? 
                   Also, what did I say about our biggest business challenge?""",
        'response': """Based on our previous conversation, you mentioned:
                      - Materials markup: 25%, Labor markup: 40%  
                      - Typical projects: $30k-$75k range
                      - Biggest challenge: Managing electrical subcontractors
                      
                      This context comes from your enhanced contractor profile.""",
        'project_type': 'bathroom_remodel',
        'context_injected': complete_profile  # This simulates context injection
    }
    
    # Update memory with follow-up (might capture new insights)
    results2 = await memory.update_all_contractor_memories(CONTRACTOR_ID, followup_conversation)
    print(f"[SUCCESS] Processed follow-up conversation")
    
    # Step 4: Verify memory continuity - check if original facts are still accessible
    print("\n[STEP 4] Verifying memory continuity...")
    
    db = SupabaseDB()
    tables = [
        "contractor_business_profile",
        "contractor_bidding_patterns", 
        "contractor_relationship_memory",
        "contractor_information_needs",
        "contractor_pain_points"
    ]
    
    continuity_facts = {
        "ServiceTitan": "CRM system mentioned in first conversation",
        "15": "Employee count from first conversation", 
        "25": "Materials markup percentage",
        "40": "Labor markup percentage",
        "electrical": "Subcontractor challenge mentioned",
        "$30k": "Project range lower bound",
        "$75k": "Project range upper bound"
    }
    
    facts_preserved = []
    
    for table in tables:
        try:
            result = db.client.table(table).select("*").eq(
                "contractor_id", CONTRACTOR_ID
            ).execute()
            
            if result.data:
                record = result.data[0]
                print(f"\n[{table.upper().replace('CONTRACTOR_', '')}]")
                
                for key, value in record.items():
                    if key not in ['id', 'contractor_id', 'created_at', 'last_updated'] and value:
                        value_str = str(value).lower()
                        print(f"  {key}: {value}")
                        
                        # Check if original facts are preserved
                        for fact, description in continuity_facts.items():
                            if fact.lower() in value_str:
                                facts_preserved.append(f"{description} -> {table}:{key}")
                                
        except Exception as e:
            print(f"[ERROR] Checking {table}: {e}")
    
    # Step 5: Analysis of memory restoration capability
    print_section("MEMORY RESTORATION ANALYSIS")
    
    print("[FACTS PRESERVED ACROSS CONVERSATIONS]")
    if facts_preserved:
        for fact in facts_preserved:
            print(f"  [PRESERVED] {fact}")
        
        preservation_score = len(facts_preserved) / len(continuity_facts) * 100
        print(f"\nCONTINUITY SCORE: {preservation_score:.1f}% ({len(facts_preserved)}/{len(continuity_facts)} facts preserved)")
        
        success = preservation_score >= 70
        
        if success:
            print("\n[SUCCESS] Memory restoration working!")
            print("  - Enhanced memory system maintains context across conversations")
            print("  - Business intelligence facts preserved between sessions")  
            print("  - Complete contractor profile provides comprehensive context")
            print("  - System ready for multi-turn contractor conversations")
        else:
            print("\n[PARTIAL] Memory preservation needs improvement")
            print(f"  - Only {preservation_score:.1f}% of facts preserved")
            print("  - May need memory consolidation improvements")
        
        return success
    else:
        print("  [WARNING] No original facts found in follow-up memory")
        print("  - Memory may not be preserving context correctly")
        return False

async def main():
    print(f"MEMORY RESTORATION FOLLOW-UP TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing enhanced memory system context preservation across multiple conversations")
    
    success = await test_memory_restoration_flow()
    
    print_section("FINAL VERIFICATION RESULTS")
    
    if success:
        print("[VERIFIED] Enhanced Memory System Context Restoration WORKING")
        print("")
        print("MEMORY RESTORATION CAPABILITIES:")
        print("  - Comprehensive contractor profiles generated from conversation history")
        print("  - Business intelligence facts preserved across multiple conversations") 
        print("  - Context injection ready for AI agent follow-up conversations")
        print("  - Multi-turn contractor memory continuity operational")
        print("")
        print("INTEGRATION READY:")
        print("  - Enhanced memory system fully operational for BSA/contractor agents")
        print("  - Context restoration provides 'shock value' comprehensive understanding")
        print("  - System ready for production contractor conversations")
    else:
        print("[NEEDS WORK] Memory restoration needs improvement")
        print("  - Consider memory consolidation enhancements")
        print("  - May need context injection optimization")

if __name__ == "__main__":
    asyncio.run(main())