"""
Supabase database connection and operations for Instabids
"""

import logging
import os
from datetime import datetime
from typing import Any, Optional

from dotenv import load_dotenv
from supabase import Client, create_client


# Load environment variables
load_dotenv()

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
        state: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Save or update conversation state in the database

        Args:
            user_id: User's profile ID
            thread_id: LangGraph thread ID
            agent_type: Type of agent (CIA, CoIA, etc.)
            state: Conversation state dictionary

        Returns:
            Saved conversation record
        """
        try:
            # Check if conversation already exists
            existing = self.client.table("ai_conversations").select("*").eq(
                "thread_id", thread_id
            ).execute()

            conversation_data = {
                "user_id": user_id,
                "agent_type": agent_type,
                "thread_id": thread_id,
                "state": state,
                "updated_at": datetime.utcnow().isoformat()
            }

            if existing.data:
                # Update existing conversation
                result = self.client.table("ai_conversations").update(
                    conversation_data
                ).eq("thread_id", thread_id).execute()
                logger.info(f"Updated conversation state for thread {thread_id}")
            else:
                # Create new conversation
                conversation_data["created_at"] = datetime.utcnow().isoformat()
                result = self.client.table("ai_conversations").insert(
                    conversation_data
                ).execute()
                logger.info(f"Created new conversation state for thread {thread_id}")

            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error saving conversation state: {e!s}")
            raise

    async def load_conversation_state(
        self,
        thread_id: str
    ) -> Optional[dict[str, Any]]:
        """
        Load conversation state from the database

        Args:
            thread_id: LangGraph thread ID

        Returns:
            Conversation state or None if not found
        """
        try:
            result = self.client.table("ai_conversations").select("*").eq(
                "thread_id", thread_id
            ).execute()

            if result.data:
                logger.info(f"Loaded conversation state for thread {thread_id}")
                return result.data[0]
            else:
                logger.info(f"No conversation state found for thread {thread_id}")
                return None

        except Exception as e:
            logger.error(f"Error loading conversation state: {e!s}")
            raise

    async def get_or_create_test_user(self) -> str:
        """
        Get or create a test user for development

        Returns:
            User ID
        """
        test_email = "test@instabids.com"

        try:
            # Check if test user exists
            result = self.client.table("profiles").select("*").eq(
                "email", test_email
            ).execute()

            if result.data:
                logger.info(f"Found existing test user: {result.data[0]['id']}")
                return result.data[0]["id"]

            # Create test user directly in profiles table
            # Generate a proper UUID
            import uuid
            test_user_id = str(uuid.uuid4())

            profile_data = {
                "id": test_user_id,
                "email": test_email,
                "full_name": "Test User",
                "role": "homeowner",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # Try to insert the test user
            result = self.client.table("profiles").insert(profile_data).execute()

            if result.data:
                logger.info(f"Created test user with ID: {test_user_id}")
                return test_user_id
            else:
                # If insert fails (maybe ID exists), try to get by ID
                result = self.client.table("profiles").select("*").eq(
                    "id", test_user_id
                ).execute()
                if result.data:
                    return test_user_id

        except Exception as e:
            logger.error(f"Error with test user: {e!s}")
            # Use a fallback test user ID (proper UUID)
            import uuid
            fallback_id = str(uuid.uuid4())
            logger.warning(f"Using fallback test user ID: {fallback_id}")
            return fallback_id

# Create a singleton instance
db = SupabaseDB()
