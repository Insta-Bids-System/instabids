import os
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

# Test with anon key
print("Testing with ANON key:")
try:
    anon_client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )
    # Try to insert into outreach_campaigns
    result = anon_client.table('outreach_campaigns').insert({
        'name': 'Test Campaign Anon',
        'status': 'draft'
    }).execute()
    print("SUCCESS with anon key!")
except Exception as e:
    print(f"FAILED with anon key: {e}")

print("\nTesting with SERVICE ROLE key:")
try:
    service_client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    )
    # Try to insert into outreach_campaigns
    result = service_client.table('outreach_campaigns').insert({
        'name': 'Test Campaign Service',
        'status': 'draft'
    }).execute()
    print("SUCCESS with service role key!")
    print(f"Created campaign: {result.data}")
except Exception as e:
    print(f"FAILED with service role key: {e}")

# Also test just listing tables
print("\nTesting table listing with service role:")
try:
    # Try to select from outreach_campaigns
    result = service_client.table('outreach_campaigns').select('*').limit(1).execute()
    print(f"Table query successful! Found {len(result.data)} records")
except Exception as e:
    print(f"Table query failed: {e}")