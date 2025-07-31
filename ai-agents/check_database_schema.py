#!/usr/bin/env python3
"""
Check database schema for profiles and agent_conversations tables
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(override=True)

def check_database():
    """Check database schema"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    print("Checking database schema...\n")
    
    # Check profiles table
    try:
        print("1. Checking profiles table:")
        result = supabase.table('profiles').select("*").limit(1).execute()
        if result.data:
            print("   Table exists with columns:", list(result.data[0].keys()))
            print("   Sample record ID field:", result.data[0].get('id') or result.data[0].get('user_id'))
        else:
            print("   Table exists but is empty")
            
        # Try to get column info
        print("\n2. Trying different ID fields:")
        for field in ['id', 'user_id', 'profile_id']:
            try:
                test = supabase.table('profiles').select(field).limit(1).execute()
                if test.data:
                    print(f"   Found field '{field}' with value: {test.data[0].get(field)}")
            except Exception as e:
                if "Could not find" in str(e):
                    print(f"   Field '{field}' does not exist")
                    
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Check agent_conversations table
    try:
        print("\n3. Checking agent_conversations table:")
        result = supabase.table('agent_conversations').select("*").limit(1).execute()
        if result.data:
            print("   Table exists with columns:", list(result.data[0].keys()))
        else:
            print("   Table exists but is empty")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Check if we can insert a test user
    try:
        print("\n4. Attempting to find or create test user:")
        import uuid
        
        # First try to find any existing user
        existing = supabase.table('profiles').select("*").limit(5).execute()
        if existing.data:
            print(f"   Found {len(existing.data)} existing users")
            for user in existing.data:
                print(f"   - ID: {user.get('id')}, Email: {user.get('email')}")
            
            # Use first user for testing
            test_user_id = existing.data[0].get('id')
            print(f"\n   Using existing user ID for testing: {test_user_id}")
            return test_user_id
        else:
            print("   No existing users found")
            
            # Try to create a new user
            test_id = str(uuid.uuid4())
            test_user = {
                'id': test_id,  # Try 'id' instead of 'user_id'
                'email': f'test_{test_id[:8]}@instabids.com',
                'full_name': 'Test User',
                'role': 'homeowner'
            }
            
            print(f"\n   Attempting to create user with ID: {test_id}")
            create_result = supabase.table('profiles').insert(test_user).execute()
            
            if create_result.data:
                print("   SUCCESS: Created test user")
                return test_id
            else:
                print("   Failed to create user")
                
    except Exception as e:
        print(f"   ERROR: {e}")
        
    return None


if __name__ == "__main__":
    user_id = check_database()
    if user_id:
        print(f"\n\nSUCCESS: Can use user ID '{user_id}' for testing")
    else:
        print("\n\nFAILED: Could not find or create a test user")