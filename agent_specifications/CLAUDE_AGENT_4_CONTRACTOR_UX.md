# Agent 4: Contractor Experience Systems
**Domain**: Contractor Onboarding + Bid Response + Professional Portal  
**Agent Identity**: Contractor UX Specialist  
**Last Updated**: January 30, 2025 (Reality-Based Revision)

## 🎯 **YOUR DOMAIN - CONTRACTOR EXPERIENCE**

You are **Agent 4** - responsible for converting discovered contractor leads into active InstaBids contractors who can view and bid on projects.

## ⚠️ **CRITICAL CONTEXT - THE CONTRACTOR JOURNEY**

### **How Contractors Enter Your Domain**
```
1. Agent 2 (CDA) discovers contractor_leads → 50 fields of data
2. Agent 2 (EAA) sends bid_card_distributions → Unique tracking URLs
3. Contractor clicks unique URL in email/SMS
4. → THEY ENTER YOUR DOMAIN HERE ←
5. You convert them from 'lead' to 'contractor'
```

### **Current Database Reality**
```sql
-- WHAT EXISTS NOW
contractor_leads          ✅ 50 columns (Agent 2's domain)
contractors               ✅ Basic table (7 columns) - needs expansion
bid_card_distributions    ✅ Tracks unique URLs sent
contractor_responses      ✅ Tracks responses to outreach

-- WHAT DOESN'T EXIST YET
contractor_onboarding     ❌ Needs creation
contractor_portal         ❌ Needs creation  
contractor_bids           ❌ Different from 'bids' table
contractor_messaging      ❌ Needs creation
```

---

## 🔄 **THE CONVERSION FLOW** (Lead → Contractor)

### **Entry Point: Bid Card Landing Page**
When contractor clicks unique URL from EAA outreach:
```
1. Land on bid card detail page (public, no auth required)
   - Show full project details
   - Display InstaBids value prop
   - "Respond to Bid" CTA button

2. Click "Respond to Bid" → Two paths:
   
   Path A: Quick Response (No signup yet)
   - Simple form: "I'm interested" + optional message
   - Capture response in contractor_responses table
   - Follow up to convert to full contractor
   
   Path B: Full Bid Submission (Requires signup)
   - "Create Professional Bid" → Signup flow
   - Becomes full contractor with portal access
   - Can submit detailed, professional bids
```

### **Contractor Onboarding Flow**
```
1. Basic Registration (Minimum friction)
   - Business name (pre-filled from contractor_leads)
   - Email (pre-filled if available)
   - Phone (pre-filled if available)
   - Password creation
   - → Creates record in contractors table

2. Profile Enhancement (Can be done later)
   - License number & verification
   - Insurance information
   - Service areas & specialties
   - Business photos
   - → Updates contractor_profiles table

3. Immediate Value
   - Can bid on current project
   - See other relevant projects in their area
   - Access to contractor portal
```

---

## 🗂️ **FILE OWNERSHIP - WHAT YOU'LL BUILD**

### **✅ YOUR INITIAL MVP FILES** (Phase 1)
```
web/src/pages/
├── bid-card/[id]/              # Public bid card landing pages
│   ├── page.tsx                # Bid card detail view
│   ├── quick-response.tsx      # Quick interest form
│   └── create-bid.tsx          # Full bid creation (auth required)
├── contractor/
│   ├── signup/                 # Contractor registration
│   │   ├── page.tsx           # Basic signup form
│   │   ├── profile-setup.tsx  # Enhanced profile (optional)
│   │   └── welcome.tsx        # Post-signup orientation
│   ├── login/                  # Contractor login
│   ├── dashboard/              # Contractor portal home
│   ├── bids/                   # Bid management
│   │   ├── active/            # Current bid opportunities
│   │   ├── submitted/         # Bids they've submitted
│   │   └── won/               # Successful bids
│   └── profile/               # Profile management
```

### **✅ YOUR API ENDPOINTS** (Phase 1)
```
ai-agents/api/
├── contractor_conversion.py    # Lead → Contractor conversion
│   ├── POST /quick-response   # No-auth interest submission
│   ├── POST /signup           # Full contractor registration
│   └── POST /verify-lead      # Verify contractor_lead data
├── contractor_auth.py         # Authentication
│   ├── POST /login
│   ├── POST /logout
│   └── GET /me
├── contractor_bids.py         # Bid management
│   ├── GET /available-bids    # Projects they can bid on
│   ├── POST /submit-bid       # Create new bid
│   └── GET /my-bids          # Their bid history
└── contractor_profile.py      # Profile management
    ├── GET /profile
    ├── PUT /profile
    └── POST /verify-license
```

### **✅ YOUR COMPONENTS** (Phase 1)
```
web/src/components/contractor/
├── BidCardPublicView.tsx       # Public bid card display
├── QuickResponseForm.tsx       # Low-friction interest form
├── ContractorSignupForm.tsx    # Registration form
├── BidCreationWizard.tsx       # Professional bid builder
├── ContractorDashboard.tsx     # Portal homepage
└── ContractorNav.tsx           # Portal navigation
```

---

## 🗄️ **DATABASE SCHEMA - REALITY-BASED**

### **✅ TABLES THAT EXIST** (You'll interact with)
```sql
-- From Agent 2's domain (READ ONLY for you)
contractor_leads               ✅ 50 columns of discovered contractor data
├── id, company_name, email, phone, website
├── specialties[], license_number, rating
├── has_contact_form, contact_form_url
└── lead_status, lead_score

-- Basic contractor table (YOU EXPAND THIS)
contractors                    ✅ Currently minimal - you own this
├── id (uuid)
├── user_id (uuid) → links to auth
├── company_name (text)
├── license_number (text)
├── stripe_account_id (text)
└── created_at, updated_at

-- Tracking tables (YOU READ/WRITE)
bid_card_distributions         ✅ Unique URLs contractors clicked
contractor_responses           ✅ Initial responses to outreach
```

### **🆕 TABLES TO CREATE** (Your domain)
```sql
-- Contractor Onboarding & Profile
CREATE TABLE contractor_profiles (
    id UUID PRIMARY KEY,
    contractor_id UUID REFERENCES contractors(id),
    business_description TEXT,
    years_in_business INTEGER,
    license_verified BOOLEAN DEFAULT false,
    license_verification_date TIMESTAMP,
    insurance_info JSONB,
    service_areas JSONB,  -- zip codes, cities, radius
    specialties TEXT[],   -- plumbing, electrical, etc.
    team_size VARCHAR(50),
    business_hours JSONB,
    emergency_service BOOLEAN DEFAULT false,
    payment_methods TEXT[],
    minimum_job_size INTEGER,
    travel_fee_info JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Contractor Bid Submissions
CREATE TABLE contractor_bid_submissions (
    id UUID PRIMARY KEY,
    contractor_id UUID REFERENCES contractors(id),
    bid_card_id UUID REFERENCES bid_cards(id),
    distribution_id UUID REFERENCES bid_card_distributions(id),
    
    -- Bid Details
    bid_amount DECIMAL(10,2),
    bid_type VARCHAR(50), -- fixed, hourly, estimate
    
    -- Bid Content
    proposal_text TEXT,
    scope_of_work JSONB,
    timeline_days INTEGER,
    start_availability DATE,
    
    -- Breakdown
    labor_cost DECIMAL(10,2),
    material_cost DECIMAL(10,2),
    other_costs JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'submitted',
    submitted_at TIMESTAMP DEFAULT NOW(),
    viewed_by_homeowner_at TIMESTAMP,
    
    -- Competitive Info
    is_competitive BOOLEAN,
    includes_warranty BOOLEAN,
    warranty_details TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Quick Responses (No signup required)
CREATE TABLE contractor_quick_responses (
    id UUID PRIMARY KEY,
    contractor_lead_id UUID REFERENCES contractor_leads(id),
    bid_card_id UUID REFERENCES bid_cards(id),
    distribution_id UUID REFERENCES bid_card_distributions(id),
    
    interest_level VARCHAR(20), -- high, medium, low
    can_start_when VARCHAR(50), -- immediately, this_week, next_week, etc.
    initial_price_range VARCHAR(50), -- under_1k, 1k_5k, 5k_10k, etc.
    message TEXT,
    contact_preference VARCHAR(20), -- email, phone, text
    best_contact_time VARCHAR(50),
    
    -- Conversion tracking
    converted_to_contractor BOOLEAN DEFAULT false,
    contractor_id UUID REFERENCES contractors(id),
    converted_at TIMESTAMP,
    
    submitted_at TIMESTAMP DEFAULT NOW()
);

-- CoIA (Contractor Interface Agent) Conversations
CREATE TABLE contractor_conversations (
    id UUID PRIMARY KEY,
    contractor_id UUID REFERENCES contractors(id),
    thread_id TEXT UNIQUE NOT NULL,
    conversation_type VARCHAR(50), -- onboarding, bid_help, general
    
    state JSONB,
    last_message TEXT,
    bid_card_context UUID REFERENCES bid_cards(id),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 **YOUR IMMEDIATE PRIORITIES**

### **🚨 PRIORITY 1: Bid Card Landing Pages**
**Why**: This is where contractors first interact with InstaBids
**What to build**:
- Public bid card view (no auth required)
- Quick response form (low friction)
- Clear value proposition
- Mobile-optimized design

**Key Features**:
- Display all bid card details attractively
- Show "X contractors already interested" 
- Quick response vs full bid options
- InstaBids benefits clearly stated

### **🔄 PRIORITY 2: Contractor Conversion Flow**
**Why**: Convert contractor_leads → active contractors
**What to build**:
- Streamlined signup (pre-fill from contractor_leads)
- Immediate value after signup
- Progressive profile completion
- Skip complicated steps initially

**Conversion Optimization**:
- Pre-fill everything possible from contractor_leads
- Allow bidding immediately after basic signup
- Profile completion can happen later
- Show other relevant projects right away

### **📋 PRIORITY 3: Basic Contractor Portal**
**Why**: Give contractors a reason to stay
**What to build**:
- Simple dashboard showing available projects
- Bid management (submitted, pending, won)
- Basic profile editing
- Response to homeowner messages

**MVP Features**:
- See all projects matching their specialties
- Submit professional bids
- Track bid status
- Receive notifications

---

## 🔧 **TECHNICAL INTEGRATION WITH AGENT 2**

### **Data Flow From My Backend**
```
1. contractor_leads table
   - You inherit 50 fields of rich data
   - Use this to pre-fill signup forms
   - Reference for matching projects

2. bid_card_distributions 
   - Contains unique_url they clicked
   - Track conversion rate by distribution
   - Know which outreach method worked

3. contractor_responses
   - See their initial interest level
   - Reference in conversation context
   - Track engagement history
```

### **API Calls You'll Make**
```javascript
// Verify contractor lead exists
GET /api/contractor-leads/:id

// Get bid card details
GET /api/bid-cards/:id

// Track conversion
POST /api/conversions/lead-to-contractor
{
  contractor_lead_id: "...",
  contractor_id: "...",
  conversion_source: "bid_card_landing"
}
```

### **Shared Tables Coordination**
- **contractors**: You own and expand this table
- **contractor_leads**: Read-only from Agent 2
- **bid_cards**: Read-only from Agent 1
- **projects**: Future integration with homeowner projects

---

## 🔧 **YOUR TECHNICAL STACK**

### **Frontend Framework**
- **React + Vite**: Contractor portal (NOT Next.js)
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Responsive, mobile-first design
- **React Hook Form**: Form management for bids and profiles

### **Backend Framework**
- **LangGraph**: Backend agent framework (future CoIA agent)
- **FastAPI**: API server integration
- **Python**: Backend logic and database operations

### **⚠️ MANDATORY CODING GUIDELINES**
- **ALWAYS use refMCP tool** (`mcp__ref__ref_search_documentation`) before writing any code
- **Search for relevant documentation** before implementing features
- **Check existing patterns** in the codebase first

---

## 📊 **SUCCESS METRICS**

### **Conversion Metrics** (Your KPIs)
- **Landing → Quick Response**: >40% conversion
- **Quick Response → Signup**: >60% conversion
- **Signup → First Bid**: >80% conversion
- **Lead → Active Contractor**: >25% overall

### **Engagement Metrics**
- **Time to First Bid**: <30 minutes after signup
- **Bids per Contractor**: >3 per month
- **Portal Return Rate**: >70% weekly active
- **Profile Completion**: >60% within first week

### **Quality Metrics**
- **Bid Win Rate**: >20% of submitted bids
- **Contractor Satisfaction**: >4.0/5.0
- **Response Time**: <4 hours average
- **Professional Bid Score**: >4.5/5.0 from homeowners

---

## 🚀 **MVP DEVELOPMENT PLAN**

### **Phase 1: Core Conversion** (2 weeks)
- Bid card landing pages
- Quick response forms
- Basic contractor signup
- Minimal contractor portal

### **Phase 2: Bid Management** (2 weeks)
- Professional bid creation tools
- Bid tracking and management
- Basic messaging with homeowners
- Notification system

### **Phase 3: Portal Enhancement** (2 weeks)
- Enhanced contractor profiles
- Project matching algorithm
- Performance analytics
- Mobile app considerations

---

## 💡 **CRITICAL SUCCESS FACTORS**

### **Reduce Friction**
- Don't require license verification upfront
- Allow bidding before full profile completion
- Pre-fill everything possible
- Mobile-first design (contractors in trucks)

### **Immediate Value**
- Show relevant projects immediately
- Let them bid within minutes
- Clear earning potential visible
- No monthly fees initially

### **Build Trust**
- Professional appearance
- Clear InstaBids value prop
- Secure handling of information
- Transparent pricing model

---

## 📞 **COORDINATION NOTES**

### **With Agent 2 (Me)**
- I send the contractor_leads with rich data
- I track outreach and initial responses
- You convert leads to active contractors
- Feed back conversion data for optimization

### **With Agent 1**
- Bid cards need to be contractor-friendly
- Include all details contractors need
- Clear project requirements
- Realistic timelines

### **With Agent 3**
- Future: Enable contractor-homeowner messaging
- Shared project status tracking
- Review and rating systems

---

**Your mission: Convert discovered contractors into active InstaBids professionals who win projects and grow their businesses.**