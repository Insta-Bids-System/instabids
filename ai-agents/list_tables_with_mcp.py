#!/usr/bin/env python3
"""
Use Supabase MCP tool via SQL function to list all tables
"""
import os
import subprocess
import json
from dotenv import load_dotenv

# Load environment
parent_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(parent_dir, '.env'), override=True)

def create_listing_function():
    """Create the table listing function using MCP"""
    
    # Read the SQL file
    with open('create_table_listing_function.sql', 'r') as f:
        sql = f.read()
    
    # Use supabase CLI to run the migration
    project_id = "dukeqfbvzszyegnamvmd"
    
    print("Creating table listing function in Supabase...")
    print("\nPlease run this SQL in your Supabase Dashboard SQL Editor:")
    print("=" * 60)
    print(sql)
    print("=" * 60)
    
    print("\nOnce created, you can use this Python code to list tables:")
    print("""
from supabase import create_client
import os

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))

# Call the function
result = supabase.rpc('list_all_public_tables').execute()

# Display tables
for table in result.data:
    print(f"Table: {table['table_name']}")
    """)

if __name__ == "__main__":
    create_listing_function()