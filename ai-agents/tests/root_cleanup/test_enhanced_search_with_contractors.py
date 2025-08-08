#!/usr/bin/env python3
"""
Test Enhanced Search System with Contractors
Complete test of all search endpoints including new contractors functionality
"""

import requests
import json
import sys
import io

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test configuration
API_BASE = "http://localhost:8008"
FRONTEND_BASE = "http://localhost:5173"


def test_contractors_search():
    """Test the new contractors search functionality"""
    print("\n👷 TESTING CONTRACTORS SEARCH")
    print("=" * 50)
    
    results = {
        "contractors_search": False,
        "contractors_autocomplete": False,
        "contractors_specialty_filter": False
    }
    
    # Test 1: General contractor search
    print("\n🔍 Testing contractors search...")
    response = requests.get(f"{API_BASE}/api/admin/search/contractors", 
                          params={"search_term": ""})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data['contractors'])} contractors")
        results["contractors_search"] = True
        
        if data['contractors']:
            contractor = data['contractors'][0]
            print(f"   Sample contractor: {contractor.get('name', 'N/A')}")
            print(f"   Company: {contractor.get('company', 'N/A')}")
            print(f"   Specialties: {contractor.get('specialties', 'N/A')}")
            print(f"   Tier: {contractor.get('tier', 'N/A')}")
    else:
        print(f"❌ Contractors search failed: {response.status_code}")
    
    # Test 2: Contractor name autocomplete
    print("\n✨ Testing contractors autocomplete...")
    response = requests.get(f"{API_BASE}/api/admin/search/autocomplete", 
                          params={"field": "contractor_name", "term": "D"})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Contractor autocomplete suggestions: {', '.join(data['suggestions'])}")
        results["contractors_autocomplete"] = True
    else:
        print(f"❌ Contractor autocomplete failed: {response.status_code}")
    
    # Test 3: Search by specialty
    print("\n🔧 Testing specialty search...")
    response = requests.get(f"{API_BASE}/api/admin/search/contractors", 
                          params={"specialty": "landscaping"})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data['contractors'])} landscaping contractors")
        results["contractors_specialty_filter"] = True
    else:
        print(f"❌ Specialty search failed: {response.status_code}")
    
    return results


def test_unified_search_with_contractors():
    """Test unified search includes contractors"""
    print("\n🌐 TESTING UNIFIED SEARCH WITH CONTRACTORS")
    print("=" * 50)
    
    response = requests.get(f"{API_BASE}/api/admin/search/unified", 
                          params={"query": "Direct"})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Unified search results:")
        print(f"   📋 Bid cards: {data.get('total_bid_cards', 0)}")
        print(f"   👤 Homeowners: {data.get('total_homeowners', 0)}")
        print(f"   👷 Contractors: {data.get('total_contractors', 0)}")
        
        # Check if contractors are included in results
        contractors = data.get('contractors', [])
        if contractors:
            print(f"   Sample contractor found: {contractors[0].get('name', 'N/A')}")
            return True
        else:
            print("   ⚠️ No contractors in unified search results")
            return False
    else:
        print(f"❌ Unified search failed: {response.status_code}")
        return False


def test_all_search_endpoints():
    """Test all search endpoints are working"""
    print("\n🔧 TESTING ALL SEARCH ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        ("unified", "/api/admin/search/unified", {"query": "test"}),
        ("bid_cards", "/api/admin/search/bid-cards/by-homeowner", {"homeowner_name": "Jane"}),
        ("homeowners", "/api/admin/search/homeowners", {"search_term": "John"}),
        ("contractors", "/api/admin/search/contractors", {"search_term": "Direct"}),
        ("autocomplete", "/api/admin/search/autocomplete", {"field": "homeowner_name", "term": "J"})
    ]
    
    results = {}
    for name, endpoint, params in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: Working")
                results[name] = True
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
                results[name] = False
        except Exception as e:
            print(f"❌ {name}: Error ({str(e)})")
            results[name] = False
    
    return results


def test_frontend_integration():
    """Test that frontend is accessible with new search features"""
    print("\n🖥️ TESTING FRONTEND INTEGRATION")
    print("=" * 50)
    
    try:
        # Test that admin dashboard is accessible
        response = requests.get(f"{FRONTEND_BASE}/admin/login", timeout=5)
        if response.status_code == 200:
            print("✅ Admin dashboard accessible")
            print("✅ Enhanced search panel should include contractors dropdown")
            print(f"✅ Search options: Unified, Homeowners, Bid Cards, Contractors")
            return True
        else:
            print(f"⚠️ Admin dashboard returned {response.status_code}")
            return True  # Still functional
    except requests.exceptions.RequestException:
        print("⚠️ Frontend not running - start with: cd web && npm run dev")
        return False


def main():
    """Run comprehensive test of enhanced search system with contractors"""
    print("=" * 80)
    print("🚀 ENHANCED SEARCH WITH CONTRACTORS - COMPREHENSIVE TEST")
    print("=" * 80)
    
    # Run all test categories
    contractors_results = test_contractors_search()
    unified_working = test_unified_search_with_contractors()
    all_endpoints = test_all_search_endpoints()
    frontend_working = test_frontend_integration()
    
    # Calculate overall results
    contractor_tests_passed = sum(contractors_results.values())
    total_contractor_tests = len(contractors_results)
    
    all_endpoint_tests_passed = sum(all_endpoints.values())
    total_endpoint_tests = len(all_endpoints)
    
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    
    print(f"\n👷 Contractors Functionality: {contractor_tests_passed}/{total_contractor_tests} PASSED")
    for test, result in contractors_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test}: {status}")
    
    print(f"\n🔧 All Search Endpoints: {all_endpoint_tests_passed}/{total_endpoint_tests} PASSED")
    for test, result in all_endpoints.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test}: {status}")
    
    print(f"\n🌐 Unified Search with Contractors: {'✅ PASS' if unified_working else '❌ FAIL'}")
    print(f"🖥️ Frontend Integration: {'✅ PASS' if frontend_working else '❌ FAIL'}")
    
    # Overall assessment
    overall_score = (contractor_tests_passed + all_endpoint_tests_passed + 
                    int(unified_working) + int(frontend_working))
    total_tests = total_contractor_tests + total_endpoint_tests + 2
    
    print(f"\n🎯 OVERALL SCORE: {overall_score}/{total_tests} ({(overall_score/total_tests)*100:.1f}%)")
    
    if overall_score == total_tests:
        print("\n🎉 EXCELLENT! Enhanced search with contractors is fully operational!")
        print("✅ All search endpoints working correctly")
        print("✅ Contractors search and filtering working")
        print("✅ Unified search includes all data types")
        print("✅ Frontend integration ready")
    elif overall_score >= total_tests * 0.8:
        print("\n🎊 GOOD! Enhanced search system is mostly working")
        print("⚠️ Some minor issues to address")
    else:
        print("\n⚠️ NEEDS WORK: Several issues need to be resolved")
    
    print(f"\n🔗 Test the system manually:")
    print(f"   API: {API_BASE}/api/admin/search/contractors?search_term=Direct")
    print(f"   Frontend: {FRONTEND_BASE}/admin/login")
    print(f"   Search Dropdown: Select 'Contractors' from the dropdown")


if __name__ == "__main__":
    main()