#!/usr/bin/env python3
"""
Test Contractor Job Agent with REAL bid cards in database.
This will verify the agent can find actual bid cards and return them to contractors.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv(override=True)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cja.agent import ContractorJobAgent

async def test_agent_finds_real_bid_cards():
    """Test that the agent can find and return actual bid cards"""
    print("=" * 60)
    print("TESTING CONTRACTOR AGENT WITH REAL BID CARDS")
    print("=" * 60)
    
    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found!")
        return False
    
    # Initialize agent
    agent = ContractorJobAgent(api_key=api_key)
    
    # Test contractor in Florida
    contractor_id = "test_florida_contractor"
    contractor_info = {
        "company_name": "Florida Test Contracting",
        "location": "33442",  # Boca Raton, FL
        "services": ["general contracting", "home repairs"],
        "years_experience": 10
    }
    
    print(f"Testing contractor in zip {contractor_info['location']}")
    print("Sending message: 'Show me all available jobs within 25 miles'")
    
    try:
        # Test the agent
        result = await agent.process_message(
            contractor_id=contractor_id,
            message="Show me all available jobs within 25 miles",
            contractor_info=contractor_info
        )
        
        print(f"\nAgent Response:")
        print(f"Intent: {result['intent']}")
        print(f"Search Criteria: {result.get('search_criteria', {})}")
        
        jobs_found = result.get('jobs_found', [])
        print(f"\nJobs Found: {len(jobs_found)}")
        
        if jobs_found:
            print("\nFirst 3 jobs:")
            for i, job in enumerate(jobs_found[:3], 1):
                print(f"  {i}. {job.get('title', 'Untitled Project')}")
                print(f"     Location: {job['location']['city']}, {job['location']['state']} {job['location']['zip_code']}")
                print(f"     Budget: ${job['budget_range']['min']:,} - ${job['budget_range']['max']:,}")
                print(f"     Distance: {job.get('distance_miles', 'Unknown')} miles")
                print(f"     Status: {job.get('status', 'Unknown')}")
                print()
            
            # Test the agent's response quality
            response_text = result['response']
            print(f"Agent Response Text:")
            print(f"'{response_text}'")
            
            # Check if response is helpful
            if len(jobs_found) > 0 and len(response_text) > 50:
                print("\n✅ SUCCESS: Agent found real bid cards and provided helpful response!")
                return True
            else:
                print("\n❌ FAIL: Agent response not helpful enough")
                return False
        else:
            print("\n❌ FAIL: No jobs found - this suggests the radius search isn't working")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

async def test_api_endpoint_directly():
    """Test the API endpoint directly to confirm it works"""
    print("\n" + "=" * 60)
    print("TESTING API ENDPOINT DIRECTLY")
    print("=" * 60)
    
    import requests
    
    try:
        response = requests.get(
            "http://localhost:8008/api/contractor-jobs/search",
            params={
                "zip_code": "33442",
                "radius_miles": 25,
                "page": 1,
                "page_size": 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            jobs = data['job_opportunities']
            
            print(f"API Response: Found {data['total']} total jobs")
            print(f"Zip codes searched: {data['zip_codes_searched']}")
            print(f"Jobs in this page: {len(jobs)}")
            
            if jobs:
                print("\nFirst job details:")
                job = jobs[0]
                print(f"  Title: {job['title']}")
                print(f"  Location: {job['location']['zip_code']}")
                print(f"  Distance: {job['distance_miles']} miles")
                print(f"  Budget: ${job['budget_range']['min']:,} - ${job['budget_range']['max']:,}")
                
                print("\n✅ API endpoint is working and returning real bid cards!")
                return True
            else:
                print("\n❌ API returned no jobs")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("TESTING CONTRACTOR JOB AGENT WITH REAL DATABASE")
        print("Testing both agent conversations AND direct API calls")
        
        # Test API first
        api_works = await test_api_endpoint_directly()
        
        # Test agent if API works
        if api_works:
            agent_works = await test_agent_finds_real_bid_cards()
        else:
            agent_works = False
            print("\nSkipping agent test since API is not working")
        
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        
        if api_works and agent_works:
            print("✅ CONFIRMED: Both API and Agent are working with real bid cards!")
            print("✅ Ready for cleanup and documentation updates")
        else:
            print("❌ NOT READY: Issues found that need fixing first")
            if not api_works:
                print("  - API endpoint not working properly")
            if not agent_works:
                print("  - Agent not providing good responses")
        
        return api_works and agent_works
    
    success = asyncio.run(main())
    if success:
        print("\n🎉 SYSTEM IS FULLY OPERATIONAL!")
    else:
        print("\n⚠️  DO NOT PROCEED WITH CLEANUP YET")