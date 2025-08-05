# InstaBids - AI-Powered Contractor Marketplace

<div align="center">
  <img src="assets/instabids-logo.png" alt="Instabids Logo" width="200"/>
  
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
  [![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
  [![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](#)
  
  **AI-powered contractor marketplace with real-time monitoring and intelligent automation**
</div>

## 🚀 System Overview

InstaBids is a production-ready AI-powered marketplace featuring **7 operational agents** that handle everything from homeowner conversations to contractor outreach. The system includes real-time monitoring, multi-project memory, and verified email/form automation.

### ✅ **Current Status: FULLY OPERATIONAL**
- **7 Core Agents**: All tested and verified with real-world functionality
- **Admin Dashboard**: Real-time monitoring and management system
- **Email Automation**: Verified MCP integration with actual email sending
- **Form Automation**: Confirmed website form submissions with proof
- **Multi-Project Memory**: Cross-project awareness and context persistence
- **Database Integration**: 33+ tables in Supabase with full CRUD operations

### 🎯 **Key Features**
- 🤖 **7 Specialized AI Agents** with Claude Opus 4 & Claude 3.7 Sonnet
- 💬 **Intelligent Conversations** - Multi-turn project scoping with memory
- 📧 **Real Email Outreach** - Verified contractor outreach via MCP tools
- 🌐 **Website Form Automation** - Automated contractor website submissions  
- 📊 **Live Admin Dashboard** - Real-time monitoring with WebSocket updates
- 🎨 **Design Assistant** - AI-powered inspiration and style recognition
- 💾 **Multi-Project Memory** - Cross-project user awareness and context

## 🏗️ Project Structure

```
instabids/
├── web/                    # React + Vite frontend (port 5173)
├── ai-agents/             # Python backend with AI agents (port 8008)
│   ├── agents/           # 8 specialized AI agents
│   ├── api/              # FastAPI endpoints
│   └── database/         # Supabase integration
├── mobile/                # React Native apps (future)
├── supabase/             # Database schema and functions
├── agent_specifications/ # Detailed docs for development agents
└── additional_projects/  # 5 expansion projects for dev teams
```

## 🤖 The 7 Operational AI Agents

### **Core Pipeline Agents** ✅ FULLY TESTED
1. **CIA** (Customer Interface Agent) - Claude Opus 4 conversations with multi-project memory
2. **JAA** (Job Assessment Agent) - LangGraph workflow for bid card generation  
3. **CDA** (Contractor Discovery Agent) - 3-tier contractor sourcing system
4. **EAA** (External Acquisition Agent) - Multi-channel outreach with real email sending
5. **WFA** (Website Form Automation Agent) - Playwright browser automation with verified submissions

### **Specialized Agents** ✅ OPERATIONAL
6. **IRIS** (Design Inspiration Assistant) - Claude 3.7 Sonnet for design analysis
7. **COIA** (Contractor Interface Agent) - Complete contractor onboarding with auth

### **Supporting Infrastructure** ✅ PRODUCTION-READY
- **Admin Dashboard**: Real-time monitoring with WebSocket integration
- **Multi-Project Memory**: Cross-project user context and preferences
- **Timing & Orchestration**: Mathematical contractor calculation system
- **Database Integration**: 33+ Supabase tables with full CRUD operations

## 📚 Essential Documentation

**For Developers & Contributors - Read These First:**
- **[Complete System Architecture](docs/agent_6_central_docs/SYSTEM_INTERDEPENDENCY_MAP.md)** - How all components connect
- **[Complete File Structure](docs/agent_6_central_docs/CODEBASE_OVERVIEW.md)** - Where everything is located  
- **[Development Workflow](docs/agent_6_central_docs/DEVELOPMENT_WORKFLOW.md)** - Standardized process for all agents
- **[Current Build Status](CLAUDE.md)** - ⭐ CRITICAL - Current system state & instructions

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account
- API keys for Claude Opus 4 & Claude 3.7 Sonnet

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Insta-Bids-System/instabids.git
cd instabids
```

2. Install frontend dependencies:
```bash
cd web
npm install
```

3. Install backend dependencies:
```bash
cd ../ai-agents
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Start the development servers:

Frontend:
```bash
cd web
npm run dev
```

Backend:
```bash
cd ai-agents
python main.py
```

## 🛠️ Tech Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Python + FastAPI + LangGraph
- **Database**: Supabase (PostgreSQL + Auth + Storage + Realtime)
- **AI Models**: Multi-model approach (Claude 3.5, Grok 4, O3, Groq)
- **Infrastructure**: Vercel (frontend), Modal/Railway (AI services)

## 📚 Additional Projects

The repository includes 5 major expansion projects in the `additional_projects/` folder:

1. **Brand Ambassador Platform** - Gamified referral system
2. **Social Media Automation** - Full autonomous brand presence
3. **Influencer Partnership System** - Automated influencer discovery
4. **Property Manager Platform** - B2B expansion for property management
5. **AI Education Platform** - Transform contractors with AI knowledge

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Vision

Instabids aims to become THE AI platform for the entire contractor ecosystem, transforming from a simple marketplace into the operating system that powers the trades industry.

---

<div align="center">
  <p>Built with ❤️ by the Instabids Team</p>
  <p>
    <a href="https://instabids.com">Website</a> •
    <a href="https://docs.instabids.com">Documentation</a> •
    <a href="https://twitter.com/instabids">Twitter</a>
  </p>
</div>
