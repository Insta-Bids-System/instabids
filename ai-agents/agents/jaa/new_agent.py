"""
NEW JAA Agent - Updated for InstaBids 12 Data Points System
"""
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from supabase import create_client
from dotenv import load_dotenv
from .new_extractor import NewJAAExtractor


class NewJobAssessmentAgent:
    """Updated JAA for InstaBids focused data extraction"""
    
    def __init__(self):
        """Initialize JAA with Supabase connection"""
        print("[NEW JAA] Initializing Job Assessment Agent")
        
        # Load environment
        load_dotenv(override=True)
        
        # Initialize Supabase
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize new extractor
        self.extractor = NewJAAExtractor()
    
    def process_conversation(self, thread_id: str) -> Dict[str, Any]:
        """Process CIA conversation and create InstaBids bid card"""
        try:
            print(f"[NEW JAA] Processing conversation: {thread_id}")
            
            # Load conversation from database
            conversation_result = self.supabase.table('agent_conversations').select("*").eq('thread_id', thread_id).execute()
            
            if not conversation_result.data:
                return {"success": False, "error": f"No conversation found for thread_id: {thread_id}"}
            
            conversation_record = conversation_result.data[0]
            conversation_state = json.loads(conversation_record['state'])
            
            print(f"[NEW JAA] Loaded conversation with {len(conversation_state.get('messages', []))} messages")
            
            # Extract bid card data using new extractor
            print(f"[NEW JAA] Extracting InstaBids bid card data...")
            bid_card_data = self.extractor.extract_bid_card_data({'state': conversation_state})
            
            # Generate bid card number (keep under 20 chars)
            timestamp = datetime.now().strftime("%m%d%H%M%S")  # Shorter format
            bid_card_number = f"BC{timestamp}"  # Remove dash to save space
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(bid_card_data)
            
            # Create bid card record
            # Note: Store full thread_id in bid_document, use shortened version for column
            bid_card_record = {
                'cia_thread_id': thread_id[-20:],  # Last 20 chars to fit VARCHAR(20)
                'bid_card_number': bid_card_number,
                'public_token': bid_card_number,  # Use bid_card_number as public token
                'project_type': bid_card_data['project_type'],
                'urgency_level': bid_card_data['urgency_level'],
                'complexity_score': complexity_score,
                'contractor_count_needed': bid_card_data['contractor_requirements']['contractor_count'],
                'budget_min': bid_card_data['budget_min'],
                'budget_max': bid_card_data['budget_max'],
                # Store all InstaBids data in bid_document JSONB field
                'bid_document': {
                    'bid_card_number': bid_card_number,
                    'full_cia_thread_id': thread_id,  # Store full thread_id here
                    'all_extracted_data': bid_card_data,
                    'complexity_score': complexity_score,
                    'generated_at': datetime.now().isoformat(),
                    'extraction_method': 'NewJAAExtractor',
                    'instabids_version': '2.0'
                },
                'requirements_extracted': True,
                'status': 'ready',  # Shortened to fit VARCHAR(20)
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            print(f"[NEW JAA] Saving bid card to database...")
            
            # Save to database
            save_result = self.supabase.table('bid_cards').insert(bid_card_record).execute()
            
            if save_result.data:
                print(f"[NEW JAA] SUCCESS: Created bid card {bid_card_number}")
                print(f"[NEW JAA] Project: {bid_card_data['project_type']}")
                print(f"[NEW JAA] Service Type: {bid_card_data['service_type']}")
                print(f"[NEW JAA] Budget: ${bid_card_data['budget_min']}-${bid_card_data['budget_max']}")
                print(f"[NEW JAA] Group Bidding: {bid_card_data['group_bidding_potential']}")
                print(f"[NEW JAA] Intention Score: {bid_card_data['intention_score']}/10")
                
                return {
                    "success": True,
                    "bid_card_number": bid_card_number,
                    "bid_card_data": bid_card_data,
                    "complexity_score": complexity_score,
                    "database_record": save_result.data[0]
                }
            else:
                return {"success": False, "error": "Failed to save bid card to database"}
                
        except Exception as e:
            print(f"[NEW JAA ERROR] Failed to process conversation: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def modify_bid_card(self, bid_card_number: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Modify existing bid card with new InstaBids data handling"""
        try:
            print(f"[NEW JAA] Modifying bid card: {bid_card_number}")
            print(f"[NEW JAA] Modifications: {modifications}")
            
            # Get existing bid card
            existing_result = self.supabase.table('bid_cards').select("*").eq('bid_card_number', bid_card_number).execute()
            
            if not existing_result.data:
                return {"success": False, "error": f"No bid card found with number: {bid_card_number}"}
            
            existing_card = existing_result.data[0]
            print(f"[NEW JAA] Found existing bid card: {existing_card['project_type']}")
            
            # Prepare updates
            updates = {}
            modifications_applied = []
            
            # Handle service type changes
            if 'service_type' in modifications and modifications['service_type'] is not None:
                # Update in bid_document
                bid_document = existing_card.get('bid_document', {})
                bid_document.setdefault('all_extracted_data', {})['service_type'] = modifications['service_type']
                updates['bid_document'] = bid_document
                modifications_applied.append('service_type')
            
            # Handle budget context changes
            if 'budget_context' in modifications and modifications['budget_context'] is not None:
                bid_document = existing_card.get('bid_document', {})
                bid_document.setdefault('all_extracted_data', {})['budget_context'] = modifications['budget_context']
                updates['bid_document'] = bid_document
                modifications_applied.append('budget_context')
            
            # Handle group bidding changes
            if 'group_bidding_potential' in modifications and modifications['group_bidding_potential'] is not None:
                bid_document = existing_card.get('bid_document', {})
                bid_document.setdefault('all_extracted_data', {})['group_bidding_potential'] = modifications['group_bidding_potential']
                updates['bid_document'] = bid_document
                modifications_applied.append('group_bidding_potential')
            
            # Handle intention score changes
            if 'intention_score' in modifications and modifications['intention_score'] is not None:
                bid_document = existing_card.get('bid_document', {})
                bid_document.setdefault('all_extracted_data', {})['intention_score'] = modifications['intention_score']
                updates['bid_document'] = bid_document
                modifications_applied.append('intention_score')
            
            # Handle frequency changes (for ongoing services)
            if 'frequency' in modifications and modifications['frequency'] is not None:
                bid_document = existing_card.get('bid_document', {})
                all_extracted_data = bid_document.setdefault('all_extracted_data', {})
                
                # Update service frequency
                all_extracted_data['service_frequency'] = modifications['frequency']
                
                # Update project description to include new frequency
                current_desc = all_extracted_data.get('project_description', '')
                if 'weekly' in current_desc:
                    all_extracted_data['project_description'] = current_desc.replace('weekly', modifications['frequency'])
                elif 'bi-weekly' in current_desc:
                    all_extracted_data['project_description'] = current_desc.replace('bi-weekly', modifications['frequency'])
                else:
                    all_extracted_data['project_description'] = f"{current_desc}. Service frequency: {modifications['frequency']}"
                
                updates['bid_document'] = bid_document
                modifications_applied.append('service_frequency')
            
            # Handle budget changes (if specific amounts provided)
            if 'budget_min' in modifications and modifications['budget_min'] is not None:
                updates['budget_min'] = int(modifications['budget_min'])
                modifications_applied.append('budget_min')
            
            if 'budget_max' in modifications and modifications['budget_max'] is not None:
                updates['budget_max'] = int(modifications['budget_max'])
                modifications_applied.append('budget_max')
            
            # Handle urgency changes
            if 'urgency_level' in modifications and modifications['urgency_level'] is not None:
                updates['urgency_level'] = modifications['urgency_level']
                modifications_applied.append('urgency_level')
            
            # Recalculate complexity if needed
            if updates.get('bid_document'):
                updated_data = updates['bid_document']['all_extracted_data']
                complexity_score = self._calculate_complexity_score(updated_data)
                updates['complexity_score'] = complexity_score
                modifications_applied.append('complexity_score')
            
            # Always update timestamp
            updates['updated_at'] = datetime.now().isoformat()
            
            if updates:
                print(f"[NEW JAA] Applying updates: {list(updates.keys())}")
                
                # Apply updates
                update_result = self.supabase.table('bid_cards').update(updates).eq('bid_card_number', bid_card_number).execute()
                
                if update_result.data:
                    print(f"[NEW JAA] SUCCESS: Modified bid card {bid_card_number}")
                    print(f"[NEW JAA] Updated fields: {', '.join(modifications_applied)}")
                    
                    return {
                        "success": True,
                        "bid_card_number": bid_card_number,
                        "modifications_applied": modifications_applied,
                        "updated_card": update_result.data[0]
                    }
                else:
                    return {"success": False, "error": "Failed to update bid card"}
            else:
                return {"success": False, "error": "No valid modifications provided"}
                
        except Exception as e:
            print(f"[NEW JAA ERROR] Failed to modify bid card: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def _calculate_complexity_score(self, bid_card_data: Dict[str, Any]) -> int:
        """Calculate complexity score for InstaBids projects"""
        score = 5  # Base score
        
        # Service type complexity
        service_type = bid_card_data.get('service_type', '')
        service_complexity = {
            'labor_only': 1,
            'handyman': 2,
            'repair': 3,
            'ongoing_service': 4,
            'appliance_repair': 5,
            'installation': 7
        }
        score += service_complexity.get(service_type, 5)
        
        # Project type complexity
        project_type = bid_card_data.get('project_type', '')
        if 'remodel' in project_type:
            score += 3
        elif 'kitchen' in project_type or 'bathroom' in project_type:
            score += 2
        elif 'lawn' in project_type or 'clean' in project_type:
            score += 0
        
        # Special requirements add complexity
        if bid_card_data.get('special_requirements'):
            score += 2
        
        # Material preferences add complexity
        if bid_card_data.get('material_preferences'):
            score += 1
        
        # Images reduce complexity (better specifications)
        if bid_card_data.get('images') and len(bid_card_data['images']) > 0:
            score -= 1
        
        # Group bidding reduces complexity (standardized work)
        if bid_card_data.get('group_bidding_potential'):
            score -= 1
        
        # Clamp to reasonable range
        return max(1, min(10, score))