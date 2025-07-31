"""Create a test user in Supabase with proper profile setup"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get Supabase credentials from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_SERVICE_KEY: {'Set' if SUPABASE_SERVICE_KEY else 'Not set'}")
    sys.exit(1)

# Create Supabase client with service role key to bypass RLS
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def create_test_user():
    """Create a test user that bypasses email confirmation"""
    try:
        # Use service role to create user without email confirmation
        response = supabase.auth.admin.create_user({
            "email": "test.homeowner.working@instabids.com",
            "password": "testpass123",
            "email_confirm": True,  # Bypass email confirmation
            "user_metadata": {
                "full_name": "Test Homeowner Working"
            }
        })
        
        print(f"✅ User created successfully!")
        print(f"User ID: {response.user.id}")
        print(f"Email: {response.user.email}")
        
        # Create profile for the user
        profile_data = {
            "id": response.user.id,
            "role": "homeowner",
            "full_name": "Test Homeowner Working",
            "phone": "555-0100"
        }
        
        profile_response = supabase.table("profiles").insert(profile_data).execute()
        print(f"✅ Profile created successfully!")
        
        return response.user
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

if __name__ == "__main__":
    print("Creating test user in Supabase...")
    user = create_test_user()
    
    if user:
        print("\n✅ Test user created successfully!")
        print("\nYou can now login with:")
        print("Email: test.homeowner.working@instabids.com")
        print("Password: testpass123")