"""
LangGraph Node Wrappers for Unified COIA Agent
Converts existing COIA implementations into LangGraph-compatible nodes
"""

import logging
import os
from datetime import datetime
from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command

from .agent import CoIAAgent
from .openai_o3_agent import OpenAIO3CoIA
from .research_based_agent import ResearchBasedCoIAAgent
from .unified_state import UnifiedCoIAState


logger = logging.getLogger(__name__)


class CoIANodeWrapper:
    """Base wrapper class for COIA agent nodes"""

    def __init__(self):
        """Initialize with environment detection"""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_places_key = os.getenv("GOOGLE_PLACES_API_KEY")

        # Initialize agents (lazy loading)
        self._conversation_agent = None
        self._research_agent = None
        self._intelligence_agent = None

        # Capability detection
        self.has_playwright = self._check_playwright()
        self.has_google_places = bool(self.google_places_key)
        self.has_memory = self._check_supabase()

    def _check_playwright(self) -> bool:
        """Check if Playwright is available"""
        try:
            import playwright
            return True
        except ImportError:
            return False

    def _check_supabase(self) -> bool:
        """Check if Supabase credentials are available"""
        return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"))

    @property
    def conversation_agent(self) -> CoIAAgent:
        """Lazy load conversation agent"""
        if self._conversation_agent is None:
            self._conversation_agent = CoIAAgent(self.api_key)
        return self._conversation_agent

    @property
    def research_agent(self) -> ResearchBasedCoIAAgent:
        """Lazy load research agent"""
        if self._research_agent is None:
            self._research_agent = ResearchBasedCoIAAgent(self.api_key)
        return self._research_agent

    @property
    def intelligence_agent(self) -> OpenAIO3CoIA:
        """Lazy load intelligence agent (using Claude Opus 4 instead of O3)"""
        if self._intelligence_agent is None:
            # Use Claude Opus 4 for intelligence mode as O3 from Claude doesn't exist
            self._intelligence_agent = OpenAIO3CoIA(
                api_key=self.api_key,  # Claude API key
                google_places_api_key=self.google_places_key
            )
        return self._intelligence_agent

    def _extract_user_message(self, state: UnifiedCoIAState) -> str:
        """Extract the latest user message from state"""
        messages = state.get("messages", [])
        if not messages:
            return ""

        # Get the last human message
        for msg in reversed(messages):
            if (hasattr(msg, "type") and msg.type == "human") or isinstance(msg, HumanMessage):
                return msg.content

        return ""

    def _update_state_from_response(
        self,
        state: UnifiedCoIAState,
        response: str,
        agent_response: dict[str, Any],
        current_mode: str
    ) -> dict[str, Any]:
        """Update state based on agent response - NOW USING ALL AGENT DATA"""
        updates = {}

        # Add response message
        current_messages = state.get("messages", [])
        current_messages.append(AIMessage(content=response))
        updates["messages"] = current_messages

        # Update last_updated
        updates["last_updated"] = datetime.now().isoformat()

        # CRITICAL: Extract ALL profile data from agent response
        profile_progress = agent_response.get("profile_progress", {})
        if profile_progress:
            # FIXED: Merge agent profile data with existing profile instead of overwriting
            if profile_progress.get("collectedData"):
                existing_profile = state.get("contractor_profile", {})
                agent_profile = profile_progress["collectedData"]
                
                # Merge profiles: existing data takes precedence over null/empty agent data
                merged_profile = existing_profile.copy()
                for key, value in agent_profile.items():
                    # Only update if agent has meaningful data and existing doesn't
                    if value and (not merged_profile.get(key)):
                        merged_profile[key] = value
                
                updates["contractor_profile"] = merged_profile
            updates["profile_completeness"] = profile_progress.get("completeness", 0.0)

        # ENHANCED: Additional profile extraction from messages
        # Extract user messages to get profile data that agent missed
        user_messages = state.get("messages", [])
        if user_messages:
            latest_user_message = None
            for msg in reversed(user_messages):
                if hasattr(msg, "type") and msg.type == "human":
                    latest_user_message = msg.content
                    break

            if latest_user_message:
                # Enhance profile data with smart extraction  
                updates_profile = updates.get("contractor_profile")
                state_profile = state.get("contractor_profile", {})
                
                # Profile merging logic
                
                current_profile = updates_profile or state_profile
                try:
                    enhanced_profile = self._smart_profile_extraction(latest_user_message, current_profile)
                    # Ensure we got a valid dictionary back
                    if isinstance(enhanced_profile, dict):
                        updates["contractor_profile"] = enhanced_profile
                    else:
                        # If extraction failed, preserve current profile
                        updates["contractor_profile"] = current_profile
                except Exception as e:
                    # If extraction crashes, preserve current profile
                    logger.warning(f"Profile extraction failed: {e}")
                    updates["contractor_profile"] = current_profile
                
                # Recalculate completeness
                updates["profile_completeness"] = self._calculate_profile_completeness(updates["contractor_profile"])

                # Map profile data to state fields for mode detection
                profile_to_map = updates["contractor_profile"]
                if profile_to_map.get("company_name"):
                    updates["company_name"] = profile_to_map["company_name"]
                if profile_to_map.get("website"):
                    updates["company_website"] = profile_to_map["website"]

        # CRITICAL: Extract business detection from research agent
        if "business_name" in agent_response:
            updates["company_name"] = agent_response["business_name"]
        if "website" in agent_response:
            updates["company_website"] = agent_response["website"]

        # CRITICAL: Extract research data from research agent
        if agent_response.get("research_data"):
            updates["research_findings"] = agent_response["research_data"]
            updates["website_research_status"] = "completed"

            # Extract company info from research data
            research_data = agent_response["research_data"]
            if isinstance(research_data, dict):
                if research_data.get("company_name"):
                    updates["company_name"] = research_data["company_name"]
                if research_data.get("website"):
                    updates["company_website"] = research_data["website"]
                if research_data.get("business_info"):
                    updates["business_info"] = research_data["business_info"]
        else:
            # Mark research as completed even if no data returned to prevent infinite loops
            updates["website_research_status"] = "attempted"

        # CRITICAL: Always mark research as completed to prevent infinite loops
        updates["research_completed"] = True

        # CRITICAL: Extract intelligence data from intelligence agent
        if agent_response.get("intelligence_data"):
            updates["intelligence_data"] = agent_response["intelligence_data"]
        if agent_response.get("google_places_data"):
            updates["google_places_data"] = agent_response["google_places_data"]
        if agent_response.get("returning_contractor_id"):
            updates["returning_contractor_id"] = agent_response["returning_contractor_id"]
            updates["persistent_memory_loaded"] = True

        # CRITICAL: Check for contractor creation (completion)
        if agent_response.get("contractor_id"):
            updates["completion_ready"] = True
            updates["contractor_id"] = agent_response["contractor_id"]
            updates["contractor_created"] = True
            updates["conversion_successful"] = True

        # CRITICAL: Extract stage information
        if agent_response.get("stage"):
            # Map agent stages to current_mode if needed
            stage = agent_response["stage"]
            if stage in ["research_confirmation", "website_request", "research_correction"]:
                updates["current_mode"] = "research"
            elif stage == "completed":
                updates["completion_ready"] = True

        return updates

    def _smart_profile_extraction(self, user_message: str, current_profile: dict[str, Any]) -> dict[str, Any]:
        """Enhanced profile extraction that works from any conversation turn"""
        import re

        # Start with current profile
        profile = current_profile.copy()
        user_input = user_message.lower().strip()

        # Extract company/business name
        company_patterns = [
            r"i'm\s+(?!from\s)([^.,!]+?)\s*[.,!]",  # "I'm StateDebug Plumbing." but NOT "I'm from..."
            r"i'm\s+(\w+)\s+from\s+([^.,]+)",  # "I'm John from HVAC Solutions"
            r"(?:i'm\s+)from\s+([^.,]+)",  # "I'm from HVAC Solutions"
            r"company\s+is\s+([^.,]+)",  # "company is HVAC Solutions"
            r"business\s+is\s+([^.,]+)",  # "business is HVAC Solutions"
            r"i\s+own\s+([^.,]+)",  # "I own HVAC Solutions"
            r"we're\s+([^.,]+)",  # "We're HVAC Solutions"
            r"my\s+company\s+is\s+([^.,]+)",  # "my company is HVAC Solutions"
            r"account\s+(?:for\s+)?([^.,\s]+(?:\s+[^.,\s]+)*)",  # "create account for ABC Company"
        ]

        for i, pattern in enumerate(company_patterns):
            match = re.search(pattern, user_input)
            if match:
                groups = match.groups()
                if groups:
                    # For pattern 0 ("I'm CompanyName"), use first group
                    # For pattern 1 ("I'm John from CompanyName"), use second group (last)  
                    # For other patterns, use last group
                    if i == 0:  # "I'm CompanyName" pattern
                        potential_company = groups[0].strip()
                    else:
                        potential_company = groups[-1].strip()  # Last capture group
                    
                    # Clean up common words that shouldn't be company names
                    if not any(word in potential_company for word in ["doing", "been", "years", "work", "specialize", "usually"]):
                        profile["company_name"] = potential_company.title()
                        break

        # Extract years in business (fix the confusion with service radius)
        # Only extract if we don't already have years_in_business
        if not profile.get("years_in_business"):
            years_patterns = [
                r"(\d+)\s+years?\s+(?:of\s+)?(?:experience|in\s+business|doing)",  # "15 years in business"
                r"been\s+in\s+business\s+(\d+)\s+years?",  # "been in business 15 years"
                r"been\s+doing\s+.+\s+for\s+(\d+)\s+years?",  # "been doing HVAC for 15 years"
                r"(\d+)\s+years?\s+of\s+.+\s+(?:experience|work)",  # "15 years of experience"
                r"in\s+business\s+(?:for\s+)?(\d+)\s+years?",  # "in business 15 years"
                r"been\s+\w+\s+for\s+(\d+)\s+years?",  # "been painting for 15 years"
                r"we've\s+been\s+\w+\s+for\s+(\d+)\s+years?",  # "we've been painting for 15 years"
            ]

            for pattern in years_patterns:
                match = re.search(pattern, user_input)
                if match:
                    years = int(match.group(1))
                    if 1 <= years <= 50:  # Reasonable range
                        profile["years_in_business"] = years
                        break

        # Extract service area/radius
        service_patterns = [
            r"within\s+(\d+)\s+miles?\s+of\s+([^.,]+)",  # "within 25 miles of downtown Miami"
            r"(\d+)\s+mile\s+radius\s+(?:of\s+|around\s+)?([^.,]+)",  # "25 mile radius of Miami"
            r"work\s+in\s+([^.,]+)",  # "work in Miami"
            r"serve\s+([^.,]+)",  # "serve Miami area"
            r"repairs?\s+in\s+([^.,]+)",  # "repairs in Dallas"
            r"in\s+([^.,]+)\s+area",  # "in Dallas area"
            r"(?:located|based)\s+in\s+([^.,]+)",  # "located in Dallas"
        ]

        for pattern in service_patterns:
            match = re.search(pattern, user_input)
            if match:
                if len(match.groups()) == 2:  # Has both radius and location
                    radius = int(match.group(1))
                    location = match.group(2).strip()
                    profile["service_radius_miles"] = radius
                    profile["service_areas"] = [location.title()]
                else:  # Just location
                    location = match.group(1).strip()
                    profile["service_areas"] = [location.title()]
                break

        # Extract main service type (CRITICAL for matching)
        service_type_keywords = {
            "Roofing": ["roof", "roofing", "shingle", "tile roof", "metal roof"],
            "Plumbing": ["plumb", "pipe", "drain", "water heater", "faucet", "toilet"],
            "HVAC": ["hvac", "heating", "cooling", "air condition", "ac", "furnace"],
            "Electrical": ["electric", "wiring", "outlet", "breaker", "lighting"],
            "Landscaping": ["landscap", "lawn", "yard", "garden", "turf", "grass"],
            "Painting": ["paint", "stain", "drywall", "wallpaper"],
            "Flooring": ["floor", "tile", "carpet", "hardwood", "laminate"],
            "General Contractor": ["general contractor", "gc", "remodel", "renovation"],
            "Pool": ["pool", "spa", "hot tub"],
            "Concrete": ["concrete", "driveway", "sidewalk", "foundation"],
            "Fencing": ["fence", "fencing", "gate"],
            "Windows & Doors": ["window", "door", "sliding", "french door"]
        }
        
        if not profile.get("main_service_type"):
            for service_type, keywords in service_type_keywords.items():
                if any(keyword in user_input for keyword in keywords):
                    profile["main_service_type"] = service_type
                    break
        
        # Extract service subtypes (CRITICAL for matching)
        service_subtype_patterns = {
            "New installation": ["new install", "installation", "new construction", "install new"],
            "Repair/service": ["repair", "fix", "service", "maintenance", "troubleshoot"],
            "Replacement": ["replac", "swap out", "upgrade", "change out"],
            "Emergency repair": ["emergency", "urgent", "24/7", "same day", "asap"],
            "Maintenance": ["maintenance", "upkeep", "service plan", "preventive"]
        }
        
        subtypes = profile.get("service_subtypes", [])
        for subtype, keywords in service_subtype_patterns.items():
            if any(keyword in user_input for keyword in keywords) and subtype not in subtypes:
                subtypes.append(subtype)
        if subtypes:
            profile["service_subtypes"] = subtypes
        
        # Extract business size category (CRITICAL for matching)
        business_size_indicators = {
            "INDIVIDUAL_HANDYMAN": [
                "handyman", "solo", "one man", "one-man", "just me", "by myself",
                "independent", "freelance"
            ],
            "OWNER_OPERATOR": [
                "owner operator", "owner-operator", "small business", "family business",
                "me and my", "couple guys", "small team", "few employees"
            ],
            "LOCAL_BUSINESS_TEAMS": [
                "crew", "teams", "multiple crews", "employees", "staff of",
                "local company", "established business", "been in business"
            ],
            "NATIONAL_COMPANY": [
                "national", "franchise", "corporate", "multiple locations",
                "nationwide", "chain", "branches"
            ]
        }
        
        if not profile.get("business_size_category"):
            # Check years in business as a hint
            years = profile.get("years_in_business") or 0
            
            # Check explicit keywords first
            for size_category, keywords in business_size_indicators.items():
                if any(keyword in user_input for keyword in keywords):
                    profile["business_size_category"] = size_category
                    break
            
            # If not found, infer from context
            if not profile.get("business_size_category"):
                if "we" in user_input or "our" in user_input:
                    if years > 10:
                        profile["business_size_category"] = "LOCAL_BUSINESS_TEAMS"
                    else:
                        profile["business_size_category"] = "OWNER_OPERATOR"
                elif "i" in user_input or "my" in user_input:
                    profile["business_size_category"] = "OWNER_OPERATOR"
        
        # Extract specializations
        specialization_keywords = {
            "commercial": ["commercial", "office buildings", "commercial properties"],
            "residential": ["residential", "home", "house"],
            "high-end": ["high-end", "luxury", "premium", "upscale"],
            "hotels": ["hotel", "hospitality", "resort"],
            "emergency": ["emergency", "24/7", "urgent"],
            "new construction": ["new construction", "new build"],
            "renovation": ["renovation", "remodel", "retrofit"]
        }

        specializations = profile.get("specializations", [])
        for spec_name, keywords in specialization_keywords.items():
            if any(keyword in user_input for keyword in keywords) and spec_name not in specializations:
                specializations.append(spec_name)

        if specializations:
            profile["specializations"] = specializations
        
        # Extract ZIP codes (CRITICAL for matching)
        zip_pattern = r'\b\d{5}\b'
        zip_matches = re.findall(zip_pattern, user_input)
        if zip_matches:
            existing_zips = profile.get("zip_codes", [])
            for zip_code in zip_matches:
                if zip_code not in existing_zips:
                    existing_zips.append(zip_code)
            profile["zip_codes"] = existing_zips

        # Extract email addresses
        email_patterns = [
            r"email\s+is\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",  # "email is info@example.com"
            r"email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",  # "email: info@example.com"
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",  # any email pattern
        ]
        
        for pattern in email_patterns:
            match = re.search(pattern, user_input)
            if match:
                email = match.group(1).strip()
                if "@" in email and "." in email:
                    profile["email"] = email
                    break
        
        # Extract phone numbers
        phone_patterns = [
            r"phone\s+is\s+([\(\)\d\s\-]+)",  # "phone is (561) 504-9621"
            r"phone:\s*([\(\)\d\s\-]+)",  # "phone: (561) 504-9621"
            r"(\(\d{3}\)\s*\d{3}-\d{4})",  # "(561) 504-9621"
            r"(\d{3}-\d{3}-\d{4})",  # "561-504-9621"
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, user_input)
            if match:
                phone = match.group(1).strip()
                if len(phone) >= 10:  # Minimum valid phone number length
                    profile["phone"] = phone
                    break
        
        # Extract website URLs
        website_patterns = [
            r"website\s+is\s+([^\s.,]+\.com)",  # "website is example.com"
            r"at\s+([^\s.,]+\.com)",  # "at example.com"
            r"visit\s+([^\s.,]+\.com)",  # "visit example.com"
            r"check\s+out\s+([^\s.,]+\.com)",  # "check out example.com"
            r"find\s+.*\s+at\s+([^\s.,]+\.com)",  # "find more at example.com"
            r"([a-zA-Z0-9-]+\.com)",  # basic domain.com pattern
        ]

        for pattern in website_patterns:
            match = re.search(pattern, user_input)
            if match:
                potential_website = match.group(1).strip()
                # Basic validation - should contain .com and not be too long
                if ".com" in potential_website and len(potential_website) < 50:
                    # Ensure it starts with http if not present
                    if not potential_website.startswith("http"):
                        potential_website = f"https://{potential_website}"
                    profile["website"] = potential_website
                    break

        # Extract differentiators from conversation
        if any(word in user_input for word in ["specialize", "focus", "expert", "certified", "licensed"]):
            current_diff = profile.get("differentiators", "")
            if current_diff:
                profile["differentiators"] = f"{current_diff}. {user_message}"
            else:
                profile["differentiators"] = user_message

        return profile

    def _calculate_profile_completeness(self, profile: dict[str, Any]) -> float:
        """Calculate profile completeness percentage"""
        required_fields = [
            "company_name", "contact_name", "email", "phone",
            "primary_trade", "years_in_business", "service_areas"
        ]

        completed = sum(1 for field in required_fields if profile.get(field))
        return (completed / len(required_fields)) * 100.0

    def _determine_next_mode(self, state: UnifiedCoIAState, agent_response: dict[str, Any], state_updates: dict[str, Any] = None) -> Optional[str]:
        """Determine if we should transition to a different mode"""
        current_mode = state.get("current_mode", "conversation")

        # Helper function to get value from state or updates
        def get_value(key):
            if state_updates and key in state_updates:
                return state_updates[key]
            return state.get(key)

        # Check for research triggers
        if current_mode == "conversation":
            company_website = get_value("company_website")
            research_completed = get_value("research_completed")
            has_playwright = self.has_playwright

            logger.info(f"Mode detection - company_website: {company_website}, research_completed: {research_completed}, has_playwright: {has_playwright}")

            if (company_website and
                not research_completed and
                has_playwright):
                logger.info("Triggering research mode!")
                return "research"

        # Check for intelligence triggers
        if current_mode in ["conversation", "research"]:
            if (get_value("company_name") and
                get_value("business_info") and
                not get_value("intelligence_data") and
                self.has_google_places):
                return "intelligence"

        # Check for completion
        if agent_response.get("completed", False):
            return None  # Stay in current mode for completion message

        return current_mode  # Stay in current mode


# Node Functions for LangGraph
node_wrapper = CoIANodeWrapper()


async def conversation_node(state: UnifiedCoIAState) -> Command:
    """
    Conversation mode node - handles basic contractor onboarding conversation
    Uses the original CoIA agent implementation
    """
    try:
        logger.info(f"Conversation node processing - Mode: {state.get('current_mode')}")

        # Extract user message
        user_message = node_wrapper._extract_user_message(state)
        if not user_message:
            return {"error_state": "No user message found"}

        # Create conversation state for the agent
        session_id = state.get("session_id", "unknown")
        contractor_lead_id = state.get("contractor_lead_id")
        interface = state.get("interface", "chat")

        # Call the conversation agent
        agent_response = await node_wrapper.conversation_agent.process_message(
            session_id=session_id,
            user_message=user_message,
            context={"contractor_lead_id": contractor_lead_id, "interface": interface}
        )

        if not agent_response.get("response"):
            return {"error_state": "Conversation agent failed: No response received"}

        # Update state based on response
        updates = node_wrapper._update_state_from_response(
            state,
            agent_response["response"],
            agent_response,
            "conversation"
        )
        
        # LANDING PAGE SIGNUP LINK GENERATION
        # Check if we're on landing page and have enough profile data
        if interface == "landing_page":
            profile = updates.get("contractor_profile") or state.get("contractor_profile", {})
            
            # Check if user is requesting account creation
            user_input_lower = user_message.lower()
            wants_account = any(phrase in user_input_lower for phrase in [
                "create account", "sign up", "signup", "get started",
                "start receiving", "bid opportunities", "create my account",
                "set up account", "register", "join"
            ])
            
            # Check if we have minimum required data (more flexible)
            has_minimum_data = (
                profile.get("email") and 
                (profile.get("company_name") or profile.get("business_name") or 
                 profile.get("primary_trade") or len(profile.get("specializations", [])) > 0)
            )
            
            if wants_account and has_minimum_data:
                # Generate signup link
                from .signup_link_generator import generate_contractor_signup_link, create_signup_message
                
                signup_data = generate_contractor_signup_link(profile, contractor_lead_id)
                
                if signup_data.get("success"):
                    # Add signup link to response
                    signup_message = create_signup_message(signup_data)
                    
                    # Append signup message to response
                    current_messages = updates.get("messages", state.get("messages", []))
                    if current_messages and len(current_messages) > 0:
                        # Update the last AI message with signup link
                        last_message = current_messages[-1]
                        if hasattr(last_message, "content"):
                            last_message.content = f"{last_message.content}\n\n{signup_message}"
                    
                    # Store signup data in state
                    updates["signup_link_generated"] = True
                    updates["signup_data"] = signup_data
                    updates["profile_ready_for_signup"] = True
                    
                    logger.info(f"Generated signup link for {profile.get('company_name')}")
            
            # Check if profile is complete enough to offer signup
            elif has_minimum_data and not wants_account:
                completeness = node_wrapper._calculate_profile_completeness(profile)
                if completeness >= 60:  # 60% complete profile
                    updates["profile_ready_for_signup"] = True

        # IN-APP AUTHENTICATED BEHAVIOR
        # Check if we're in authenticated chat mode (not landing page)
        if interface == "chat" and state.get("contractor_id"):
            # This is an authenticated contractor
            profile = updates.get("contractor_profile") or state.get("contractor_profile", {})
            
            # For authenticated contractors, enhance with full features
            updates["authenticated_contractor"] = True
            updates["can_search_bid_cards"] = True
            updates["can_view_analytics"] = True
            updates["can_manage_profile"] = True
            
            # Add personalized greeting if first message
            messages = state.get("messages", [])
            if len(messages) <= 2:  # First exchange
                company_name = profile.get("company_name", "there")
                # Personalize the response
                if hasattr(updates.get("messages", [])[-1], "content"):
                    original_response = updates["messages"][-1].content
                    personalized = f"Welcome back, {company_name}! {original_response}"
                    updates["messages"][-1].content = personalized
        
        # Determine next mode
        next_mode = node_wrapper._determine_next_mode(state, agent_response, updates)

        if next_mode and next_mode != "conversation":
            # Transition to different mode
            updates["previous_mode"] = "conversation"
            updates["current_mode"] = next_mode
            updates["transition_reason"] = f"Detected {next_mode} opportunity"
            updates["mode_confidence"] = 0.8

            return Command(
                goto="mode_detector",  # Let mode detector route to appropriate node
                update=updates
            )
        else:
            # Stay in conversation mode or complete
            updates["current_mode"] = "conversation"
            # Return updates directly - LangGraph will handle completion automatically
            return updates

    except Exception as e:
        logger.error(f"Error in conversation node: {e}")
        return {"error_state": f"Conversation node error: {e!s}"}


async def research_node(state: UnifiedCoIAState) -> Command:
    """
    Research mode node - handles website research and data enrichment
    Uses the research-based CoIA agent implementation  
    """
    try:
        logger.info(f"Research node processing - Company: {state.get('company_name')}")

        if not node_wrapper.has_playwright:
            # Fallback to conversation mode if Playwright not available
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": "Playwright not available - fallback to conversation",
                    "mode_confidence": 1.0
                }
            )

        # Get company information for research
        company_name = state.get("company_name")
        company_website = state.get("company_website")

        if not company_name:
            # Need more info, go back to conversation
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": "Need company name for research",
                    "mode_confidence": 1.0
                }
            )

        # Create research context
        research_context = {
            "company_name": company_name,
            "website": company_website,
            "business_info": state.get("business_info", {})
        }

        # Call research agent
        agent_response = await node_wrapper.research_agent.process_message(
            session_id=state.get("session_id", "unknown"),
            user_message=f"Research company: {company_name}",
            context=research_context
        )

        if not agent_response.get("response"):
            # Research failed, continue with conversation
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": "Research failed: No response received",
                    "website_research_status": "failed",
                    "mode_confidence": 1.0
                }
            )

        # Update state with research results
        updates = node_wrapper._update_state_from_response(
            state,
            agent_response.get("response", "Research completed"),
            agent_response,
            "research"
        )

        # Determine next step
        next_mode = node_wrapper._determine_next_mode(state, agent_response, updates)

        if next_mode == "intelligence":
            # Move to intelligence mode
            updates["previous_mode"] = "research"
            updates["current_mode"] = "intelligence"
            updates["transition_reason"] = "Research complete - moving to intelligence enhancement"
            updates["mode_confidence"] = 0.9

            return Command(goto="intelligence", update=updates)
        else:
            # Return to conversation with research data
            updates["previous_mode"] = "research"
            updates["current_mode"] = "conversation"
            updates["transition_reason"] = "Research complete - returning to conversation"
            updates["mode_confidence"] = 1.0

            return Command(goto="conversation", update=updates)

    except Exception as e:
        logger.error(f"Error in research node: {e}")
        return Command(
            goto="conversation",
            update={
                "error_state": f"Research node error: {e!s}",
                "current_mode": "conversation",
                "website_research_status": "failed"
            }
        )


async def intelligence_node(state: UnifiedCoIAState) -> Command:
    """
    Intelligence mode node - handles advanced data processing and Google Places integration
    Uses the OpenAI O3-based agent (but with Claude Opus 4)
    """
    try:
        logger.info(f"Intelligence node processing - Company: {state.get('company_name')}")

        if not node_wrapper.has_google_places:
            # Fallback to conversation if Google Places not available
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": "Google Places API not available - fallback to conversation",
                    "mode_confidence": 1.0
                }
            )

        # Get data for intelligence processing
        company_name = state.get("company_name")
        business_info = state.get("business_info", {})
        research_data = state.get("research_findings")

        if not company_name:
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": "Need company data for intelligence processing",
                    "mode_confidence": 1.0
                }
            )

        # Create intelligence context
        intelligence_context = {
            "company_name": company_name,
            "business_info": business_info,
            "research_data": research_data,
            "contractor_profile": state.get("contractor_profile", {})
        }

        # Call intelligence agent
        agent_response = await node_wrapper.intelligence_agent.process_message(
            session_id=state.get("session_id", "unknown"),
            user_message=f"Enhance intelligence for: {company_name}",
            context=intelligence_context
        )

        if not agent_response.get("response"):
            # Intelligence failed, continue with conversation
            return Command(
                goto="conversation",
                update={
                    "current_mode": "conversation",
                    "transition_reason": "Intelligence processing failed: No response received",
                    "mode_confidence": 1.0
                }
            )

        # Update state with intelligence results
        updates = node_wrapper._update_state_from_response(
            state,
            agent_response.get("response", "Intelligence processing completed"),
            agent_response,
            "intelligence"
        )

        # Intelligence processing complete - return to conversation
        updates["previous_mode"] = "intelligence"
        updates["current_mode"] = "conversation"
        updates["transition_reason"] = "Intelligence processing complete - returning to conversation"
        updates["mode_confidence"] = 1.0

        return Command(goto="conversation", update=updates)

    except Exception as e:
        logger.error(f"Error in intelligence node: {e}")
        return Command(
            goto="conversation",
            update={
                "error_state": f"Intelligence node error: {e!s}",
                "current_mode": "conversation"
            }
        )


async def mode_detector_node(state: UnifiedCoIAState) -> dict[str, Any]:
    """
    Mode detector node - determines which mode to route to based on current state
    This is called for mode transitions and routing decisions
    """
    try:
        current_mode = state.get("current_mode", "conversation")
        interface = state.get("interface", "chat")

        logger.info(f"Mode detector - Current mode: {current_mode}, Interface: {interface}")
        
        # MODIFIED: Allow research mode on landing page for business discovery
        # Landing page can use research mode if company detected
        if interface == "landing_page":
            # Extract profile data first to see if we can do research
            user_message = node_wrapper._extract_user_message(state)
            if user_message:
                current_profile = state.get("contractor_profile", {})
                enhanced_profile = node_wrapper._smart_profile_extraction(user_message, current_profile)
                
                # If company name detected, allow mode switching
                company_name = enhanced_profile.get("company_name") or state.get("company_name")
                if company_name:
                    logger.info(f"Landing page: company name detected '{company_name}' - allowing research mode")
                    # Don't return here - let normal mode detection logic run
                else:
                    # No company name - stay in conversation mode
                    return {
                        "mode_detector_decision": "conversation",
                        "current_mode": "conversation", 
                        "transition_reason": "Landing page: no company name detected"
                    }
            else:
                # No message - default to conversation
                return {
                    "mode_detector_decision": "conversation",
                    "current_mode": "conversation",
                    "transition_reason": "Landing page: no user message"
                }

        # CRITICAL: Extract profile data BEFORE routing decisions
        user_message = node_wrapper._extract_user_message(state)
        updates = {}

        if user_message:
            # Always extract profile data from user messages
            current_profile = state.get("contractor_profile", {})
            enhanced_profile = node_wrapper._smart_profile_extraction(user_message, current_profile)

            if enhanced_profile and any(enhanced_profile.values()):
                updates["contractor_profile"] = enhanced_profile
                updates["profile_completeness"] = node_wrapper._calculate_profile_completeness(enhanced_profile)

                # Also update top-level fields for mode detection
                if enhanced_profile.get("company_name"):
                    updates["company_name"] = enhanced_profile["company_name"]
                if enhanced_profile.get("website"):
                    updates["company_website"] = enhanced_profile["website"]

                logger.info(f"Mode detector extracted profile data: {list(enhanced_profile.keys())}")

            # Now check for bid card search mode
            user_input = user_message.lower()
            bid_search_keywords = [
                "show me projects", "find projects", "search projects",
                "kitchen projects", "bathroom projects", "lawn care projects",
                "hvac projects", "plumbing projects", "electrical projects",
                "emergency projects", "urgent projects", "projects near me",
                "available projects", "bid on projects", "show me bids",
                "find work", "looking for work", "emergency hvac", "emergency plumbing"
            ]

            if any(keyword in user_input for keyword in bid_search_keywords):
                logger.info("Mode detector triggering BID CARD SEARCH mode!")
                updates["mode_detector_decision"] = "bid_card_search"
                updates["current_mode"] = "bid_card_search"
                updates["transition_reason"] = "Bid card search keywords detected"
                return updates

        # Respect explicit specialized modes (research, intelligence)
        if current_mode in ["research", "intelligence"]:
            logger.info(f"Mode detector keeping specialized mode: {current_mode}")
            return {"mode_detector_decision": current_mode}

        # Determine mode based on state and capabilities
        company_name = state.get("company_name")
        has_website = bool(state.get("company_website"))
        research_completed = state.get("research_completed", False)
        has_intelligence_data = bool(state.get("intelligence_data"))

        logger.info(f"Mode detection - company_name: {company_name}, has_website: {has_website}, research_completed: {research_completed}, has_playwright: {node_wrapper.has_playwright}")

        # Research mode conditions - MODIFIED to trigger on company name alone
        if (company_name and
            not research_completed and
            node_wrapper.has_playwright):
            logger.info(f"Mode detector triggering RESEARCH mode for company: {company_name}")
            return {
                "mode_detector_decision": "research",
                "current_mode": "research", 
                "transition_reason": f"Company name '{company_name}' detected - triggering research mode for website discovery"
            }

        # Intelligence mode conditions
        if (company_name and
            (research_completed or state.get("business_info")) and
            not has_intelligence_data and
            node_wrapper.has_google_places):
            logger.info("Mode detector triggering INTELLIGENCE mode!")
            return {
                "mode_detector_decision": "intelligence",
                "current_mode": "intelligence",
                "transition_reason": "Research complete - triggering intelligence mode"
            }

        # Bid card search detection already handled above

        # Default to conversation
        logger.info("Mode detector defaulting to CONVERSATION mode")
        return {
            "mode_detector_decision": "conversation",
            "current_mode": "conversation"
        }

    except Exception as e:
        logger.error(f"Error in mode detector: {e}")
        return {
            "mode_detector_decision": "conversation",
            "current_mode": "conversation",
            "error_state": f"Mode detector error: {e!s}"
        }


# Export node functions for graph construction
__all__ = [
    "CoIANodeWrapper",
    "conversation_node",
    "intelligence_node",
    "mode_detector_node",
    "research_node"
]
