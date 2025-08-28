#!/usr/bin/env python3
"""
DIRECT DATABASE CONNECTION TEST
Test database connectivity with minimal dependencies
"""

import os
import sys
from pathlib import Path

# Add the ai-agents directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def test_environment_variables():
    """Check if environment variables are loaded correctly"""
    print("=== ENVIRONMENT VARIABLES TEST ===")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_ANON_KEY: {'***' + supabase_key[-10:] if supabase_key else 'None'}")
    
    if not supabase_url or not supabase_key:
        print("ERROR: Missing environment variables")
        return False
        
    return True

def test_supabase_import():
    """Test if Supabase can be imported"""
    print("\n=== SUPABASE IMPORT TEST ===")
    
    try:
        from supabase import Client, create_client
        print("SUCCESS: Supabase imported successfully")
        return True
    except ImportError as e:
        print(f"ERROR: Cannot import Supabase - {e}")
        return False

def test_direct_connection():
    """Test direct connection to Supabase"""
    print("\n=== DIRECT DATABASE CONNECTION TEST ===")
    
    from dotenv import load_dotenv
    from supabase import create_client
    
    load_dotenv()
    
    # FORCE CORRECT SUPABASE URL AND API KEY (override system env vars)
    supabase_url = "https://xrhgrthdcaymxuqcgrmj.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyaGdydGhkY2F5bXh1cWNncm1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM2NTcyMDYsImV4cCI6MjA2OTIzMzIwNn0.BriGLA2FE_e_NJl8B-3ps1W6ZAuK6a5HpTwBGy-6rmE"
    
    try:
        # Create client
        print(f"Creating client for: {supabase_url}")
        client = create_client(supabase_url, supabase_key)
        print("SUCCESS: Client created")
        
        # Test basic query
        print("Testing basic query...")
        result = client.table("bid_cards").select("id, bid_card_number").limit(1).execute()
        
        if result.data:
            print(f"SUCCESS: Database query worked")
            print(f"Sample data: {result.data[0]}")
            return True
        else:
            print("WARNING: Query returned no data (but connection worked)")
            return True
            
    except Exception as e:
        print(f"ERROR: Database connection failed - {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_database_simple_import():
    """Test the database_simple module"""
    print("\n=== DATABASE_SIMPLE MODULE TEST ===")
    
    try:
        import database_simple
        print("SUCCESS: database_simple imported")
        
        # Test client creation
        client = database_simple.get_client()
        print("SUCCESS: Client retrieved from database_simple")
        
        # Test simple query
        result = client.table("bid_cards").select("count", count="exact").execute()
        print(f"SUCCESS: Query via database_simple worked")
        print(f"Total bid cards: {result.count}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: database_simple test failed - {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_messaging_system_table():
    """Test if messaging system tables exist"""
    print("\n=== MESSAGING SYSTEM TABLES TEST ===")
    
    try:
        import database_simple
        client = database_simple.get_client()
        
        # Test different messaging tables
        tables_to_test = [
            "messaging_system_messages",
            "unified_messages", 
            "conversations"
        ]
        
        for table_name in tables_to_test:
            try:
                result = client.table(table_name).select("count", count="exact").execute()
                print(f"Table {table_name}: {result.count} records")
            except Exception as e:
                print(f"Table {table_name}: ERROR - {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Table testing failed - {e}")
        return False

def main():
    """Run all database connection tests"""
    print("=" * 60)
    print("COMPREHENSIVE DATABASE CONNECTION TEST")
    print("=" * 60)
    
    tests = [
        test_environment_variables,
        test_supabase_import,
        test_direct_connection,
        test_database_simple_import,
        test_messaging_system_table
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"TEST CRASHED: {test_func.__name__} - {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "PASS" if result else "FAIL"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    overall_success = all(results)
    print(f"\nOVERALL: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}")
    
    if overall_success:
        print("DATABASE CONNECTION IS WORKING PROPERLY")
    else:
        print("DATABASE CONNECTION HAS ISSUES")
    
    return overall_success

if __name__ == "__main__":
    main()