"""
JAA (Job Assessment Agent) - Clean Implementation
Converts CIA conversations to bid cards using BetterJAAExtractor
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from supabase import create_client
from dotenv import load_dotenv
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from create_better_extractor import BetterJAAExtractor


class JobAssessmentAgent:
    """JAA - Converts CIA conversations to professional bid cards"""
    
    def __init__(self):
        """Initialize JAA with Supabase connection"""
        load_dotenv(override=True)
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.extractor = BetterJAAExtractor()
        print("[JAA] Initialized Job Assessment Agent")
    
    def process_conversation(self, cia_thread_id: str) -> Dict[str, Any]:
        """
        Main JAA function: Convert CIA conversation to bid card
        
        Args:
            cia_thread_id: Thread ID from CIA conversation
            
        Returns:
            Dict with success status and bid card data
        """
        print(f"\n[JAA] Processing conversation: {cia_thread_id}")
        
        try:
            # Step 1: Load conversation from Supabase
            print("[JAA] Loading conversation from database...")
            result = self.supabase.table('agent_conversations').select("*").eq('thread_id', cia_thread_id).execute()
            
            if not result.data or len(result.data) == 0:
                return {
                    'success': False,
                    'error': f'No conversation found for thread_id: {cia_thread_id}'
                }
            
            conversation_data = result.data[0]  # Get first (and only) result
            
            # Parse state if it's JSON string
            state = conversation_data.get('state', {})
            if isinstance(state, str):
                state = json.loads(state)
                conversation_data['state'] = state
            
            print(f"[JAA] Loaded conversation with {len(state.get('messages', []))} messages")
            
            # Step 2: Extract all 12 data points
            print("[JAA] Extracting bid card data...")
            bid_card_data = self.extractor.extract_bid_card_data(conversation_data)
            
            # Step 3: Generate bid card
            bid_card_number = self._generate_bid_card_number()
            complexity_score = self._calculate_complexity_score(bid_card_data)
            
            # Step 4: Save to bid_cards table
            print("[JAA] Saving bid card to database...")
            bid_card_record = {
                'cia_thread_id': cia_thread_id[-20:],  # Truncate to fit VARCHAR(20)
                'bid_card_number': bid_card_number,
                'project_type': bid_card_data['project_type'],
                'urgency_level': bid_card_data['urgency_level'],
                'complexity_score': complexity_score,
                'contractor_count_needed': bid_card_data['contractor_requirements']['contractor_count'],
                'budget_min': bid_card_data['budget_min'],
                'budget_max': bid_card_data['budget_max'],
                # Store all extracted data in bid_document INCLUDING INSTABIDS DATA
                'bid_document': {
                    'bid_card_number': bid_card_number,
                    'full_cia_thread_id': cia_thread_id,  # Store full thread ID
                    'all_extracted_data': bid_card_data,
                    'complexity_score': complexity_score,
                    'generated_at': datetime.now().isoformat(),
                    'extraction_method': 'BetterJAAExtractor',
                    # INSTABIDS SPECIFIC DATA
                    'service_type': bid_card_data.get('service_type'),
                    'group_bidding_potential': bid_card_data.get('group_bidding_potential'),
                    'intention_score': bid_card_data.get('intention_score'),
                    'budget_context': bid_card_data.get('budget_context'),
                    'timeline_urgency': bid_card_data.get('timeline_urgency'),
                    'instabids_version': '2.0'
                },
                'status': 'generated'
            }
            
            save_result = self.supabase.table('bid_cards').insert(bid_card_record).execute()
            
            if save_result.data:
                print(f"[JAA] SUCCESS: Created bid card {bid_card_number}")
                print(f"[JAA] Budget: ${bid_card_data['budget_min']}-${bid_card_data['budget_max']}")
                print(f"[JAA] Project: {bid_card_data['project_type']}")
                print(f"[JAA] Contractors needed: {bid_card_data['contractor_requirements']['contractor_count']}")
                
                return {
                    'success': True,
                    'bid_card_number': bid_card_number,
                    'bid_card_data': bid_card_data,
                    'cia_thread_id': cia_thread_id,
                    'database_id': save_result.data[0]['id']
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save bid card to database'
                }
                
        except Exception as e:
            print(f"[JAA ERROR] Failed to process conversation: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_bid_card_number(self) -> str:
        """Generate unique bid card number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"BC-{timestamp}"
    
    def _calculate_complexity_score(self, bid_card_data: Dict[str, Any]) -> int:
        """Calculate project complexity score (1-10)"""
        score = 5  # Base score
        
        # Budget impact
        budget_max = bid_card_data.get('budget_max', 0)
        if budget_max > 50000:
            score += 3
        elif budget_max > 25000:
            score += 2
        elif budget_max > 10000:
            score += 1
        elif budget_max < 2000:
            score -= 2
        
        # Urgency impact
        if bid_card_data.get('urgency_level') == 'emergency':
            score += 2
        elif bid_card_data.get('urgency_level') == 'week':
            score += 1
        
        # Specialties required
        specialties = bid_card_data.get('contractor_requirements', {}).get('specialties_required', [])
        score += len(specialties)
        
        # Concerns mentioned
        concerns = bid_card_data.get('concerns_issues', [])
        score += len(concerns) * 0.5
        
        # Special requirements
        special_reqs = bid_card_data.get('special_requirements', [])
        score += len(special_reqs)
        
        return max(1, min(10, int(score)))  # Clamp between 1-10
    
    def modify_bid_card(self, bid_card_number: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify an existing bid card with new specifications
        
        Args:
            bid_card_number: The bid card number to modify (e.g., "BC-20250729165023")
            modifications: Dict of changes to make
            
        Returns:
            Dict with success status and updated bid card data
        """
        print(f"\n[JAA] Modifying bid card: {bid_card_number}")
        print(f"[JAA] Modifications: {modifications}")
        
        try:
            # Step 1: Load existing bid card
            result = self.supabase.table('bid_cards').select("*").eq('bid_card_number', bid_card_number).execute()
            
            if not result.data or len(result.data) == 0:
                return {
                    'success': False,
                    'error': f'No bid card found with number: {bid_card_number}'
                }
            
            existing_card = result.data[0]
            bid_card_id = existing_card['id']
            
            print(f"[JAA] Found existing bid card: {existing_card['project_type']}")
            
            # Step 2: Apply modifications
            updates = {}
            
            # Handle project type changes
            if 'project_type' in modifications:
                updates['project_type'] = modifications['project_type']
            
            # Handle budget changes
            if 'budget_min' in modifications and modifications['budget_min'] is not None:
                updates['budget_min'] = int(modifications['budget_min'])
            if 'budget_max' in modifications and modifications['budget_max'] is not None:
                updates['budget_max'] = int(modifications['budget_max'])
            
            # Handle urgency changes
            if 'urgency_level' in modifications:
                updates['urgency_level'] = modifications['urgency_level']
            
            # Handle contractor count changes
            if 'contractor_count_needed' in modifications and modifications['contractor_count_needed'] is not None:
                updates['contractor_count_needed'] = int(modifications['contractor_count_needed'])
            
            # Handle bid document modifications (materials, timeline, frequency, etc.)
            if any(key in modifications for key in ['materials', 'timeline', 'frequency', 'special_notes', 'project_description']):
                bid_document = existing_card.get('bid_document', {})
                
                if 'materials' in modifications:
                    if 'all_extracted_data' not in bid_document:
                        bid_document['all_extracted_data'] = {}
                    bid_document['all_extracted_data']['materials_preferences'] = modifications['materials']
                
                if 'timeline' in modifications:
                    if 'all_extracted_data' not in bid_document:
                        bid_document['all_extracted_data'] = {}
                    bid_document['all_extracted_data']['timeline_start'] = modifications['timeline']
                
                if 'frequency' in modifications:
                    if 'all_extracted_data' not in bid_document:
                        bid_document['all_extracted_data'] = {}
                    # Store frequency in appropriate field for lawn care/service projects
                    bid_document['all_extracted_data']['service_frequency'] = modifications['frequency']
                    # Also update project description to include frequency
                    current_desc = bid_document.get('all_extracted_data', {}).get('project_description', '')
                    if 'weekly' in current_desc and modifications['frequency'] == 'bi-weekly':
                        updated_desc = current_desc.replace('weekly', 'bi-weekly')
                        bid_document['all_extracted_data']['project_description'] = updated_desc
                
                if 'special_notes' in modifications:
                    if 'all_extracted_data' not in bid_document:
                        bid_document['all_extracted_data'] = {}
                    bid_document['all_extracted_data']['special_requirements'] = modifications['special_notes']
                
                if 'project_description' in modifications:
                    if 'all_extracted_data' not in bid_document:
                        bid_document['all_extracted_data'] = {}
                    bid_document['all_extracted_data']['project_description'] = modifications['project_description']
                
                # Add modification history
                if 'modification_history' not in bid_document:
                    bid_document['modification_history'] = []
                
                bid_document['modification_history'].append({
                    'modified_at': datetime.now().isoformat(),
                    'modifications': modifications,
                    'modified_by': 'CIA_agent'
                })
                
                updates['bid_document'] = bid_document
            
            # Recalculate complexity if needed
            if any(key in updates for key in ['budget_max', 'urgency_level']):
                # Create mock bid_card_data for complexity calculation
                mock_data = {
                    'budget_max': updates.get('budget_max', existing_card.get('budget_max', 0)),
                    'urgency_level': updates.get('urgency_level', existing_card.get('urgency_level', 'flexible')),
                    'contractor_requirements': {'specialties_required': []},
                    'concerns_issues': [],
                    'special_requirements': []
                }
                updates['complexity_score'] = self._calculate_complexity_score(mock_data)
            
            # Step 3: Update in database
            print(f"[JAA] Applying updates: {list(updates.keys())}")
            update_result = self.supabase.table('bid_cards').update(updates).eq('id', bid_card_id).execute()
            
            if update_result.data:
                updated_card = update_result.data[0]
                print(f"[JAA] SUCCESS: Modified bid card {bid_card_number}")
                print(f"[JAA] Updated fields: {', '.join(updates.keys())}")
                
                return {
                    'success': True,
                    'bid_card_number': bid_card_number,
                    'modifications_applied': list(updates.keys()),
                    'updated_card': updated_card,
                    'original_card': existing_card
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update bid card in database'
                }
                
        except Exception as e:
            print(f"[JAA ERROR] Failed to modify bid card: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }


# Test the clean JAA agent
if __name__ == "__main__":
    jaa = JobAssessmentAgent()
    
    # Test with a real conversation ID (you'd replace this)
    test_thread_id = "session_0912f528-924c-4a7c-8b70-2708b3f5f227_1753744456.540726"
    
    result = jaa.process_conversation(test_thread_id)
    
    if result['success']:
        print(f"\n✅ JAA Test Passed!")
        print(f"Created bid card: {result['bid_card_number']}")
    else:
        print(f"\n❌ JAA Test Failed: {result['error']}")
