#!/usr/bin/env python3
"""
Create bid_cards table in Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def create_bid_cards_table():
    """Create the bid_cards table in Supabase"""
    
    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_KEY/ANON_KEY")
        return False
    
    try:
        # Create Supabase client
        supabase = create_client(url, key)
        
        # Read SQL file
        with open('create_bid_cards_table.sql', 'r') as f:
            sql = f.read()
        
        # Execute SQL
        print("Creating bid_cards table...")
        
        # Note: Supabase Python client doesn't have direct SQL execution
        # We'll use the REST API approach
        import requests
        
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        
        # Execute via REST API
        response = requests.post(
            f"{url}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={'query': sql}
        )
        
        if response.status_code == 200:
            print("✅ bid_cards table created successfully!")
            return True
        else:
            # If exec_sql doesn't exist, let's check if table already exists
            response = requests.get(
                f"{url}/rest/v1/bid_cards?limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ bid_cards table already exists!")
                return True
            else:
                print(f"❌ Failed to create table: {response.status_code}")
                print(f"Response: {response.text}")
                print("\nPlease create the table manually using Supabase SQL Editor:")
                print("1. Go to your Supabase dashboard")
                print("2. Navigate to SQL Editor")
                print("3. Copy and paste the contents of create_bid_cards_table.sql")
                print("4. Click 'Run'")
                return False
                
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = create_bid_cards_table()
    exit(0 if success else 1)