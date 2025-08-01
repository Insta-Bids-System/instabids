# Product Requirements Document (PRD)
# Homeowner-Contractor Communication & Project Management System

**Version**: 1.0  
**Date**: July 31, 2025  
**Status**: Planning Phase  
**Priority**: High  

---

## 📋 Executive Summary

This PRD outlines the development of a comprehensive communication and project management system that enables secure, AI-mediated interactions between homeowners and contractors within the InstaBids platform. The system replaces basic bid card displays with rich, interactive workspaces that maintain platform control while providing exceptional user experiences.

---

## 🎯 Problem Statement

### Current State Issues:
1. **Basic Bid Card Display**: Homeowners see minimal project information despite rich backend data (10-12 extracted fields)
2. **No Communication System**: No way for homeowners and contractors to communicate through the platform
3. **Missing Project Management**: No tools for project modifications, bid comparisons, or ongoing communication
4. **Security Gaps**: Risk of users bypassing platform through direct contact information exchange
5. **Limited Contractor Tools**: No AI assistance for contractors creating competitive bids

### Business Impact:
- **Revenue Leakage**: Users bypass platform after initial connection
- **Poor User Experience**: Rich data not properly displayed or utilized
- **Competitive Disadvantage**: Other platforms offer better communication tools
- **Scalability Issues**: Current architecture cannot support complex multi-user interactions

---

## 🎯 Goals & Success Metrics

### Primary Goals:
1. **Platform Control**: Keep all communication within InstaBids system
2. **Rich User Experience**: Display and utilize all extracted project data
3. **Secure Communication**: Filter out contact information and maintain privacy
4. **AI-Assisted Workflows**: Provide intelligent assistance to both user types
5. **Scalable Architecture**: Support multiple contractors per project, group bidding

### Success Metrics:
- **User Retention**: 90% of users continue using platform communication (vs. bypassing)
- **Project Completion**: 80% of projects with active communication complete through platform
- **Communication Volume**: 5x increase in platform messages vs. current external communication
- **User Satisfaction**: 4.5+ star rating for communication features
- **Revenue Protection**: 95% of transactions remain on-platform

---

## 👥 User Stories & Requirements

### 🏠 Homeowner Stories:

**As a homeowner, I want to:**
1. **View Complete Project Details**: See all 10-12 extracted data fields in an organized, expandable interface
2. **Manage Project Images**: View, organize, and selectively share photos with different contractors
3. **Communicate with Contractors**: Message individual contractors or broadcast to all
4. **Compare Bids**: View contractor proposals side-by-side with comparison tools
5. **Modify Projects**: Chat with AI to adjust budgets, timelines, or requirements
6. **Track Communications**: See complete message history with each contractor
7. **Share Documents**: Upload and share additional project documents securely
8. **Group Project Management**: Connect related projects (kitchen + bathroom) for bulk negotiations

### 👷 Contractor Stories:

**As a contractor, I want to:**
1. **View Project Brief**: See relevant project details without sensitive homeowner information
2. **Communicate with Homeowner**: Direct messaging thread with project context
3. **Submit Competitive Bids**: AI-assisted bid creation with cost breakdowns and timelines
4. **Share Portfolio**: Showcase relevant past work and credentials
5. **Receive Notifications**: Real-time alerts for new messages and project updates
6. **Access Project Images**: View photos shared specifically with me
7. **Get AI Assistance**: Help with bid writing, timeline estimation, and pricing
8. **Track Bid Status**: Know where my proposal stands in the selection process

### 🤖 System Stories:

**As an AI system, I need to:**
1. **Filter Communications**: Remove contact information and inappropriate content
2. **Route Messages**: Ensure contractors only see their communications
3. **Provide Context**: Maintain project awareness across all interactions
4. **Assist Users**: Offer intelligent help for both homeowners and contractors
5. **Sync Data**: Keep all interfaces updated in real-time
6. **Maintain Security**: Enforce privacy and platform control
7. **Learn Patterns**: Improve recommendations based on successful projects

---

## 🏗️ Technical Architecture

### **Agent System Architecture:**
```
🏠 Homeowner ←→ 🤖 Homeowner Agent (HMA - New)
                       ↕️
               🤖 Communication Management Agent (CMA - New)
                       ↕️
👷 Contractor ←→ 🤖 COIA Agent (Existing)
```

### **Core Components:**

#### 1. **Data Layer**
```
🗄️ Bid Card Data (Source of Truth)
├── 10-12 extracted project fields
├── Images and documents
├── Timeline and budget information
└── Status and requirements

📊 Communication Data
├── Message threads (homeowner ↔ contractor pairs)
├── Document sharing permissions
├── Bid submissions and responses
└── Activity logs and audit trails
```

#### 2. **Agent Layer**
```
🤖 Homeowner Agent (HMA) - New
├── Project modification assistance
├── Bid comparison analysis
├── Communication coaching
└── Group project coordination

🤖 Communication Management Agent (CMA) - New
├── Message filtering and redaction
├── Contact information blocking
├── Thread routing and isolation
└── Content policy enforcement

🤖 COIA Agent (Existing)
├── Contractor onboarding
├── Bid creation assistance
├── Communication support
└── Project analysis
```

#### 3. **Interface Layer**
```
🏠 HomeownerProjectWorkspace
├── ProjectOverview (full bid card display)
├── ContractorCommunications (tabbed messaging)
├── BidSubmissionsManager (comparison tools)
└── ProjectAssistant (HMA integration)

👷 ContractorBidWorkspace
├── ProjectBriefView (filtered information)
├── HomeownerCommunication (single thread)
├── BidSubmissionInterface (AI-assisted)
└── ContractorAssistant (COIA integration)
```

#### 4. **Communication Hub**
```
🔄 MessageRouter
├── Thread management and isolation
├── Real-time message delivery
├── Agent filtering integration
└── Notification system

📁 DocumentManager
├── Scoped file sharing
├── Permission management
├── Version control
└── Access logging
```

---

## 🚀 Development Phases

### **Phase 1: Enhanced Homeowner Interface (Weeks 1-2)**
**Goal**: Fix current bid card display and add basic project management

**Deliverables**:
- ✅ Enhanced bid card component showing all 10-12 fields
- ✅ Image gallery with proper photo display
- ✅ Expandable/collapsible project details
- ✅ Basic project modification through CIA agent chat
- ✅ Improved API endpoints for frontend data consumption

**Success Criteria**:
- Homeowners can see complete project information
- Photos display correctly from backend storage
- Users can modify projects through chat interface

### **Phase 2: Communication Foundation (Weeks 3-4)**
**Goal**: Build secure messaging infrastructure

**Deliverables**:
- 🔨 Communication Management Agent (CMA) development
- 🔨 Message filtering and routing system
- 🔨 Real-time messaging infrastructure (WebSocket)
- 🔨 Thread isolation and management
- 🔨 Basic homeowner-contractor messaging

**Success Criteria**:
- Messages route correctly between users
- Contact information is automatically filtered
- Real-time communication works reliably

### **Phase 3: Homeowner Agent & Advanced Features (Weeks 5-6)**
**Goal**: Add intelligent homeowner assistance

**Deliverables**:
- 🔨 Homeowner Agent (HMA) development
- 🔨 Bid comparison and analysis tools
- 🔨 Multi-contractor communication management
- 🔨 Document sharing with permission controls
- 🔨 Group bidding project connections

**Success Criteria**:
- Homeowners get intelligent project assistance
- Bid comparison tools provide clear value
- Document sharing works securely

### **Phase 4: Contractor Interface & AI Assistance (Weeks 7-8)**
**Goal**: Complete contractor experience

**Deliverables**:
- 🔨 ContractorBidWorkspace interface
- 🔨 Enhanced COIA agent for bid assistance
- 🔨 Bid submission and management system
- 🔨 Contractor-specific document access
- 🔨 Portfolio and credential showcasing

**Success Criteria**:
- Contractors can submit competitive bids easily
- AI assistance improves bid quality
- Interface is clean and focused

### **Phase 5: Advanced Features & Optimization (Weeks 9-10)**
**Goal**: Polish and advanced capabilities

**Deliverables**:
- 🔨 Advanced bid comparison and analytics
- 🔨 Automated follow-up and reminder systems
- 🔨 Mobile responsive optimization
- 🔨 Performance monitoring and optimization
- 🔨 User feedback integration and improvements

**Success Criteria**:
- System performs well under load
- Mobile experience is excellent
- User feedback is highly positive

---

## 🛠️ Technical Specifications

### **New Agent Requirements:**

#### **Homeowner Agent (HMA)**
- **Model**: Claude Opus 4
- **Capabilities**:
  - Project modification and optimization
  - Bid analysis and comparison
  - Budget and timeline guidance
  - Communication coaching
  - Group project coordination
- **Integration**: Direct connection to bid card data and communication hub

#### **Communication Management Agent (CMA)**
- **Model**: Claude Opus 4 + Rule-based filtering
- **Capabilities**:
  - Contact information detection and redaction
  - Message content filtering
  - Communication policy enforcement
  - Thread routing and isolation
  - Escalation detection and handling
- **Integration**: Central hub for all platform communications

### **Database Schema Updates:**

#### **New Tables Needed:**
```sql
-- Message threads between homeowner and individual contractors
CREATE TABLE communication_threads (
    id UUID PRIMARY KEY,
    bid_card_id UUID REFERENCES bid_cards(id),
    homeowner_id UUID REFERENCES profiles(id),
    contractor_id UUID REFERENCES profiles(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Individual messages within threads
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    thread_id UUID REFERENCES communication_threads(id),
    sender_id UUID REFERENCES profiles(id),
    sender_type VARCHAR(20), -- 'homeowner' or 'contractor'
    content TEXT,
    message_type VARCHAR(20) DEFAULT 'text', -- 'text', 'image', 'document'
    filtered_content TEXT, -- CMA-processed version
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Document sharing with scoped permissions
CREATE TABLE shared_documents (
    id UUID PRIMARY KEY,
    bid_card_id UUID REFERENCES bid_cards(id),
    uploader_id UUID REFERENCES profiles(id),
    file_path TEXT,
    file_name TEXT,
    file_type VARCHAR(50),
    shared_with JSONB, -- Array of contractor IDs with access
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bid submissions from contractors
CREATE TABLE contractor_bids (
    id UUID PRIMARY KEY,
    bid_card_id UUID REFERENCES bid_cards(id),
    contractor_id UUID REFERENCES profiles(id),
    bid_amount DECIMAL(10,2),
    timeline_weeks INTEGER,
    proposal_details JSONB,
    status VARCHAR(20) DEFAULT 'submitted',
    submitted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **API Endpoints:**

#### **Communication Endpoints:**
```
POST /api/communication/send-message
GET  /api/communication/threads/{bid_card_id}
GET  /api/communication/messages/{thread_id}
POST /api/communication/share-document
GET  /api/communication/documents/{bid_card_id}
```

#### **Bid Management Endpoints:**
```
POST /api/bids/submit
GET  /api/bids/homeowner/{homeowner_id}
GET  /api/bids/contractor/{contractor_id}
PUT  /api/bids/{bid_id}/status
GET  /api/bids/compare/{bid_card_id}
```

#### **Agent Integration Endpoints:**
```
POST /api/agents/homeowner/chat
POST /api/agents/communication/filter
POST /api/agents/contractor/assist
GET  /api/agents/context/{bid_card_id}
```

---

## 🔒 Security & Privacy Requirements

### **Data Protection:**
1. **Message Encryption**: All communications encrypted in transit and at rest
2. **Access Control**: Strict role-based access to messages and documents
3. **Audit Logging**: Complete trail of all communications and data access
4. **Data Retention**: Configurable retention policies for different data types

### **Privacy Controls:**
1. **Contact Information Filtering**: Automatic detection and redaction
2. **Thread Isolation**: Contractors cannot see each other's communications
3. **Selective Sharing**: Homeowners control what each contractor sees
4. **Platform Boundaries**: Strong enforcement of platform-only communication

### **Compliance:**
1. **GDPR Compliance**: Data portability and deletion rights
2. **CCPA Compliance**: California privacy law adherence
3. **Industry Standards**: Follow construction industry privacy best practices
4. **Terms of Service**: Clear policies on communication and data use

---

## 📊 Success Criteria & KPIs

### **Technical KPIs:**
- **Message Delivery**: 99.9% successful message delivery
- **Response Time**: <200ms for message sending
- **Uptime**: 99.95% system availability
- **Scalability**: Support 1000+ concurrent conversations

### **Business KPIs:**
- **Platform Retention**: 90% of communications stay on platform
- **User Engagement**: 5x increase in platform message volume
- **Project Completion**: 80% completion rate for active projects
- **Revenue Protection**: 95% of transactions remain on-platform

### **User Experience KPIs:**
- **User Satisfaction**: 4.5+ star rating for communication features
- **Feature Adoption**: 75% of users actively use messaging within 30 days
- **Support Tickets**: <5% increase despite new feature complexity
- **Time to First Message**: <2 minutes from project creation

---

## 🚨 Risks & Mitigation

### **Technical Risks:**
1. **Scalability Issues**: Plan for horizontal scaling from day one
2. **Message Filtering Accuracy**: Extensive testing of CMA agent
3. **Real-time Performance**: WebSocket connection management and fallbacks
4. **Data Consistency**: Proper synchronization across multiple interfaces

### **Business Risks:**
1. **User Bypass**: Strong value proposition for staying on platform
2. **Contractor Adoption**: Ensure contractor interface provides clear value
3. **Feature Complexity**: Phase rollout and user education
4. **Revenue Impact**: Monitor for any negative effects on transaction volume

### **Mitigation Strategies:**
- **Comprehensive Testing**: Extensive QA for all communication scenarios
- **Gradual Rollout**: Phase-based launch with user feedback integration
- **Performance Monitoring**: Real-time dashboards and alerting
- **User Support**: Dedicated support team for communication features

---

## 🎯 Next Steps

### **Immediate Actions (Week 1):**
1. **Document Review**: Stakeholder approval of this PRD
2. **Architecture Finalization**: Technical team review and refinement
3. **Resource Allocation**: Assign development team and timeline
4. **Phase 1 Kickoff**: Begin enhanced homeowner interface development

### **Documentation Updates:**
1. **Update CLAUDE.md**: Add new agent specifications and architecture
2. **Create Agent Specifications**: Detailed specs for HMA and CMA agents
3. **Database Migration Plan**: Schema updates and data migration strategy
4. **API Documentation**: Complete endpoint specifications and examples

### **Stakeholder Communication:**
1. **Development Team Briefing**: Technical requirements and timeline
2. **Design Team Coordination**: UI/UX requirements for new interfaces
3. **QA Team Planning**: Test strategy for complex communication scenarios
4. **Product Team Alignment**: Feature prioritization and success metrics

---

## 🔄 Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | July 31, 2025 | Initial PRD creation | Claude Code |

---

*This PRD serves as the master planning document for the Homeowner-Contractor Communication & Project Management System. All development should reference and align with these requirements.*