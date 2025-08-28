import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Check environment variables
print("Environment Variable Check:")
print("-" * 40)
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY')}")
print(f"SUPABASE_SERVICE_ROLE_KEY: {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}")

# Check if .env file exists
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"\n.env file exists: {os.path.exists(env_path)}")
print(f".env path: {env_path}")

# Read .env file directly
if os.path.exists(env_path):
    print("\nDirect .env file contents (first 5 lines):")
    with open(env_path) as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            if 'KEY' in line:
                # Hide the key value for security
                parts = line.split('=', 1)
                if len(parts) == 2:
                    print(f"{parts[0]}=<hidden>")
            else:
                print(line.strip())