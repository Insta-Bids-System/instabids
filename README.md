# Instabids - AI-Powered Marketplace for Home Improvement

<div align="center">
  <img src="assets/instabids-logo.png" alt="Instabids Logo" width="200"/>
  
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
  [![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
  
  **Revolutionizing home improvement by eliminating traditional sales meetings through AI**
</div>

## 🚀 Overview

Instabids is an AI-powered marketplace that connects homeowners with contractors without the need for traditional sales meetings. Homeowners save an average of 20% on projects while contractors only pay when selected, eliminating wasted lead costs.

### Key Features
- 🤖 **8 Specialized AI Agents** orchestrating the entire process
- 💬 **Conversational Project Scoping** - Chat with AI, upload photos, get professional bid cards
- 💰 **Pay-for-Connection Model** - Contractors only pay $30 when selected
- 🎯 **No Corporate Middleman** - Money flows directly between parties
- 📱 **Multi-Platform** - Web, mobile (coming soon), and API access

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

## 🤖 The 8 AI Agents

1. **CIA** (Customer Interface Agent) - Converses with homeowners using Claude 3.5 Sonnet
2. **JAA** (Job Assessment Agent) - Converts conversations into structured bid cards
3. **CDA** (Contractor Discovery Agent) - Finds qualified contractors using Grok 4
4. **EAA** (External Acquisition Agent) - Recruits new contractors when needed
5. **WFA** (Website Form Automation) - Automates contractor outreach
6. **SMA** (Secure Messaging Agent) - Manages anonymous communication
7. **CHO** (Communication Hub Orchestrator) - Routes all messages
8. **CRA** (Contractor Rating Agent) - Scores contractors using O3

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account
- API keys for Claude, Grok, and other AI services

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
