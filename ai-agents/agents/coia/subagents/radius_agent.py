import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def update_preferences(
    identifier: str,
    services: Optional[Union[List[str], str]] = None,
    radius_miles: Optional[int] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Radius subagent tool:
    - Updates staged profile preferences in potential_contractors
    - identifier should be the staging id (preferred) or contractor_lead_id used as id during staging
    - services may be a list or a single string
    - radius_miles updates search_radius_miles
    - optional city/state/zip_code update basic location metadata

    Returns:
      { "success": bool, "updated_fields": {...}, "id": identifier }
    """
    try:
        import os
        import sys
        from datetime import datetime

        # Normalize services to list
        if isinstance(services, str) and services.strip():
            services = [services.strip()]
        if services is None:
            services = []

        # Prepare update payload
        payload: Dict[str, Any] = {"updated_at": datetime.utcnow().isoformat()}
        if services:
            payload["services"] = services
        if isinstance(radius_miles, int):
            payload["search_radius_miles"] = radius_miles
        if city:
            payload["city"] = city
        if state:
            payload["state"] = state
        if zip_code:
            payload["zip_code"] = zip_code

        if len(payload) == 1:  # only updated_at present
            logger.info("[landing][subagent=radius] No preference fields provided to update")
            return {"success": True, "updated_fields": {}, "id": identifier}

        # DB client
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from database_simple import db  # type: ignore

        # Update by id
        result = (
            db.client
            .table("potential_contractors")
            .update(payload)
            .eq("id", identifier)
            .execute()
        )

        # Verify update (best effort)
        verify = (
            db.client
            .table("potential_contractors")
            .select("id, services, search_radius_miles, city, state, zip_code")
            .eq("id", identifier)
            .execute()
        )

        if getattr(verify, "data", None):
            logger.info(f"[landing][subagent=radius] preferences updated id={identifier} fields={list(payload.keys())}")
            return {
                "success": True,
                "updated_fields": payload,
                "id": identifier,
                "current": verify.data[0],
            }

        logger.warning(f"[landing][subagent=radius] update verify_miss id={identifier}")
        return {"success": True, "updated_fields": payload, "id": identifier}

    except Exception as e:
        logger.exception("[landing][subagent=radius] update_preferences error")
        return {"success": False, "error": str(e), "id": identifier}
