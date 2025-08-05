"""
JAA Routes - Job Assessment Agent API Endpoints
Owner: Agent 2 (Backend Core)
"""

from typing import Optional

from fastapi import APIRouter, HTTPException

# Import JAA agent
from agents.jaa.agent import JobAssessmentAgent


# Create router
router = APIRouter()

# Global JAA agent instance (initialized in main.py)
jaa_agent: Optional[JobAssessmentAgent] = None

def set_jaa_agent(agent: JobAssessmentAgent):
    """Set the JAA agent instance"""
    global jaa_agent
    jaa_agent = agent

@router.post("/process/{thread_id}")
async def process_with_jaa(thread_id: str):
    """Process CIA conversation with JAA to generate bid card"""
    if not jaa_agent:
        raise HTTPException(500, "JAA agent not initialized")

    try:
        result = jaa_agent.process_conversation(thread_id)

        if result["success"]:
            return {
                "success": True,
                "bid_card_number": result["bid_card_number"],
                "bid_card_data": result["bid_card_data"],
                "cia_thread_id": result["cia_thread_id"],
                "database_id": result["database_id"]
            }
        else:
            raise HTTPException(500, result.get("error", "Unknown error processing conversation"))

    except Exception as e:
        print(f"[JAA API ERROR] {e}")
        raise HTTPException(500, f"JAA processing failed: {e!s}")
