import asyncio
from agents.bsa.bsa_deepagents import search_bid_cards

async def test_search_directly():
    print('Testing search_bid_cards function directly...')
    
    # Test with Mike's Plumbing context - search ZIP 33442 which has bid cards
    print('Testing search for Plumbing projects in 33442...')
    result = await search_bid_cards(
        contractor_zip='33442',
        project_type='Plumbing',
        radius_miles=25
    )
    print(f'Plumbing Search Result: {result.get("total_found", 0)} found')
    
    # Test without project type filter to see all projects in area
    print('\nTesting search for ANY projects in 33442...')
    result2 = await search_bid_cards(
        contractor_zip='33442',
        radius_miles=25
    )
    
    print(f'All Projects Search Result: {result2.get("total_found", 0)} found')
    
    # Show results from the general search 
    print(f'\n--- GENERAL SEARCH (ALL PROJECTS) ---')
    print(f'Success: {result2.get("success")}')
    print(f'Total Found: {result2.get("total_found")}')
    print(f'Search Criteria: {result2.get("search_criteria")}')
    
    if result2.get('bid_cards'):
        print(f'\nFound {len(result2["bid_cards"])} bid cards in 33442 area:')
        for i, card in enumerate(result2['bid_cards'][:5], 1):
            location = card.get('location', {})
            zip_code = location.get('zip_code', 'Unknown') if isinstance(location, dict) else 'Unknown'
            city = location.get('city', 'Unknown') if isinstance(location, dict) else 'Unknown'
            budget = card.get('budget_range', {})
            min_budget = budget.get('min', 0) if isinstance(budget, dict) else 0
            max_budget = budget.get('max', 0) if isinstance(budget, dict) else 0
            
            print(f'  {i}. {card.get("project_type", "Unknown")} in {city}, {zip_code}')
            print(f'     Budget: ${min_budget}-${max_budget}')
            print(f'     Status: {card.get("status", "Unknown")}')
    else:
        print('\nNo bid cards found')
        
    # Test category matching logic
    print(f'\n--- CATEGORY MATCHING ANALYSIS ---')
    landscaping_projects = []
    plumbing_related = []
    
    if result2.get('bid_cards'):
        for card in result2['bid_cards']:
            project_type = card.get('project_type', '').lower()
            description = card.get('description', '').lower()
            
            if any(keyword in project_type for keyword in ['landscap', 'turf', 'lawn']):
                landscaping_projects.append(card.get('project_type', 'Unknown'))
            
            # Check for any plumbing-related keywords
            plumbing_keywords = ['plumb', 'drain', 'water', 'pipe', 'sewer', 'faucet', 'toilet', 'leak']
            if any(keyword in project_type + ' ' + description for keyword in plumbing_keywords):
                plumbing_related.append(card.get('project_type', 'Unknown'))
    
    print(f'Landscaping Projects Found: {len(landscaping_projects)} - {landscaping_projects[:3]}')
    print(f'Plumbing-Related Found: {len(plumbing_related)} - {plumbing_related[:3]}')
    
    print(f'\nAPI Powered: {result2.get("api_powered", False)}')
    print(f'Fallback Used: {result2.get("fallback_used", False)}')

asyncio.run(test_search_directly())