import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Reuse existing DeepAgents sync wrappers and tool instance
from ..deepagents_tools import research_business as _research_business, build_profile as _build_profile
import anyio

def research_company_basic(company_name: str, location: Optional[str] = None) -> Dict[str, Any]:
    """
    Research subagent tool:
    - Returns comprehensive contractor research data (google + tavily + extraction + social + BI)
    - Wraps coia_tools.web_search_company via DeepAgents wrapper (sync)
    """
    try:
        result = _research_business(company_name, location)
        logger.info(f"[landing][subagent=research] research_company_basic company={company_name} "
                    f"tavily_used={ 'tavily_discovery' in (result.get('data_sources') or []) } "
                    f"success_keys={list(result.keys())[:6] if isinstance(result, dict) else 'not_dict'}")
        return result if isinstance(result, dict) else {"error": "unexpected_result_type"}
    except Exception as e:
        logger.warning(f"[landing][subagent=research] research_company_basic error: {e}")
        return {"error": str(e), "company_name": company_name, "data_sources": []}


def extract_contractor_profile(company_name: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Research subagent tool:
    - Takes raw research data (184K chars) and uses GPT-4o to extract all 66 contractor fields
    - Includes intelligent synthesis for summary fields, USPs, competitive advantages
    - Returns structured profile ready for staging
    """
    try:
        logger.info(f"[landing][subagent=research] extract_profile starting for {company_name}")
        
        # Extract the different data components from research
        google_data = research_data.get('google_data', {})
        web_data = {
            'tavily_discovery': research_data.get('tavily_discovery_data', {}),
            'website_data': research_data.get('website_data', {}),
            'social_media': research_data.get('social_media_data', {}),
            'extracted_info': research_data.get('extracted_info', {})
        }
        license_data = research_data.get('license_data', {})
        
        # Call build_contractor_profile which uses GPT-4o for intelligent extraction
        profile = _build_profile(company_name, google_data, web_data, license_data)
        
        # Log what we extracted
        fields_extracted = len([k for k, v in profile.items() if v])
        logger.info(f"[landing][subagent=research] extract_profile completed - "
                   f"extracted {fields_extracted} fields with GPT-4o intelligence")
        
        # Add extraction metadata
        profile['extraction_method'] = 'gpt-4o-intelligent'
        profile['fields_extracted'] = fields_extracted
        profile['data_sources_used'] = research_data.get('data_sources', [])
        
        return profile
        
    except Exception as e:
        logger.error(f"[landing][subagent=research] extract_profile error: {e}")
        return {
            "error": str(e), 
            "company_name": company_name,
            "extraction_failed": True
        }


def stage_profile(profile: Dict[str, Any], contractor_lead_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Research subagent tool:
    - Stages (upserts) a contractor profile into potential_contractors
    - Uses coia_tools.save_potential_contractor (async) with optional post-verify read-back
    Returns:
      { "success": bool, "staging_id": "...", "company_name": "..." }
    """
    try:
        # Prefer a stable id for staging if provided
        if contractor_lead_id and "id" not in profile and "contractor_lead_id" not in profile:
            profile["contractor_lead_id"] = contractor_lead_id

        # Async bridge to existing async tool
        from ..deepagents_tools import coia_tools  # global instance

        async def _call():
            return await coia_tools.save_potential_contractor(profile)

        out = anyio.run(_call)
        ok = bool(out.get("success"))
        staging_id = out.get("staging_id")
        logger.info(f"[landing][subagent=research] stage_profile success={ok} staging_id={staging_id} "
                    f"company={out.get('company_name', profile.get('company_name') or profile.get('business_name'))}")

        # Optional: verify row exists (best-effort; do not fail flow)
        try:
            if staging_id:
                import sys, os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                from database_simple import db  # type: ignore
                verify = db.client.table("potential_contractors").select("id").eq("id", staging_id).execute()
                if getattr(verify, "data", None):
                    logger.info(f"[landing][subagent=research] stage_profile verify_ok id={staging_id}")
                else:
                    logger.warning(f"[landing][subagent=research] stage_profile verify_miss id={staging_id}")
        except Exception as verr:
            logger.debug(f"[landing][subagent=research] stage_profile verify skipped: {verr}")

        return out
    except Exception as e:
        logger.exception("[landing][subagent=research] stage_profile error")
        return {"success": False, "error": str(e)}
