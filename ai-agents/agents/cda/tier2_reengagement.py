"""
Tier 2: Re-engagement of Previous Contacts
Query previous outreach attempts for viable candidates
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from supabase import Client


class Tier2Reengagement:
    """Tier 2 contractor re-engagement from outreach history"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    def find_reengagement_candidates(self, bid_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find contractors for re-engagement from previous contacts
        
        Uses optimized query from PRD:
        SELECT * FROM contractor_outreach 
        WHERE contacted_date > (NOW() - INTERVAL '6 months')
          AND response_status != 'permanently_declined'
          AND project_match_score > 0.7
        """
        try:
            # Calculate 6 months ago threshold
            six_months_ago = datetime.now() - timedelta(days=180)
            six_months_iso = six_months_ago.isoformat()
            
            print(f"[Tier2] Searching outreach history since {six_months_ago.strftime('%Y-%m-%d')}")
            
            # Query contractor outreach history
            query = self.supabase.table('contractor_outreach').select('''
                *,
                contractors:contractor_id (*)
            ''')
            
            # Apply filters
            query = query.gte('outreach_date', six_months_iso)
            query = query.neq('response_status', 'permanently_declined')
            query = query.gte('project_match_score', 0.7)
            query = query.order('project_match_score', desc=True)
            query = query.order('outreach_date', desc=True)
            
            result = query.execute()
            outreach_records = result.data if result.data else []
            
            print(f"[Tier2] Found {len(outreach_records)} potential re-engagement candidates")
            
            # Process and score candidates
            candidates = []
            seen_contractors = set()
            
            for record in outreach_records:
                contractor_id = record.get('contractor_id')
                if not contractor_id or contractor_id in seen_contractors:
                    continue
                
                seen_contractors.add(contractor_id)
                contractor = record.get('contractors')
                
                if not contractor:
                    continue
                
                # Calculate re-engagement viability
                reengagement_score = self._calculate_reengagement_score(record, bid_data)
                
                if reengagement_score > 0.5:  # Minimum threshold for re-engagement
                    # Add Tier 2 metadata
                    contractor['discovery_tier'] = 2
                    contractor['match_score'] = reengagement_score
                    contractor['reengagement_data'] = {
                        'last_contact': record['outreach_date'],
                        'last_response': record['response_status'],
                        'previous_match_score': record['project_match_score'],
                        'contact_method': record['contact_method'],
                        'notes': record.get('notes', '')
                    }
                    contractor['match_reasons'] = self._get_reengagement_reasons(record, contractor, bid_data)
                    
                    candidates.append(contractor)
            
            # Sort by reengagement score
            candidates.sort(key=lambda x: x['match_score'], reverse=True)
            
            print(f"[Tier2] After scoring: {len(candidates)} viable re-engagement candidates")
            
            # Return top 3 from Tier 2
            return candidates[:3]
            
        except Exception as e:
            print(f"[Tier2 ERROR] Failed to find re-engagement candidates: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _calculate_reengagement_score(self, outreach_record: Dict[str, Any], bid_data: Dict[str, Any]) -> float:
        """Calculate re-engagement viability score"""
        score = 0.0
        
        # Base score from previous project match
        previous_match = float(outreach_record.get('project_match_score', 0))
        score += previous_match * 50  # Max 50 points from previous match
        
        # Response history bonus
        response_status = outreach_record.get('response_status', '')
        if response_status == 'interested':
            score += 30  # They were interested before
        elif response_status == 'pending':
            score += 15  # No response, but not declined
        elif response_status == 'declined':
            score += 5   # Declined but not permanently
        
        # Recency bonus (more recent = better)
        outreach_date_str = outreach_record.get('outreach_date', '')
        try:
            outreach_date = datetime.fromisoformat(outreach_date_str.replace('Z', '+00:00'))
            days_ago = (datetime.now() - outreach_date.replace(tzinfo=None)).days
            
            if days_ago <= 30:
                score += 15  # Very recent
            elif days_ago <= 90:
                score += 10  # Recent
            elif days_ago <= 180:
                score += 5   # Somewhat recent
        except:
            pass
        
        # Contact method preference
        contact_method = outreach_record.get('contact_method', '')
        if contact_method == 'phone':
            score += 5  # Phone contact shows more engagement
        elif contact_method == 'email':
            score += 3  # Email is good
        
        return min(100.0, max(0.0, score))
    
    def _get_reengagement_reasons(self, outreach_record: Dict[str, Any], contractor: Dict[str, Any], bid_data: Dict[str, Any]) -> List[str]:
        """Get human-readable re-engagement reasons"""
        reasons = []
        
        # Previous response
        response_status = outreach_record.get('response_status', '')
        if response_status == 'interested':
            reasons.append("Previously expressed interest")
        elif response_status == 'pending':
            reasons.append("Previous contact with no negative response")
        
        # Match score
        previous_match = float(outreach_record.get('project_match_score', 0))
        if previous_match >= 0.8:
            reasons.append("High previous project match (80%+)")
        elif previous_match >= 0.7:
            reasons.append("Good previous project match (70%+)")
        
        # Timing
        outreach_date_str = outreach_record.get('outreach_date', '')
        try:
            outreach_date = datetime.fromisoformat(outreach_date_str.replace('Z', '+00:00'))
            days_ago = (datetime.now() - outreach_date.replace(tzinfo=None)).days
            
            if days_ago <= 30:
                reasons.append("Recent contact (within 30 days)")
            elif days_ago <= 90:
                reasons.append("Recent contact (within 3 months)")
        except:
            pass
        
        # Contact quality
        notes = outreach_record.get('notes', '')
        if 'interested' in notes.lower():
            reasons.append("Showed interest in previous communication")
        if 'busy' in notes.lower():
            reasons.append("Was busy but may be available now")
        
        return reasons
    
    def create_outreach_record(self, contractor_id: str, bid_card_id: str, contact_method: str, project_match_score: float, notes: str = "") -> bool:
        """Create new outreach record for tracking"""
        try:
            record = {
                'contractor_id': contractor_id,
                'bid_card_id': bid_card_id,
                'contact_method': contact_method,
                'outreach_date': datetime.now().isoformat(),
                'response_status': 'pending',
                'project_match_score': project_match_score,
                'notes': notes
            }
            
            result = self.supabase.table('contractor_outreach').insert(record).execute()
            return bool(result.data)
            
        except Exception as e:
            print(f"[Tier2 ERROR] Failed to create outreach record: {e}")
            return False