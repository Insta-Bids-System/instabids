import os
from dotenv import load_dotenv
import pathlib

# Try different ways to load the API key
print("=== TESTING OPENAI API KEY LOADING ===")

# Method 1: Direct from current env
key1 = os.getenv("OPENAI_API_KEY")
print(f"1. From current env: {key1[:20] if key1 else 'NOT FOUND'}...")

# Method 2: Load from ../env
load_dotenv('../.env')
key2 = os.getenv("OPENAI_API_KEY")
print(f"2. After loading ../.env: {key2[:20] if key2 else 'NOT FOUND'}...")
print(f"   Full length: {len(key2) if key2 else 0} characters")

# Method 3: Direct file read
env_path = pathlib.Path(__file__).parent.parent / '.env'
print(f"3. Reading from: {env_path}")
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                actual_key = line.split('=', 1)[1].strip()
                print(f"   Found key: {actual_key[:20]}...")
                print(f"   Full length: {len(actual_key)} characters")
                
                # Test if this key works
                import openai
                try:
                    client = openai.OpenAI(api_key=actual_key)
                    response = client.models.list()
                    print("   ✅ KEY IS VALID - OpenAI API responded successfully!")
                except Exception as e:
                    print(f"   ❌ KEY ERROR: {e}")
                break