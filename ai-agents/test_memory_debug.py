#!/usr/bin/env python3
"""
Debug enhanced memory system
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.enhanced_contractor_memory import EnhancedContractorMemory
from database import SupabaseDB

# Test contractor
CONTRACTOR_ID = "523c0f63-e75c-4d65-963e-561d7f4169db"

async def test_direct_memory_update():
    """Test memory system directly without BSA"""
    print("\n" + "="*60)
    print("  DIRECT MEMORY SYSTEM TEST")
    print("="*60 + "\n")
    
    # Initialize memory system
    memory = EnhancedContractorMemory()
    
    # Check if OpenAI client initialized
    if memory.openai_client:
        print("[OK] OpenAI client initialized")
    else:
        print("[ERROR] OpenAI client not initialized - check API key")
        return False
    
    # Create rich conversation data
    conversation_data = {
        'input': """We use ServiceTitan for CRM and job management. We have 15 employees.
                   Our biggest challenge is managing electrical subcontractors.
                   We markup materials 25% and labor 40%. 
                   Cash flow is tight - customers pay in 30-60 days.
                   Looking to expand into commercial work next year.""",
        'response': "Thank you for sharing those business details.",
        'project_type': 'bathroom_remodel',
        'contractor_context': {
            'company_name': "Mike's Plumbing",
            'years_in_business': 15
        }
    }
    
    print("[INFO] Calling update_all_contractor_memories...")
    
    # Update memories
    results = await memory.update_all_contractor_memories(CONTRACTOR_ID, conversation_data)
    
    if results:
        print(f"[SUCCESS] Updated {len(results)} memory dimensions:")
        for dimension, data in results.items():
            print(f"  - {dimension}: Has data")
            # Show first few fields
            if isinstance(data, dict):
                for key, value in list(data.items())[:3]:
                    if key not in ['contractor_id', 'last_updated', 'total_updates']:
                        print(f"    * {key}: {value}")
        return True
    else:
        print("[ERROR] No memory updates returned")
        return False

async def check_database_directly():
    """Check database tables directly"""
    print("\n" + "="*60)
    print("  DATABASE VERIFICATION")
    print("="*60 + "\n")
    
    db = SupabaseDB()
    tables = [
        "contractor_bidding_patterns",
        "contractor_information_needs",
        "contractor_relationship_memory",
        "contractor_business_profile",
        "contractor_pain_points"
    ]
    
    found_any = False
    for table in tables:
        try:
            result = db.client.table(table).select("*").eq(
                "contractor_id", CONTRACTOR_ID
            ).execute()
            
            if result.data:
                print(f"[FOUND] {table}: {len(result.data)} records")
                # Show some data
                record = result.data[0]
                for key, value in list(record.items())[:3]:
                    if key not in ['id', 'contractor_id', 'created_at']:
                        print(f"    * {key}: {value}")
                found_any = True
            else:
                print(f"[EMPTY] {table}: No data")
                
        except Exception as e:
            print(f"[ERROR] {table}: {e}")
    
    return found_any

async def test_memory_extraction():
    """Test if GPT-4o is extracting insights properly"""
    print("\n" + "="*60)
    print("  GPT-4O EXTRACTION TEST")
    print("="*60 + "\n")
    
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    test_prompt = """
Analyze this contractor conversation for BUSINESS INTELLIGENCE - company size, software, challenges.

Contractor Input: "We use ServiceTitan for CRM. We have 15 employees. Cash flow is tight."

Extract business insights:
{
    "crm_system": "system name if mentioned",
    "employee_count": number if mentioned,
    "financial_pain_points": ["list of financial issues"]
}

Only include fields with clear information. Return empty {} if no insights.
"""
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=200,
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        print(f"[GPT-4o Response]:\n{content}")
        
        # Try to parse
        if content.startswith('```'):
            content = content.replace('```json', '').replace('```', '').strip()
        
        import json
        try:
            parsed = json.loads(content)
            print(f"\n[PARSED]: {parsed}")
            return True
        except:
            print(f"\n[ERROR] Could not parse JSON")
            return False
            
    except Exception as e:
        print(f"[ERROR] GPT-4o call failed: {e}")
        return False

async def main():
    print("\n" + "="*80)
    print("  ENHANCED MEMORY SYSTEM DEBUG")
    print("="*80)
    
    # Test 1: Direct memory update
    memory_worked = await test_direct_memory_update()
    
    # Test 2: Check database
    db_has_data = await check_database_directly()
    
    # Test 3: Test GPT-4o extraction
    gpt_works = await test_memory_extraction()
    
    print("\n" + "="*80)
    print("  RESULTS")
    print("="*80)
    print(f"Memory Update: {'PASS' if memory_worked else 'FAIL'}")
    print(f"Database Save: {'PASS' if db_has_data else 'FAIL'}")
    print(f"GPT-4o Extraction: {'PASS' if gpt_works else 'FAIL'}")
    
    if memory_worked and db_has_data:
        print("\n[SUCCESS] Enhanced memory system is WORKING!")
    else:
        print("\n[WARNING] Enhanced memory system needs debugging")

if __name__ == "__main__":
    asyncio.run(main())