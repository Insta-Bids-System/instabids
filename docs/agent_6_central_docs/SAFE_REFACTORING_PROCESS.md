# Safe Refactoring Process - How to Break Up main.py Without Breaking Everything

## 🎯 THE GOAL
Transform main.py (1693 lines) into organized modules WITHOUT any downtime or breaking changes.

## 🛡️ SAFETY PRINCIPLES

### 1. **One Endpoint at a Time**
- Move ONE route, test it works, then move the next
- Never move multiple endpoints at once

### 2. **Keep Old Routes Working**
- During transition, main.py imports from new files
- No API changes for frontend

### 3. **Test After Each Step**
- Run existing tests after each move
- Verify with real API calls

## 📋 STEP-BY-STEP PROCESS

### Phase 1: Setup Structure (30 minutes, NO RISK)
```bash
# Create new directories
ai-agents/
├── routers/          # New directory for routes
├── services/         # New directory for shared logic
└── main.py          # Keep original working
```

### Phase 2: Test Infrastructure First (1 hour, NO RISK)
1. Create test file that hits EVERY endpoint
2. Run it - save the output as "baseline"
3. After each change, run again and compare

### Phase 3: Move Safest Endpoints First (2 hours, LOW RISK)

#### Start with Health Check (Simplest):
```python
# 1. Create routers/health.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def health_check():
    return {"status": "online"}

# 2. In main.py, ADD (don't remove):
from routers import health
app.include_router(health.router)

# 3. Comment out old route in main.py
# 4. Test it still works
# 5. Delete commented code
```

### Phase 4: Move One Agent at a Time (4 hours, MEDIUM RISK)

Order of Operations (Safest to Riskiest):
1. **Admin routes** - Newest, least dependencies
2. **Monitoring routes** - Simple, few dependencies  
3. **EAA routes** - Self-contained
4. **CDA routes** - Some dependencies
5. **JAA routes** - Database heavy
6. **CIA routes** - Most critical, do last

### Phase 5: Update All Imports (1 hour, MEDIUM RISK)

Files that import from main.py:
```python
# Find all files that need updating:
grep -r "from main import" .
grep -r "import main" .
```

Update each to import from new locations:
```python
# Old:
from main import cia_agent

# New:
from services.agent_manager import get_cia_agent
```

## 🔍 WHAT TO WATCH FOR

### 1. **Global Variables**
```python
# Current main.py:
cia_agent = CustomerInterfaceAgent()  # Global instance

# Need to move to services/agent_manager.py:
_agents = {}

def get_cia_agent():
    if 'cia' not in _agents:
        _agents['cia'] = CustomerInterfaceAgent()
    return _agents['cia']
```

### 2. **WebSocket Connections**
- Admin WebSocket has persistent state
- Must maintain connection manager properly

### 3. **Database Connections**
- Ensure Supabase client initialized before use
- Watch for circular imports

### 4. **Middleware and CORS**
- Must be set up BEFORE routes
- Order matters in FastAPI

## 📊 TESTING CHECKLIST

### After EACH Move:
- [ ] Original endpoint returns 404
- [ ] New endpoint returns same response
- [ ] No errors in server logs
- [ ] Frontend still works
- [ ] Run integration tests

### Critical Tests:
```bash
# 1. API Health
curl http://localhost:8008/

# 2. CIA Chat (Most Critical)
python test_cia_claude_extraction.py

# 3. Admin WebSocket
python test_admin_websocket.py

# 4. Full Flow
python test_complete_system_validation.py
```

## 🚨 ROLLBACK PLAN

If ANYTHING breaks:
1. **Git stash changes**: `git stash`
2. **Restart server**: `python main.py`
3. **Verify working**: Run test suite
4. **Try again smaller**: Move fewer lines

## 📈 MIGRATION METRICS

Track these to ensure safety:
- API response times (should not increase)
- Error rates (should stay at 0)
- Test pass rate (should stay at 100%)
- Memory usage (should decrease)

## 🎯 WORLD-CLASS RESULT

### Before:
```
main.py (1693 lines) - Monolithic, hard to maintain
```

### After:
```
main.py (100 lines)           - Just app setup
routers/
├── cia_routes.py (150)       - Customer chat endpoints
├── jaa_routes.py (100)       - Bid card endpoints
├── cda_routes.py (120)       - Discovery endpoints
├── eaa_routes.py (200)       - Outreach endpoints
├── admin_routes.py (180)     - Admin dashboard
└── monitoring_routes.py (80)  - Health checks

services/
├── agent_manager.py (200)    - Agent lifecycle
├── auth_service.py (100)     - Authentication
└── database.py (150)         - DB operations
```

## ⏱️ REALISTIC TIMELINE

**With Safety First Approach:**
- Day 1: Setup + test infrastructure (2 hours)
- Day 2: Move admin + monitoring routes (2 hours)
- Day 3: Move EAA + CDA routes (2 hours)
- Day 4: Move JAA + CIA routes (2 hours)
- Day 5: Final testing + cleanup (2 hours)

**Total: 10 hours over 5 days = ZERO downtime**

## 🔑 KEY SUCCESS FACTORS

1. **Never Rush** - Slow and steady wins
2. **Test Everything** - Twice
3. **One Change at a Time** - No heroes
4. **Keep Old Code** - Until new is proven
5. **Document Changes** - For other agents

This is how world-class teams refactor without breaking production!