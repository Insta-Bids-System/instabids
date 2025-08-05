# InstaBids Complete Database Schema Map
**Last Updated**: August 2, 2025  
**Purpose**: Complete reference for all agents - understand every table and relationship

## 🎯 **DATABASE OVERVIEW**

### **Core Statistics**
- **Total Tables**: 41
- **Core Business Logic**: 15 tables
- **Supporting Systems**: 26 tables
- **Database Type**: Supabase (PostgreSQL)
- **Access Pattern**: Multi-agent shared database

## 📊 **COMPLETE TABLE INVENTORY** (All 41 Tables)

### **🏠 HOMEOWNER & PROJECT CORE** (7 tables)
```sql
homeowners              -- Homeowner profiles and accounts
├── profiles            -- Extended homeowner profile data  
├── projects            -- All home improvement projects
├── project_contexts    -- Project conversation context
├── project_photos      -- Project-related images
├── project_summaries   -- Project summary data
└── photo_storage       -- General photo storage system
```

### **💼 BID CARDS & BIDDING SYSTEM** (4 tables)
```sql
bid_cards               -- Central bid card entities
├── bids                -- Submitted contractor bids
├── bid_card_views      -- Who viewed each bid card
└── bid_card_engagement_events  -- All interactions with bid cards
```

### **🔍 CONTRACTOR DISCOVERY** (6 tables)
```sql
contractor_leads        -- Discovered potential contractors
├── contractors         -- Verified contractor accounts
├── potential_contractors -- Early discovery results
├── potential_contractors_backup -- Backup discovery data
├── contractor_discovery_cache -- Discovery performance cache
└── discovery_runs      -- Discovery session tracking
```

### **📧 OUTREACH & CAMPAIGNS** (8 tables)
```sql
outreach_campaigns      -- Campaign orchestration
├── bid_card_distributions -- Where bid cards were shared
├── campaign_contractors -- Specific contractors in campaigns
├── campaign_check_ins  -- Timing system orchestration
├── contractor_outreach_attempts -- Individual outreach attempts
├── email_tracking_events -- Email delivery tracking
├── followup_attempts   -- Follow-up outreach attempts
└── followup_logs       -- Follow-up activity logs
```

### **💬 RESPONSES & ENGAGEMENT** (5 tables)
```sql
contractor_responses    -- Contractor replies to outreach
├── response_events     -- All response event tracking
├── contractor_engagement_summary -- Engagement rollup metrics
├── manual_followup_tasks -- Human intervention tasks
└── message_templates   -- Template management system
```

### **🎨 INSPIRATION SYSTEM** (4 tables)
```sql
inspiration_boards      -- Homeowner inspiration collections
├── inspiration_conversations -- Iris chat conversations
├── inspiration_images  -- Images used in inspiration
└── generated_dream_spaces -- AI-generated design visions
```

### **🤖 AI AGENT SYSTEM** (4 tables)
```sql
agent_conversations     -- CIA/agent conversation storage
├── user_memories       -- Cross-conversation memory
├── vision_compositions -- AI vision analysis results
└── notifications       -- System notifications
```

### **💰 BUSINESS OPERATIONS** (3 tables)
```sql
payments               -- Payment processing
├── reviews            -- Reviews and ratings
└── messages           -- General messaging system
```

## 🔗 **CRITICAL RELATIONSHIPS**

### **Bid Card Ecosystem Flow**
```
homeowners → projects → bid_cards → outreach_campaigns
                     ↓                    ↓
              bid_card_views     campaign_contractors
                     ↓                    ↓  
           bid_card_engagement   contractor_outreach_attempts
                     ↓                    ↓
                   bids         contractor_responses
```

### **Contractor Journey Flow**  
```
contractor_leads → contractors → campaign_contractors
       ↓                              ↓
discovery_runs              contractor_outreach_attempts
       ↓                              ↓
contractor_discovery_cache    contractor_responses
                                      ↓
                           contractor_engagement_summary
```

### **Agent Data Flow**
```
agent_conversations → user_memories
        ↓                    ↓
project_contexts    inspiration_conversations  
        ↓                    ↓
   bid_cards        inspiration_boards
        ↓                    ↓
 vision_compositions  generated_dream_spaces
```

## 🎯 **AGENT OWNERSHIP BY TABLE**

### **Agent 1 (Frontend Flow)**
- `agent_conversations` - CIA chat storage
- `project_contexts` - Project conversation context  
- `vision_compositions` - Image analysis results
- `user_memories` - Multi-project memory

### **Agent 2 (Backend Core)**
- `bid_cards` - Central bid card management
- `contractor_leads` - Discovery results
- `outreach_campaigns` - Campaign orchestration
- `campaign_contractors` - Campaign targeting
- `contractor_outreach_attempts` - Outreach execution
- `bid_card_distributions` - Distribution tracking
- `email_tracking_events` - Email delivery
- `campaign_check_ins` - Timing system
- `contractor_responses` - Response capture
- `response_events` - Response tracking
- `contractor_engagement_summary` - Engagement metrics

### **Agent 3 (Homeowner UX)**
- `inspiration_boards` - Inspiration collections
- `inspiration_conversations` - Iris chat
- `inspiration_images` - Inspiration imagery
- `generated_dream_spaces` - AI-generated visions
- `photo_storage` - Image management

### **Agent 4 (Contractor UX)**
- `contractors` - Contractor accounts
- `bids` - Bid submissions
- `contractor_responses` - Contractor replies
- `profiles` - Contractor profiles

### **Shared Tables**
- `homeowners` - Created by Agent 1, used by all
- `projects` - Created by Agent 1, used by Agent 2
- `project_photos` - Used by Agent 1 & 3
- `messages` - Cross-agent communication
- `notifications` - System-wide notifications
- `payments` - Business operations
- `reviews` - Quality tracking

## 🚨 **CRITICAL DEPENDENCIES**

### **Must Exist First**
1. `homeowners` → Required for all project creation
2. `projects` → Required for bid card generation  
3. `bid_cards` → Required for contractor outreach
4. `contractor_leads` → Required for campaign targeting

### **Cascade Delete Relationships**
- `homeowners` deletion → cascades to `projects`, `bid_cards`
- `projects` deletion → cascades to `bid_cards`, `project_photos`
- `bid_cards` deletion → cascades to `bids`, `bid_card_views`
- `outreach_campaigns` deletion → cascades to `campaign_contractors`

## 📋 **COMMON QUERIES BY AGENT**

### **Agent 1 Queries**
```sql
-- Get homeowner's conversation history
SELECT * FROM agent_conversations WHERE user_id = ?

-- Get project context for bid card creation  
SELECT * FROM project_contexts WHERE project_id = ?

-- Store vision analysis results
INSERT INTO vision_compositions (project_id, analysis_data, ...)
```

### **Agent 2 Queries**
```sql
-- Get contractor leads for campaign
SELECT * FROM contractor_leads WHERE project_id = ?

-- Track outreach attempts
INSERT INTO contractor_outreach_attempts (campaign_id, contractor_id, ...)

-- Check campaign timing
SELECT * FROM campaign_check_ins WHERE campaign_id = ?
```

### **Agent 3 Queries**  
```sql
-- Get inspiration board data
SELECT * FROM inspiration_boards WHERE homeowner_id = ?

-- Store Iris conversation
INSERT INTO inspiration_conversations (conversation_data, ...)

-- Generate dream space
INSERT INTO generated_dream_spaces (inspiration_board_id, ...)
```

## ⚠️ **SCHEMA MAINTENANCE RULES**

### **For All Agents**
1. **Never drop tables** without checking dependencies
2. **Always use transactions** for multi-table operations
3. **Check foreign key constraints** before insertions
4. **Use proper error handling** for constraint violations

### **Schema Changes**
1. **Agent 6 approval required** for any schema modifications
2. **Update this document** immediately after schema changes  
3. **Test all affected agents** after schema updates
4. **Backup database** before major schema changes

## 📍 **QUICK REFERENCE**

### **Find Table Relationships**
```sql
-- Check what references a table
SELECT * FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY' AND table_name = 'your_table';

-- Check table dependencies  
SELECT * FROM information_schema.referential_constraints;
```

### **Performance Monitoring**
- Monitor `contractor_discovery_cache` for discovery performance
- Track `campaign_check_ins` for timing system health
- Watch `contractor_engagement_summary` for campaign effectiveness

---

**This is the definitive database reference for all InstaBids agents. Keep this updated as the system evolves!**