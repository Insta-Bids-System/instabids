# main.py Refactoring Plan - Breaking Up the Monolith

**Date**: August 1, 2025  
**Problem**: main.py has become a 1693-line monolith that every agent modifies  
**Goal**: Modularize it so agents can work independently without conflicts

## 🔍 CURRENT PROBLEMS

1. **Size**: 1693 lines and growing with every feature
2. **Merge Conflicts**: Multiple agents editing same file = constant conflicts
3. **Hard to Navigate**: Finding specific endpoints is difficult
4. **Testing Nightmare**: Can't test individual components easily
5. **Circular Dependencies**: Everything depends on everything

## 🎯 PROPOSED REFACTORING STRUCTURE

### **Option 1: Blueprint/Router Pattern** (RECOMMENDED)

```
ai-agents/
├── main.py                    # Only app initialization & router registration (100 lines)
├── routers/
│   ├── __init__.py
│   ├── cia_routes.py         # CIA endpoints (Agent 1 territory)
│   ├── jaa_routes.py         # JAA endpoints  
│   ├── cda_routes.py         # CDA endpoints (Agent 2 territory)
│   ├── eaa_routes.py         # EAA endpoints
│   ├── admin_routes.py       # Admin dashboard endpoints
│   ├── contractor_routes.py  # Contractor portal (Agent 4 territory)
│   ├── homeowner_routes.py   # Homeowner features (Agent 3 territory)
│   └── websocket_routes.py   # All WebSocket endpoints
├── services/
│   ├── agent_manager.py      # Agent initialization/lifecycle
│   ├── auth_service.py       # Authentication logic
│   └── monitoring_service.py # System monitoring
└── core/
    ├── config.py             # Configuration management
    ├── dependencies.py       # Shared dependencies
    └── middleware.py         # CORS, auth middleware
```

### **New main.py Structure** (Simplified):
```python
"""Instabids API Server - Simplified Entry Point"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.config import settings
from core.middleware import setup_middleware
from services.agent_manager import AgentManager
from routers import (
    cia_routes, jaa_routes, cda_routes, eaa_routes,
    admin_routes, contractor_routes, homeowner_routes,
    websocket_routes
)

# Initialize agent manager
agent_manager = AgentManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    await agent_manager.initialize_all_agents()
    yield
    await agent_manager.shutdown_all_agents()

# Create app
app = FastAPI(
    title="Instabids AI Agents API",
    version="2.0.0",
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Register all routers
app.include_router(cia_routes.router, prefix="/api/cia", tags=["CIA"])
app.include_router(jaa_routes.router, prefix="/api/jaa", tags=["JAA"])
app.include_router(cda_routes.router, prefix="/api/cda", tags=["CDA"])
app.include_router(eaa_routes.router, prefix="/api/eaa", tags=["EAA"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])
app.include_router(contractor_routes.router, prefix="/api/contractor", tags=["Contractor"])
app.include_router(homeowner_routes.router, prefix="/api/homeowner", tags=["Homeowner"])
app.include_router(websocket_routes.router, tags=["WebSocket"])

# Health check
@app.get("/")
async def root():
    return {"status": "online", "service": "Instabids API v2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
```

## 📁 BENEFITS OF THIS APPROACH

### **1. Agent Independence**
- Agent 1 only edits `homeowner_routes.py`
- Agent 2 only edits `cda_routes.py` and `eaa_routes.py`
- Agent 3 only edits `homeowner_routes.py` 
- Agent 4 only edits `contractor_routes.py`
- No more merge conflicts!

### **2. Clear Ownership**
```python
# In each router file:
"""
CIA Routes - Customer Interface Agent API Endpoints
Owner: Agent 1 (Frontend Flow)
DO NOT MODIFY without consulting Agent 1
"""
```

### **3. Easy Testing**
```python
# Test individual routers
from routers.cia_routes import router
# Test just CIA endpoints without loading entire app
```

### **4. Better Organization**
- Find endpoints quickly by domain
- Related code stays together
- Cleaner imports and dependencies

## 🔧 IMPLEMENTATION PLAN

### **Phase 1: Create Router Structure** (2 hours)
1. Create `routers/` directory structure
2. Create empty router files with proper imports
3. Set up `core/` utilities

### **Phase 2: Move Endpoints** (4 hours)
1. Move CIA endpoints → `cia_routes.py`
2. Move JAA endpoints → `jaa_routes.py`
3. Move CDA endpoints → `cda_routes.py`
4. Move EAA endpoints → `eaa_routes.py`
5. Move admin endpoints → `admin_routes.py`
6. Move WebSocket endpoints → `websocket_routes.py`

### **Phase 3: Extract Services** (2 hours)
1. Move agent initialization → `services/agent_manager.py`
2. Move auth logic → `services/auth_service.py`
3. Move helper functions → appropriate services

### **Phase 4: Update Imports** (1 hour)
1. Update all imports in test files
2. Update documentation
3. Test everything still works

## 🚀 QUICK WINS (Can Do Now)

### **1. Move Admin Routes First**
Since admin dashboard is newest, move it first as proof of concept:
```python
# Create: routers/admin_routes.py
# Move lines 1214-1558 from main.py
```

### **2. Extract Agent Initialization**
```python
# Create: services/agent_manager.py
# Move agent initialization logic (lines 47-99)
```

### **3. Create Route Registry**
```python
# Create: routers/__init__.py
# Central place to import all routers
```

## 📋 MIGRATION CHECKLIST

- [ ] Create directory structure
- [ ] Move health check endpoint
- [ ] Move CIA endpoints (lines 286-482)
- [ ] Move JAA endpoints (lines 587-609)
- [ ] Move CDA endpoints (lines 612-658)
- [ ] Move EAA endpoints (lines 661-839)
- [ ] Move admin endpoints (lines 1214-1558)
- [ ] Move contractor chat endpoints (lines 537-585)
- [ ] Move timing/orchestration endpoints (lines 841-1049)
- [ ] Move utility endpoints (lines 1052-1212)
- [ ] Extract agent manager service
- [ ] Update all imports
- [ ] Test each router individually
- [ ] Full integration test

## ⚠️ THINGS TO WATCH OUT FOR

1. **Global Variables**: Agent instances are global - need careful handling
2. **WebSocket State**: Admin WebSocket manager needs proper initialization
3. **Database Connections**: Ensure db imports work in all routers
4. **Circular Imports**: Be careful with service dependencies
5. **Backwards Compatibility**: Keep same API paths for frontend

## 🎯 END GOAL

Transform this:
```
main.py (1693 lines) - Everyone edits, constant conflicts
```

Into this:
```
main.py (100 lines)     - Just app setup
routers/*.py (200 each) - Agent-specific, no conflicts  
services/*.py           - Shared business logic
core/*.py               - Infrastructure
```

**Result**: Each agent can work independently without stepping on each other!