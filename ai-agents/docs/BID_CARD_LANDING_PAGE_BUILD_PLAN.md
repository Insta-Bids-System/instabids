# Bid Card Landing Page System - Build Plan

## Date: January 29, 2025

## Executive Summary
Build a complete bid card landing page system that allows contractors to view project details through unique URLs. This includes creating test contractor websites to verify the WFA (Website Form Automation) agent works end-to-end.

## Architecture Overview

### URL System Design
```
Production: https://instabids.com/bid-cards/{bid_card_id}
Development: http://localhost:3000/bid-cards/{bid_card_id}

Example: https://instabids.com/bid-cards/bc_123456789
```

### Components
1. **Bid Card Landing Pages** - Shareable project URLs
2. **Test Contractor Websites** - 3-4 sites with different form types
3. **Updated WFA Messages** - Include bid card links
4. **Tracking System** - Monitor contractor engagement

## Phase 1: Bid Card URL System (Day 1)

### 1.1 Database Updates
```sql
-- Add to bid_cards table
ALTER TABLE bid_cards ADD COLUMN IF NOT EXISTS
  public_url VARCHAR(255) GENERATED ALWAYS AS 
  ('https://instabids.com/bid-cards/' || id) STORED;

-- Add view tracking
CREATE TABLE IF NOT EXISTS bid_card_views (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  bid_card_id UUID REFERENCES bid_cards(id),
  contractor_lead_id UUID REFERENCES contractor_leads(id),
  ip_address INET,
  user_agent TEXT,
  referrer TEXT,
  viewed_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 1.2 API Endpoints
```python
# FastAPI endpoints
@app.get("/api/bid-cards/{bid_card_id}")
async def get_public_bid_card(bid_card_id: str):
    """Public endpoint for bid card viewing"""
    
@app.post("/api/bid-cards/{bid_card_id}/track-view")
async def track_bid_card_view(bid_card_id: str, tracking_data: dict):
    """Track contractor engagement"""
```

### 1.3 Security Considerations
- Public bid cards should NOT expose homeowner personal info
- Show only project details, timeline, and budget range
- Include "Claim this project" CTA for contractors

## Phase 2: Bid Card Landing Page UI (Day 1-2)

### 2.1 Page Structure
```jsx
// pages/bid-cards/[id].tsx
<BidCardLandingPage>
  <InstabidsHeader />
  <ProjectHero>
    <ProjectType />
    <UrgencyBadge />
    <LocationArea />
  </ProjectHero>
  
  <ProjectDetails>
    <ProjectScope />
    <TimelineRequirements />
    <BudgetRange />
    <ProjectImages />
  </ProjectDetails>
  
  <ContractorCTA>
    <ClaimProjectButton />
    <ViewSimilarProjects />
  </ContractorCTA>
  
  <InstabidsValueProp>
    <WhyInstabids />
    <ContractorBenefits />
  </InstabidsValueProp>
</BidCardLandingPage>
```

### 2.2 Key Features
- Responsive design for mobile contractors
- Fast loading (optimize images)
- SEO friendly (meta tags for project type)
- Track engagement metrics
- "Powered by Instabids" branding

### 2.3 Contractor Actions
1. View project details
2. Claim interest in project
3. Quick registration if not onboarded
4. Schedule callback
5. View similar projects

## Phase 3: Test Contractor Websites (Day 2-3)

### 3.1 Test Site #1: Simple Contact Form
```html
<!-- test-sites/simple-contractor/contact.html -->
<form id="contact-form">
  <input name="name" placeholder="Your Name" required>
  <input name="email" type="email" placeholder="Email" required>
  <input name="phone" type="tel" placeholder="Phone">
  <textarea name="message" placeholder="Project Details"></textarea>
  <button type="submit">Get Quote</button>
</form>
```

### 3.2 Test Site #2: Multi-Step Form
```html
<!-- test-sites/pro-contractor/quote-wizard.html -->
<div id="quote-wizard">
  <!-- Step 1: Contact Info -->
  <div class="step-1">
    <input name="first_name" placeholder="First Name">
    <input name="last_name" placeholder="Last Name">
    <input name="email" placeholder="Email">
    <button onclick="nextStep()">Next</button>
  </div>
  
  <!-- Step 2: Project Details -->
  <div class="step-2">
    <select name="project_type">
      <option>Kitchen Remodel</option>
      <option>Bathroom Remodel</option>
    </select>
    <input name="timeline" placeholder="When do you need this?">
    <button onclick="submitForm()">Submit</button>
  </div>
</div>
```

### 3.3 Test Site #3: Complex Form with Validation
```html
<!-- test-sites/enterprise-contractor/request-quote.html -->
<form id="enterprise-quote" class="validated-form">
  <fieldset>
    <legend>Contact Information</legend>
    <input name="company" placeholder="Company Name" required>
    <input name="contact_name" placeholder="Contact Person" required>
    <input name="email" type="email" required pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$">
    <input name="phone" type="tel" pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}">
  </fieldset>
  
  <fieldset>
    <legend>Project Information</legend>
    <select name="service_type" required>
      <option value="">Select Service</option>
      <option>Residential</option>
      <option>Commercial</option>
    </select>
    <textarea name="project_description" minlength="50" required></textarea>
    <input name="budget_range" placeholder="Budget Range">
  </fieldset>
  
  <div class="g-recaptcha" data-sitekey="test-key"></div>
  <button type="submit">Request Quote</button>
</form>
```

### 3.4 Test Site #4: AJAX Form
```javascript
// test-sites/modern-contractor/assets/contact.js
document.getElementById('ajax-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const response = await fetch('/api/contact', {
    method: 'POST',
    body: JSON.stringify(Object.fromEntries(formData)),
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (response.ok) {
    showSuccessMessage();
  }
});
```

## Phase 4: WFA Message Updates (Day 3)

### 4.1 Updated Message Templates
```python
# agents/wfa/message_templates.py

FORM_MESSAGES = {
    "kitchen_remodel": """
Hi! I saw your contact form and wanted to reach out about a kitchen remodeling project in {city}. 

One of our vetted homeowners needs help with their kitchen renovation and we think you'd be a great fit.

You can view the full project details here: {bid_card_url}

The project includes:
- Complete kitchen remodel
- Timeline: {timeline}
- Budget: {budget_range}

Interested? Visit the link above or reply to this message.

Best regards,
The Instabids Team
    """,
    
    "general_project": """
Hello,

We have a new {project_type} project in {location} that matches your expertise.

View details: {bid_card_url}

This is a pre-qualified homeowner ready to move forward with the right contractor.

Thanks,
Instabids - Where contractors win projects without sales meetings
    """
}
```

### 4.2 WFA Updates
```python
# Update agents/wfa/agent.py
def _fill_form_message(self, form_data: Dict, bid_card: Dict) -> str:
    """Generate message with bid card URL"""
    template = FORM_MESSAGES.get(bid_card['project_type'], FORM_MESSAGES['general_project'])
    
    return template.format(
        bid_card_url=f"https://instabids.com/bid-cards/{bid_card['id']}",
        city=bid_card['location']['city'],
        timeline=bid_card['timeline'],
        budget_range=bid_card['budget_display'],
        project_type=bid_card['project_type'],
        location=f"{bid_card['location']['city']}, {bid_card['location']['state']}"
    )
```

## Phase 5: Testing Strategy (Day 4)

### 5.1 Local Test Environment
```bash
# Terminal 1: Run test contractor sites
cd test-sites
python -m http.server 8001  # Simple site
python -m http.server 8002  # Multi-step site
python -m http.server 8003  # Complex site
python -m http.server 8004  # AJAX site

# Terminal 2: Run Instabids bid card server
cd instabids-frontend
npm run dev  # Runs on localhost:3000

# Terminal 3: Run AI agents
cd ai-agents
python main.py  # Runs on localhost:8000
```

### 5.2 End-to-End Test Flow
```python
# test_bid_card_e2e.py
async def test_complete_bid_card_flow():
    # 1. Create conversation with CIA
    conversation = await create_test_conversation()
    
    # 2. Generate bid card with JAA
    bid_card = await generate_bid_card(conversation)
    
    # 3. Discover contractors with CDA
    contractors = await discover_contractors(bid_card)
    
    # 4. Test WFA on each test site
    for contractor in contractors:
        # WFA visits site and fills form
        result = await wfa_agent.process_contractor(contractor, bid_card)
        
        # Verify form submission includes bid card URL
        assert bid_card['public_url'] in result['message_sent']
    
    # 5. Verify bid card landing page
    response = await fetch(f"http://localhost:3000/bid-cards/{bid_card['id']}")
    assert response.status == 200
    
    # 6. Track view on bid card
    view_data = await track_bid_card_view(bid_card['id'], contractor['id'])
    assert view_data['success']
```

### 5.3 Test Scenarios
1. **Happy Path**: Form found → Filled → Submitted → Bid card link included
2. **No Form Found**: Fallback to email/phone outreach
3. **Form Errors**: Handle validation, captcha, AJAX forms
4. **Landing Page**: Verify all sections render, CTAs work
5. **Tracking**: Confirm views are logged correctly

## Phase 6: Metrics & Monitoring (Day 4-5)

### 6.1 Key Metrics
```sql
-- Bid card engagement metrics
CREATE VIEW bid_card_metrics AS
SELECT 
  bc.id,
  bc.project_type,
  COUNT(DISTINCT bcv.contractor_lead_id) as unique_views,
  COUNT(bcv.id) as total_views,
  COUNT(DISTINCT coa.contractor_lead_id) as contractors_contacted,
  COUNT(DISTINCT CASE WHEN coa.response_received THEN coa.contractor_lead_id END) as contractors_responded
FROM bid_cards bc
LEFT JOIN bid_card_views bcv ON bc.id = bcv.bid_card_id
LEFT JOIN contractor_outreach_attempts coa ON bc.id = coa.bid_card_id
GROUP BY bc.id, bc.project_type;
```

### 6.2 Success Criteria
- [ ] Bid card pages load in < 2 seconds
- [ ] WFA successfully fills 3/4 test forms
- [ ] Bid card URL included in all messages
- [ ] View tracking captures contractor engagement
- [ ] Contractors can claim interest in projects

## Implementation Timeline

### Day 1: Database & API
- Morning: Create bid card URL system and tracking tables
- Afternoon: Build API endpoints for public bid cards

### Day 2: Landing Page
- Morning: Create bid card React component
- Afternoon: Style with Tailwind, add Instabids branding

### Day 3: Test Sites & WFA
- Morning: Build 4 test contractor websites
- Afternoon: Update WFA message templates

### Day 4: Integration Testing
- Morning: Set up local test environment
- Afternoon: Run end-to-end tests

### Day 5: Documentation & Deployment
- Morning: Update all documentation
- Afternoon: Deploy to staging environment

## Risk Mitigation

### Technical Risks
1. **Form Complexity**: Some forms may be too complex for WFA
   - Mitigation: Start with simple forms, iterate
   
2. **Landing Page Performance**: Images may slow loading
   - Mitigation: Implement lazy loading, optimize images
   
3. **Security**: Exposing project data publicly
   - Mitigation: Careful data filtering, no PII

### Business Risks
1. **Contractor Spam**: Mass form submissions
   - Mitigation: Rate limiting, quality messages
   
2. **Low Engagement**: Contractors ignore bid cards
   - Mitigation: A/B test messaging, clear value prop

## Success Metrics
- 50%+ form fill success rate
- 20%+ bid card view rate
- 10%+ contractor response rate
- < 2 second page load time
- Zero security incidents

## Next Steps After This Phase
1. Implement contractor onboarding flow
2. Add bid submission through landing pages
3. Create contractor dashboard
4. Implement real external discovery (Tier 3)
5. Add analytics dashboard for tracking

## Conclusion
This build plan provides a complete path to implementing bid card landing pages and verifying the entire system works end-to-end with test websites. The phased approach ensures we can test incrementally while building toward a production-ready system.