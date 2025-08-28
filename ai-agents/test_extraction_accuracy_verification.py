#!/usr/bin/env python3
"""
VERIFICATION: Enhanced Memory System Extraction Accuracy
Shows specific facts are now captured instead of generic categories
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

async def test_enhanced_extraction_accuracy():
    """Verify that enhanced prompts extract specific facts"""
    print_section("ENHANCED MEMORY EXTRACTION ACCURACY VERIFICATION")
    
    memory = EnhancedContractorMemory()
    
    if not memory.openai_client:
        print("[ERROR] OpenAI client not initialized")
        return False
    
    # Rich conversation with specific facts
    conversation_data = {
        'input': """Hi, I'm Mike from Mike's Plumbing. We use ServiceTitan for CRM and have 15 employees. 
                   We specialize in bathroom and kitchen remodeling, with projects typically in the $30k-$75k range.
                   We markup materials 25% and labor 40%. Our biggest challenge is managing electrical and HVAC 
                   subcontractors. Cash flow gets tight when customers take 60+ days to pay. We're looking to 
                   expand into commercial work next year. I prefer email for non-urgent communication but text 
                   me for emergencies.""",
        'response': "Thank you for sharing those business details, Mike.",
        'project_type': 'bathroom_remodel'
    }
    
    print("[TEST] Extracting facts from rich contractor conversation...")
    print("[INPUT] Conversation contains specific facts:")
    print("        - ServiceTitan (CRM system)")
    print("        - 15 employees") 
    print("        - $30k-$75k project range")
    print("        - 25% materials markup, 40% labor markup")
    print("        - Electrical/HVAC subcontractor challenges")
    print("        - 60+ day payment delays")
    print("        - Commercial expansion plans")
    print("        - Email/text communication preferences")
    
    # Test each memory dimension individually
    results = {}
    
    # 1. Business Memory
    try:
        business_result = await memory._update_business_memory(CONTRACTOR_ID, conversation_data)
        if business_result:
            results['business'] = business_result
    except Exception as e:
        print(f"[ERROR] Business memory: {e}")
    
    # 2. Project Memory  
    try:
        project_result = await memory._update_project_memory(CONTRACTOR_ID, conversation_data)
        if project_result:
            results['project'] = project_result
    except Exception as e:
        print(f"[ERROR] Project memory: {e}")
        
    # 3. Relationship Memory
    try:
        relationship_result = await memory._update_relationship_memory(CONTRACTOR_ID, conversation_data)  
        if relationship_result:
            results['relationship'] = relationship_result
    except Exception as e:
        print(f"[ERROR] Relationship memory: {e}")
        
    # 4. Communication Memory
    try:
        comm_result = await memory._update_communication_memory(CONTRACTOR_ID, conversation_data)
        if comm_result:
            results['communication'] = comm_result
    except Exception as e:
        print(f"[ERROR] Communication memory: {e}")
        
    # 5. Pain Points Memory
    try:
        pain_result = await memory._update_pain_points_memory(CONTRACTOR_ID, conversation_data)
        if pain_result:
            results['pain_points'] = pain_result
    except Exception as e:
        print(f"[ERROR] Pain points memory: {e}")
    
    print_section("SPECIFIC FACTS EXTRACTED")
    
    specific_facts_captured = []
    
    for dimension, data in results.items():
        print(f"\n[{dimension.upper()} MEMORY]")
        for key, value in data.items():
            if key not in ['contractor_id', 'last_updated', 'total_updates'] and value is not None:
                print(f"  {key}: {value}")
                
                # Check for specific facts
                value_str = str(value).lower()
                if any(fact in value_str for fact in ['servicetitan', '15', '25', '40', 'electrical', 'hvac', '60', 'commercial', 'email', 'text']):
                    specific_facts_captured.append(f"{dimension}: {key} = {value}")
    
    print_section("ACCURACY ANALYSIS")
    
    print("[SPECIFIC FACTS CAPTURED]:")
    if specific_facts_captured:
        for fact in specific_facts_captured:
            print(f"  [FOUND] {fact}")
        
        accuracy_score = len(specific_facts_captured) / 8 * 100  # 8 key facts in conversation
        print(f"\nACCURACY SCORE: {accuracy_score:.1f}% ({len(specific_facts_captured)}/8 key facts)")
        
        if accuracy_score >= 60:
            print("[SUCCESS] Enhanced prompts working - capturing specific facts!")
            return True
        else:
            print("[PARTIAL] Some facts captured but needs improvement")
            return False
    else:
        print("  [WARNING] No specific facts detected in extracted data")
        return False

async def main():
    print(f"EXTRACTION ACCURACY VERIFICATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing if enhanced GPT-4o prompts extract specific facts vs generic categories")
    
    success = await test_enhanced_extraction_accuracy()
    
    print_section("FINAL VERIFICATION RESULTS")
    
    if success:
        print("[VERIFIED] Enhanced Memory System Extraction WORKING")
        print("")
        print("IMPROVEMENTS IMPLEMENTED:")
        print("  - GPT-4o prompts now focus on specific facts mentioned")
        print("  - Extraction captures actual business details (CRM systems, numbers, etc.)")
        print("  - Memory system stores precise information instead of generic categories")
        print("  - Business intelligence now reflects real contractor conversations")
        print("")
        print("NEXT STEPS:")
        print("  - Enhanced memory system ready for production use")
        print("  - Fix unified memory table structure issue")
        print("  - Test memory restoration in follow-up conversations")
    else:
        print("[NEEDS WORK] Extraction accuracy still needs improvement")
        print("Consider further prompt refinement or field mapping adjustments")

if __name__ == "__main__":
    asyncio.run(main())