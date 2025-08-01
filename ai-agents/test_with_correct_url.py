import os
from supabase import create_client
from dotenv import load_dotenv

# Force load from .env file with override
load_dotenv(override=True)

# Use the correct URL and keys from .env
SUPABASE_URL = "https://xrhgrthdcaymxuqcgrmj.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print(f"Using URL: {SUPABASE_URL}")
print(f"Service key starts with: {SUPABASE_SERVICE_ROLE_KEY[:50]}...")

try:
    # Create client with correct URL
    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Test creating a campaign
    result = client.table('outreach_campaigns').insert({
        'name': 'Test Campaign - Correct URL',
        'status': 'draft',
        'bid_card_id': '123e4567-e89b-12d3-a456-426614174000'
    }).execute()
    
    print("\nSUCCESS! Campaign created:")
    print(f"Campaign ID: {result.data[0]['id']}")
    print(f"Campaign Name: {result.data[0]['name']}")
    
except Exception as e:
    print(f"\nFAILED: {e}")
    print(f"Error type: {type(e).__name__}")