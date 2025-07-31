# Contractor Discovery Flow - From Conversation to Contact

## Flow Overview

```
Homeowner Conversation (CIA)
    ↓
Extract Size Preference & Requirements (JAA)
    ↓
Discovery Strategy Selection (CDA)
    ↓
Multi-Source Discovery Execution
    ↓
Lead Enrichment & Scoring
    ↓
Outreach Campaign (EAA)
    ↓
Response Tracking & Onboarding
```

## Detailed Flow with Contractor Size

### 1. CIA - Capture Size Preference
```
Homeowner: "I need my kitchen remodeled"
CIA: "What type of contractor are you looking for?"
     • Just need a handyman for small fixes
     • Local owner who does the work themselves  
     • Small company with a crew
     • Larger company with multiple teams
     • Don't have a preference

Homeowner: "I want a small company with good reviews"
CIA: Records contractor_size_preference = 'small_business'
```

### 2. JAA - Process Requirements
```python
# JAA extracts and enhances contractor requirements
contractor_requirements = {
    'size_preference': 'small_business',
    'acceptable_sizes': ['owner_operator', 'small_business'],
    'minimum_crew_size': 3,  # Based on project scope
    'license_required': 'general_contractor',
    'minimum_insurance': 1000000,
    'minimum_rating': 4.0,
    'maximum_distance': 25  # miles
}
```

### 3. CDA - Smart Discovery Strategy

#### Tier 1: Internal Database Search
```sql
SELECT * FROM contractors 
WHERE contractor_size IN ('owner_operator', 'small_business')
  AND 'kitchen_remodeling' = ANY(specialties)
  AND '32801' = ANY(service_zip_codes)
  AND status = 'active'
  AND average_rating >= 4.0
ORDER BY average_rating DESC, response_time_minutes ASC
```

#### Tier 2: Re-engagement Search
```sql
SELECT cl.*, ces.* 
FROM contractor_leads cl
JOIN contractor_engagement_summary ces ON cl.id = ces.contractor_lead_id
WHERE cl.contractor_size IN ('owner_operator', 'small_business')
  AND ces.last_contacted_at < NOW() - INTERVAL '30 days'
  AND ces.positive_responses > 0
  AND NOT ces.opt_out_all
  AND 'kitchen' = ANY(cl.specialties)
```

#### Tier 3: External Discovery
```python
# Discovery strategy based on contractor size
def get_discovery_strategy(size_preference):
    strategies = {
        'solo_handyman': {
            'sources': ['craigslist', 'nextdoor', 'facebook_marketplace'],
            'search_terms': ['handyman', 'home repair', 'maintenance']
        },
        'owner_operator': {
            'sources': ['google_maps', 'yelp', 'facebook'],
            'search_terms': ['contractor owner', 'local remodeling']
        },
        'small_business': {
            'sources': ['google_maps', 'yelp', 'angi', 'bbb'],
            'search_terms': ['remodeling company', 'construction']
        },
        'regional_company': {
            'sources': ['bbb', 'angi', 'homeadvisor'],
            'search_terms': ['construction company', 'remodeling firm']
        },
        'national_chain': {
            'sources': ['corporate_websites', 'franchise_directories'],
            'search_terms': ['home depot pro', 'lowes pro services']
        }
    }
    return strategies.get(size_preference)
```

## Implementation Plan - Step by Step

### Phase 1: Update Existing Agents (Week 1)
1. **CIA Updates**
   - Add contractor size preference questions
   - Update conversation state to capture preference
   - Add size flexibility options

2. **JAA Updates**
   - Extract contractor size requirements
   - Map project complexity to minimum crew size
   - Determine license/insurance needs by project value

### Phase 2: Core Database Setup (Week 1-2)
1. **Create Migration 004_contractor_discovery.sql**
   - contractor_leads table
   - discovery_runs table
   - Basic indexes

2. **Create Migration 005_contractor_outreach.sql**
   - contractor_outreach_attempts
   - contractor_engagement_summary

3. **Create Migration 006_contractors.sql**
   - Full contractors table for onboarded
   - contractor_lifecycle_events

### Phase 3: Discovery Implementation (Week 2-3)
1. **Google Places Integration**
   ```python
   # agents/cda/sources/google_places_discovery.py
   class GooglePlacesDiscovery:
       def search_contractors(self, location, contractor_size, specialties):
           # Implement Google Places API search
           # Parse business hours, reviews to estimate size
   ```

2. **Web Scraping Framework**
   ```python
   # agents/cda/sources/web_scraper_base.py
   class ContractorScraper:
       def identify_contractor_size(self, business_data):
           # Use employee count, review patterns, etc
   ```

### Phase 4: Lead Management System (Week 3-4)
1. **Lead Scoring Algorithm**
   - Score based on: ratings, reviews, response history
   - Factor in contractor size match
   - Location proximity scoring

2. **Enrichment Pipeline**
   - License verification
   - Insurance checking
   - Business entity validation

### Phase 5: Integration & Testing (Week 4)
1. **Update CDA Agent**
   - Real database queries instead of mock
   - Implement 3-tier search with size filtering
   - Add lead scoring

2. **Update EAA Agent**
   - Use real contractor data
   - Personalize outreach by contractor size
   - Track engagement properly

## API Endpoints Needed

```python
# Discovery Management
POST   /api/discovery/search
GET    /api/discovery/runs/{run_id}
GET    /api/discovery/leads?size=small_business&status=qualified

# Lead Management  
GET    /api/leads/{lead_id}
POST   /api/leads/{lead_id}/enrich
PUT    /api/leads/{lead_id}/qualify

# Contractor Management
GET    /api/contractors?size=owner_operator&specialty=kitchen
POST   /api/contractors/onboard
GET    /api/contractors/{id}/metrics

# Analytics
GET    /api/analytics/discovery-sources
GET    /api/analytics/contractor-funnel
GET    /api/analytics/size-distribution
```

## Key Decisions Needed

1. **Discovery Sources Priority**
   - Which external sources to implement first?
   - Build vs buy (APIs vs scraping)?

2. **Contractor Size Detection**
   - How to auto-detect size from external data?
   - Manual verification required?

3. **Lead Quality Thresholds**
   - Minimum rating to consider?
   - Required verifications?
   - Disqualification criteria?

4. **Outreach Limits**
   - Max attempts per contractor?
   - Time between attempts?
   - Channel preferences by size?