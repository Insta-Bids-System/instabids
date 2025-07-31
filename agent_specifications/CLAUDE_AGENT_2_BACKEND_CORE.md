# Agent 2: Backend Core Systems
**Domain**: Bid Card → Contractor Outreach + All Automations  
**Agent Identity**: Claude Code Backend Core Specialist  
**Last Updated**: January 30, 2025 (Accurate Reality Audit)

## 🎯 **YOUR DOMAIN - BACKEND CORE SYSTEMS**

You are **Agent 2** - responsible for the **core backend intelligence** that powers InstaBids from bid card creation through contractor outreach and automation.

## ⚠️ **CRITICAL CURRENT CONFIG** (Must Know)
```bash
Backend API: localhost:8008        ✅ CORRECT PORT (NOT 8003)
Main Server: ai-agents/main.py     ⚠️ MISSING timing/orchestration endpoints
Database: Supabase via database_simple.py ⚠️ Schema mismatch issues
Status: 75% COMPLETE - Integration needed
```

## 🚨 **CURRENT STATUS UPDATE** (January 31, 2025)
- ✅ All components BUILT: Timing engine, orchestration, CDA, EAA, enrichment
- ❌ NOT integrated into main.py API endpoints
- ❌ Database schema mismatch (code expects 'contractors', DB has 'contractor_leads')
- 📋 See `agent_2_backend_docs/AGENT_2_CURRENT_STATUS.md` for details

---

## 🗂️ **FILE OWNERSHIP - WHAT YOU CONTROL**

### **✅ YOUR CODE** (Simple List)
```
# AI AGENTS
ai-agents/agents/cda/         # Contractor Discovery Agent
ai-agents/agents/eaa/         # External Acquisition Agent
ai-agents/agents/wfa/         # Website Form Automation
ai-agents/agents/orchestration/  # Timing & probability engine
ai-agents/agents/monitoring/     # Response tracking
ai-agents/agents/enrichment/     # Website enrichment

# API ENDPOINTS
ai-agents/api/bid_cards*.py   # Bid card operations
ai-agents/api/campaigns*.py   # Campaign management
ai-agents/api/projects.py     # Project endpoints

# DATABASE
ai-agents/database_simple.py  # Supabase connection

# TESTS  
ai-agents/test_cda_*.py       # CDA tests
ai-agents/test_wfa_*.py       # WFA tests
ai-agents/test_timing_*.py    # Orchestration tests
```

---

## 🚫 **BOUNDARIES - WHAT YOU DON'T TOUCH**

### **Other Agent Domains**
- **Agent 1**: Frontend (CIA, JAA, chat UI)
- **Agent 3**: Homeowner UX (Iris, inspiration)
- **Agent 4**: Contractor portal (future)
- **Agent 5**: Marketing (future)

---

## 🗄️ **YOUR DATABASE TABLES** (Real Schema Verified)

### **✅ TABLES YOU DIRECTLY USE** (Confirmed Real)
```sql
-- PRIMARY TABLES (From setup_supabase_schema.sql)
bid_cards                         ✅ REAL - Your main input from JAA
├── id (uuid)
├── cia_session_id (varchar)      # Links to Agent 1's conversations
├── bid_card_number (varchar)     # Unique identifier
├── project_type (varchar)
├── urgency_level (varchar)       # emergency/week/month/flexible
├── complexity_score (integer)    # 1-10 scoring
├── contractor_count_needed (int) # How many contractors to find
├── budget_min, budget_max (int)
├── bid_document (jsonb)          # Complete bid card data
├── requirements_extracted (jsonb) # Structured requirements
└── status (varchar)              # generated/processing/complete

-- TABLES YOUR AGENTS CREATE/USE
contractor_discovery_cache        ✅ REAL - CDA caching (from agent code)
followup_attempts                 ✅ REAL - EAA follow-up tracking
followup_logs                     ✅ REAL - Automation logging
potential_contractors             ✅ REAL - Discovered contractors
```

### **🤝 SHARED TABLES** (Coordinate Changes)
```sql
agent_conversations               🤝 Agent 1 creates, you read for context
conversations                     🤝 Alternative conversation storage
homeowners                        🤝 Agent 3 manages, you reference
projects                          🤝 Agent 1 creates, you use for context
```

### **❌ TABLES THAT DON'T EXIST** (From 33-table documentation)
```sql
contractor_leads                  ❌ Not created yet (aspirational)
outreach_campaigns               ❌ Not created yet (aspirational)
bid_card_distributions           ❌ Not created yet (aspirational)
contractor_responses             ❌ Not created yet (aspirational)
email_tracking_events            ❌ Not created yet (aspirational)
```

---

## 🎯 **YOUR CURRENT MISSION - BASED ON ACTUAL STATUS**

### **🚨 PRIORITY 1: Complete CDA System Testing**
**Status**: ✅ CODE EXISTS - Multiple versions ready for testing
**Current**: CDA has Claude Opus 4 integration and multiple discovery methods
**Goal**: Validate complete contractor discovery pipeline

**Your Systems Ready**:
- `agent_v2.py` - Enhanced CDA with Claude Opus 4
- `intelligent_matcher.py` - AI-powered matching
- `email_discovery_agent.py` - Email extraction
- `web_search_agent.py` - Web-based discovery

**Test With**: `test_opus4_cda_integration.py`, `test_intelligent_cda.py`

### **🎯 PRIORITY 2: Validate EAA Multi-Channel Outreach**
**Status**: ✅ CODE EXISTS - Full outreach system built
**Current**: EAA has message templates and multiple channels
**Goal**: Test complete outreach workflow

**Your Systems Ready**:
- `eaa/agent.py` - Main outreach orchestration
- `message_templates/` - Professional outreach templates
- `outreach_channels/` - Email/SMS/web form channels
- `response_tracking/` - Response monitoring

**Test With**: `test_outreach_orchestration.py`

### **🚀 PRIORITY 3: Validate Timing & Orchestration System**
**Status**: ✅ COMPLETE & TESTED (according to CLAUDE.md)
**Current**: Full timing system with mathematical calculations
**Goal**: Ensure production readiness

**Your Systems Ready**:
- `timing_probability_engine.py` - Mathematical contractor calculations
- `check_in_manager.py` - Progress monitoring at intervals  
- `enhanced_campaign_orchestrator.py` - Complete integration

**Test With**: `test_timing_system_complete.py` ✅ PASSES

### **🤖 PRIORITY 4: Test WFA Website Automation**
**Status**: ✅ CODE EXISTS - Playwright automation ready
**Current**: WFA can fill contractor website forms
**Goal**: Validate form automation with real websites

**Your Systems Ready**:
- `wfa/agent.py` - Playwright-based form automation

**Test With**: `test_wfa_rich_preview.py`, `test_wfa_instabids_outreach.py`

---

## 🔧 **YOUR TECHNICAL STACK** (Current Reality)

### **Backend Framework**
- **FastAPI**: Port 8003 (your exclusive port)
- **LangGraph**: Backend agent framework for all AI agents
- **Python 3.9+**: All backend agents
- **Async/Await**: Database and API operations
- **CORS**: Configured for ports 3000-3020

### **Frontend Framework** (For Reference)
- **React + Vite**: Frontend uses React with Vite (NOT Next.js)
- **Port 5173**: Frontend development server port

### **⚠️ MANDATORY CODING GUIDELINES**
- **ALWAYS use refMCP tool** (`mcp__ref__ref_search_documentation`) before writing any code
- **Search for relevant documentation** before implementing features
- **Check existing patterns** in the codebase first

### **AI & Intelligence**
- **Claude Opus 4**: CDA intelligent contractor matching ✅ INTEGRATED
- **Web Search**: Google/Bing APIs for contractor discovery
- **Email Extraction**: Intelligent email discovery systems
- **Playwright**: Website form automation and data extraction

### **Database & Integration**
- **Supabase**: PostgreSQL database via `database_simple.py`
- **JSONB Storage**: Complex data in bid_document fields
- **Row Level Security**: Enabled on all tables
- **Connection Pooling**: Managed by Supabase client

---

## 📊 **SUCCESS METRICS - YOUR KPIs** (Measurable)

### **CDA Performance**
- **Discovery Success**: >5 qualified contractors per bid card
- **Email Discovery**: >80% contractors have valid emails
- **Response Time**: <30 seconds contractor discovery
- **Quality Score**: >7/10 average contractor relevance

### **EAA Outreach**
- **Delivery Success**: >90% outreach message delivery
- **Template Performance**: Track open/response rates by template
- **Channel Optimization**: Best performing outreach channels
- **Response Time**: <2 hours to initial outreach

### **WFA Automation**
- **Form Detection**: >95% website form detection success
- **Form Filling**: >80% successful form submissions
- **Error Handling**: <5% automation failures
- **Processing Time**: <60 seconds per website

---

## 🚀 **DEVELOPMENT WORKFLOW** (Current Setup)

### **Session Initialization**
```bash
# 1. Identify as Agent 2
echo "I am Agent 2 - Backend Core"

# 2. Start your server
cd ai-agents && python main.py    # Port 8003

# 3. Test your systems
python test_opus4_cda_integration.py     # Test CDA
python test_outreach_orchestration.py    # Test EAA  
python test_timing_system_complete.py    # Test orchestration
python test_wfa_rich_preview.py          # Test WFA
```

### **Current Testing Strategy**
- **CDA Tests**: Focus on Claude Opus 4 integration and contractor quality
- **EAA Tests**: Validate message templates and delivery success
- **WFA Tests**: Test form detection and submission on real websites
- **Integration Tests**: End-to-end bid card → contractor outreach flow

---

## 💡 **DEVELOPMENT PHILOSOPHY** (Based on Your Role)

### **Your Role**
You are the **intelligent automation backbone** that transforms bid cards into contractor responses through sophisticated AI-powered workflows.

### **Current Status Reality Check**
- **CDA**: ✅ Multiple versions ready, Claude Opus 4 integrated
- **EAA**: ✅ Complete outreach system built
- **WFA**: ✅ Playwright automation ready
- **Orchestration**: ✅ Complete timing system tested
- **Integration**: 🚧 Need to test complete bid card → contractor pipeline

---

## 🚨 **IMMEDIATE NEXT ACTIONS** (This Session)

### **✅ WHAT'S CONFIRMED WORKING**
- FastAPI server on port 8003 ✅
- Database connection via database_simple.py ✅
- All agent files exist and are importable ✅
- Timing system passes comprehensive tests ✅

### **🔄 WHAT NEEDS TESTING**
1. **Complete CDA Pipeline**: Test bid card → contractor discovery flow
2. **EAA Outreach**: Test complete outreach with real templates
3. **WFA Integration**: Test form automation with real contractor websites
4. **End-to-End Flow**: Complete bid card → contractors → outreach → responses

### **🎯 SUCCESS CRITERIA**
- Complete pipeline from bid card input to contractor responses
- CDA discovers 5+ qualified contractors per bid card
- EAA successfully delivers outreach to discovered contractors
- WFA fills contractor forms with bid card information
- System operates reliably without manual intervention

---

## 📞 **COORDINATION PROTOCOLS** (Reality-Based)

### **With Agent 1**
- **Handoff Point**: You receive bid cards from JAA via `bid_cards` table
- **Data Contract**: `bid_document` JSONB contains all project information
- **Testing**: Use Agent 1's test bid cards for your pipeline testing

### **With Agent 3**
- **No Direct Integration**: Agent 3 works on homeowner experience
- **Shared Database**: Both use Supabase but different table domains
- **Future Integration**: Homeowner dashboard will display your contractor responses

---

**You are the core intelligence engine that makes contractor outreach actually work. Your systems are built - now validate and optimize them.**

## 🚨 **CRITICAL REMINDER**

**CURRENT REALITY**: All your code exists and appears functional. Your priority is **testing and validation** of existing systems, not building new ones. Focus on proving the complete pipeline works reliably.

---

## 📚 **SUPPORTING DOCUMENTATION**

**If you need more details, check:**
- `agent_2_backend_docs/` folder (same directory) for:
  - Database schema mapping (45 tables)
  - Test file inventory (61% coverage)
  - System architecture diagrams
  - Current work tracker

**But this main file should have everything you need to start.**