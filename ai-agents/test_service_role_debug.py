"""
Debug service role authentication
"""
import os
from dotenv import load_dotenv
from database_service import SupabaseService

# Load environment
load_dotenv(override=True)

print("=== Service Role Debug ===\n")

# Check environment variables
anon_key = os.getenv("SUPABASE_ANON_KEY")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"ANON_KEY exists: {bool(anon_key)}")
print(f"ANON_KEY prefix: {anon_key[:20] if anon_key else 'None'}...")
print(f"SERVICE_KEY exists: {bool(service_key)}")
print(f"SERVICE_KEY prefix: {service_key[:20] if service_key else 'None'}...")

# Test service role client
print("\n--- Testing Service Role Client ---")
try:
    service_client = SupabaseService(use_service_role=True)
    print(f"Service client initialized successfully")
    print(f"Using service role: {service_client.use_service_role}")
    
    # Try a simple query
    result = service_client.client.table('potential_contractors').select('id').limit(1).execute()
    print(f"Test query successful: {len(result.data)} rows")
    
    # Try creating a test campaign
    print("\n--- Testing Campaign Creation ---")
    import uuid
    from datetime import datetime
    
    campaign_data = {
        'id': str(uuid.uuid4()),
        'name': 'Test Service Role Campaign',
        'bid_card_id': str(uuid.uuid4()),
        'status': 'draft',
        'created_at': datetime.now().isoformat(),
        'campaign_config': {
            'test': True,
            'urgency': 'standard'
        }
    }
    
    result = service_client.client.table('outreach_campaigns').insert(campaign_data).execute()
    
    if result.data:
        print(f"SUCCESS! Campaign created: {result.data[0]['id']}")
        
        # Clean up
        service_client.client.table('outreach_campaigns').delete().eq('id', result.data[0]['id']).execute()
        print("Test campaign deleted")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()