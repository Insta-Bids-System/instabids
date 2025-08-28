# InstaBids System Architecture & File Location Map
**Complete Guide to Main Agents, Entry Points, and Unified Memory System**

---

## 🚀 Main Entry Points

### **Primary Backend Entry Point**
```
📁 C:\Users\Not John Or Justin\Documents\instabids\ai-agents\main.py
```
- **Purpose**: FastAPI application with 40+ routers
- **Port**: 8008 (ONLY backend port)
- **Startup**: `cd ai-agents && python main.py`
- **Status**: ✅ FULLY OPERATIONAL - All agents load through this single entry point

---

## 🤖 Main Agent Files (Core AI Systems)

### **CIA - Customer Interface Agent (GPT-5)**
```
📁 ai-agents/agents/cia/agent.py
📁 ai-agents/routers/cia_routes_unified.py (API Router)
```
- **Purpose**: Homeowner conversations and bid card creation
- **AI Model**: GPT-5 with vision capabilities
- **Status**: ✅ FULLY OPERATIONAL
- **Memory**: Uses unified conversation system + potential bid cards

### **JAA - Job Assessment Agent (Claude Opus 4)**
```
📁 ai-agents/agents/jaa/agent.py  
📁 ai-agents/routers/jaa_routes.py (API Router)
```
- **Purpose**: Intelligent bid card updates and job assessment
- **AI Model**: Claude Opus 4
- **Status**: ✅ FULLY OPERATIONAL
- **Memory**: Updates bid cards directly, no conversation storage needed

### **IRIS - Intelligent Room & Inspiration System**
```
📁 ai-agents/agents/iris/agent.py
📁 ai-agents/agents/iris/api/routes.py (API Router)
```
- **Purpose**: Photo analysis and design inspiration
- **AI Model**: Claude with vision capabilities
- **Status**: ✅ FULLY OPERATIONAL (Modular Architecture)
- **Memory**: Unified conversation system + inspiration boards

### **COIA - Contractor Onboarding Agent (DeepAgents)**
```
📁 ai-agents/agents/coia/landing_deepagent.py (Main DeepAgent)
📁 ai-agents/routers/coia_landing_api.py (API Router)
```
- **Purpose**: Contractor landing page onboarding with 5 subagents
- **AI Framework**: DeepAgents with parallel orchestration
- **Status**: ✅ DEEPAGENTS FRAMEWORK
- **Memory**: State persistence via contractor_lead_id system

### **BSA - Bid Submission Agent (DeepAgents)**
```
📁 ai-agents/agents/bsa/agent.py
📁 ai-agents/routers/bsa_stream.py (API Router)
```
- **Purpose**: Contractor bid submission and management
- **AI Framework**: DeepAgents with checkpointing
- **Status**: ✅ OPTIMIZED DEEPAGENTS
- **Memory**: LangGraph checkpointing + context caching

### **CDA - Contractor Discovery Agent (Claude Opus 4)**
```
📁 ai-agents/agents/cda/agent.py
📁 ai-agents/routers/contractor_management_api_fixed.py (API Router)
```
- **Purpose**: Intelligent contractor matching and discovery
- **AI Model**: Claude Opus 4 for nuanced decisions
- **Status**: ✅ OPERATIONAL
- **Memory**: Contractor discovery cache + outreach tracking

### **EAA - External Acquisition Agent**
```
📁 ai-agents/agents/eaa/agent.py
📁 ai-agents/routers/campaign_management_api.py (API Router)
```
- **Purpose**: Multi-channel contractor outreach campaigns
- **AI Model**: Claude for email generation
- **Status**: ✅ MULTI-CHANNEL OUTREACH
- **Memory**: Campaign tracking + response monitoring

### **WFA - Website Form Automation Agent**
```
📁 ai-agents/agents/wfa/agent.py
📁 (Uses general automation endpoints)
```
- **Purpose**: Playwright-powered website form submission
- **AI Model**: Claude Opus 4 for intelligent form filling
- **Status**: ✅ OPERATIONAL
- **Memory**: Form submission tracking

### **Intelligent Messaging System (GPT-4o Security)**
```
📁 ai-agents/agents/intelligent_messaging/agent.py
📁 ai-agents/routers/intelligent_messaging_api.py (API Router)
```
- **Purpose**: BUSINESS CRITICAL - Contact info filtering and security
- **AI Model**: GPT-4o for advanced security analysis
- **Status**: ✅ FULLY OPERATIONAL
- **Memory**: Message analysis + agent comments storage

---

## 🧠 Unified Memory Backend System

### **Central Memory Architecture**
The unified memory system replaces fragmented conversation storage with a cohesive 5-table system that ALL agents use for conversation saving/retrieval.

### **Core Memory Tables**
```sql
-- Main conversation container
unified_conversations: conversation_id, user_id, agent_type, title, status, metadata

-- Individual messages  
unified_conversation_messages: message_id, conversation_id, sender_type, content, images

-- Persistent memory across conversations
unified_conversation_memory: memory_id, conversation_id, memory_type, key, value

-- Agent-specific context storage
unified_conversation_context: context_id, conversation_id, agent_type, context_data

-- Cross-agent shared state
unified_conversation_state: state_id, conversation_id, state_type, state_data
```

### **Unified Memory API Router**
```
📁 ai-agents/routers/unified_conversation_api.py
```
- **Purpose**: Single API for all conversation operations
- **Endpoints**: 
  - `POST /conversations/create` - Start new conversation
  - `POST /conversations/{id}/message` - Send message
  - `POST /conversations/{id}/memory` - Store memory
  - `GET /conversations/{id}/context` - Retrieve context

### **Agent-Specific Memory Systems**

#### **CIA Memory Integration**
```
📁 ai-agents/agents/cia/unified_integration.py
```
- **Saves**: Conversation turns, extracted project data, user preferences
- **Retrieves**: Previous conversations, project context, homeowner history
- **Special Features**: Potential bid card real-time tracking

#### **IRIS Memory Integration**  
```
📁 ai-agents/agents/iris/services/memory_manager.py
```
- **Saves**: Image analysis results, inspiration board data, design preferences
- **Retrieves**: Previous room analysis, user design history, inspiration context
- **Special Features**: Image-specific context storage

#### **COIA State Persistence**
```
📁 ai-agents/agents/coia/memory_integration.py
```
- **Saves**: 30+ contractor profile fields, business research, conversation state
- **Retrieves**: Complete contractor profile restoration via contractor_lead_id
- **Special Features**: Return visitor recognition with "Welcome back!"

#### **BSA Memory Integration**
```
📁 ai-agents/agents/bsa/memory_integration.py
```
- **Saves**: Bid submission context, contractor preferences, project history
- **Retrieves**: Previous bids, contractor profile, project requirements
- **Special Features**: Context caching with TTL (1hr contractors, 30min memory)

---

## 🔄 How Each Agent Saves & Retrieves Conversations

### **Standard Flow for All Agents:**

#### **1. Conversation Creation**
```python
# Every agent starts conversations the same way
POST /api/conversations/create
{
    "user_id": "user-123",
    "agent_type": "CIA",  # or IRIS, COIA, BSA, etc.
    "title": "Kitchen Remodel Discussion",
    "context_type": "project",
    "contractor_lead_id": "lead-456"  # For contractor agents
}
```

#### **2. Message Saving**  
```python
# Every message gets saved consistently
POST /api/conversations/{conversation_id}/message
{
    "sender_type": "user",  # or "agent"
    "content": "I want to remodel my kitchen",
    "images": ["base64_image_data"],  # Optional
    "metadata": {"extracted_data": {...}}  # Agent-specific data
}
```

#### **3. Memory Storage**
```python
# Agents store different types of memory
POST /api/conversations/{conversation_id}/memory  
{
    "memory_type": "preference",  # or "fact", "project_detail"
    "key": "budget_range", 
    "value": {"min": 5000, "max": 15000},
    "confidence": 0.9
}
```

#### **4. Context Retrieval**
```python
# Agents retrieve context when resuming conversations
GET /api/conversations/{conversation_id}/context
# Returns: messages, memory, agent-specific context, shared state
```

### **Agent-Specific Conversation Patterns:**

#### **CIA (Customer Interface Agent)**
- **Saves**: Project requirements, budget preferences, timeline needs, homeowner communication style
- **Retrieves**: Previous projects, user preferences, conversation history for context
- **Integration**: `/api/cia/` endpoints use unified conversation system automatically

#### **IRIS (Inspiration System)**
- **Saves**: Image analysis results, room preferences, style choices, inspiration board contents  
- **Retrieves**: Previous room analysis, user design history, inspiration context
- **Integration**: `/api/iris/unified-chat` endpoint handles all conversation + image storage

#### **COIA (Contractor Onboarding)**
- **Saves**: Company info, business research, service areas, specialties, conversation progress
- **Retrieves**: Complete contractor profile, research findings, conversation state
- **Integration**: `/api/coia/landing` with contractor_lead_id for permanent memory

#### **BSA (Bid Submission Agent)**
- **Saves**: Bid details, contractor preferences, project understanding, submission context
- **Retrieves**: Contractor profile, previous bids, project requirements
- **Integration**: DeepAgents framework with LangGraph checkpointing + unified storage

#### **Intelligent Messaging System**
- **Saves**: Message analysis results, security flags, agent comments, filtered content
- **Retrieves**: Conversation context for security analysis, previous security actions
- **Integration**: `/api/intelligent-messages/` endpoints for all homeowner-contractor communication

---

## 📊 Memory System Benefits

### **Cross-Agent Intelligence**
- **CIA** can reference IRIS room analysis when discussing projects
- **BSA** can access CIA conversation context when contractors submit bids  
- **All agents** learn from user preferences across different conversations

### **Persistent Context**
- **Return visits**: Users get "Welcome back!" with full context restoration
- **Project continuity**: Conversations resume exactly where they left off
- **Learning system**: Agents improve responses based on user history

### **Data Consistency**
- **Single source of truth**: All conversation data in unified tables
- **No data fragmentation**: Replaces 15+ separate conversation storage systems
- **Easy querying**: Admin can see all user interactions across all agents

---

## 🛠️ Development Workflow

### **Adding New Agent Conversation Support**
1. **Import unified system**: `from routers.unified_conversation_api import create_conversation`
2. **Create conversation**: Use standard conversation creation endpoint
3. **Save messages**: Use unified message saving system
4. **Store context**: Save agent-specific data to memory tables
5. **Retrieve context**: Load previous conversations on agent initialization

### **Testing Conversation Flow**
```bash
# Test conversation creation
curl -X POST "http://localhost:8008/api/conversations/create" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "agent_type": "CIA"}'

# Test message sending  
curl -X POST "http://localhost:8008/api/conversations/{id}/message" \
  -H "Content-Type: application/json" \
  -d '{"sender_type": "user", "content": "Hello"}'
```

---

## 🎯 Key Takeaways

### **Single Backend Architecture**
- **One main.py**: All agents load through single FastAPI application
- **Modular routers**: Each agent has dedicated API router
- **Unified memory**: All agents use same conversation storage system

### **Agent Independence** 
- **Separate agent files**: Each agent has its own core logic
- **Dedicated routers**: API endpoints organized by agent
- **Shared memory**: Common conversation system for consistency

### **Memory Unification**
- **5-table system**: Replaces fragmented storage
- **Cross-agent sharing**: Agents can access each other's context
- **Persistent state**: Conversations survive across sessions

This architecture provides both **agent autonomy** (each agent can work independently) and **system coherence** (unified memory and API structure across all agents).