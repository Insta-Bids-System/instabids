"""
Persistent Memory System for Contractor Interface Agent (CoIA)
Purpose: Save and load complete contractor conversation history from Supabase
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict
from supabase import create_client, Client
import os
from dotenv import load_dotenv

from .state import CoIAConversationState, ConversationMessage, ContractorProfile, coia_state_manager

# Load environment
load_dotenv(override=True)

logger = logging.getLogger(__name__)

class CoIAPersistentMemory:
    """Persistent memory system for contractor conversations"""
    
    def __init__(self):
        """Initialize with Supabase connection"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase not available - memory will not persist")
            self.supabase = None
        else:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            logger.info("CoIA Persistent Memory initialized with Supabase")
    
    async def save_conversation_state(self, state: CoIAConversationState) -> bool:
        """Save complete conversation state to database"""
        if not self.supabase:
            logger.warning("No database connection - state not saved")
            return False
        
        try:
            # Convert state to JSON-serializable format
            state_data = self._serialize_state(state)
            
            # Check if conversation already exists
            existing = self.supabase.table('agent_conversations').select('*').eq(
                'thread_id', state.session_id
            ).execute()
            
            conversation_data = {
                'user_id': state.contractor_id or '00000000-0000-0000-0000-000000000000',  # Use anonymous UUID
                'agent_type': 'coia',
                'thread_id': state.session_id,
                'state': state_data,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if existing.data:
                # Update existing conversation
                result = self.supabase.table('agent_conversations').update(
                    conversation_data
                ).eq('thread_id', state.session_id).execute()
                logger.info(f"Updated contractor conversation: {state.session_id}")
            else:
                # Create new conversation
                conversation_data['created_at'] = datetime.utcnow().isoformat()
                result = self.supabase.table('agent_conversations').insert(
                    conversation_data
                ).execute()
                logger.info(f"Saved new contractor conversation: {state.session_id}")
            
            return result.data is not None
            
        except Exception as e:
            logger.error(f"Error saving contractor conversation: {e}")
            return False
    
    async def load_conversation_state(self, session_id: str) -> Optional[CoIAConversationState]:
        """Load complete conversation state from database"""
        if not self.supabase:
            logger.warning("No database connection - cannot load state")
            return None
        
        try:
            result = self.supabase.table('agent_conversations').select('*').eq(
                'thread_id', session_id
            ).eq('agent_type', 'coia').execute()
            
            if result.data:
                conversation = result.data[0]
                state_data = conversation.get('state', {})
                
                # Deserialize state from JSON
                state = self._deserialize_state(state_data, session_id)
                logger.info(f"Loaded contractor conversation: {session_id}")
                return state
            else:
                logger.info(f"No saved conversation found for: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading contractor conversation: {e}")
            return None
    
    async def get_contractor_conversation_history(self, contractor_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a specific contractor"""
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.table('agent_conversations').select('*').eq(
                'user_id', contractor_id
            ).eq('agent_type', 'coia').order('created_at', desc=True).execute()
            
            conversations = []
            for conv in result.data:
                state_data = conv.get('state', {})
                conversations.append({
                    'session_id': conv['thread_id'],
                    'created_at': conv['created_at'],
                    'updated_at': conv['updated_at'],
                    'current_stage': state_data.get('current_stage', 'unknown'),
                    'completed': state_data.get('completed', False),
                    'message_count': len(state_data.get('messages', [])),
                    'business_name': state_data.get('research_data', {}).get('company_name', 'Unknown')
                })
            
            logger.info(f"Found {len(conversations)} conversations for contractor {contractor_id}")
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting contractor history: {e}")
            return []
    
    async def is_returning_contractor(self, business_name: str, phone: str, email: str) -> Optional[str]:
        """Check if contractor has previous conversations based on business info"""
        if not self.supabase:
            return None
        
        try:
            # First check the contractor_leads table for existing contractors
            contractors_result = self.supabase.table('contractor_leads').select('*').execute()
            
            for contractor in contractors_result.data:
                # Check for matches in business name, phone, or email
                matches = []
                if contractor.get('company_name', '').lower() == business_name.lower():
                    matches.append('name')
                if contractor.get('phone') == phone and phone:
                    matches.append('phone')
                if contractor.get('email') == email and email:
                    matches.append('email')
                
                # If we have at least 1 strong match (name + phone/email), consider it the same contractor
                if len(matches) >= 2 or ('name' in matches and ('phone' in matches or 'email' in matches)):
                    contractor_id = contractor['id']
                    logger.info(f"Found returning contractor in contractor_leads: {contractor_id} (matches: {matches})")
                    return contractor_id
            
            # Also check conversation history as fallback
            conversations_result = self.supabase.table('agent_conversations').select('*').eq(
                'agent_type', 'coia'
            ).execute()
            
            for conv in conversations_result.data:
                state_data = conv.get('state', {})
                research_data = state_data.get('research_data', {})
                
                # Check for matches in business name, phone, or email
                matches = []
                if research_data.get('company_name', '').lower() == business_name.lower():
                    matches.append('name')
                if research_data.get('phone') == phone and phone:
                    matches.append('phone')
                if research_data.get('email') == email and email:
                    matches.append('email')
                
                # If we have at least 2 matches, consider it the same contractor
                if len(matches) >= 2:
                    # Look up contractor_id from the conversation state
                    contractor_id = state_data.get('contractor_id')
                    if contractor_id and contractor_id != '00000000-0000-0000-0000-000000000000':
                        logger.info(f"Found returning contractor in conversations: {contractor_id} (matches: {matches})")
                        return contractor_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking returning contractor: {e}")
            return None
    
    def _serialize_state(self, state: CoIAConversationState) -> Dict[str, Any]:
        """Convert CoIAConversationState to JSON-serializable dict"""
        
        # Convert messages to dict format
        messages = []
        for msg in state.messages:
            messages.append({
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'stage': msg.stage,
                'profile_updates': msg.profile_updates
            })
        
        # Convert research_data if it exists
        research_data = None
        if hasattr(state, 'research_data') and state.research_data:
            research_data = {
                'company_name': state.research_data.company_name,
                'website': state.research_data.website,
                'email': state.research_data.email,
                'phone': state.research_data.phone,
                'services': state.research_data.services,
                'service_areas': state.research_data.service_areas,
                'address': state.research_data.address,
                'years_experience': state.research_data.years_experience,
                'hours': state.research_data.hours,
                'social_media': state.research_data.social_media,
                'google_listing_url': state.research_data.google_listing_url,
                'place_id': state.research_data.place_id
            }
        
        return {
            'session_id': state.session_id,
            'contractor_lead_id': state.contractor_lead_id,
            'contractor_id': state.contractor_id,
            'current_stage': state.current_stage,
            'messages': messages,
            'last_updated': state.last_updated.isoformat(),
            'profile': asdict(state.profile),
            'business_research': state.business_research,
            'research_completed': state.research_completed,
            'research_confirmed': state.research_confirmed,
            'research_data': research_data,
            'original_project_id': state.original_project_id,
            'source_channel': state.source_channel,
            'matching_projects_count': state.matching_projects_count,
            'completed': state.completed,
            'completed_at': state.completed_at.isoformat() if state.completed_at else None,
            'conversion_successful': state.conversion_successful
        }
    
    def _deserialize_state(self, state_data: Dict[str, Any], session_id: str) -> CoIAConversationState:
        """Convert JSON dict back to CoIAConversationState"""
        from .intelligent_research_agent import RealBusinessData
        
        # Create new state object
        state = CoIAConversationState(
            session_id=session_id,
            contractor_lead_id=state_data.get('contractor_lead_id'),
            contractor_id=state_data.get('contractor_id'),
            current_stage=state_data.get('current_stage', 'welcome'),
            original_project_id=state_data.get('original_project_id'),
            source_channel=state_data.get('source_channel'),
            matching_projects_count=state_data.get('matching_projects_count', 0),
            completed=state_data.get('completed', False),
            conversion_successful=state_data.get('conversion_successful', False)
        )
        
        # Set timestamps
        if state_data.get('last_updated'):
            state.last_updated = datetime.fromisoformat(state_data['last_updated'])
        if state_data.get('completed_at'):
            state.completed_at = datetime.fromisoformat(state_data['completed_at'])
        
        # Restore messages
        for msg_data in state_data.get('messages', []):
            message = ConversationMessage(
                role=msg_data['role'],
                content=msg_data['content'],
                timestamp=datetime.fromisoformat(msg_data['timestamp']),
                stage=msg_data.get('stage'),
                profile_updates=msg_data.get('profile_updates')
            )
            state.messages.append(message)
        
        # Restore profile
        profile_data = state_data.get('profile', {})
        state.profile = ContractorProfile(
            primary_trade=profile_data.get('primary_trade'),
            years_in_business=profile_data.get('years_in_business'),
            business_name=profile_data.get('business_name'),
            service_areas=profile_data.get('service_areas', []),
            service_radius_miles=profile_data.get('service_radius_miles'),
            specializations=profile_data.get('specializations', []),
            differentiators=profile_data.get('differentiators'),
            license_info=profile_data.get('license_info'),
            insurance_verified=profile_data.get('insurance_verified', False),
            team_size=profile_data.get('team_size'),
            minimum_project_size=profile_data.get('minimum_project_size'),
            preferred_project_types=profile_data.get('preferred_project_types', []),
            availability=profile_data.get('availability'),
            response_time=profile_data.get('response_time'),
            warranty_offered=profile_data.get('warranty_offered', False),
            certifications=profile_data.get('certifications', [])
        )
        
        # Restore research data
        research_data_dict = state_data.get('research_data')
        if research_data_dict:
            state.research_data = RealBusinessData(
                company_name=research_data_dict.get('company_name', ''),
                website=research_data_dict.get('website', ''),
                email=research_data_dict.get('email', ''),
                phone=research_data_dict.get('phone', ''),
                services=research_data_dict.get('services', []),
                service_areas=research_data_dict.get('service_areas', []),
                address=research_data_dict.get('address', ''),
                years_experience=research_data_dict.get('years_experience', 0),
                hours=research_data_dict.get('hours', {}),
                social_media=research_data_dict.get('social_media', {}),
                google_listing_url=research_data_dict.get('google_listing_url', ''),
                place_id=research_data_dict.get('place_id', '')
            )
        
        # Restore other research fields
        state.business_research = state_data.get('business_research')
        state.research_completed = state_data.get('research_completed', False)
        state.research_confirmed = state_data.get('research_confirmed', False)
        
        return state

# Enhanced state manager with persistent memory
class PersistentCoIAStateManager:
    """Enhanced CoIA state manager with database persistence"""
    
    def __init__(self):
        self.memory = CoIAPersistentMemory()
        self._states: Dict[str, CoIAConversationState] = {}
    
    async def create_session(self, session_id: str, contractor_lead_id: Optional[str] = None,
                            original_project_id: Optional[str] = None) -> CoIAConversationState:
        """Create a new conversation session"""
        
        # First try to load existing conversation
        existing_state = await self.memory.load_conversation_state(session_id)
        if existing_state:
            self._states[session_id] = existing_state
            logger.info(f"Restored existing conversation: {session_id}")
            return existing_state
        
        # Create new session
        state = CoIAConversationState(
            session_id=session_id,
            contractor_lead_id=contractor_lead_id,
            original_project_id=original_project_id
        )
        self._states[session_id] = state
        
        # Save to database
        await self.memory.save_conversation_state(state)
        
        return state
    
    async def get_session(self, session_id: str) -> Optional[CoIAConversationState]:
        """Get existing conversation session"""
        
        # Check memory first
        if session_id in self._states:
            return self._states[session_id]
        
        # Try to load from database
        state = await self.memory.load_conversation_state(session_id)
        if state:
            self._states[session_id] = state
            return state
        
        return None
    
    async def update_session(self, session_id: str, state: CoIAConversationState):
        """Update conversation session"""
        self._states[session_id] = state
        
        # Save to database
        await self.memory.save_conversation_state(state)
    
    async def check_returning_contractor(self, business_name: str, phone: str = None, email: str = None) -> Optional[str]:
        """Check if this is a returning contractor"""
        return await self.memory.is_returning_contractor(business_name or '', phone or '', email or '')
    
    async def get_contractor_history(self, contractor_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a contractor"""
        return await self.memory.get_contractor_conversation_history(contractor_id)
    
    def delete_session(self, session_id: str):
        """Delete conversation session from memory (keeps database record)"""
        if session_id in self._states:
            del self._states[session_id]
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs in memory"""
        return list(self._states.keys())

# Create enhanced global state manager
persistent_coia_state_manager = PersistentCoIAStateManager()