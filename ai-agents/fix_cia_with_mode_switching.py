"""
FIX CIA WITH MODE SWITCHING
Show how to integrate mode switching into CIA agent
"""

def integrate_mode_switching():
    """Show the integration pattern"""
    
    print("\n" + "="*70)
    print("CIA MODE SWITCHING INTEGRATION")
    print("="*70)
    
    code = '''
# In CIA agent.py, update handle_conversation method:

async def handle_conversation(self, user_id: str, message: str, 
                            session_id: Optional[str] = None,
                            project_id: Optional[str] = None) -> Dict[str, Any]:
    """Handle conversation with mode switching"""
    
    # Initialize mode manager
    if not hasattr(self, 'mode_manager'):
        self.mode_manager = ModeManager()
    
    # Get user context
    user_bid_cards = await self._find_user_bid_cards(user_id)
    context = {
        'user_bid_cards': user_bid_cards,
        'has_active_project': bool(project_id),
        'message_count': state.get('message_count', 0)
    }
    
    # Determine mode
    mode = self.mode_manager.analyze_intent(message, context)
    mode_context = self.mode_manager.get_mode_context(mode)
    
    print(f"[CIA] Mode: {mode.value}")
    
    # MODE-SPECIFIC LOGIC
    if mode == AgentMode.ACTION:
        # ACTION MODE - Skip project decisions, go straight to modifications
        
        # Check if this is a modification
        is_mod, mod_details = self.modification_handler.detect_modification(message)
        
        if is_mod and user_bid_cards:
            # Find relevant bid card
            project_type = mod_details.get('project_type')
            bid_card = user_bid_cards[0]  # Or filter by project_type
            
            # Apply modification immediately
            result = await self._apply_bid_card_modification(
                bid_card['bid_card_number'],
                mod_details['modifications']
            )
            
            if result.get('success'):
                response = self.modification_handler.format_modification_response(
                    mod_details['modifications'],
                    bid_card['bid_card_number'],
                    bid_card['project_type']
                )
            else:
                response = "I couldn't update that. Let me try again."
            
            return {
                "response": response,
                "session_id": session_id,
                "mode": "action",
                "modification_applied": True
            }
    
    else:
        # CONVERSATION MODE - Normal friendly interaction
        
        # Add mode context to system prompt
        modified_prompt = self.system_prompt + mode_context['system_modifier']
        
        # Continue with normal Claude conversation
        response = await self._generate_claude_response(
            message, 
            state, 
            modified_prompt
        )
        
        return {
            "response": response,
            "session_id": session_id,
            "mode": "conversation",
            "ready_for_jaa": self._check_if_ready(state)
        }
'''
    
    print(code)
    
    print("\n" + "="*70)
    print("KEY BENEFITS OF MODE SWITCHING")
    print("="*70)
    
    print("\n1. CLEAR SEPARATION OF CONCERNS")
    print("   - Conversation Mode: Focus on gathering info")
    print("   - Action Mode: Focus on executing changes")
    
    print("\n2. NO MORE CONFUSION")
    print("   - In Action Mode, CIA skips project decision logic")
    print("   - Goes straight to finding and modifying bid cards")
    
    print("\n3. SMOOTH TRANSITIONS")
    print("   - Natural switching between modes")
    print("   - User doesn't feel the technical switch")
    
    print("\n4. BETTER USER EXPERIENCE")
    print("   - Friendly Alex when chatting")
    print("   - Efficient assistant when modifying")
    
    print("\n" + "="*70)
    print("EXAMPLE CONVERSATION FLOW")
    print("="*70)
    
    examples = [
        {
            "user": "I need a kitchen renovation",
            "mode": "CONVERSATION",
            "cia": "Hi! I'm Alex from Instabids. I'd love to help with your kitchen renovation!"
        },
        {
            "user": "Budget is $50,000",
            "mode": "CONVERSATION", 
            "cia": "Perfect! A $50,000 budget gives us great options. What timeline are you thinking?"
        },
        {
            "user": "Actually, change the budget to $60,000",
            "mode": "ACTION",
            "cia": "I've updated your kitchen renovation bid card (BC-123) with the new budget of $60,000."
        },
        {
            "user": "What else do you need to know?",
            "mode": "CONVERSATION",
            "cia": "I've completed that update. Let me check what else we need for your kitchen project..."
        }
    ]
    
    for ex in examples:
        print(f"\nUSER: {ex['user']}")
        print(f"[MODE: {ex['mode']}]")
        print(f"CIA: {ex['cia']}")

if __name__ == "__main__":
    integrate_mode_switching()