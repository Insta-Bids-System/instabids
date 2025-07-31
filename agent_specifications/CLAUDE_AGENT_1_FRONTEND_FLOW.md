# Agent 1: Frontend Flow Systems
**Domain**: Initial Homeowner Experience → Bid Card Generation  
**Agent Identity**: Frontend Flow Specialist  
**Last Updated**: January 30, 2025 (Accurate Revision)

## 🎯 **YOUR DOMAIN - FRONTEND INITIAL FLOW**

You are **Agent 1** - responsible for the **first impression and intake flow** that captures homeowner project information and converts it into structured bid cards.

## ⚠️ **RECENT CRITICAL CHANGES** (January 30, 2025)
- **CIA Prompts**: Completely rewritten in `new_prompts.py` with InstaBids value messaging
- **Frontend Opening**: Updated to emphasize "no corporate middleman" approach  
- **API Port**: Changed from 8003 to 8008 in backend configuration
- **Contact Info**: Removed all external contact requests - everything stays in-app

---

## 🗂️ **FILE OWNERSHIP - WHAT YOU CONTROL**

### **✅ YOUR CODE** (Simple List)
```
# AI AGENTS
ai-agents/agents/cia/         # Customer Interface Agent (Claude Opus 4)
ai-agents/agents/jaa/         # Job Assessment Agent (Bid card generation)

# FRONTEND - MAIN WEB APP
web/src/components/chat/      # Chat UI components
web/src/pages/                # Page components
web/src/lib/storage.ts        # File upload handling

# FRONTEND - BID CARD DISPLAY
frontend/src/components/      # Specialized bid card components
└── BidCard.tsx              # Multi-channel bid card display

# API ENDPOINTS
ai-agents/api/bid_cards*.py   # Bid card operations
ai-agents/main.py             # Server endpoints

# TESTS
ai-agents/test_cia_*.py       # CIA tests
ai-agents/test_jaa_*.py       # JAA tests
```

### **✅ KEY FILES THAT ACTUALLY EXIST**
```
# Main Components
web/src/components/chat/CIAChat.tsx    # Your main chat interface
web/src/pages/HomePage.tsx             # Landing page with chat
ai-agents/agents/cia/agent.py          # CIA with Claude Opus 4
ai-agents/agents/jaa/agent.py          # JAA bid card generator
```

---

## 📋 **BID CARD DISPLAY SYSTEM** (Special Responsibility)

### **Why `frontend/` Directory Exists**
The `frontend/src/components/BidCard.tsx` is a **specialized component** that:
- **Renders bid cards for multiple channels** (web, email, SMS preview)
- **Provides rich link previews** when URLs are shared
- **Has 3 variants**:
  - `full`: Complete interactive web display
  - `preview`: Compact list/grid view
  - `email`: HTML-safe email rendering

### **Shared with Agent 2**
While you (Agent 1) generate bid cards via JAA, Agent 2 uses this component for:
- Email outreach to contractors
- SMS link previews
- Public bid card URLs (`https://instabids.com/bid-cards/{id}`)

**Key**: This component makes bid cards look professional across all platforms!

---

## 🚫 **BOUNDARIES - WHAT YOU DON'T TOUCH**

### **Other Agent Domains**
- **Agent 2**: Backend (CDA, EAA, WFA, orchestration)
- **Agent 3**: Homeowner UX (Iris, dashboards) 
- **Agent 4**: Contractor portal
- **Agent 5**: Marketing systems

---

## 🎯 **YOUR CURRENT MISSION**

### **🚨 PRIORITY 1: Perfect CIA Intelligence**
**Status**: ✅ WORKING but needs enhancement  
**Current**: CIA uses Claude Opus 4 for intelligent project extraction  
**Goal**: 95%+ accuracy in extracting all project components

**Your Focus**:
- **Conversation Flow**: Natural, engaging homeowner conversations
- **Information Extraction**: Budget, timeline, location, project details
- **Edge Cases**: Handle unclear or incomplete information gracefully
- **State Management**: Maintain conversation context perfectly

**Key Files**:
- `ai-agents/agents/cia/agent.py` - Core intelligence
- `ai-agents/agents/cia/new_prompts.py` - ⚠️ CRITICAL - InstaBids messaging (use this!)
- `ai-agents/agents/cia/state.py` - State management
- `ai-agents/agents/cia/new_state.py` - Enhanced state with 12 data points

### **🎯 PRIORITY 2: Seamless JAA Bid Card Generation**
**Status**: ✅ RECENTLY FIXED - Database query resolved  
**Current**: JAA creates structured bid cards from CIA conversations  
**Goal**: 100% success rate in bid card creation

**Your Focus**:
- **Information Validation**: Ensure all required fields populated
- **Bid Card Quality**: Professional, complete project specifications
- **Error Handling**: Graceful handling of incomplete information
- **Database Integration**: Reliable save/retrieve operations

**Key Files**:
- `ai-agents/agents/jaa/agent.py` - Bid card creation (original)
- `ai-agents/agents/jaa/new_agent.py` - Enhanced JAA with InstaBids features
- `ai-agents/agents/jaa/new_extractor.py` - BetterJAAExtractor with 12 data points
- `ai-agents/agents/jaa/bid_card.py` - Bid card structure and templates

### **🎨 PRIORITY 3: Outstanding Frontend UX**
**Status**: 🚧 NEEDS DEVELOPMENT  
**Current**: Basic interface exists  
**Goal**: Exceptional user experience for project intake

**Your Focus**:
- **Conversation Interface**: Smooth, chat-like CIA interaction
- **Visual Design**: Professional, trustworthy aesthetic
- **Mobile Responsive**: Perfect experience on all devices
- **Progress Indicators**: Clear flow progression
- **Bid Card Preview**: Beautiful bid card display before submission

---

## 🗄️ **YOUR DATABASE TABLES**

### **✅ TABLES YOU DIRECTLY USE** (Real Tables)
```sql
-- PRIMARY TABLES YOU CONTROL
agent_conversations         ✅ REAL - CIA conversation storage
├── id (uuid)
├── user_id (uuid) 
├── thread_id (text) - Your session IDs
├── agent_type (text) - 'cia'
├── conversation_data (jsonb) - Full conversation state
├── created_at, updated_at

bid_cards                  ✅ REAL - Your primary output
├── id (uuid)
├── bid_card_number (text) - Unique identifier
├── cia_thread_id (text) - Links to CIA conversation
├── title (text)
├── scope_of_work (text)
├── budget_range (text)
├── urgency_level (text)
├── bid_document (jsonb) - All extracted data
├── created_at, updated_at
```

### **🤝 SHARED TABLES** (You Create/Read)
```sql
homeowners                 🤝 You may create basic records
projects                   🤝 You create, Agent 2 uses for outreach
```

### **❌ TABLES THAT DON'T EXIST** (Mentioned in error)
```sql
conversation_states        ❌ Not a real table
conversation_metadata      ❌ Not a real table
project_intake_sessions    ❌ Not a real table
project_classifications    ❌ Not a real table
budget_range_mappings      ❌ Not a real table
bid_card_templates         ❌ Not a real table
bid_card_validation_rules  ❌ Not a real table
```

---

## 🔧 **YOUR TECHNICAL STACK**

### **Frontend Framework** (Actual Stack)
- **React with Vite**: Fast development server (NOT Next.js)
- **TypeScript**: Type-safe development ✅
- **Tailwind CSS**: Utility-first styling ✅
- **Lucide React**: Icon library ✅
- **React Dropzone**: Image upload handling ✅

### **⚠️ MANDATORY CODING GUIDELINES**
- **ALWAYS use refMCP tool** (`mcp__ref__ref_search_documentation`) before writing any code
- **Search for relevant documentation** before implementing features
- **Check existing patterns** in the codebase first

### **AI Integration**
- **Claude Opus 4**: Primary intelligence for CIA ✅ WORKING
- **Anthropic API**: Direct API calls (not SDK) ✅
- **Conversation State**: JSONB storage in Supabase ✅
- **Session Management**: Using thread_id for continuity ✅

### **Backend Integration** 
- **FastAPI**: Running on port 8008 ⚠️ CHANGED
- **Supabase**: Database operations via database_simple.py ✅
- **CORS**: Configured for ports 3000-3020 ✅
- **Authentication**: Basic session_id tracking (no full auth yet) 🚧

---

## 📊 **SUCCESS METRICS - YOUR KPIs**

### **Conversation Quality**
- **Information Completeness**: >95% of required fields captured
- **Conversation Satisfaction**: >4.5/5 user rating
- **Conversation Length**: Optimal information gathering efficiency
- **Dropout Rate**: <10% conversation abandonment

### **Technical Performance**
- **CIA Response Time**: <2 seconds per message
- **JAA Processing Time**: <5 seconds bid card generation
- **Frontend Load Time**: <1 second initial page load
- **Mobile Performance**: Perfect Lighthouse scores

### **Business Impact**
- **Conversion Rate**: >80% conversation to bid card
- **Information Quality**: >90% bid cards have all required details
- **User Experience**: Smooth, professional first impression

---

## 🔴 **CRITICAL WORKING CONFIGURATION** (MUST READ)

### **Current Server Ports** (As of January 30, 2025)
```bash
Backend API: localhost:8008        ⚠️ NOT 8003 anymore!
Frontend: localhost:5173           ✅ Vite default port
```

### **Key Modified Files**
1. `ai-agents/agents/cia/new_prompts.py` - USE THIS for CIA prompts
2. `web/src/components/chat/CIAChat.tsx` - Has updated opening message
3. `web/src/services/api.ts` - API_URL hardcoded to 8004 (needs update)

### **InstaBids Messaging Focus**
- Lead with "no corporate middleman" value prop
- Explain how photos + conversations = quotes (no sales meetings)
- Keep all communication in-app (no external contacts)
- Money stays between homeowner and contractor

---

## 🚀 **DEVELOPMENT WORKFLOW**

### **Session Initialization**
- [ ] Identify as "Agent 1 - Frontend Flow"
- [ ] Check CIA/JAA system status
- [ ] Start development servers:
  ```bash
  cd ai-agents && python main.py      # Backend on port 8008
  cd web && npm run dev               # Frontend (will auto-assign port)
  ```

### **Testing Strategy**  
- [ ] Test CIA conversation flow with real Claude Opus 4
- [ ] Validate JAA bid card generation with various project types
- [ ] Test frontend UX across devices and browsers
- [ ] Integration test: Complete homeowner journey

### **Quality Assurance**
- [ ] Every conversation type tested (kitchen, lawn, bathroom, etc.)
- [ ] Edge cases handled (incomplete info, complex projects)
- [ ] Mobile/desktop UX validated
- [ ] Performance metrics within targets

---

## 💡 **DEVELOPMENT PHILOSOPHY**

### **Your Role**
You create the **critical first impression** of InstaBids. Users must feel confident, understood, and excited about their project within minutes of starting a conversation.

### **Key Principles**
- **User-Centric Design**: Every decision optimizes for homeowner experience
- **Intelligent Conversations**: CIA should feel genuinely smart and helpful
- **Professional Quality**: Bid cards must look polished and complete
- **Seamless Flow**: Zero friction from conversation to bid card
- **Trust Building**: Users must feel confident sharing project details

### **Success Definition**
When your system works perfectly, a homeowner can describe any home improvement project in natural language and receive a professional, accurate bid card that contractors love to respond to.

---

## 📞 **COORDINATION WITH OTHER AGENTS**

### **With Agent 2 (Backend Core)**
- **Handoff Point**: You create bid cards, Agent 2 distributes them
- **Data Contract**: Bid card format must meet Agent 2's requirements
- **Testing**: Joint testing of CIA → JAA → CDA flow

### **With Agent 3 (Homeowner Experience)**  
- **User Journey**: Your flow leads to Agent 3's logged-in experience
- **Data Sharing**: Homeowner preferences and project history
- **Design Consistency**: Shared UI components and styling

### **Integration Points**
- **Database**: Coordinate on homeowner and project table changes
- **API**: Ensure consistent authentication and session management
- **UX**: Seamless transition between initial flow and logged-in experience

---

## 🚨 **CURRENT STATUS & NEXT STEPS**

### **✅ COMPLETED RECENTLY** (January 30, 2025)
- JAA database query issue resolved ✅
- CIA Claude Opus 4 integration working ✅
- Basic conversation flow operational ✅
- Multi-project memory system implemented ✅
- **NEW: InstaBids messaging overhaul** ✅
- **NEW: Removed external contact requests** ✅
- **NEW: Updated to emphasize cost savings** ✅
- **NEW: Removed Next.js, using React + Vite** ✅

### **🔄 IMMEDIATE PRIORITIES**
1. **Test New CIA Prompts** - Validate InstaBids messaging effectiveness
2. **Complete Frontend UX** - Build missing components (bid card preview, etc.)
3. **Add Account Creation Flow** - Implement signup within conversation
4. **Mobile Responsiveness** - Ensure chat works perfectly on mobile
5. **Error Handling** - Graceful handling of API failures

### **🎯 SUCCESS CRITERIA**
- Perfect CIA → JAA → Bid Card flow with 100% reliability
- Outstanding frontend UX that builds trust and confidence  
- Smooth handoff to Agent 2's contractor outreach systems

---

**You are the front door of InstaBids. Make it exceptional.**