"""
DeepAgents tool wrappers for COIA.

These are synchronous callables that wrap our existing async COIA tools so they can be
registered with deepagents.create_deep_agent as plain Python functions.

All real implementations are delegated to ai-agents/agents/coia/tools.py (coia_tools)
and adapters where appropriate. This module contains zero business logic.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Import the tool-of-record (async methods)
from .tools import COIATools
coia_tools = COIATools()


def _run_async(coro_func, *args, **kwargs):
    """
    Run an async function in a synchronous context using anyio.
    DeepAgents expects sync callables; our underlying tools are async.
    """
    try:
        import anyio
        return anyio.run(coro_func, *args, **kwargs)
    except Exception as e:
        logger.exception("Error running async tool via anyio.run")
        raise e


# --------------- Public sync tools (registered in deepagents) ---------------

def extract_company_info(text: str) -> Dict[str, Any]:
    """
    Minimal extractor for company hints from free text.
    Prefer the agent LLM to refine, this is only to seed an initial name.

    Returns: {"company_name": str, "location_hint": str}
    """
    logger.info(f"🔍 [IDENTITY-AGENT] FIRED - Extracting from: '{text[:50]}...'")
    try:
        text = (text or "").strip()
        # Extremely conservative heuristic: first line as name
        name = (text.splitlines()[0] if "\n" in text else text)[:120]
        # crude location hint from common patterns
        location_hint = ""
        # Examples: "in Fort Lauderdale", "at Miami", ", FL"
        lowered = text.lower()
        for marker in [" in ", " at ", ", "]:
            if marker in lowered:
                try:
                    # take a small slice after marker
                    location_hint = text.lower().split(marker, 1)[1][:60].strip()
                except Exception:
                    pass
                break
        result = {"company_name": name, "location_hint": location_hint}
        logger.info(f"✅ [IDENTITY-AGENT] SUCCESS - Extracted: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ [IDENTITY-AGENT] ERROR - {e}")
        return {"company_name": "", "location_hint": ""}


def research_business(company_name: str, location: Optional[str] = None) -> Dict[str, Any]:
    """
    Wrap coia_tools.web_search_company → returns structured research data.
    """
    logger.info(f"🔬 [RESEARCH-AGENT] FIRED - Researching: '{company_name}' in '{location}'")
    try:
        result = _run_async(coia_tools.web_search_company, company_name, location)
        completeness = result.get('completeness', 0) if isinstance(result, dict) else 0
        logger.info(f"✅ [RESEARCH-AGENT] SUCCESS - Found {completeness}% data completeness")
        return result
    except Exception as e:
        logger.error(f"❌ [RESEARCH-AGENT] ERROR - {e}")
        raise


def build_profile(
    company_name: str,
    google_data: Optional[Dict[str, Any]] = None,
    web_data: Optional[Dict[str, Any]] = None,
    license_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Wrap coia_tools.build_contractor_profile → returns a 66-field profile.
    DB writes are gated by WRITE_LEADS_ON_RESEARCH env flag inside the tool.
    """
    return _run_async(coia_tools.build_contractor_profile, company_name, google_data, web_data, license_data)


def create_contractor_account(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrap coia_tools.create_contractor_account → authoritative contractors insert.
    """
    company_name = profile.get('company_name', 'Unknown')
    logger.info(f"👤 [ACCOUNT-AGENT] FIRED - Creating contractor account for: '{company_name}'")
    try:
        result = _run_async(coia_tools.create_contractor_account, profile)
        contractor_id = result.get('id', 'None')
        logger.info(f"✅ [ACCOUNT-AGENT] SUCCESS - Created contractor account ID: {contractor_id}")
        return result
    except Exception as e:
        logger.error(f"❌ [ACCOUNT-AGENT] ERROR - {e}")
        raise


def save_potential_contractor(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrap coia_tools.save_potential_contractor → stage profile in potential_contractors.
    Used by Landing research-agent before promotion to contractors.
    """
    logger.info(f"💾 [RESEARCH-AGENT] FIRED - Staging contractor profile for: '{profile.get('company_name', 'Unknown')}'")
    try:
        result = _run_async(coia_tools.save_potential_contractor, profile)
        logger.info(f"✅ [RESEARCH-AGENT] SUCCESS - Staged profile, ID: {result.get('id', 'None')}")
        return result
    except Exception as e:
        logger.error(f"❌ [RESEARCH-AGENT] ERROR - Failed to stage profile: {e}")
        raise


def search_bid_cards(contractor_profile: Dict[str, Any], location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Wrap coia_tools.search_bid_cards → adapter-backed privacy-aware projects.
    """
    company_name = contractor_profile.get('company_name', 'Unknown')
    logger.info(f"📋 [PROJECTS-AGENT] FIRED - Searching projects for: '{company_name}' near '{location}'")
    try:
        result = _run_async(coia_tools.search_bid_cards, contractor_profile, location)
        project_count = len(result) if isinstance(result, list) else 0
        logger.info(f"✅ [PROJECTS-AGENT] SUCCESS - Found {project_count} matching projects")
        return result
    except Exception as e:
        logger.error(f"❌ [PROJECTS-AGENT] ERROR - {e}")
        raise


def collect_radius_preferences(radius_miles: int, services: List[str], contractor_lead_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool for RADIUS-AGENT to collect service area and service types.
    Updates the staged contractor profile with radius and services.
    """
    logger.info(f"📍 [RADIUS-AGENT] FIRED - Setting radius: {radius_miles} miles, services: {services}")
    try:
        # For now, just return the collected data
        # In future, this could update the potential_contractors record
        result = {
            "radius_miles": radius_miles,
            "services": services,
            "contractor_lead_id": contractor_lead_id,
            "radius_set": True,
            "services_count": len(services)
        }
        logger.info(f"✅ [RADIUS-AGENT] SUCCESS - Collected {len(services)} services with {radius_miles} mile radius")
        return result
    except Exception as e:
        logger.error(f"❌ [RADIUS-AGENT] ERROR - {e}")
        return {"radius_set": False, "error": str(e)}


def get_contractor_context(contractor_lead_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Synchronous wrapper around the ContractorContextAdapter to preload context
    (profile, bid history, available projects, conversation history).
    """
    try:
        import os
        import sys
        # Add repo root for adapter import resolution if needed
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from adapters.contractor_context import ContractorContextAdapter  # type: ignore

        adapter = ContractorContextAdapter()
        ctx = adapter.get_contractor_context(contractor_lead_id, session_id)
        return ctx or {}
    except Exception as e:
        logger.warning(f"get_contractor_context failed: {e}")
        return {}
