#!/usr/bin/env python3
"""
Test improved GPT-4o extraction accuracy with specific fact prompts
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
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

async def test_specific_fact_extraction():
    """Test that the improved prompts extract specific facts"""
    print_section("IMPROVED EXTRACTION ACCURACY TEST")
    
    # Initialize memory system
    memory = EnhancedContractorMemory()
    
    if not memory.openai_client:
        print("[ERROR] OpenAI client not initialized - check API key")
        return False
    
    # Create conversation with rich specific facts
    conversation_data = {
        'input': """Hi, I'm Mike from Mike's Plumbing. We use ServiceTitan for our CRM and job management. 
                   We have 15 employees and have been in business for 15 years. We specialize in bathroom 
                   and kitchen remodeling, with our sweet spot being projects in the $30k-$75k range.
                   
                   Our pricing is competitive: we markup materials 25% and labor 40%. We typically require 
                   30% down, 40% at rough-in, and 30% at completion.
                   
                   The biggest challenge we face is managing electrical and HVAC subcontractors. Finding 
                   reliable subs is tough, and coordinating schedules is a nightmare. Cash flow can be 
                   tight when customers take 60+ days to pay.
                   
                   We're looking to expand into commercial work next year and hoping to add 5 more techs. 
                   I prefer email for non-urgent stuff but text me for emergencies. I like detailed 
                   proposals with material breakdowns and timeline charts.
                   
                   For this bathroom project, I can do it for $45,000 with a 3-week timeline.""",
        'response': "Thank you for sharing those detailed business insights, Mike.",
        'project_type': 'bathroom_remodel',
        'bid_amount': 45000,
        'contractor_context': {
            'company_name': "Mike's Plumbing",
            'years_in_business': 15
        }
    }
    
    print("[INFO] Testing improved extraction prompts...")
    
    # Update memories with improved prompts
    results = await memory.update_all_contractor_memories(CONTRACTOR_ID, conversation_data)
    
    if not results:
        print("[ERROR] No memory updates returned")
        return False
    
    print(f"[SUCCESS] Updated {len(results)} memory dimensions")
    
    # Verify database contents
    db = SupabaseDB()
    tables = [
        "contractor_business_profile",
        "contractor_bidding_patterns",
        "contractor_relationship_memory",
        "contractor_information_needs",
        "contractor_pain_points"
    ]
    
    specific_facts_found = []
    
    for table in tables:
        try:
            result = db.client.table(table).select("*").eq(
                "contractor_id", CONTRACTOR_ID
            ).execute()
            
            if result.data:
                record = result.data[0]
                print(f"\n[CHECKING] {table}:")
                
                # Check for specific facts from conversation
                for key, value in record.items():
                    if key not in ['id', 'contractor_id', 'created_at', 'last_updated'] and value:
                        print(f"  - {key}: {value}")
                        
                        # Check if specific facts were captured
                        if isinstance(value, (str, int, float)):
                            value_str = str(value).lower()
                            
                            # Check for specific facts from conversation
                            conversation_facts = [
                                "servicetitan", "15", "bathroom", "kitchen", "$30k", "$75k", 
                                "25%", "40%", "30%", "electrical", "hvac", "subcontractor", 
                                "60+ days", "commercial", "email", "text", "emergencies",
                                "material breakdown", "timeline charts", "$45,000", "3-week"
                            ]
                            
                            for fact in conversation_facts:
                                if fact.replace('$', '').replace('%', '').replace('-', '').replace('+', '') in value_str.replace('$', '').replace('%', '').replace('-', '').replace('+', ''):
                                    specific_facts_found.append(f"{table}: {key} = {value}")
        except Exception as e:
            print(f"[ERROR] Checking {table}: {e}")
    
    print_section("SPECIFIC FACTS CAPTURED")
    
    if specific_facts_found:
        for fact in specific_facts_found:
            print(f"[CAPTURED] {fact}")
            
        accuracy_score = len(specific_facts_found) / 20 * 100  # 20 specific facts in conversation
        print(f"\nIMPROVED ACCURACY SCORE: {accuracy_score:.1f}% ({len(specific_facts_found)}/20 facts captured)")
        
        return accuracy_score > 50  # Should capture at least 50% of specific facts
    else:
        print("[WARNING] No specific facts captured - prompts may still need adjustment")
        return False

async def main():
    print(f"IMPROVED EXTRACTION ACCURACY TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test improved extraction
    accuracy_passed = await test_specific_fact_extraction()
    
    print_section("FINAL RESULTS")
    
    if accuracy_passed:
        print("[SUCCESS] IMPROVED PROMPTS WORKING!")
        print("   - Specific facts extracted instead of generic categories")
        print("   - Memory system captures actual business details")
        print("   - GPT-4o extracts precise information from conversations")
    else:
        print("[NEEDS WORK] Extraction accuracy still needs improvement")
        print("   - Prompts may need further refinement")
        print("   - Field mappings might need adjustment")
        print("   - Consider alternative extraction approach")

if __name__ == "__main__":
    asyncio.run(main())