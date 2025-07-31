"""
Demonstrate LLM Intelligence and Decision-Making
Shows how each agent thinks and makes intelligent decisions
"""
import os
import sys
import json
from pathlib import Path

# Add the agents directory to the path
sys.path.append(str(Path(__file__).parent))

print("=" * 80)
print("INSTABIDS LLM INTELLIGENCE DEMONSTRATION")
print("How Claude Opus 4 Thinks Through the Entire Process")
print("=" * 80)

def show_cia_intelligence():
    """Show how CIA understands nuanced homeowner needs"""
    print("\n1. CIA (Customer Interface Agent) - Understanding Nuanced Requirements")
    print("-" * 70)
    
    homeowner_message = """
    I have water damage in my master bathroom. The shower has been leaking 
    for a while and now there's mold behind the tiles. I need someone who 
    can handle this carefully - I have young kids and I'm worried about 
    the health implications. I'd prefer a smaller, family-owned business 
    rather than a big corporate chain. Someone who will take their time 
    and do it right, not just rush through it. Budget is around $8-12k.
    """
    
    print("HOMEOWNER MESSAGE:")
    print(homeowner_message)
    
    print("\nCIA REASONING:")
    print("  > Detecting water damage AND mold - this is a health hazard")
    print("  > Young kids mentioned - safety is a PRIMARY concern")
    print("  > Preference for 'family-owned' over 'corporate' - values trust/care")
    print("  > Emphasis on 'do it right' vs 'rush' - quality over speed")
    print("  > Budget range $8-12k - mid-range, realistic for scope")
    
    print("\nCIA DECISION: Categorize as urgent health/safety issue")
    print("REASONING: Mold + kids = immediate attention needed")
    
    cia_extraction = {
        "project_type": "Bathroom Restoration - Water Damage & Mold",
        "urgency": "HIGH - Active mold with children in home",
        "key_requirements": {
            "safety": "Critical - mold remediation with kids",
            "contractor_type": "Family-owned preferred",
            "approach": "Careful, thorough, not rushed"
        },
        "budget": {"min": 8000, "max": 12000},
        "emotional_context": "Worried parent, needs reassurance"
    }
    
    print("\nEXTRACTED CONTEXT FOR JAA:")
    print(json.dumps(cia_extraction, indent=2))

def show_jaa_intelligence():
    """Show how JAA converts conversation to actionable bid card"""
    print("\n2. JAA (Job Assessment Agent) - Creating Smart Bid Cards")
    print("-" * 70)
    
    print("JAA REASONING:")
    print("  > Mold remediation requires specialized contractors")
    print("  > Family with kids = need 3-5 contractors for quick response")
    print("  > Budget $8-12k indicates full tile replacement likely")
    print("  > Health hazard = mark as 'Emergency' urgency")
    print("  > Family-owned preference = add to special requirements")
    
    print("\nJAA DECISION: Create Emergency bid with 5 contractors")
    print("REASONING: Health hazard + kids = maximum urgency & options")
    
    bid_card = {
        "title": "Emergency Bathroom Mold Remediation - Family Home",
        "urgency": "Emergency", 
        "timeline": "ASAP - Active mold with children",
        "scope_of_work": [
            "Mold inspection and testing",
            "Safe mold remediation (family-safe methods)",
            "Tile removal and disposal",
            "Water damage repair",
            "New tile installation",
            "Preventive waterproofing"
        ],
        "contractors_needed": 5,
        "special_requirements": {
            "contractor_type": "family_owned_preferred",
            "safety_priority": "child_safe_products",
            "work_style": "careful_not_rushed"
        }
    }
    
    print("\nGENERATED BID CARD:")
    print(json.dumps(bid_card, indent=2))

def show_cda_intelligence():
    """Show how Opus 4 CDA matches contractors intelligently"""
    print("\n3. CDA (Contractor Discovery) - Opus 4 Intelligent Matching") 
    print("-" * 70)
    
    # Simulated contractor database
    contractors = [
        {
            "name": "Smith Family Restoration",
            "size": "small",
            "years": 15,
            "specialties": ["water damage", "mold remediation"],
            "certifications": ["IICRC", "EPA RRP"],
            "recent_review": "Took great care with our nursery renovation"
        },
        {
            "name": "MegaCorp Restoration Services",
            "size": "large",
            "franchise": True,
            "specialties": ["water damage", "fire", "mold"],
            "response_time": "24/7 emergency"
        },
        {
            "name": "Johnson & Sons Bathroom Specialists",
            "size": "small",
            "family_owned": True,
            "years": 22,
            "specialties": ["bathrooms", "tile work"],
            "note": "Father started it, sons run it now"
        }
    ]
    
    print("AVAILABLE CONTRACTORS:")
    for c in contractors:
        print(f"  - {c['name']} ({c['size']} company)")
    
    print("\nCDA OPUS 4 REASONING:")
    print("  > Bid requires: family-owned + mold expertise + child safety focus")
    print("  > Analyzing 'Smith Family Restoration'...")
    print("    * Name suggests family business")
    print("    * IICRC certified for mold")
    print("    * Review mentions 'nursery' - experience with child safety")
    print("  > Analyzing 'MegaCorp Restoration'...")
    print("    * Large franchise - opposite of family-owned preference")
    print("    * Has mold expertise")
    print("    * Likely to rush for volume")
    print("  > Analyzing 'Johnson & Sons'...")
    print("    * Explicitly family-owned for 22 years")
    print("    * 'Father & sons' = multi-generational care")
    print("    * No specific mold certification mentioned")
    
    scores = [
        {
            "contractor": "Smith Family Restoration",
            "score": 92,
            "reasoning": "Perfect fit: family business + mold certified + proven child-safe work"
        },
        {
            "contractor": "Johnson & Sons",
            "score": 78,
            "reasoning": "Strong family values but needs mold certification verification"
        },
        {
            "contractor": "MegaCorp",
            "score": 45,
            "reasoning": "Has expertise but conflicts with family-owned preference"
        }
    ]
    
    print("\nCDA OPUS 4 DECISION: Prioritize Smith Family & Johnson & Sons")
    print("REASONING: Both align with family preference, Smith has mold expertise")
    
    print("\nMATCH SCORES:")
    for s in sorted(scores, key=lambda x: x['score'], reverse=True):
        print(f"  {s['score']}/100 - {s['contractor']}")
        print(f"         {s['reasoning']}")

def show_response_intelligence():
    """Show how LLM analyzes contractor responses"""
    print("\n4. Response Analysis - Hot Lead Detection")
    print("-" * 70)
    
    responses = [
        {
            "contractor": "Smith Family Restoration",
            "message": "We can come TODAY! Mold with kids is serious - my team is EPA certified and we use only child-safe products. Can be there in 2 hours for assessment. We just finished a similar job for a family with a newborn.",
            "response_time": "15 minutes"
        },
        {
            "contractor": "Johnson & Sons",
            "message": "Thanks for reaching out. We're pretty booked but could squeeze you in next Thursday for a look.",
            "response_time": "3 hours"
        }
    ]
    
    print("CONTRACTOR RESPONSES:")
    
    for resp in responses:
        print(f"\n{resp['contractor']} (responded in {resp['response_time']}):")
        print(f'"{resp["message"]}"')
        
        if resp['contractor'] == "Smith Family Restoration":
            print("\nRESPONSE ANALYZER REASONING:")
            print("  > Immediate response time (15 min) = high interest")
            print("  > Offers same-day service = understands urgency")
            print("  > Mentions EPA cert + child-safe = addresses concerns")
            print("  > References similar job with newborn = relevant experience")
            print("  > Multiple urgency indicators: 'TODAY!', 'serious', '2 hours'")
            
            print("\nANALYZER DECISION: HOT LEAD - Score: 0.95/1.0")
            print("REASONING: Urgent response + addresses all concerns + immediate availability")
        else:
            print("\nRESPONSE ANALYZER REASONING:")
            print("  > Slow response (3 hours) = lower priority")
            print("  > 'Pretty booked' = limited availability") 
            print("  > 'Next Thursday' = doesn't grasp urgency")
            print("  > No mention of mold expertise or child safety")
            
            print("\nANALYZER DECISION: COOL LEAD - Score: 0.35/1.0")
            print("REASONING: Low urgency recognition + no expertise demonstration")

def show_followup_intelligence():
    """Show how LLM creates personalized follow-ups"""
    print("\n5. Follow-up Automation - Personalized Re-engagement")
    print("-" * 70)
    
    context = {
        "contractor": "Johnson & Sons",
        "original_bid": "Emergency mold remediation - family home",
        "no_response_days": 2,
        "homeowner_concern": "child safety",
        "contractor_strength": "family-owned for 22 years"
    }
    
    print("FOLLOW-UP CONTEXT:")
    print(f"  - No response from {context['contractor']} for {context['no_response_days']} days")
    print(f"  - Original bid: {context['original_bid']}")
    
    print("\nFOLLOW-UP AGENT REASONING:")
    print("  > Day 2 no response = try different angle")
    print("  > They're family-owned = appeal to family values")
    print("  > Homeowner has kids = emphasize shared understanding")
    print("  > Don't mention 'no response' = positive framing")
    print("  > Create urgency without desperation")
    
    followup = {
        "channel": "SMS",  
        "message": "Hi Johnson & Sons! Quick question - as a family business, you probably understand how concerning mold can be with young kids at home. We have a family in [area] dealing with this right now. Even if you're booked, any advice you could share? They specifically wanted a family-owned company they could trust. - Instabids",
        "strategy": "Appeal to expertise + family values"
    }
    
    print("\nFOLLOW-UP AGENT DECISION: Send SMS with family-focused angle")
    print("REASONING: Leverages their identity as family business")
    
    print("\nGENERATED FOLLOW-UP:")
    print(f"Channel: {followup['channel']}")
    print(f"Message: {followup['message']}")
    print(f"Strategy: {followup['strategy']}")

def show_system_flow():
    """Show how it all connects"""
    print("\n6. COMPLETE SYSTEM FLOW - DATA & DECISIONS")
    print("-" * 70)
    
    flow = """
    1. CIA extracts nuanced understanding → agent_conversations table
       └─> Stores: thread_id, emotional context, key concerns
    
    2. JAA creates structured bid card → bid_cards table  
       └─> Stores: urgency level, contractors_needed, special_requirements
    
    3. CDA discovers and scores contractors → contractor_leads + discovery_runs
       └─> Stores: match_scores, selection_reasoning, bid-specific context
    
    4. Distribution tracking → bid_card_distributions
       └─> Stores: unique URLs, sent timestamps, methods used
    
    5. Response analysis → contractor_responses  
       └─> Stores: is_hot_lead, sentiment, hot_lead_score, reasoning
    
    6. Follow-up decisions → followup_attempts
       └─> Stores: personalized messages, channel selection, timing
    
    Each step: LLM makes intelligent decision → Database captures result
    """
    
    print(flow)

def show_key_insights():
    """Show the key insights about LLM-database integration"""
    print("\n7. KEY INSIGHTS: LLMs + Database = Intelligence + Structure")
    print("-" * 70)
    
    print("TRADITIONAL AUTOMATION (Database-Driven):")
    print("  -- Simple status update")
    print("  UPDATE contractor_responses")
    print("  SET status = 'followup_needed'") 
    print("  WHERE response_time > interval '24 hours';")
    
    print("\nSMART LLM INTEGRATION (Intelligence-Driven):")
    print("  # LLM analyzes response content")
    print("  analysis = opus_4.analyze_response(response_text, bid_context)")
    print("  ")
    print("  # LLM makes nuanced decision")
    print("  db.update_contractor_response(")
    print("      is_hot_lead=analysis.enthusiasm > 0.8,")
    print("      sentiment=analysis.sentiment,")
    print("      hot_lead_reasons=analysis.reasoning,")
    print("      urgency_detected=analysis.contains_urgent_language")
    print("  )")
    
    print("\nTHE KEY DIFFERENCE:")
    print("  - Database: Provides structure, relationships, audit trail")
    print("  - LLMs: Provide intelligence, understanding, decision-making")
    print("  - Together: Structure + Intelligence = Powerful automation")
    
    print("\nThe database doesn't dictate behavior - it captures the intelligent")
    print("decisions made by LLMs and maintains the relationships needed for")
    print("the system to function cohesively.")

if __name__ == "__main__":
    show_cia_intelligence()
    show_jaa_intelligence()
    show_cda_intelligence() 
    show_response_intelligence()
    show_followup_intelligence()
    show_system_flow()
    show_key_insights()
    
    print("\n" + "=" * 80)
    print("CONCLUSION: This is NOT if-then automation - it's true AI understanding!")
    print("The database captures LLM intelligence, it doesn't restrict it.")
    print("Each agent reasons about the specific situation and makes nuanced decisions.")
    print("=" * 80)