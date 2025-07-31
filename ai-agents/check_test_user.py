#!/usr/bin/env python3
"""
Check if test user exists in database
"""
from database_simple import SupabaseDB

db = SupabaseDB()

# Check if test user exists
email = 'test.homeowner@instabids.com'
user_id = 'e6e47a24-95ad-4af3-9ec5-f17999917bc3'

print("=== CHECKING TEST USER ===")

# Check auth.users table (if accessible)
try:
    auth_users = db.client.table('auth.users').select('*').eq('email', email).execute()
    print(f"Auth users: {len(auth_users.data) if auth_users.data else 0}")
    if auth_users.data:
        for user in auth_users.data:
            print(f"  Auth ID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Created: {user['created_at']}")
except Exception as e:
    print(f"Cannot access auth.users: {e}")

# Check profiles table
try:
    profiles = db.client.table('profiles').select('*').eq('id', user_id).execute()
    print(f"Profiles: {len(profiles.data) if profiles.data else 0}")
    if profiles.data:
        for profile in profiles.data:
            print(f"  Profile ID: {profile['id']}")
            print(f"  Email: {profile.get('email', 'N/A')}")
            print(f"  Name: {profile.get('full_name', 'N/A')}")
            print(f"  Role: {profile.get('role', 'N/A')}")
except Exception as e:
    print(f"Cannot access profiles: {e}")

# Check homeowners table
try:
    homeowners = db.client.table('homeowners').select('*').eq('id', user_id).execute()
    print(f"Homeowners: {len(homeowners.data) if homeowners.data else 0}")
    if homeowners.data:
        for homeowner in homeowners.data:
            print(f"  Homeowner ID: {homeowner['id']}")
            print(f"  Email: {homeowner.get('email', 'N/A')}")
            print(f"  Status: {homeowner.get('status', 'N/A')}")
except Exception as e:
    print(f"Cannot access homeowners: {e}")

# Try to create the user if missing
print("\n=== CREATING TEST USER ===")
try:
    # Check if user exists first
    existing_homeowner = db.client.table('homeowners').select('*').eq('id', user_id).execute()
    
    if not existing_homeowner.data:
        print("Creating homeowner...")
        homeowner_data = {
            'id': user_id,
            'email': email,
            'full_name': 'Test Homeowner',
            'phone': '555-0123',
            'status': 'active',
            'preferences': {},
            'created_at': '2025-07-31T00:00:00Z'
        }
        
        result = db.client.table('homeowners').insert(homeowner_data).execute()
        if result.data:
            print(f"  Created homeowner: {result.data[0]['id']}")
        else:
            print("  Failed to create homeowner")
    else:
        print("Homeowner already exists")
        
    # Also create profile
    existing_profile = db.client.table('profiles').select('*').eq('id', user_id).execute()
    
    if not existing_profile.data:
        print("Creating profile...")
        profile_data = {
            'id': user_id,
            'email': email,
            'full_name': 'Test Homeowner',
            'role': 'homeowner',
            'created_at': '2025-07-31T00:00:00Z'
        }
        
        result = db.client.table('profiles').insert(profile_data).execute()
        if result.data:
            print(f"  Created profile: {result.data[0]['id']}")
        else:
            print("  Failed to create profile")
    else:
        print("Profile already exists")
        
except Exception as e:
    print(f"Error creating user: {e}")

print(f"\n=== FINAL STATUS ===")
print(f"Email: {email}")
print(f"Password: testpass123")
print(f"User ID: {user_id}")
print("Note: User may need to be created in Supabase Auth separately")