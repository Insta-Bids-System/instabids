import os
import sys

# Check what's in the actual environment
print("Environment variables related to Supabase:")
for key, value in os.environ.items():
    if 'SUPABASE' in key.upper():
        print(f"{key} = {value[:50]}...")

# Check system environment vs dotenv
print("\n\nChecking dotenv loading:")
from dotenv import load_dotenv

# First show what's in environment before loading
url_before = os.getenv('SUPABASE_URL')
print(f"SUPABASE_URL before dotenv: {url_before}")

# Load with override
load_dotenv(override=True)
url_after = os.getenv('SUPABASE_URL')
print(f"SUPABASE_URL after dotenv: {url_after}")

# Show where dotenv is loading from
from pathlib import Path
env_path = Path('.env')
print(f"\n.env file exists: {env_path.exists()}")
print(f".env absolute path: {env_path.absolute()}")

# Try parent directory
parent_env = Path('../.env')
print(f"\nParent .env exists: {parent_env.exists()}")
print(f"Parent .env absolute path: {parent_env.absolute()}")