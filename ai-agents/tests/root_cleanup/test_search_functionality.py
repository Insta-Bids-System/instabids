#!/usr/bin/env python3
"""
Test Admin Search Functionality
Tests all search endpoints to ensure they work correctly
"""

import requests
import json
import sys
import io

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test configuration
API_BASE = "http://localhost:8008"


def test_search_bid_cards_by_homeowner():
    """Test searching bid cards by homeowner ID and name"""
    print("\n🔍 Testing bid card search by homeowner...")
    
    # Test by homeowner name (partial match)
    response = requests.get(f"{API_BASE}/api/admin/search/bid-cards/by-homeowner", 
                          params={"homeowner_name": "Jane"})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['bid_cards'])} bid cards for homeowners named 'Jane'")
        
        # Show first result if available
        if result['bid_cards']:
            card = result['bid_cards'][0]
            print(f"   📋 Sample: {card.get('bid_card_number')} - {card.get('homeowner_name')}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False


def test_search_homeowners():
    """Test searching homeowners by various criteria"""
    print("\n👤 Testing homeowner search...")
    
    # Test general search term
    response = requests.get(f"{API_BASE}/api/admin/search/homeowners", 
                          params={"search_term": "Jane"})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['homeowners'])} homeowners matching 'Jane'")
        
        # Show first result if available
        if result['homeowners']:
            homeowner = result['homeowners'][0]
            print(f"   👤 Sample: {homeowner.get('homeowner_name')} ({homeowner.get('bid_card_count', 0)} bid cards)")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False


def test_unified_search():
    """Test unified search across all entities"""
    print("\n🌐 Testing unified search...")
    
    # Test searching for a term across all entities
    response = requests.get(f"{API_BASE}/api/admin/search/unified", 
                          params={"query": "kitchen"})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Unified search for 'kitchen':")
        print(f"   📋 Bid cards: {result['total_bid_cards']}")
        print(f"   👤 Homeowners: {result['total_homeowners']}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False


def test_homeowner_summary():
    """Test getting homeowner summary"""
    print("\n📊 Testing homeowner summary...")
    
    # First get a homeowner ID from bid cards
    bid_cards_response = requests.get(f"{API_BASE}/api/admin/search/bid-cards/by-homeowner", 
                                    params={"limit": 1})
    
    if bid_cards_response.status_code == 200:
        bid_cards_result = bid_cards_response.json()
        
        if bid_cards_result['bid_cards']:
            homeowner_id = bid_cards_result['bid_cards'][0].get('homeowner_id')
            
            if homeowner_id:
                # Test homeowner summary
                response = requests.get(f"{API_BASE}/api/admin/search/homeowner/{homeowner_id}/summary")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Homeowner summary for {result['homeowner_name']}:")
                    print(f"   📊 Total bid cards: {result['statistics']['total_bid_cards']}")
                    print(f"   💰 Budget range: ${result['statistics']['total_budget_range']['min']:,} - ${result['statistics']['total_budget_range']['max']:,}")
                    print(f"   🏗️ Project types: {', '.join(result['statistics']['project_types'])}")
                    
                    return True
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")
                    return False
            else:
                print("⚠️ No homeowner_id found in bid cards")
                return False
        else:
            print("⚠️ No bid cards found to test homeowner summary")
            return False
    else:
        print(f"❌ Failed to get bid cards: {bid_cards_response.status_code}")
        return False


def test_autocomplete():
    """Test autocomplete functionality"""
    print("\n✨ Testing autocomplete...")
    
    # Test homeowner name autocomplete
    response = requests.get(f"{API_BASE}/api/admin/search/autocomplete", 
                          params={"field": "homeowner_name", "term": "J"})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Autocomplete for homeowner names starting with 'J':")
        for suggestion in result['suggestions'][:3]:  # Show first 3
            print(f"   💡 {suggestion}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False


def test_bid_card_search_by_id():
    """Test searching bid cards by specific homeowner ID"""
    print("\n🎯 Testing bid card search by homeowner ID...")
    
    # Get a homeowner ID from existing data
    response = requests.get(f"{API_BASE}/api/admin/search/homeowners", params={"limit": 1})
    
    if response.status_code == 200:
        result = response.json()
        
        if result['homeowners']:
            homeowner_id = result['homeowners'][0]['homeowner_id']
            
            # Search bid cards by this specific homeowner ID
            bid_search = requests.get(f"{API_BASE}/api/admin/search/bid-cards/by-homeowner", 
                                    params={"homeowner_id": homeowner_id})
            
            if bid_search.status_code == 200:
                bid_result = bid_search.json()
                print(f"✅ Found {len(bid_result['bid_cards'])} bid cards for homeowner ID {homeowner_id}")
                return True
            else:
                print(f"❌ Bid search failed: {bid_search.status_code}")
                return False
        else:
            print("⚠️ No homeowners found to test with")
            return False
    else:
        print(f"❌ Homeowner search failed: {response.status_code}")
        return False


def main():
    """Run complete search functionality test"""
    print("=" * 60)
    print("🚀 ADMIN SEARCH FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        test_search_bid_cards_by_homeowner,
        test_search_homeowners,
        test_unified_search,
        test_homeowner_summary,
        test_autocomplete,
        test_bid_card_search_by_id
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} PASSED")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL SEARCH FUNCTIONALITY TESTS PASSED!")
        print("✅ Admin search API is fully operational")
    else:
        print("⚠️ Some tests failed. Check backend server and database.")
    
    print(f"\n🔗 Test the search API directly at:")
    print(f"   {API_BASE}/api/admin/search/bid-cards/by-homeowner?homeowner_name=Jane")
    print(f"   {API_BASE}/api/admin/search/homeowners?search_term=Jane")
    print(f"   {API_BASE}/api/admin/search/unified?query=kitchen")


if __name__ == "__main__":
    main()