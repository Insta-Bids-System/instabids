import os
from dotenv import load_dotenv
import base64
import json

load_dotenv()

# Get the keys
anon = os.getenv('SUPABASE_ANON_KEY', '')
service = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

# Check if they're different
print('Keys are different:', anon != service)
print('Anon key starts with:', anon[:50] if anon else 'Not set')
print('Service key starts with:', service[:50] if service else 'Not set')

# Decode the JWT payload to see the role
def decode_jwt_payload(token):
    try:
        # JWT format is header.payload.signature
        payload = token.split('.')[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return f"Error: {e}"

print('\nAnon key payload:', decode_jwt_payload(anon))
print('Service key payload:', decode_jwt_payload(service))

# Check if service role key has correct role
service_payload = decode_jwt_payload(service)
if isinstance(service_payload, dict):
    print(f"\nService role key has role: {service_payload.get('role')}")
    print(f"Expected: 'service_role', Got: '{service_payload.get('role')}'")