# Next Steps Build & Test Plan

## Phase 1: Database Schema Creation (Day 1)
**Goal**: Create all missing tables for the intelligent automation system to function

### 1.1 Create Core Distribution Tables
```sql
-- Track which contractors received which bid cards
CREATE TABLE bid_card_distributions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  bid_card_id UUID REFERENCES bid_cards(id),
  contractor_id UUID REFERENCES contractor_leads(id),
  distributed_at TIMESTAMP DEFAULT NOW(),
  distribution_method TEXT, -- 'email', 'sms', 'website_form'
  distribution_status TEXT DEFAULT 'pending', -- 'pending', 'sent', 'failed'
  email_opened BOOLEAN DEFAULT FALSE,
  email_opened_at TIMESTAMP,
  link_clicked BOOLEAN DEFAULT FALSE,
  link_clicked_at TIMESTAMP,
  response_received BOOLEAN DEFAULT FALSE,
  response_received_at TIMESTAMP,
  response_type TEXT, -- 'interested', 'not_interested', 'needs_info'
  response_content TEXT,
  follow_ups_sent INTEGER DEFAULT 0,
  last_follow_up_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_bid_distributions_bid ON bid_card_distributions(bid_card_id);
CREATE INDEX idx_bid_distributions_contractor ON bid_card_distributions(contractor_id);
CREATE INDEX idx_bid_distributions_status ON bid_card_distributions(distribution_status);
```

### 1.2 Create Campaign Management Tables
```sql
-- Outreach campaigns
CREATE TABLE outreach_campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  bid_card_id UUID REFERENCES bid_cards(id),
  contractor_count INTEGER,
  channels TEXT[], -- Array of channels: ['email', 'sms', 'website_form']
  status TEXT DEFAULT 'draft', -- 'draft', 'scheduled', 'active', 'completed'
  schedule JSONB, -- Scheduling configuration
  metrics JSONB DEFAULT '{}', -- Campaign metrics
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Campaign-contractor mappings
CREATE TABLE campaign_contractors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  campaign_id UUID REFERENCES outreach_campaigns(id),
  contractor_id UUID REFERENCES contractor_leads(id),
  channel TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  scheduled_at TIMESTAMP,
  sent_at TIMESTAMP,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 1.3 Create Response Tracking Tables
```sql
-- Detailed contractor responses
CREATE TABLE contractor_responses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  distribution_id UUID REFERENCES bid_card_distributions(id),
  contractor_id UUID REFERENCES contractor_leads(id),
  bid_card_id UUID REFERENCES bid_cards(id),
  response_channel TEXT, -- 'email', 'sms', 'phone', 'website'
  response_type TEXT, -- 'interested', 'not_interested', 'needs_info', 'negotiating'
  interest_level INTEGER CHECK (interest_level >= 1 AND interest_level <= 10),
  response_content TEXT,
  follow_up_required BOOLEAN DEFAULT FALSE,
  hot_lead BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Email tracking events
CREATE TABLE email_tracking_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  distribution_id UUID REFERENCES bid_card_distributions(id),
  event_type TEXT, -- 'sent', 'delivered', 'opened', 'clicked', 'bounced'
  event_data JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 1.4 Implementation Plan
- [ ] Use Supabase MCP to create tables
- [ ] Add RLS policies for security
- [ ] Create database migration script
- [ ] Test table creation in development

## Phase 2: CIA Enhancement (Day 2)
**Goal**: Improve CIA to extract all required fields for complete bid cards

### 2.1 Enhanced Field Extraction
Update CIA to capture:
- [x] project_type (already working)
- [x] budget_min/max (already working)
- [ ] project_description - Detailed summary of work needed
- [ ] timeline_start - When they want to begin
- [ ] urgency - Extract from phrases like "ASAP", "urgent", "flexible"
- [ ] address - Full location extraction
- [ ] property_type - Residential, commercial, etc.
- [ ] current_condition - Existing issues/damage

### 2.2 Implementation
```python
# agents/cia/agent.py - Enhanced extraction
def _extract_and_update_info(self, state: Dict[str, Any], message: str) -> None:
    """Enhanced extraction logic"""
    collected = state["collected_info"]
    
    # Existing extractions...
    
    # NEW: Timeline extraction
    if any(word in message_lower for word in ["start", "begin", "asap", "urgent", "week"]):
        # Extract timeline and urgency
        
    # NEW: Address extraction
    if re.search(r'\d{5}', message):  # Zip code
        # Extract full address
        
    # NEW: Description builder
    if not collected.get("project_description"):
        # Build description from conversation
```

### 2.3 Testing
- [ ] Create test conversations with all fields
- [ ] Verify extraction accuracy
- [ ] Update test_step_1_cia.py with new assertions

## Phase 3: End-to-End Integration (Day 3)
**Goal**: Complete flow from conversation to contractor response

### 3.1 Integration Test Script
```python
# test_full_integration.py
async def test_full_integration():
    """Test complete intelligent automation flow"""
    
    # Step 1: CIA conversation with all fields
    cia_result = await create_complete_conversation()
    assert cia_result['ready_for_jaa'] == True
    
    # Step 2: JAA bid card generation
    jaa_result = await process_with_jaa(cia_result['session_id'])
    assert jaa_result['success'] == True
    bid_card_id = jaa_result['database_id']
    
    # Step 3: Opus 4 CDA discovery
    cda_result = await discover_contractors(bid_card_id)
    assert len(cda_result['contractors']) >= 3
    
    # Step 4: Create distributions
    dist_result = await create_distributions(bid_card_id, contractors)
    assert dist_result['success'] == True
    
    # Step 5: Email extraction for missing emails
    email_result = await extract_missing_emails(contractors)
    
    # Step 6: Outreach campaign
    campaign_result = await create_and_execute_campaign(bid_card_id, contractors)
    
    # Step 7: Simulate responses
    response_result = await simulate_contractor_responses(distributions)
    
    # Step 8: Check hot leads
    hot_leads = await get_hot_leads(bid_card_id)
    
    # Step 9: Follow-up automation
    followup_result = await run_followup_campaign()
    
    return all_results
```

### 3.2 Performance Testing
- [ ] Measure response times for each component
- [ ] Test with 10, 25, 50 contractors
- [ ] Identify bottlenecks (especially web search)

## Phase 4: Production Readiness (Day 4)
**Goal**: Prepare for deployment

### 4.1 Error Handling & Logging
- [ ] Add comprehensive error handling to all agents
- [ ] Implement structured logging with levels
- [ ] Add retry logic for external API calls
- [ ] Create error recovery mechanisms

### 4.2 Configuration Management
```python
# config/production.py
PRODUCTION_CONFIG = {
    'timeouts': {
        'web_search': 30,  # seconds
        'email_extraction': 60,
        'opus_4_call': 30
    },
    'batch_sizes': {
        'contractor_discovery': 10,
        'email_extraction': 5,
        'follow_up': 20
    },
    'retry_policy': {
        'max_attempts': 3,
        'backoff_factor': 2
    }
}
```

### 4.3 API Documentation
- [ ] Document all internal APIs
- [ ] Create OpenAPI/Swagger specs
- [ ] Write integration guide

## Phase 5: Monitoring & Analytics (Day 5)
**Goal**: Add visibility into system performance

### 5.1 Metrics to Track
```python
# Key Performance Indicators
METRICS = {
    'cia_metrics': [
        'conversations_started',
        'conversations_completed', 
        'avg_messages_to_complete',
        'field_extraction_accuracy'
    ],
    'jaa_metrics': [
        'bid_cards_created',
        'avg_processing_time',
        'extraction_success_rate'
    ],
    'cda_metrics': [
        'contractors_discovered',
        'avg_match_score',
        'tier_distribution',
        'web_search_success_rate'
    ],
    'outreach_metrics': [
        'emails_sent',
        'open_rate',
        'click_rate',
        'response_rate'
    ],
    'conversion_metrics': [
        'hot_leads_generated',
        'contractors_engaged',
        'bids_received',
        'projects_awarded'
    ]
}
```

### 5.2 Dashboard Creation
- [ ] Create Supabase views for metrics
- [ ] Build real-time dashboard
- [ ] Set up alerts for failures

## Testing Checklist

### Unit Tests (Per Component)
- [ ] CIA: Field extraction accuracy
- [ ] JAA: Bid card completeness
- [ ] CDA: Contractor matching logic
- [ ] Email Extraction: Domain parsing
- [ ] Orchestrator: Channel selection
- [ ] Monitor: Event tracking
- [ ] Follow-up: Strategy selection

### Integration Tests
- [ ] CIA → JAA data flow
- [ ] JAA → CDA bid card passing
- [ ] CDA → Distribution creation
- [ ] Distribution → Outreach execution
- [ ] Response → Hot lead detection
- [ ] Non-response → Follow-up trigger

### Load Tests
- [ ] 100 concurrent conversations
- [ ] 500 contractor discoveries per hour
- [ ] 1000 emails per campaign
- [ ] 10,000 tracking events per day

### Security Tests
- [ ] SQL injection prevention
- [ ] API authentication
- [ ] Rate limiting
- [ ] Data privacy compliance

## Deployment Strategy

### Stage 1: Development Testing
- All components running locally
- Using test data
- Manual verification

### Stage 2: Staging Environment
- Deploy to staging server
- Use production-like data
- Automated testing

### Stage 3: Limited Production
- 10% of traffic
- Monitor closely
- Quick rollback plan

### Stage 4: Full Production
- 100% traffic
- 24/7 monitoring
- On-call support

## Success Criteria

1. **Functional Success**
   - CIA captures 90%+ of required fields
   - JAA creates bid cards in <5 seconds
   - CDA finds 5+ relevant contractors per bid
   - 20%+ email open rate
   - 5%+ response rate
   - 2%+ hot lead rate

2. **Performance Success**
   - End-to-end flow <2 minutes
   - 99.9% uptime
   - <100ms API response times
   - Support 1000+ concurrent users

3. **Business Success**
   - 50+ bid cards created daily
   - 250+ contractors contacted daily
   - 10+ hot leads generated daily
   - 5+ projects matched daily

## Timeline

**Week 1**
- Day 1: Database schema creation
- Day 2: CIA enhancement
- Day 3: Integration testing
- Day 4: Production readiness
- Day 5: Monitoring setup

**Week 2**
- Days 6-7: Load testing
- Days 8-9: Security audit
- Day 10: Staging deployment

**Week 3**
- Days 11-12: Limited production
- Days 13-14: Monitoring and fixes
- Day 15: Full production launch

## Risk Mitigation

1. **Database Performance**
   - Risk: Slow queries with large datasets
   - Mitigation: Proper indexing, query optimization

2. **External API Limits**
   - Risk: Rate limiting from Google Maps, Claude
   - Mitigation: Caching, request queuing, fallbacks

3. **Email Deliverability**
   - Risk: Emails marked as spam
   - Mitigation: Proper authentication, warming

4. **System Complexity**
   - Risk: Difficult to debug issues
   - Mitigation: Comprehensive logging, monitoring

This plan provides a structured approach to completing the intelligent automation system with proper testing at each stage.