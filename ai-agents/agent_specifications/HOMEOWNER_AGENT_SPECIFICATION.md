# Homeowner Agent (HMA) - Technical Specification

**Agent ID**: HMA  
**Agent Name**: Homeowner Agent  
**Version**: 1.0  
**Model**: Claude Opus 4 (claude-opus-4-20250514)  
**Status**: 🚧 In Development (Phase 3)  

---

## 🎯 Purpose & Role

The Homeowner Agent (HMA) serves as an intelligent assistant dedicated to helping homeowners manage their projects, communicate effectively with contractors, and make informed decisions throughout the project lifecycle.

### Primary Responsibilities:
1. **Project Management**: Help homeowners modify budgets, timelines, and requirements
2. **Bid Analysis**: Provide intelligent comparison and evaluation of contractor proposals
3. **Communication Coaching**: Guide homeowners in effective contractor communication
4. **Decision Support**: Offer data-driven recommendations for project choices
5. **Group Project Coordination**: Manage related projects (kitchen + bathroom, etc.)

---

## 🏗️ Technical Architecture

### Core Components:
```
🤖 Homeowner Agent (HMA)
├── ProjectModificationEngine - Budget/timeline/scope changes
├── BidAnalysisEngine - Contractor proposal comparison
├── CommunicationCoach - Message guidance and templates
├── DecisionSupportEngine - Data-driven recommendations
└── GroupProjectManager - Multi-project coordination
```

### Integration Points:
- **CIA Agent**: Inherits project conversation history and context
- **CMA Agent**: Routes filtered communications from contractors
- **Database**: Direct access to bid cards, conversations, and project data
- **Frontend**: HomeownerProjectWorkspace interface

---

## 🎯 Capabilities & Features

### 1. Project Modification Assistance
**Input**: Natural language modification requests
**Process**: 
- Parse modification intent (budget, timeline, scope, materials)
- Validate changes against project constraints
- Update bid card data through JAA integration
- Notify relevant contractors of changes

**Examples**:
- "I want to increase the kitchen budget to $50,000"
- "Can we extend the timeline by 2 weeks?"
- "Add premium appliances to the project scope"

### 2. Bid Comparison & Analysis
**Input**: Multiple contractor bids for same project
**Process**:
- Analyze bid components (cost, timeline, materials, approach)
- Identify strengths and weaknesses of each proposal
- Flag unusual pricing or timeline discrepancies
- Provide comparison matrix and recommendations

**Output**: Structured comparison with pros/cons and recommendations

### 3. Communication Coaching
**Input**: Homeowner's intended message to contractor(s)
**Process**:
- Review message for clarity and professionalism
- Suggest improvements or alternative phrasing
- Ensure message contains necessary context and information
- Check for potential misunderstandings

**Output**: Improved message with explanation of changes

### 4. Decision Support
**Input**: Decision scenario (choosing contractor, approving changes, etc.)
**Process**:
- Gather relevant data (contractor history, pricing, reviews)
- Apply decision frameworks (cost-benefit, risk analysis)
- Present options with clear trade-offs
- Recommend optimal choice with reasoning

**Output**: Decision recommendation with supporting data

### 5. Group Project Management
**Input**: Related projects (kitchen + bathroom remodel)
**Process**:
- Identify project relationships and dependencies
- Coordinate timing and contractor scheduling
- Optimize budget allocation across projects
- Manage bulk negotiations and discounts

**Output**: Coordinated project plan with optimized outcomes

---

## 🧠 AI Model Configuration

### Model Parameters:
```yaml
model: claude-opus-4-20250514
temperature: 0.3  # Lower for more consistent, factual responses
max_tokens: 4000
system_prompt: |
  You are the Homeowner Agent for InstaBids, an AI assistant dedicated to helping 
  homeowners successfully manage their home improvement projects. You have access 
  to complete project data, contractor communications, and bid information.
  
  Your role is to:
  1. Help homeowners make informed decisions about their projects
  2. Provide clear analysis of contractor bids and proposals
  3. Coach homeowners in effective communication with contractors
  4. Assist with project modifications and budget planning
  5. Coordinate related projects for optimal outcomes
  
  Always maintain homeowner advocacy while being fair and professional about contractors.
  Base recommendations on data and best practices, not assumptions.
```

### Context Management:
- **Project History**: Full access to CIA conversation history
- **Bid Data**: Complete bid card information with all extracted fields
- **Contractor Information**: Profiles, past performance, current communications
- **Market Data**: Regional pricing, timeline standards, quality indicators

---

## 📊 Data Access & Permissions

### Database Access:
```sql
-- Full read access to homeowner's projects
SELECT * FROM bid_cards WHERE homeowner_id = :homeowner_id;
SELECT * FROM agent_conversations WHERE user_id = :homeowner_id;
SELECT * FROM contractor_bids WHERE bid_card_id IN (:homeowner_bid_cards);
SELECT * FROM communication_threads WHERE homeowner_id = :homeowner_id;

-- Update permissions for project modifications
UPDATE bid_cards SET budget_min = :new_min, budget_max = :new_max 
WHERE id = :bid_card_id AND homeowner_id = :homeowner_id;
```

### External APIs:
- **Pricing Database**: Regional cost data for accurate estimates
- **Contractor Registry**: Background checks, licensing, insurance status
- **Market Analytics**: Trends, seasonal pricing, demand indicators

---

## 🔄 Workflow Integration

### Standard Conversation Flow:
1. **Context Loading**: Retrieve full project and communication history
2. **Intent Analysis**: Determine homeowner's specific need or question
3. **Data Gathering**: Collect relevant information for informed response
4. **Processing**: Apply appropriate engine (modification, analysis, coaching, etc.)
5. **Response Generation**: Provide helpful, actionable guidance
6. **Action Execution**: Update database or trigger other agents as needed
7. **Follow-up Scheduling**: Set reminders or next steps if appropriate

### Integration with Other Agents:
- **CIA Agent**: Inherits context, may escalate complex modifications
- **CMA Agent**: Receives coaching input for message filtering and routing
- **JAA Agent**: Triggers bid card updates for project modifications
- **COIA Agent**: Indirectly coordinates through CMA for contractor communications

---

## 🛡️ Security & Privacy

### Data Protection:
- **Homeowner Advocacy**: Always prioritize homeowner's best interests
- **Confidentiality**: Never share homeowner's budget limits or private concerns with contractors
- **Secure Processing**: All data encrypted and processed within secure boundaries
- **Audit Trail**: Log all recommendations and actions for accountability

### Access Controls:
- **Homeowner-Specific**: Only access data for authenticated homeowner
- **Time-Limited Sessions**: Authentication tokens expire appropriately
- **Action Permissions**: Verify homeowner authority for any modifications
- **Privacy Compliance**: Follow GDPR/CCPA requirements for data handling

---

## 🚀 API Endpoints

### Core HMA Endpoints:
```
POST /api/agents/homeowner/chat
- Purpose: General homeowner assistance and conversation
- Input: message, project_context, session_id
- Output: response, actions_taken, follow_up_needed

POST /api/agents/homeowner/analyze-bids
- Purpose: Compare and analyze contractor bids
- Input: bid_card_id, contractor_bids[]
- Output: comparison_matrix, recommendations, risk_assessment

POST /api/agents/homeowner/modify-project
- Purpose: Help with project modifications
- Input: bid_card_id, modification_request, constraints
- Output: modified_project, impact_analysis, contractor_notifications

POST /api/agents/homeowner/coach-communication
- Purpose: Improve homeowner messages to contractors
- Input: intended_message, recipient_contractors, context
- Output: improved_message, explanation, communication_tips

GET /api/agents/homeowner/project-status/{bid_card_id}
- Purpose: Get comprehensive project status and recommendations
- Input: bid_card_id
- Output: project_summary, active_communications, next_steps, recommendations
```

---

## 📈 Success Metrics

### Performance KPIs:
- **Response Accuracy**: 95% of recommendations rated helpful by homeowners
- **Project Success Rate**: 85% of HMA-assisted projects complete successfully
- **Communication Quality**: 90% improvement in homeowner-contractor message clarity
- **Decision Satisfaction**: 4.5+ star rating for decision support features

### Technical KPIs:
- **Response Time**: <2 seconds for standard queries
- **Context Accuracy**: 98% accurate project context retrieval
- **Integration Success**: 99.9% successful API calls to other agents
- **Data Consistency**: Zero data corruption or loss incidents

---

## 🔧 Development Requirements

### Phase 3 Deliverables (Weeks 5-6):
1. **Core HMA Engine**: Basic project assistance and bid analysis
2. **API Integration**: Connect with CIA, CMA, and database
3. **Frontend Integration**: HomeownerProjectWorkspace interface
4. **Testing Suite**: Comprehensive testing of all capabilities
5. **Documentation**: User guides and technical documentation

### Dependencies:
- **CMA Agent**: Must be completed first for communication filtering
- **Database Schema**: New tables for messages and bids
- **Frontend Components**: HomeownerProjectWorkspace interface
- **Authentication**: User session management and permissions

---

## 🧪 Testing Strategy

### Test Scenarios:
1. **Project Modification**: Test budget, timeline, and scope changes
2. **Bid Analysis**: Compare multiple contractor proposals
3. **Communication Coaching**: Improve homeowner messages
4. **Decision Support**: Choose between contractor options
5. **Group Projects**: Coordinate multiple related projects
6. **Error Handling**: Graceful failure and recovery
7. **Security**: Unauthorized access attempts and data protection

### Test Data:
- **Sample Projects**: Kitchen, bathroom, roofing, landscaping
- **Mock Contractors**: Various proposal styles and pricing
- **Homeowner Personas**: Different experience levels and preferences
- **Edge Cases**: Unusual requests, conflicting data, system errors

---

*This specification serves as the technical blueprint for the Homeowner Agent (HMA) development. All implementation should align with these requirements and capabilities.*