# Router Migration Guide - For All Agents

## 🚨 ATTENTION ALL AGENTS: main.py is being broken up!

### Current Problem:
- main.py = 1693 lines = constant merge conflicts
- Everyone editing same file = chaos

### Solution:
- Each agent gets their OWN router file
- No more conflicts!

## 📁 New Structure:

```
ai-agents/
├── main.py              ← Now just imports routers (100 lines)
├── routers/
│   ├── __init__.py
│   ├── cia_routes.py    ← Agent 1 edits this
│   ├── jaa_routes.py    ← Agent 2 edits this  
│   ├── cda_routes.py    ← Agent 2 edits this
│   ├── eaa_routes.py    ← Agent 2 edits this
│   ├── admin_routes.py  ← Agent 2 edits this
│   ├── homeowner_routes.py ← Agent 3 edits this
│   └── contractor_routes.py ← Agent 4 edits this
```

## 🎯 HOW TO MIGRATE YOUR ENDPOINTS:

### Step 1: Find Your Endpoints in main.py
```python
# Search for your endpoints:
# Agent 1: Look for @app.post("/api/cia/
# Agent 2: Look for @app.post("/api/jaa/, @app.post("/api/cda/, etc.
# Agent 3: Look for @app.get("/api/homeowner/
# Agent 4: Look for @app.post("/api/contractor/
```

### Step 2: Create Your Router File
```python
# Example: routers/cia_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Import what you need
from agents.cia.agent import get_cia_agent
from database.database_simple import get_supabase_client

# Create router
router = APIRouter()

# Move your endpoints here (change @app to @router):
@router.post("/chat")  # Note: prefix removed
async def chat(request: ChatRequest):
    # Your existing code
    pass
```

### Step 3: Update main.py Import
```python
# In main.py, Agent 6 will add:
from routers import cia_routes
app.include_router(cia_routes.router, prefix="/api/cia", tags=["CIA"])
```

## ⚠️ IMPORTANT RULES:

1. **Change @app to @router** in your file
2. **Remove the prefix** from your routes ("/api/cia/chat" → "/chat")
3. **Keep all your imports** at the top
4. **Test your endpoints** after moving

## 📋 MIGRATION CHECKLIST:

### For Each Endpoint You Move:
- [ ] Copy endpoint from main.py
- [ ] Paste in your router file
- [ ] Change @app to @router
- [ ] Remove prefix from path
- [ ] Update imports
- [ ] Test it still works
- [ ] Delete from main.py

## 🧪 TESTING YOUR MIGRATION:

```bash
# Test your specific endpoints:
# Agent 1:
curl http://localhost:8008/api/cia/chat

# Agent 2:
curl http://localhost:8008/api/jaa/process/123

# Agent 3:
curl http://localhost:8008/api/homeowner/profile/123

# Agent 4:
curl http://localhost:8008/api/contractor/chat
```

## 🚨 WHO DOES WHAT:

### Agent 6 (QA) Will:
1. Create router directory structure ✓
2. Update main.py to import routers ✓
3. Move admin routes as example ✓
4. Test everything still works ✓

### Each Agent Should:
1. Wait for Agent 6's setup
2. Move YOUR endpoints only
3. Test YOUR endpoints work
4. Commit with message: "Migrated [agent] routes to router pattern"

## 📅 TIMELINE:

1. **Hour 1**: Agent 6 sets up structure + example
2. **Hour 2**: All agents migrate their routes IN PARALLEL
3. **Hour 3**: Testing and cleanup

## ❓ QUESTIONS?

- If endpoint has shared logic → Put in services/ folder
- If unsure about an endpoint → Ask in comments
- If something breaks → Git revert and try again

## 🎯 END RESULT:

- No more merge conflicts
- Each agent owns their file
- Faster development
- Professional codebase

Let's do this! 🚀