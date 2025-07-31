"""
Simplified Supabase database connection for development
Uses a conversations table without auth dependencies
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables with override to fix system env conflicts
load_dotenv(override=True)

logger = logging.getLogger(__name__)

class SupabaseDB:
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.client: Client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
    
    async def save_conversation_state(
        self, 
        user_id: str, 
        thread_id: str, 
        agent_type: str, 
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save or update conversation state in the database
        """
        try:
            # For development, we'll use agent_conversations without user validation
            # Check if conversation already exists
            existing = self.client.table('agent_conversations').select('*').eq(
                'thread_id', thread_id
            ).execute()
            
            # Debug logging
            if isinstance(state, dict) and 'collected_info' in state:
                collected_info = state.get('collected_info', {})
                print(f"[DB DEBUG] Saving state with collected_info:")
                print(f"  budget_min: {collected_info.get('budget_min')}")
                print(f"  budget_max: {collected_info.get('budget_max')}")
                print(f"  project_type: {collected_info.get('project_type')}")
            
            conversation_data = {
                'user_id': user_id,  # This will be a simple string for now
                'agent_type': agent_type,
                'thread_id': thread_id,
                'state': state,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if existing.data:
                # Update existing conversation
                result = self.client.table('agent_conversations').update(
                    conversation_data
                ).eq('thread_id', thread_id).execute()
                logger.info(f"Updated conversation state for thread {thread_id}")
            else:
                # Create new conversation
                conversation_data['created_at'] = datetime.utcnow().isoformat()
                result = self.client.table('agent_conversations').insert(
                    conversation_data
                ).execute()
                logger.info(f"Created new conversation state for thread {thread_id}")
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error saving conversation state: {str(e)}")
            # Don't raise - just log and continue
            return None
    
    async def load_conversation_state(
        self, 
        thread_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load conversation state from the database
        """
        try:
            result = self.client.table('agent_conversations').select('*').eq(
                'thread_id', thread_id
            ).execute()
            
            if result.data:
                logger.info(f"Loaded conversation state for thread {thread_id}")
                
                # Debug logging
                conversation = result.data[0]
                state = conversation.get('state', {})
                if isinstance(state, dict) and 'collected_info' in state:
                    collected_info = state.get('collected_info', {})
                    print(f"[DB DEBUG] Loaded state with collected_info:")
                    print(f"  budget_min: {collected_info.get('budget_min')}")
                    print(f"  budget_max: {collected_info.get('budget_max')}")
                    print(f"  project_type: {collected_info.get('project_type')}")
                
                return result.data[0]
            else:
                logger.info(f"No conversation state found for thread {thread_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading conversation state: {str(e)}")
            return None
    
    async def get_or_create_test_user(self) -> str:
        """
        For development, get or create a test user in profiles table
        """
        try:
            # Check if test user exists
            result = self.client.table('profiles').select('id').eq(
                'email', 'test@instabids.dev'
            ).execute()
            
            if result.data:
                # Return existing user ID
                return result.data[0]['id']
            else:
                # Create new test user
                new_user = self.client.table('profiles').insert({
                    'email': 'test@instabids.dev',
                    'full_name': 'Test User',
                    'role': 'homeowner'
                }).execute()
                
                if new_user.data:
                    logger.info(f"Created test user: {new_user.data[0]['id']}")
                    return new_user.data[0]['id']
                else:
                    # If we can't create, use a fixed UUID
                    return "00000000-0000-0000-0000-000000000001"
                    
        except Exception as e:
            logger.error(f"Error with test user: {e}")
            # Return a valid UUID format as fallback
            return "00000000-0000-0000-0000-000000000001"
    
    async def transfer_anonymous_conversation(self, session_id: str, new_user_id: str) -> bool:
        """
        Transfer anonymous conversation to newly signed up user
        """
        try:
            # Update all conversations with this session_id from anonymous to real user
            result = self.client.table('agent_conversations').update({
                'user_id': new_user_id,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('thread_id', session_id).eq('user_id', '00000000-0000-0000-0000-000000000000').execute()
            
            if result.data:
                logger.info(f"Transferred {len(result.data)} conversations from anonymous to user {new_user_id}")
                return True
            else:
                logger.info(f"No anonymous conversations found for session {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error transferring conversation: {e}")
            return False

# Create a singleton instance
db = SupabaseDB()
