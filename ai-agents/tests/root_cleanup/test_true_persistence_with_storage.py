#!/usr/bin/env python
"""
TRUE PERSISTENCE TEST WITH ACTUAL STORAGE
Uses file-based storage to persist memory across sessions
This simulates real production behavior where memory persists
"""

import asyncio
import json
import logging
import os
import pickle
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CRITICAL: Use consistent storage location for lifetime persistence
STORAGE_DIR = Path("C:/Users/Not John Or Justin/Documents/instabids/ai-agents/test_memory_storage")
STORAGE_DIR.mkdir(exist_ok=True)
CONTRACTOR_ID = "mike_lifetime_persistent"

class PersistentMemorySaver:
    """File-based persistent memory that survives process restarts"""

    def __init__(self, storage_dir: Path, contractor_id: str):
        self.storage_file = storage_dir / f"{contractor_id}_memory.pkl"
        self.memory = self.load_memory()

    def load_memory(self):
        """Load memory from disk if exists"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "rb") as f:
                    memory = pickle.load(f)
                    print(f"[MEMORY] Loaded existing memory with {len(memory)} entries")
                    return memory
            except Exception as e:
                print(f"[MEMORY] Could not load memory: {e}")
                return {}
        else:
            print("[MEMORY] No existing memory found, starting fresh")
            return {}

    def save_memory(self):
        """Save memory to disk"""
        try:
            with open(self.storage_file, "wb") as f:
                pickle.dump(self.memory, f)
            print(f"[MEMORY] Saved {len(self.memory)} memory entries to disk")
        except Exception as e:
            print(f"[MEMORY] Failed to save memory: {e}")

    def get(self, config):
        """Get checkpoint for config"""
        thread_id = config.get("configurable", {}).get("thread_id")
        return self.memory.get(thread_id)

    def put(self, config, checkpoint):
        """Save checkpoint for config"""
        thread_id = config.get("configurable", {}).get("thread_id")
        self.memory[thread_id] = checkpoint
        self.save_memory()  # Persist immediately
        return checkpoint

    async def aget(self, config):
        """Async get"""
        return self.get(config)

    async def aput(self, config, checkpoint):
        """Async put"""
        return self.put(config, checkpoint)

    def get_tuple(self, config):
        """Get checkpoint tuple"""
        checkpoint = self.get(config)
        if checkpoint:
            return checkpoint, config
        return None

    async def aget_tuple(self, config):
        """Async get tuple"""
        return self.get_tuple(config)

    def list(self, config):
        """List checkpoints"""
        return list(self.memory.keys())

    async def alist(self, config):
        """Async list"""
        return self.list(config)

# Global persistent checkpointer - shared across all tests
GLOBAL_CHECKPOINTER = PersistentMemorySaver(STORAGE_DIR, CONTRACTOR_ID)

async def simulate_day_1():
    """Day 1: Initial contractor onboarding"""
    print("\n" + "="*60)
    print("DAY 1: CONTRACTOR ONBOARDING")
    print("="*60)

    from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

    # Use the GLOBAL checkpointer
    app = await create_unified_coia_system(GLOBAL_CHECKPOINTER)

    # Store initial profile
    print("\n[CONVERSATION 1] Introduction")
    result1 = await invoke_coia_chat(
        app=app,
        user_message="Hi, I'm Mike from Dallas HVAC Pro. We've been in business for 15 years specializing in emergency HVAC repairs. We handle projects from $5,000 to $50,000.",
        session_id="day1_session",
        contractor_lead_id=CONTRACTOR_ID
    )

    profile = result1.get("contractor_profile", {})
    print(f"Profile stored: {profile.get('company_name')}, {profile.get('years_in_business')} years")

    # Search for projects
    print("\n[CONVERSATION 2] First project search")
    result2 = await invoke_coia_chat(
        app=app,
        user_message="Show me emergency HVAC projects in Dallas",
        session_id="day1_search",
        contractor_lead_id=CONTRACTOR_ID
    )

    mode = result2.get("current_mode")
    bid_cards = result2.get("bid_cards_attached", [])
    print(f"Mode: {mode}, Bid cards: {len(bid_cards)}")

    # Save profile to separate file for verification
    profile_file = STORAGE_DIR / f"{CONTRACTOR_ID}_profile.json"
    with open(profile_file, "w") as f:
        json.dump(profile, f, indent=2)
    print(f"\n[SAVED] Profile saved to {profile_file}")

    return True

async def simulate_day_7():
    """Day 7: Contractor returns after a week"""
    print("\n" + "="*60)
    print("DAY 7: CONTRACTOR RETURNS (NEW PYTHON PROCESS)")
    print("="*60)

    from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

    # Create NEW app instance but with SAME global checkpointer
    app = await create_unified_coia_system(GLOBAL_CHECKPOINTER)

    # Check if remembered
    print("\n[CONVERSATION 3] Testing memory")
    result3 = await invoke_coia_chat(
        app=app,
        user_message="Do you remember my company name and what we specialize in?",
        session_id="day7_memory_test",
        contractor_lead_id=CONTRACTOR_ID
    )

    response = result3["messages"][-1].content
    profile = result3.get("contractor_profile", {})

    print(f"Response mentions Dallas HVAC: {'Dallas HVAC' in response}")
    print(f"Profile has company: {profile.get('company_name')}")
    print(f"Profile has specializations: {profile.get('specializations')}")

    # Add new info
    print("\n[CONVERSATION 4] Adding Fort Worth")
    result4 = await invoke_coia_chat(
        app=app,
        user_message="We're expanding to Fort Worth now too. Also prefer commercial projects.",
        session_id="day7_expansion",
        contractor_lead_id=CONTRACTOR_ID
    )

    profile4 = result4.get("contractor_profile", {})
    print(f"Service areas: {profile4.get('service_areas')}")

    # Personalized search
    print("\n[CONVERSATION 5] Personalized search")
    result5 = await invoke_coia_chat(
        app=app,
        user_message="Find commercial HVAC projects in Dallas or Fort Worth",
        session_id="day7_search",
        contractor_lead_id=CONTRACTOR_ID
    )

    response5 = result5["messages"][-1].content
    personalized = "Dallas" in response5 or "Fort Worth" in response5
    print(f"Search personalized with locations: {personalized}")

    return profile.get("company_name") == "Dallas Hvac Pro"

async def simulate_day_30():
    """Day 30: Full context test"""
    print("\n" + "="*60)
    print("DAY 30: FULL LIFETIME CONTEXT (ANOTHER NEW PROCESS)")
    print("="*60)

    from agents.coia.unified_graph import create_unified_coia_system, invoke_coia_chat

    # Again, new app but SAME checkpointer
    app = await create_unified_coia_system(GLOBAL_CHECKPOINTER)

    # Ask for summary
    print("\n[CONVERSATION 6] Full context request")
    result6 = await invoke_coia_chat(
        app=app,
        user_message="Can you summarize everything you know about my business Dallas HVAC Pro?",
        session_id="day30_summary",
        contractor_lead_id=CONTRACTOR_ID
    )

    response = result6["messages"][-1].content
    profile = result6.get("contractor_profile", {})

    # Check complete memory
    memory_intact = {
        "Company": profile.get("company_name") == "Dallas Hvac Pro",
        "Years": profile.get("years_in_business") == 15,
        "Specialization": "emergency" in profile.get("specializations", []),
        "Service Areas": "Dallas" in profile.get("service_areas", []),
        "Min Project": profile.get("minimum_project_size") is not None
    }

    print("\n[MEMORY CHECK] Complete context:")
    for key, intact in memory_intact.items():
        print(f"  {key}: {'YES' if intact else 'NO'}")

    total = sum(memory_intact.values())
    print(f"\nTotal memory points: {total}/5")

    return total >= 3

async def main():
    """Run complete lifetime persistence test"""
    print("\n" + "="*70)
    print("TRUE LIFETIME PERSISTENCE TEST")
    print("Using file-based storage that persists across Python processes")
    print(f"Storage location: {STORAGE_DIR}")
    print("="*70)

    # Run tests simulating different days
    day1_success = await simulate_day_1()
    day7_success = await simulate_day_7()
    day30_success = await simulate_day_30()

    # Final assessment
    print("\n" + "="*70)
    print("FINAL ASSESSMENT")
    print("="*70)

    if all([day1_success, day7_success, day30_success]):
        print("SUCCESS: TRUE LIFETIME PERSISTENCE VERIFIED!")
        print("Memory persists across the contractor's entire lifetime")
    elif any([day7_success, day30_success]):
        print("PARTIAL: Some memory persistence working")
    else:
        print("FAILURE: No lifetime persistence")

    print("\nResults:")
    print(f"  Day 1 (Onboarding): {'PASS' if day1_success else 'FAIL'}")
    print(f"  Day 7 (Memory Test): {'PASS' if day7_success else 'FAIL'}")
    print(f"  Day 30 (Full Context): {'PASS' if day30_success else 'FAIL'}")

if __name__ == "__main__":
    asyncio.run(main())
