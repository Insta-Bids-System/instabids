"""
CoIA (Contractor Interface Agent) Core Implementation
Purpose: Claude Opus 4 integration for contractor onboarding conversations
"""

import json
import asyncio
import logging
import os
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from supabase import create_client, Client
from dotenv import load_dotenv

from .state import CoIAConversationState, coia_state_manager, ContractorProfile
from .prompts import (
    COIA_SYSTEM_PROMPT, 
    STAGE_PROMPTS, 
    TRADE_SPECIFIC_RESPONSES,
    RESPONSE_TEMPLATES,
    get_trade_context
)

# Load environment
load_dotenv(override=True)

logger = logging.getLogger(__name__)

class CoIAAgent:
    """CoIA - Contractor Interface Agent powered by Claude Opus 4"""
    
    def __init__(self, api_key: str):
        """Initialize CoIA with Claude Opus 4 and database connection"""
        self.llm = ChatAnthropic(
            model="claude-3-opus-20240229",  # Claude Opus 4
            anthropic_api_key=api_key,
            temperature=0.7,
            max_tokens=1000
        )
        self.output_parser = StrOutputParser()
        self.chain = self.llm | self.output_parser
        
        # Initialize Supabase client for contractors table
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not found - contractor profiles will not be saved")
            self.supabase = None
        else:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            logger.info("CoIA Supabase client initialized")
        
    async def process_message(self, session_id: str, user_message: str, 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user message and return CoIA response with profile updates"""
        
        # Get or create conversation state
        state = coia_state_manager.get_session(session_id)
        if not state:
            state = coia_state_manager.create_session(session_id)
            
        # Add user message to conversation
        state.add_message('user', user_message, state.current_stage)
        
        try:
            # Generate response using Claude Opus 4
            response_data = await self._generate_response(state, user_message, context)
            
            # Extract profile updates from response
            profile_updates = self._extract_profile_updates(
                user_message, 
                response_data.get('content', ''),
                state.current_stage
            )
            
            # Update profile if we have new data
            if profile_updates:
                state.update_profile(profile_updates)
            
            # Determine next stage
            next_stage = self._determine_next_stage(state, response_data.get('content', ''))
            
            # Add assistant message to conversation
            state.add_message(
                'assistant', 
                response_data.get('content', ''),
                next_stage,
                profile_updates
            )
            
            # Update state manager
            coia_state_manager.update_session(session_id, state)
            
            # Check for completion
            contractor_id = None
            if next_stage == 'completed' and state.profile.calculate_completeness() >= 0.8:
                contractor_id = await self._create_contractor_profile(state)
                if contractor_id:
                    state.mark_completed(contractor_id)
                    coia_state_manager.update_session(session_id, state)
            
            return {
                'response': response_data.get('content', ''),
                'stage': next_stage,
                'profile_progress': {
                    'completeness': state.profile.calculate_completeness(),
                    'stage': next_stage,
                    'collectedData': state.profile.to_dict(),
                    'matchingProjects': await self._count_matching_projects(state.profile)
                },
                'contractor_id': contractor_id,
                'session_data': state.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error processing CoIA message: {e}")
            
            # Fallback response
            fallback_response = "I apologize, but I'm having trouble processing that right now. Could you please try rephrasing your response?"
            
            state.add_message('assistant', fallback_response, state.current_stage)
            coia_state_manager.update_session(session_id, state)
            
            return {
                'response': fallback_response,
                'stage': state.current_stage,
                'profile_progress': {
                    'completeness': state.profile.calculate_completeness(),
                    'stage': state.current_stage,
                    'collectedData': state.profile.to_dict(),
                    'matchingProjects': 0
                },
                'contractor_id': None,
                'session_data': state.to_dict()
            }
    
    async def _generate_response(self, state: CoIAConversationState, 
                               user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response using Claude Opus 4"""
        
        # Build conversation history for context
        conversation_history = ""
        for msg in state.messages[-10:]:  # Last 10 messages for context
            role = "Human" if msg.role == 'user' else "Assistant"
            conversation_history += f"{role}: {msg.content}\n"
        
        # Get stage-specific context
        stage_prompt = STAGE_PROMPTS.get(state.current_stage, "")
        
        # Get trade-specific context if we have it
        trade_context = ""
        if state.profile.primary_trade:
            trade_info = get_trade_context(state.profile.primary_trade)
            trade_context = f"Trade Context: {json.dumps(trade_info, indent=2)}"
        
        # Build context string
        context_str = f"""
Profile Data: {json.dumps(state.profile.to_dict(), indent=2)}
Stage Context: {stage_prompt}
{trade_context}
Additional Context: {json.dumps(context or {}, indent=2)}
"""
        
        # Build the full prompt
        system_prompt = COIA_SYSTEM_PROMPT.format(
            context=context_str,
            conversation_history=conversation_history,
            current_stage=state.current_stage,
            profile_completeness=round(state.profile.calculate_completeness() * 100)
        )
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Generate response
        response = await self.chain.ainvoke(messages)
        
        return {
            'content': response.strip(),
            'stage': state.current_stage
        }
    
    def _extract_profile_updates(self, user_message: str, ai_response: str, current_stage: str) -> Dict[str, Any]:
        """Extract profile updates from user message based on current stage"""
        updates = {}
        user_input = user_message.lower().strip()
        
        if current_stage == 'welcome':
            # Extract primary trade
            trade_keywords = {
                'general contractor': ['general', 'contractor', 'gc', 'general contractor'],
                'plumber': ['plumb', 'plumbing'],
                'electrician': ['electric', 'electrical'],
                'hvac': ['hvac', 'heating', 'cooling', 'air conditioning'],
                'painter': ['paint', 'painting'],
                'flooring': ['floor', 'flooring', 'carpet', 'tile', 'hardwood'],
                'roofing': ['roof', 'roofing'],
                'landscaping': ['landscape', 'landscaping', 'yard', 'garden']
            }
            
            for trade, keywords in trade_keywords.items():
                if any(keyword in user_input for keyword in keywords):
                    updates['primary_trade'] = trade.title()
                    break
                    
        elif current_stage == 'experience':
            # Extract years of experience
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                years = int(numbers[0])
                if 0 <= years <= 50:  # Sanity check
                    updates['years_in_business'] = years
                    
        elif current_stage == 'service_area':
            # Extract service area information
            # Look for city names, zip codes, and radius
            zip_codes = re.findall(r'\b\d{5}\b', user_input)
            if zip_codes:
                updates['service_areas'] = zip_codes
            
            # Extract city names (simple heuristic)
            if 'mile' in user_input:
                miles = re.findall(r'(\d+)\s*mile', user_input)
                if miles:
                    updates['service_radius_miles'] = int(miles[0])
            
            # If no specific data extracted, store the whole response
            if not updates:
                updates['service_areas'] = [user_input]
                
        elif current_stage == 'differentiators':
            # Store differentiators
            updates['differentiators'] = user_input
            
            # Look for specific keywords
            if 'warranty' in user_input or 'guarantee' in user_input:
                updates['warranty_offered'] = True
            
            if 'license' in user_input:
                updates['license_info'] = user_input
                
            if 'insurance' in user_input:
                updates['insurance_verified'] = True
        
        return updates
    
    def _determine_next_stage(self, state: CoIAConversationState, ai_response: str) -> str:
        """Determine the next conversation stage based on current state and AI response"""
        current_stage = state.current_stage
        profile = state.profile
        
        stage_flow = {
            'welcome': 'experience',
            'experience': 'service_area', 
            'service_area': 'differentiators',
            'differentiators': 'completed',
            'completed': 'completed'
        }
        
        # Check if we have enough information to advance
        if current_stage == 'welcome' and profile.primary_trade:
            return stage_flow['welcome']
        elif current_stage == 'experience' and profile.years_in_business is not None:
            return stage_flow['experience']
        elif current_stage == 'service_area' and len(profile.service_areas) > 0:
            return stage_flow['service_area']
        elif current_stage == 'differentiators' and profile.differentiators:
            return stage_flow['differentiators']
        
        return current_stage
    
    async def _count_matching_projects(self, profile: ContractorProfile) -> int:
        """Count projects matching contractor profile (mock implementation)"""
        # TODO: Implement real project matching logic
        base_count = 5
        
        # Add projects based on trade
        if profile.primary_trade:
            if 'general' in profile.primary_trade.lower():
                base_count += 8
            elif 'plumb' in profile.primary_trade.lower():
                base_count += 6
            elif 'electric' in profile.primary_trade.lower():
                base_count += 4
        
        # Add projects based on experience
        if profile.years_in_business:
            if profile.years_in_business > 10:
                base_count += 3
            elif profile.years_in_business > 5:
                base_count += 2
        
        return min(base_count, 25)  # Cap at 25 projects
    
    async def _create_contractor_profile(self, state: CoIAConversationState) -> Optional[str]:
        """Create contractor profile in contractors table"""
        if not self.supabase:
            logger.warning("Supabase not initialized - cannot create contractor profile")
            return None
            
        try:
            # Convert CoIA profile data to contractors table format
            profile = state.profile
            
            # Generate a temporary user_id (in production, this would come from auth)
            temp_user_id = str(uuid.uuid4())
            
            # Build service areas JSON
            service_areas = {}
            if profile.service_areas:
                service_areas['zip_codes'] = profile.service_areas
            if profile.service_radius_miles:
                service_areas['radius_miles'] = profile.service_radius_miles
            # Note: primary_location not available in current ContractorProfile
            
            # Build insurance info JSON if available
            insurance_info = {}
            if profile.license_info:
                insurance_info = {'license_info': profile.license_info}
            if profile.insurance_verified:
                insurance_info['insurance_verified'] = True
            if profile.warranty_offered:
                insurance_info['warranty_offered'] = True
            
            # Prepare contractor data for contractors table
            contractor_data = {
                'user_id': temp_user_id,
                'company_name': profile.business_name or f"{profile.primary_trade} Professional",
                'specialties': [profile.primary_trade] + (profile.specializations or []),
                'service_areas': service_areas if service_areas else None,
                'license_number': profile.license_info if isinstance(profile.license_info, str) else None,
                'insurance_info': insurance_info if insurance_info else None,
                'tier': 1,  # New contractors start at Tier 1
                'availability_status': 'available',
                'total_jobs': max(0, (profile.years_in_business or 0) * 15),  # Estimate based on experience
                'verified': bool(profile.license_info),  # Verified if has license info
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Insert into contractors table
            result = self.supabase.table('contractors').insert(contractor_data).execute()
            
            if result.data and len(result.data) > 0:
                contractor_id = result.data[0]['id']
                logger.info(f"✅ Created contractor profile: {contractor_id}")
                logger.info(f"Company: {contractor_data['company_name']}")
                logger.info(f"Specialties: {contractor_data['specialties']}")
                logger.info(f"Service Areas: {contractor_data['service_areas']}")
                
                # Note: Website enrichment would be triggered here if website URL was collected
                # Future enhancement: Add website collection to CoIA conversation flow
                
                return contractor_id
            else:
                logger.error("Failed to create contractor profile - no data returned")
                return None
                
        except Exception as e:
            logger.error(f"Error creating contractor profile: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def _enrich_contractor_profile(self, contractor_id: str, website_url: str):
        """Enrich contractor profile using web scraping (async background task)"""
        try:
            logger.info(f"🔍 Starting profile enrichment for contractor {contractor_id} from {website_url}")
            
            # Import the existing enrichment system
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'enrichment'))
            
            from agents.enrichment.playwright_website_enricher import PlaywrightWebsiteEnricher
            
            # Initialize enricher (would use MCP client in full implementation)
            enricher = PlaywrightWebsiteEnricher(mcp_client=None, llm_client=self.llm)
            
            # Prepare contractor data for enrichment
            contractor_data = {
                'website': website_url,
                'contractor_id': contractor_id
            }
            
            # Run enrichment
            enriched_data = await enricher.enrich_contractor_from_website(contractor_data)
            
            if enriched_data and self.supabase:
                # Update contractor profile with enriched data
                update_data = {}
                
                if enriched_data.email:
                    # Could store in a separate contacts table or JSON field
                    update_data['insurance_info'] = {'contact_email': enriched_data.email}
                
                if enriched_data.service_areas:
                    # Update service areas with discovered zip codes
                    existing_areas = {}
                    contractor = self.supabase.table('contractors').select('service_areas').eq('id', contractor_id).execute()
                    if contractor.data:
                        existing_areas = contractor.data[0].get('service_areas', {}) or {}
                    
                    existing_areas['discovered_zip_codes'] = enriched_data.service_areas
                    update_data['service_areas'] = existing_areas
                
                if enriched_data.business_size:
                    # Map business size to tier
                    size_to_tier = {
                        'INDIVIDUAL_HANDYMAN': 1,
                        'OWNER_OPERATOR': 1,
                        'LOCAL_BUSINESS_TEAMS': 2,
                        'NATIONAL_COMPANY': 3
                    }
                    if enriched_data.business_size in size_to_tier:
                        update_data['tier'] = size_to_tier[enriched_data.business_size]
                
                if enriched_data.certifications:
                    # Store certifications in insurance_info
                    insurance_info = update_data.get('insurance_info', {})
                    insurance_info['certifications'] = enriched_data.certifications
                    update_data['insurance_info'] = insurance_info
                
                # Update database if we have enriched data
                if update_data:
                    update_data['updated_at'] = datetime.utcnow().isoformat()
                    result = self.supabase.table('contractors').update(update_data).eq('id', contractor_id).execute()
                    
                    if result.data:
                        logger.info(f"✅ Profile enrichment complete for contractor {contractor_id}")
                        logger.info(f"Updated fields: {list(update_data.keys())}")
                    else:
                        logger.warning(f"Failed to update enriched data for contractor {contractor_id}")
            
        except Exception as e:
            logger.error(f"Error enriching contractor profile {contractor_id}: {e}")
            # Don't raise - enrichment failure shouldn't break profile creation

# Global CoIA agent instance (will be initialized with API key)
coia_agent: Optional[CoIAAgent] = None

def initialize_coia(api_key: str) -> CoIAAgent:
    """Initialize global CoIA agent instance"""
    global coia_agent
    coia_agent = CoIAAgent(api_key)
    return coia_agent

def get_coia_agent() -> Optional[CoIAAgent]:
    """Get global CoIA agent instance"""
    return coia_agent