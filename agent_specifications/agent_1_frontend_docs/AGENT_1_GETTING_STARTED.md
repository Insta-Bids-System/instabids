# Agent 1: Getting Started Guide
**Purpose**: Complete onboarding for CIA + JAA agents and frontend connections  
**Last Updated**: January 30, 2025  
**Scope**: Customer Interface Agent, Job Assessment Agent, Frontend components

## 🎯 **AGENT 1 DOMAIN OVERVIEW**

**My Responsibility**:
- **CIA Agent** - LangGraph backend agent that handles homeowner conversations using Claude Opus 4
- **JAA Agent** - LangGraph backend agent that converts conversations into professional bid cards
- **Frontend Connections** - React components that provide user interfaces for these agents

**Key Files I Own**:
```
ai-agents/agents/cia/          # CIA agent backend
ai-agents/agents/jaa/          # JAA agent backend  
web/src/components/chat/       # Chat interface components
frontend/src/components/       # Bid card display components
```

---

## 🚀 **QUICK START (5 Minutes)**

### **1. Start the Backend (CIA + JAA agents)**
```bash
cd ai-agents
python main.py
# Server starts on http://localhost:8008
# Health check: curl localhost:8008/
```

### **2. Start the Frontend (Chat interface)**
```bash
cd web
npm run dev
# Frontend starts on http://localhost:5173
# Access: http://localhost:5173
```

### **3. Test CIA Agent**
```bash
cd ai-agents
python test_cia_claude_extraction.py
# Expected: ✅ "Ready for JAA: True, Missing Fields: []"
```

### **4. Test Complete CIA → JAA Flow**
```bash
cd ai-agents  
python test_complete_system_validation.py
# Expected: ✅ "Complete CIA → JAA → CDA flow working"
```

---

## 🏗️ **DEVELOPMENT ENVIRONMENT SETUP**

### **Prerequisites**
- Python 3.11+ (for LangGraph agents)
- Node.js 18+ (for React frontend)
- Anthropic API key (Claude Opus 4)
- Supabase account and credentials

### **Environment Configuration**
```bash
# ai-agents/.env (Backend environment)
ANTHROPIC_API_KEY=your_anthropic_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# web/.env (Frontend environment) 
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### **Installation Steps**
```bash
# 1. Backend Dependencies (Python)
cd ai-agents
pip install -r requirements.txt

# 2. Frontend Dependencies (Node.js)
cd ../web
npm install

# 3. Test Backend Setup
cd ../ai-agents
python -c "from agents.cia.agent import CustomerInterfaceAgent; print('✅ CIA imported')"
python -c "from agents.jaa.agent import JobAssessmentAgent; print('✅ JAA imported')"

# 4. Test Frontend Setup
cd ../web
npm run type-check
# Expected: ✅ No TypeScript errors
```

---

## 🧠 **UNDERSTANDING THE CIA AGENT**

### **What CIA Does**
The Customer Interface Agent (CIA) is the first point of contact with homeowners. It:
- Conducts intelligent conversations using Claude Opus 4
- Extracts 12+ key project data points from natural language
- Handles file uploads and image analysis
- Manages conversation state and persistence
- Integrates with multi-project memory system

### **CIA File Structure**
```
ai-agents/agents/cia/
├── agent.py           # Main CIA class with Claude integration
├── prompts.py         # Claude prompts and message templates  
├── state.py          # Conversation state management
├── new_prompts.py    # Enhanced InstaBids messaging
└── __init__.py       # Package initialization
```

### **Key CIA Capabilities**
```python
# CIA extracts these data points:
1. Project Type (lawn care, kitchen remodel, etc.)
2. Budget Range ($500-800, around $25k, etc.)
3. Timeline/Urgency (ASAP, next month, flexible)
4. Location (address, city, state, zip)
5. Project Scope (detailed work description)
6. Property Details (size, type, access)
7. Materials/Preferences (specific brands, styles)
8. Images/Photos (analysis and storage)
9. Special Requirements (permits, licenses)
10. Homeowner Preferences (communication, scheduling)
11. Concerns/Issues (problems to address)
12. Contractor Requirements (specialties needed)
```

### **Testing CIA Agent**
```bash
# Test CIA directly via API
curl -X POST http://localhost:8008/api/cia/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "I need help with lawn care, my grass is knee-high and I have a half-acre property in Melbourne, FL 32904. Budget is around $500-800 and I need it done ASAP.",
    "session_id": "test_session"
  }'

# Expected response includes:
# - project_type: "lawn care"
# - budget_range: "$500-800"
# - urgency_level: "emergency"
# - location: "Melbourne, FL 32904"
# - ready_for_jaa: true
```

---

## 🎯 **UNDERSTANDING THE JAA AGENT**

### **What JAA Does**
The Job Assessment Agent (JAA) processes CIA conversations and creates professional bid cards:
- Reads conversation data from CIA sessions
- Extracts structured data using intelligent parsing
- Generates professional bid card documents
- Calculates project complexity and contractor requirements
- Saves bid cards to database for contractor outreach

### **JAA File Structure**
```
ai-agents/agents/jaa/
├── agent.py           # Main JAA class and processing logic
├── bid_card.py        # Bid card data structure and formatting
├── new_agent.py       # Enhanced JAA implementation
├── prompts.py         # JAA-specific prompts
└── __init__.py        # Package initialization
```

### **JAA Processing Flow**
```python
# JAA workflow:
1. Receive session_id from CIA completion
2. Load conversation data from Supabase
3. Extract 12 key data points using Claude
4. Calculate complexity score (1-10)
5. Determine contractor count needed  
6. Generate professional bid card document
7. Save to bid_cards table
8. Return bid card with unique URL
```

### **Testing JAA Agent**
```bash
# Test JAA processing (after CIA conversation)
curl -X POST http://localhost:8008/api/jaa/process/test_session

# Expected response:
# - bid_card_number: "BC-20250130123456"  
# - database_id: UUID of saved bid card
# - bid_card_data: Complete structured data
# - unique_url: URL for contractor access
```

---

## 🎨 **UNDERSTANDING THE FRONTEND COMPONENTS**

### **CIAChat.tsx - Main Chat Interface**
**Location**: `web/src/components/chat/CIAChat.tsx`  
**Purpose**: Provides the user interface for CIA conversations

```tsx
// Key features:
- Real-time chat with CIA agent
- File upload with drag-and-drop
- Message persistence and history
- InstaBids value proposition messaging
- Mobile responsive (needs improvement)
- Error handling and retry logic
```

**Current Issues**:
- ❌ Breaks on mobile screens (fixed width layout)
- ❌ File upload doesn't support camera on mobile
- ❌ Touch targets too small for mobile users

### **BidCard.tsx - Bid Card Display**
**Location**: `frontend/src/components/BidCard.tsx`  
**Purpose**: Displays bid cards in multiple formats

```tsx
// Three variants:
1. Full variant - Complete web display
2. Preview variant - List/summary view  
3. Email variant - HTML-safe for contractor emails

// Features:
- Professional photo gallery
- Mobile responsive design ✅
- Rich link preview support
- Action buttons for contractors
```

### **Frontend Architecture**
```
web/src/
├── components/
│   ├── chat/
│   │   ├── CIAChat.tsx        # Main chat interface
│   │   └── ...other chat components
│   ├── common/
│   │   ├── Button.tsx         # Shared UI components
│   │   └── LoadingSpinner.tsx
│   └── ui/                    # UI library components
├── pages/
│   ├── HomePage.tsx           # Landing page with chat
│   └── ChatPage.tsx           # Dedicated chat page
├── services/
│   └── api.ts                 # API calls to backend
└── types/                     # TypeScript type definitions
```

---

## 🔧 **DEVELOPMENT WORKFLOW**

### **Making Changes to CIA Agent**
```bash
# 1. Edit agent logic
nano ai-agents/agents/cia/agent.py

# 2. Test changes
cd ai-agents
python test_cia_claude_extraction.py

# 3. Test via API
python main.py  # Start server
# Test with curl or frontend

# 4. Check logs
tail -f ai-agents/logs/cia.log
```

### **Making Changes to JAA Agent**
```bash
# 1. Edit JAA logic
nano ai-agents/agents/jaa/agent.py

# 2. Test CIA → JAA flow
cd ai-agents
python test_complete_system_validation.py

# 3. Check bid card output
# Look for bid cards in Supabase database
```

### **Making Changes to Frontend**
```bash
# 1. Edit React components
nano web/src/components/chat/CIAChat.tsx

# 2. Test in browser
cd web
npm run dev
# Visit http://localhost:5173

# 3. Check TypeScript
npm run type-check

# 4. Test mobile responsiveness
# Use browser dev tools or real device
```

### **Testing Complete Integration**
```bash
# Full end-to-end test:
1. Start backend: cd ai-agents && python main.py
2. Start frontend: cd web && npm run dev  
3. Open http://localhost:5173
4. Have conversation with CIA
5. Verify bid card creation
6. Check Supabase database tables
```

---

## 🐛 **COMMON ISSUES & TROUBLESHOOTING**

### **Backend Issues**

#### **CIA Agent Not Starting**
```bash
# Check Python dependencies
pip install -r requirements.txt

# Check environment variables
echo $ANTHROPIC_API_KEY
# Should not be empty

# Check logs
python main.py 2>&1 | grep -i error
```

#### **JAA Database Errors**
```bash
# Common error: "PGRST116: JSON object requested"
# Solution: Check Supabase connection
python -c "
import os
from supabase import create_client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)
result = supabase.table('agent_conversations').select('*').limit(1).execute()
print(f'Connection: {result}')
"
```

#### **Claude API Issues**
```bash
# Test Claude API directly
python -c "
import os
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
response = client.messages.create(
    model='claude-3-opus-20240229',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print(f'Claude: {response.content[0].text}')
"
```

### **Frontend Issues**

#### **Frontend Won't Start**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :5173
```

#### **API Connection Issues**
```bash
# Check CORS settings
# Backend should allow frontend origin

# Verify API endpoints
curl http://localhost:8008/
# Should return agent status
```

#### **Mobile Layout Issues**
```bash
# Common problems:
- Missing viewport meta tag in index.html
- Fixed width containers in CSS
- Touch targets smaller than 44px
- File upload not supporting camera

# Test on real devices or browser dev tools
```

---

## 📊 **MONITORING & DEBUGGING**

### **Backend Monitoring**
```bash
# CIA Agent status
curl http://localhost:8008/api/cia/health

# JAA Agent status  
curl http://localhost:8008/api/jaa/health

# Database connectivity
python scripts/check_supabase_connection.py

# Claude API status
python scripts/test_claude_api.py
```

### **Frontend Monitoring**
```bash
# Development server logs
npm run dev 2>&1 | grep -i error

# Browser console errors
# Open dev tools → Console tab

# Network requests
# Open dev tools → Network tab
# Look for failed API calls
```

### **Database Monitoring**
```sql
-- Check recent conversations
SELECT * FROM agent_conversations 
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;

-- Check recent bid cards
SELECT * FROM bid_cards 
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;

-- Check agent conversation → bid card relationship
SELECT 
  ac.session_id,
  ac.created_at as conversation_time,
  bc.bid_card_number,
  bc.created_at as bid_card_time
FROM agent_conversations ac
LEFT JOIN bid_cards bc ON ac.session_id = bc.cia_session_id
ORDER BY ac.created_at DESC
LIMIT 10;
```

---

## 🎯 **NEXT STEPS AFTER SETUP**

### **1. Verify Everything Works**
- [ ] CIA agent responds intelligently ✅
- [ ] JAA creates bid cards from conversations ✅  
- [ ] Frontend chat interface functional ✅
- [ ] File upload working ✅
- [ ] Mobile experience (needs work ❌)

### **2. Focus Areas for Development**
1. **Mobile Responsiveness** - Fix CIAChat.tsx mobile layout
2. **User Experience** - Add bid card preview system
3. **Account Integration** - Seamless signup flow
4. **Error Handling** - Graceful failure recovery

### **3. Testing Strategy**
- Manual testing on desktop ✅ working
- Manual testing on mobile ❌ needs fixes
- Automated testing when features mature

### **4. Performance Optimization**
- CIA response time: Currently 1-3 seconds ✅
- JAA processing time: Currently <1 second ✅
- Frontend load time: Currently <2 seconds ✅
- Mobile performance: Needs optimization ❌

---

## 📚 **ESSENTIAL DOCUMENTATION**

### **For CIA Agent Development**
- `CLAUDE_AGENT_1_FRONTEND_FLOW.md` - Complete agent specification
- `AGENT_1_FRONTEND_SYSTEMS_STATUS.md` - Current system status
- `ai-agents/agents/cia/prompts.py` - Claude prompt engineering

### **For JAA Agent Development**  
- `CIA_TO_JAA_BUILD_PLAN.md` - Integration workflow
- `BID_CARD_EXTRACTION_MAP.md` - Data extraction guide
- `ai-agents/agents/jaa/bid_card.py` - Bid card structure

### **For Frontend Development**
- `AGENT_1_COMPONENT_MAP.md` - Component inventory
- `web/src/components/chat/CIAChat.tsx` - Main chat component
- `frontend/src/components/BidCard.tsx` - Bid card display

### **For System Integration**
- `AGENT_1_BUILD_PRIORITIES.md` - Development roadmap
- Database schema documentation
- API endpoint documentation

---

## 🆘 **GETTING HELP**

### **Self-Service Debugging**
1. Check this guide first
2. Review error logs in terminal
3. Test individual components
4. Check database tables in Supabase
5. Verify environment variables

### **Development Resources**
- Claude Opus 4 API documentation
- LangGraph framework docs  
- React + TypeScript guides
- Supabase documentation

### **Common Commands Reference**
```bash
# Backend (CIA + JAA)
cd ai-agents && python main.py                    # Start server
python test_cia_claude_extraction.py              # Test CIA
python test_complete_system_validation.py         # Test full flow

# Frontend (React)
cd web && npm run dev                              # Start frontend
npm run type-check                                # Check TypeScript
npm run build                                     # Build for production

# Database (Supabase)
# Use Supabase dashboard or SQL commands
```

---

**🎯 Remember: My domain is CIA + JAA agents + their frontend connections. Focus on intelligent conversation handling and professional bid card generation. The mobile experience is the current top priority.**

**Ready to start? Run the Quick Start commands and verify everything works, then dive into mobile responsiveness improvements!**