#!/usr/bin/env python3
"""
Check for duplicate contractors in the database
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database_simple import SupabaseDB

db = SupabaseDB()

print("CHECKING FOR DUPLICATE CONTRACTORS")
print("=" * 80)

# 1. Check for exact company name duplicates
print("\n1. Checking for exact company name duplicates...")

# Get all contractors
all_contractors = db.client.table('potential_contractors')\
    .select("id,company_name,website,phone,city,state")\
    .order('company_name')\
    .execute()

if all_contractors.data:
    from collections import defaultdict
    
    # Group by company name
    name_groups = defaultdict(list)
    for contractor in all_contractors.data:
        name = contractor['company_name'].lower().strip()
        name_groups[name].append(contractor)
    
    # Find duplicates
    duplicates_found = False
    for name, contractors in name_groups.items():
        if len(contractors) > 1:
            duplicates_found = True
            print(f"\nDUPLICATE: '{contractors[0]['company_name']}' appears {len(contractors)} times:")
            for c in contractors:
                print(f"  - ID: {c['id'][:8]}... | {c.get('city', '')}, {c.get('state', '')} | {c.get('website', 'No website')}")
    
    if not duplicates_found:
        print("No exact name duplicates found")

# 2. Check for phone number duplicates
print("\n\n2. Checking for phone number duplicates...")
phone_groups = defaultdict(list)
for contractor in all_contractors.data:
    if contractor.get('phone'):
        phone = contractor['phone'].strip()
        phone_groups[phone].append(contractor)

duplicates_found = False
for phone, contractors in phone_groups.items():
    if len(contractors) > 1:
        duplicates_found = True
        print(f"\nDUPLICATE PHONE: {phone} used by {len(contractors)} contractors:")
        for c in contractors:
            print(f"  - {c['company_name']} (ID: {c['id'][:8]}...)")

if not duplicates_found:
    print("No phone number duplicates found")

# 3. Check for website duplicates
print("\n\n3. Checking for website duplicates...")
website_groups = defaultdict(list)
for contractor in all_contractors.data:
    if contractor.get('website'):
        # Normalize website
        website = contractor['website'].lower().strip()
        website = website.replace('https://', '').replace('http://', '').replace('www.', '')
        website = website.rstrip('/')
        website_groups[website].append(contractor)

duplicates_found = False
for website, contractors in website_groups.items():
    if len(contractors) > 1:
        duplicates_found = True
        print(f"\nDUPLICATE WEBSITE: {contractors[0]['website']} used by {len(contractors)} contractors:")
        for c in contractors:
            print(f"  - {c['company_name']} (ID: {c['id'][:8]}...)")

if not duplicates_found:
    print("No website duplicates found")

# 4. Summary
print("\n\n" + "="*80)
print("DUPLICATE PREVENTION RECOMMENDATIONS")
print("="*80)
print("\n1. Add UNIQUE constraints in database:")
print("   - phone (when not null)")
print("   - website (when not null, normalized)")
print("   - (company_name, city, state) combination")
print("\n2. Before inserting new contractors:")
print("   - Check if phone exists")
print("   - Check if website exists (normalized)")
print("   - Check if company_name + location exists")
print("\n3. During discovery/enrichment:")
print("   - Skip contractors that already exist")
print("   - Update existing records instead of creating new")