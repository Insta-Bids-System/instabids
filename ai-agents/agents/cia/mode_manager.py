"""
CIA Mode Manager - Switches between conversation and action modes
"""
from enum import Enum
from typing import Any, Optional


class AgentMode(Enum):
    """CIA operating modes"""
    CONVERSATION = "conversation"  # Gathering info, being friendly Alex
    ACTION = "action"              # Backend operations, modifications
    DECISION = "decision"          # Analyzing what mode to be in

class ModeManager:
    """Manages CIA's mode switching"""

    def __init__(self):
        self.current_mode = AgentMode.CONVERSATION
        self.mode_indicators = {
            # Action mode triggers
            "action": [
                "change", "update", "modify", "edit", "increase", "decrease",
                "switch", "replace", "make it", "mark as", "set to",
                "actually", "instead", "correction", "fix", "urgent", "emergency",
                "rush", "asap", "now urgent", "is urgent", "make urgent"
            ],
            # Conversation mode triggers
            "conversation": [
                "need", "want", "looking for", "interested in", "planning",
                "thinking about", "considering", "help me", "what", "how"
            ]
        }

    def analyze_intent(self, message: str, context: dict[str, Any]) -> AgentMode:
        """Determine which mode CIA should be in"""
        message_lower = message.lower()

        # Check if we have existing bid cards
        has_bid_cards = context.get("user_bid_cards", [])

        # Count indicators
        action_score = sum(1 for indicator in self.mode_indicators["action"]
                          if indicator in message_lower)
        conversation_score = sum(1 for indicator in self.mode_indicators["conversation"]
                               if indicator in message_lower)

        # Decision logic
        if has_bid_cards and action_score > 0:
            # User has bid cards and message contains action words
            return AgentMode.ACTION
        elif action_score > conversation_score:
            # More action words than conversation words
            return AgentMode.ACTION
        else:
            # Default to conversation mode
            return AgentMode.CONVERSATION

    def get_mode_context(self, mode: AgentMode) -> dict[str, Any]:
        """Get the appropriate context for the current mode"""

        if mode == AgentMode.ACTION:
            return {
                "system_modifier": """
[ACTION MODE ACTIVE]
You are now in backend action mode. Your personality shifts to be more direct and efficient.
- Skip pleasantries and get straight to the task
- Look up relevant bid cards immediately
- Apply modifications without asking for clarification
- Confirm actions with brief, professional responses
- Focus on: "What needs to be done?" not "What else do I need to know?"
""",
                "priorities": [
                    "Find existing bid cards",
                    "Apply modifications",
                    "Update database records",
                    "Confirm completion"
                ],
                "skip_project_decision": True
            }

        else:  # CONVERSATION mode
            return {
                "system_modifier": """
[CONVERSATION MODE ACTIVE]
You are Alex, the friendly project assistant. Focus on understanding and gathering information.
- Be warm and conversational
- Ask clarifying questions
- Guide them through the process
- Make them feel heard and supported
- Focus on: "What else do I need to know?" not "What should I change?"
""",
                "priorities": [
                    "Understand project needs",
                    "Gather missing information",
                    "Build rapport",
                    "Guide to completion"
                ],
                "skip_project_decision": False
            }

    def should_switch_mode(self, current_mode: AgentMode,
                          message: str,
                          context: dict[str, Any]) -> Optional[AgentMode]:
        """Determine if we should switch modes"""

        new_mode = self.analyze_intent(message, context)

        if new_mode != current_mode:
            return new_mode

        return None

    def format_mode_switch_response(self, from_mode: AgentMode, to_mode: AgentMode) -> str:
        """Generate a smooth transition message when switching modes"""

        if from_mode == AgentMode.CONVERSATION and to_mode == AgentMode.ACTION:
            return "Let me take care of that for you right away."
        elif from_mode == AgentMode.ACTION and to_mode == AgentMode.CONVERSATION:
            return "I've completed that update. What else can I help you with?"

        return ""
