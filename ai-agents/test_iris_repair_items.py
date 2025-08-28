#!/usr/bin/env python3
"""Test IRIS repair item management functionality"""

from api.iris_agent_actions import IRISActionSystem
import json

# Initialize IRIS actions
iris_actions = IRISActionSystem()

# Your potential bid card ID
potential_bid_card_id = '0e9a839a-984c-4391-ace6-0f62342e4524'

print('Testing IRIS Repair Item Management')
print('=' * 50)

# 1. Add a repair item
print('\n1. Adding repair item...')
result = iris_actions.add_repair_item(
    potential_bid_card_id=potential_bid_card_id,
    item_description='Replace damaged roof shingles',
    severity='high',
    category='roofing',
    estimated_cost=2500
)
print(f'Result: {json.dumps(result, indent=2)}')

if result.get('success'):
    repair_item_id = result['item']['id']
    print(f'\nCreated repair item ID: {repair_item_id}')
    
    # 2. List repair items
    print('\n2. Listing all repair items...')
    list_result = iris_actions.list_repair_items(potential_bid_card_id)
    print(f'Result: {json.dumps(list_result, indent=2)}')
    
    # 3. Update the repair item
    print('\n3. Updating repair item severity to urgent...')
    update_result = iris_actions.update_repair_item(
        potential_bid_card_id=potential_bid_card_id,
        repair_item_id=repair_item_id,
        updates={'severity': 'urgent', 'estimated_cost': 3000}
    )
    print(f'Result: {json.dumps(update_result, indent=2)}')
    
    # 4. Add another repair item
    print('\n4. Adding second repair item...')
    result2 = iris_actions.add_repair_item(
        potential_bid_card_id=potential_bid_card_id,
        item_description='Clean and seal gutters',
        severity='medium',
        category='roofing',
        estimated_cost=500
    )
    print(f'Result: {json.dumps(result2, indent=2)}')
    
    # 5. List all repair items again
    print('\n5. Listing all repair items after additions...')
    final_list = iris_actions.list_repair_items(potential_bid_card_id)
    print(f'Total items: {final_list.get("total_items", 0)}')
    print(f'Total cost: ${final_list.get("total_estimated_cost", 0):,.2f}')
    
    for idx, item in enumerate(final_list.get('repair_items', []), 1):
        print(f'\n  Item {idx}: {item["description"]}')
        print(f'    - Severity: {item["severity"]}')
        print(f'    - Category: {item["category"]}')
        print(f'    - Cost: ${item["estimated_cost"]:,.2f}')
else:
    print('Failed to add repair item!')