"""
Landing Onboarding DeepAgent for COIA

Creates a DeepAgents-powered agent focused on the unauthenticated landing page flow:
- Extract company hints from free text
- Perform fast, real research (Tavily/GPT via coia_tools.web_search_company)
- Optionally build initial profile (writes gated by WRITE_LEADS_ON_RESEARCH)
- Ask for explicit consent before creating a contractor account
- Return structured fields and provenance notes
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from deepagents import create_deep_agent
except Exception as _e:  # Do not crash import-time
    create_deep_agent = None  # type: ignore

from .subagents.identity_agent import extract_company_info, validate_company_exists
from .subagents.research_agent import research_company_basic, extract_contractor_profile, stage_profile
from .subagents.radius_agent import update_preferences
from .subagents.projects_agent import find_matching_projects
from .subagents.account_agent import create_account_from_staging

logger = logging.getLogger(__name__)

_agent = None  # cached instance


def _instructions() -> str:
    """
    System prompt for Landing Onboarding Agent.
    """
    return """
You are COIA (Landing Onboarding), the Contractor Onboarding Intelligence Agent.

CRITICAL MEMORY MANAGEMENT:
- You have access to conversation context from previous interactions
- Check context for: staging_id, company_name, contractor_profile, services_preferences
- If staging_id exists in context, use it for radius and project operations
- Always preserve staging_id when calling stage_profile

Operate as a coordinator that DELEGATES to subagents:
- identity-agent: extract/confirm business footprint (minimal lookup only)
- research-agent: perform verified research and stage profile data
- radius-agent: collect services/radius preferences (PASS staging_id if available)
- projects-agent: show preview opportunities on request (USE staging_id if available)
- account-agent: create accounts ONLY after explicit consent (promotion step)

Your job:
- Extract company details from free text (delegate minimal lookup to identity-agent)
- When company is confirmed, perform REAL research (delegate to research-agent) to obtain verified data
- Return structured fields first: phone, email, website, services, years_in_business
- Provide brief provenance (how data was found), avoid hallucination
- Build/stage profile data (potential_contractors) via research-agent; do NOT promote yet
- CRITICAL: Save staging_id from stage_profile response for future operations
- When user asks to update radius or find projects, use the saved staging_id
- NEVER create an account without explicit consent; only account-agent may call create_contractor_account
- After successful creation, communicate that the account exists (contractor_created=true) and that staging was promoted

Rules:
- Prefer real data from research; if unknown, return "unknown" rather than making it up
- Keep initial responses fast; offer deeper research when the user requests it
- If the user asks for projects, delegate to projects-agent (search_bid_cards helper)

Outputs:
- Always surface: phone, email, website, services, years_in_business when available
- Mention data provenance (e.g., "Found on company website/about page" or "Google Business listing")
- Keep messages concise and production-grade
"""


def get_agent() -> Any:
    """
    Returns a cached DeepAgents agent instance for the landing flow.
    Safe to call repeatedly.
    """
    global _agent
    if _agent is not None:
        return _agent

    if create_deep_agent is None:
        raise RuntimeError(
            "deepagents is not installed or import failed. "
            "Install with `pip install deepagents` and ensure environment is configured."
        )

    tools = [
        extract_company_info,          # identity
        validate_company_exists,       # identity minimal confirmation
        research_company_basic,        # research - get raw data
        extract_contractor_profile,    # research - GPT-4o intelligent extraction
        stage_profile,                 # research → potential_contractors
        update_preferences,            # radius
        find_matching_projects,        # projects
        create_account_from_staging,   # account promotion
    ]

    # Subagents: identity, research, radius, projects, account
    identity_subagent = {
        "name": "identity-agent",
        "description": "Extract and confirm the business footprint from free text.",
        "prompt": (
            "You extract/confirm the business name and minimal footprint (address/phone/website). "
            "Use extract_company_info for parsing, and research_business ONLY to fetch a minimal confirmation card. "
            "Do not run deep research or staging here."
        ),
    }

    research_subagent = {
        "name": "research-agent",
        "description": "Perform verified research and stage profile data (potential_contractors).",
        "prompt": (
            "CRITICAL WORKFLOW - YOU MUST FOLLOW THIS EXACTLY:\n"
            "1. Use research_company_basic to gather raw research data (Google, Tavily, website extraction)\n"
            "2. Use extract_contractor_profile to intelligently extract all 66 fields using GPT-4o\n"
            "   - This extracts phone, email, website, services, years_in_business\n"
            "   - Plus intelligent fields like USPs, competitive advantages, business summaries\n"
            "3. Use stage_profile to save the extracted profile to potential_contractors\n"
            "Build comprehensive profiles with real data. NO hallucination. NO fallback data.\n"
            "Do NOT create accounts here; wait for explicit consent handled by account-agent."
        ),
    }

    radius_subagent = {
        "name": "radius-agent",
        "description": "Collect services/radius preferences and update staged profile.",
        "prompt": (
            "Collect search radius (10/25/50 miles) and additional services. "
            "CRITICAL: Use the staging_id from context when calling update_preferences. "
            "The staging_id should be available from previous stage_profile calls. "
            "Update the staged profile accordingly. Keep interactions short and clear."
        ),
    }

    projects_subagent = {
        "name": "projects-agent",
        "description": "Preview matching projects on request.",
        "prompt": (
            "On user request, use search_bid_cards with the staged profile and preferences. "
            "Present a concise preview list with rationale. Full details after signup is acceptable."
        ),
    }

    account_subagent = {
        "name": "account-agent",
        "description": "Create contractor account only after explicit consent (promotion step).",
        "prompt": (
            "ONLY proceed if the user explicitly consents to account creation. "
            "Use create_contractor_account to promote the staged profile into the contractors table. "
            "On success set contractor_created=true and return normalized account data. "
            "Ensure staging is marked converted (e.g., store promoted_contractor_id)."
        ),
    }

    _agent = create_deep_agent(
        tools=tools,
        instructions=_instructions(),
        subagents=[identity_subagent, research_subagent, radius_subagent, projects_subagent, account_subagent],
    )
    logger.info("Landing DeepAgent created")
    return _agent


# Usage example (caller responsibility):
# agent = get_agent()
# result = agent.invoke({"messages": [{"role": "user", "content": "I run JM Holiday Lighting in Fort Lauderdale"}]})
# The router should wrap this with state restore/save as needed.
