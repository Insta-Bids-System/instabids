"""
Simple direct Supabase connection test
"""
import os
from dotenv import load_dotenv

# Load environment variables from current directory
load_dotenv()

print("=== DIRECT SUPABASE CONNECTION TEST ===")
print(f"Current directory: {os.getcwd()}")

# Get environment variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

print(f"SUPABASE_URL: {url}")
print(f"SUPABASE_ANON_KEY: {key[:20]}..." if key else "None")

try:
    # Try direct connection
    from supabase import create_client
    supabase = create_client(url, key)
    
    print("Supabase client created successfully")
    
    # Try a simple query
    result = supabase.table('conversations').select("*").limit(1).execute()
    print(f"Query executed - found {len(result.data)} conversations")
    
    if result.data:
        session_id = result.data[0].get('session_id', 'No session_id')
        print(f"First conversation session_id: {session_id}")
    
    print("CONNECTION SUCCESSFUL!")
    
except Exception as e:
    print(f"CONNECTION FAILED: {e}")
    import traceback
    traceback.print_exc()