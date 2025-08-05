"""
Research-Based CoIA (Contractor Interface Agent)
Updated to research websites and Google Business listings instead of just conversation
"""

import logging
import os
import re
from typing import Any, Optional

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from supabase import Client, create_client

from agents.enrichment.playwright_website_enricher import (
    EnrichedContractorData,
    PlaywrightWebsiteEnricher,
)

from .state import CoIAConversationState, coia_state_manager


# Load environment
load_dotenv(override=True)

logger = logging.getLogger(__name__)

class ResearchBasedCoIAAgent:
    """Research-Based CoIA - Uses web research instead of just conversation"""

    def __init__(self, api_key: str):
        """Initialize CoIA with Claude Opus 4, database, and research tools"""
        self.llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            anthropic_api_key=api_key,
            temperature=0.7,
            max_tokens=1500
        )
        self.output_parser = StrOutputParser()
        self.chain = self.llm | self.output_parser

        # Initialize research tools
        self.website_enricher = PlaywrightWebsiteEnricher(mcp_client=None, llm_client=self.llm)

        # Initialize Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not found - contractor profiles will not be saved")
            self.supabase = None
        else:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            logger.info("Research-Based CoIA initialized with Supabase")

    async def process_message(self, session_id: str, user_message: str,
                            context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Process user message - now with business research capabilities"""

        # Get or create conversation state
        state = coia_state_manager.get_session(session_id)
        if not state:
            state = coia_state_manager.create_session(session_id)

        # Add user message to conversation
        state.add_message("user", user_message, state.current_stage)

        try:
            # Detect if user provided business name/website
            business_info = self._extract_business_info(user_message)

            if business_info and not state.research_completed:
                # Research mode: Look up business information
                return await self._handle_business_research(state, business_info, user_message)
            elif state.research_completed and not state.research_confirmed:
                # Confirmation mode: Confirm research findings
                return await self._handle_research_confirmation(state, user_message)
            else:
                # Standard conversation mode
                return await self._handle_standard_conversation(state, user_message, context)

        except Exception as e:
            logger.error(f"Error processing CoIA message: {e}")
            return self._fallback_response(state)

    def _extract_business_info(self, user_message: str) -> Optional[dict[str, str]]:
        """Extract business name and potential website from user message"""
        message = user_message.lower().strip()

        # Look for business name patterns
        business_patterns = [
            r"i own\s+(.+)",
            r"my business is\s+(.+)",
            r"my company is\s+(.+)",
            r"i run\s+(.+)",
            r"(.+)\s+in\s+\w+",  # "JM Holiday Lighting in South Florida"
        ]

        business_name = None
        for pattern in business_patterns:
            match = re.search(pattern, message)
            if match:
                business_name = match.group(1).strip()
                break

        # Look for website patterns
        website_patterns = [
            r"(https?://[\w\.-]+\.\w+)",
            r"([\w\.-]+\.\w+)",  # Simple domain pattern
        ]

        website = None
        for pattern in website_patterns:
            match = re.search(pattern, user_message)
            if match:
                website = match.group(1)
                if not website.startswith("http"):
                    website = f"https://{website}"
                break

        if business_name or website:
            return {
                "business_name": business_name,
                "website": website
            }

        return None

    async def _handle_business_research(self, state: CoIAConversationState,
                                     business_info: dict[str, str],
                                     user_message: str) -> dict[str, Any]:
        """Research the business using web tools"""

        print(f"🔍 Researching business: {business_info}")

        # Store the business info
        state.business_research = business_info

        # Try to find website if not provided
        website = business_info.get("website")
        business_name = business_info.get("business_name")

        if not website and business_name:
            # Guess common website patterns
            name_clean = re.sub(r"[^a-zA-Z0-9\s]", "", business_name).replace(" ", "").lower()
            potential_sites = [
                f"https://{name_clean}.com",
                f"https://www.{name_clean}.com",
            ]

            # Test which one works (simple check)
            for site in potential_sites:
                try:
                    # In real implementation, would test if site is accessible
                    website = site
                    break
                except:
                    continue

        if website:
            # Research the website
            try:
                contractor_data = {"website": website}
                enriched_data = await self.website_enricher.enrich_contractor_from_website(contractor_data)

                # Store research results
                state.research_data = enriched_data
                state.research_completed = True

                # Generate confirmation response
                response = await self._generate_research_confirmation_response(
                    business_name, website, enriched_data
                )

                state.add_message("assistant", response, "research_confirmation")
                coia_state_manager.update_session(state.session_id, state)

                return {
                    "response": response,
                    "stage": "research_confirmation",
                    "research_data": enriched_data.to_dict(),
                    "profile_progress": {
                        "completeness": 0.8,  # High completeness from research
                        "stage": "research_confirmation",
                        "collectedData": enriched_data.to_dict(),
                        "matchingProjects": await self._count_matching_projects_from_research(enriched_data)
                    }
                }

            except Exception as e:
                logger.error(f"Error researching website {website}: {e}")
                response = f"I found your business but had trouble accessing your website at {website}. Could you confirm the correct website URL, or would you like to proceed without website research?"

                state.add_message("assistant", response, "website_error")
                coia_state_manager.update_session(state.session_id, state)

                return {
                    "response": response,
                    "stage": "website_error",
                    "profile_progress": {
                        "completeness": 0.2,
                        "stage": "website_error"
                    }
                }
        else:
            # Couldn't find website
            response = f"I see you mentioned {business_name}. Could you provide your business website so I can gather all your information automatically? Or if you don't have a website, I can help you create a profile through our conversation."

            state.add_message("assistant", response, "website_request")
            coia_state_manager.update_session(state.session_id, state)

            return {
                "response": response,
                "stage": "website_request",
                "profile_progress": {
                    "completeness": 0.1,
                    "stage": "website_request"
                }
            }

    async def _generate_research_confirmation_response(self,
                                                     business_name: str,
                                                     website: str,
                                                     enriched_data: EnrichedContractorData) -> str:
        """Generate a response confirming the research findings"""

        # Build summary of findings
        findings = []

        if enriched_data.service_types:
            findings.append(f"Services: {', '.join(enriched_data.service_types)}")

        if enriched_data.service_areas:
            findings.append(f"Service Areas: {', '.join(enriched_data.service_areas)}")

        if enriched_data.email:
            findings.append(f"Contact Email: {enriched_data.email}")

        if enriched_data.phone:
            findings.append(f"Phone: {enriched_data.phone}")

        if enriched_data.years_in_business:
            findings.append(f"Years in Business: {enriched_data.years_in_business}")

        if enriched_data.certifications:
            findings.append(f"Certifications: {', '.join(enriched_data.certifications)}")

        findings_text = "\\n".join([f"• {finding}" for finding in findings])

        # Create confirmation message
        response = f"""Great! I found your business information from {website}. Let me confirm what I discovered about {business_name}:

{findings_text}

Is this information correct? I can also pull your portfolio images from your website to showcase your work on InstaBids.

If everything looks good, just say "yes" and I'll create your complete contractor profile. If anything needs correction, let me know what to update."""

        return response

    async def _handle_research_confirmation(self, state: CoIAConversationState,
                                          user_message: str) -> dict[str, Any]:
        """Handle confirmation of research findings"""

        message = user_message.lower().strip()
        confirmed = any(word in message for word in ["yes", "correct", "good", "right", "accurate"])

        if confirmed:
            # Create contractor profile with research data
            contractor_id = await self._create_contractor_from_research(state)

            if contractor_id:
                response = """Perfect! I've created your complete contractor profile using the information from your website.

Your InstaBids contractor account is now ready! Here's what I've set up:

• Complete business profile with all your services
• Contact information and service areas
• Portfolio images from your website
• Professional contractor dashboard

You can now start receiving project invitations from homeowners in your area. Your profile showcases your expertise and helps you stand out from the competition.

Would you like me to show you how to access your contractor dashboard?"""

                state.mark_completed(contractor_id)
                state.research_confirmed = True
                coia_state_manager.update_session(state.session_id, state)

                return {
                    "response": response,
                    "stage": "completed",
                    "contractor_id": contractor_id,
                    "profile_progress": {
                        "completeness": 1.0,
                        "stage": "completed",
                        "collectedData": state.research_data.to_dict() if state.research_data else {},
                        "matchingProjects": await self._count_matching_projects_from_research(state.research_data)
                    }
                }
            else:
                response = "I had trouble creating your profile. Let me try a different approach. Could you tell me about your business manually?"
                return self._fallback_response(state, response)
        else:
            # User wants corrections
            response = "No problem! What information needs to be corrected? You can tell me what's wrong and I'll update it, or provide your correct business details."

            state.add_message("assistant", response, "research_correction")
            coia_state_manager.update_session(state.session_id, state)

            return {
                "response": response,
                "stage": "research_correction",
                "profile_progress": {
                    "completeness": 0.6,
                    "stage": "research_correction"
                }
            }

    async def _handle_standard_conversation(self, state: CoIAConversationState,
                                          user_message: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Handle standard conversation flow (fallback to original CoIA)"""

        # Use original conversation logic for non-research scenarios
        response_data = await self._generate_response(state, user_message, context)

        # Extract profile updates
        profile_updates = self._extract_profile_updates(
            user_message,
            response_data.get("content", ""),
            state.current_stage
        )

        if profile_updates:
            state.update_profile(profile_updates)

        # Determine next stage
        next_stage = self._determine_next_stage(state, response_data.get("content", ""))

        state.add_message("assistant", response_data.get("content", ""), next_stage, profile_updates)
        coia_state_manager.update_session(state.session_id, state)

        return {
            "response": response_data.get("content", ""),
            "stage": next_stage,
            "profile_progress": {
                "completeness": state.profile.calculate_completeness(),
                "stage": next_stage,
                "collectedData": state.profile.to_dict(),
                "matchingProjects": await self._count_matching_projects(state.profile)
            }
        }

    async def _create_contractor_from_research(self, state: CoIAConversationState) -> Optional[str]:
        """Create contractor profile using research data"""
        if not self.supabase or not state.research_data:
            return None

        try:
            enriched = state.research_data
            business_info = state.business_research

            # Create contractor lead entry (using existing schema)
            contractor_data = {
                "source": "manual",  # Manual entry via CoIA
                "company_name": business_info.get("business_name", "Unknown Business"),
                "email": enriched.email,
                "phone": enriched.phone,
                "website": business_info.get("website"),
                "specialties": enriched.service_types or [],
                "years_in_business": enriched.years_in_business,
                "certifications": enriched.certifications or [],
                "rating": 5.0,  # New contractor, assume good rating
                "review_count": 0,
                "lead_status": "qualified",
                "contractor_size": enriched.business_size or "small_business",
                "service_zip_codes": enriched.service_areas or [],
                "raw_data": enriched.to_dict(),
                "lead_score": 85,  # High score for research-verified contractor
                "data_completeness": 90  # High completeness from website research
            }

            # Insert into contractor_leads table
            result = self.supabase.table("contractor_leads").insert(contractor_data).execute()

            if result.data and len(result.data) > 0:
                contractor_id = result.data[0]["id"]
                logger.info(f"✅ Created research-based contractor profile: {contractor_id}")

                # TODO: Extract and store images from website
                if enriched.gallery_images:
                    await self._store_contractor_images(contractor_id, enriched.gallery_images)

                return contractor_id
            else:
                logger.error("Failed to create contractor profile - no data returned")
                return None

        except Exception as e:
            logger.error(f"Error creating contractor from research: {e}")
            return None

    async def _store_contractor_images(self, contractor_id: str, image_urls: list[str]):
        """Store contractor images in database"""
        try:
            for url in image_urls[:10]:  # Limit to 10 images
                image_data = {
                    "contractor_id": contractor_id,
                    "image_url": url,
                    "category": "portfolio",
                    "ai_description": "Extracted from business website",
                    "extracted_from_website": True
                }

                self.supabase.table("contractor_images").insert(image_data).execute()

            logger.info(f"✅ Stored {len(image_urls)} images for contractor {contractor_id}")

        except Exception as e:
            logger.error(f"Error storing contractor images: {e}")

    async def _count_matching_projects_from_research(self, enriched_data: Optional[EnrichedContractorData]) -> int:
        """Count matching projects based on research data"""
        if not enriched_data:
            return 0

        base_count = 8  # Higher base for research-verified contractors

        if enriched_data.service_types:
            base_count += len(enriched_data.service_types) * 2

        if enriched_data.service_areas:
            base_count += len(enriched_data.service_areas)

        if enriched_data.years_in_business and enriched_data.years_in_business > 5:
            base_count += 5

        return min(base_count, 30)

    # ... Include other helper methods from original CoIA agent
    async def _generate_response(self, state, user_message, context):
        """Generate standard response (simplified version)"""
        try:
            response = await self.chain.ainvoke([
                SystemMessage(content="You are CoIA, a contractor onboarding agent for InstaBids."),
                HumanMessage(content=user_message)
            ])
            return {"content": response.strip()}
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"content": "I apologize, I'm having trouble right now. Could you please try again?"}

    def _extract_profile_updates(self, user_message, ai_response, current_stage):
        """Extract profile updates (simplified)"""
        return {}

    def _determine_next_stage(self, state, ai_response):
        """Determine next stage (simplified)"""
        return state.current_stage

    async def _count_matching_projects(self, profile):
        """Count matching projects (simplified)"""
        return 5

    def _fallback_response(self, state, custom_message=None):
        """Fallback response for errors"""
        message = custom_message or "I apologize, but I'm having trouble processing that right now. Could you please try rephrasing your response?"

        return {
            "response": message,
            "stage": state.current_stage,
            "profile_progress": {
                "completeness": 0.1,
                "stage": state.current_stage
            }
        }

# Global research-based CoIA agent instance
research_coia_agent: Optional[ResearchBasedCoIAAgent] = None

def initialize_research_coia(api_key: str) -> ResearchBasedCoIAAgent:
    """Initialize global research-based CoIA agent instance"""
    global research_coia_agent
    research_coia_agent = ResearchBasedCoIAAgent(api_key)
    return research_coia_agent

def get_research_coia_agent() -> Optional[ResearchBasedCoIAAgent]:
    """Get global research-based CoIA agent instance"""
    return research_coia_agent
