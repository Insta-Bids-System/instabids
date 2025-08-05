# Endpoint Ownership Map - Who Touches What

## 🎯 OWNERSHIP BY DEVELOPMENT AGENT

### **Agent 1 (Frontend Flow) Owns:**
```python
# cia_routes.py - Customer chat interface
@router.get("/api/cia/conversation/{session_id}")  # Line 286
@router.post("/api/cia/chat")                      # Line 344

# Frontend support endpoints
@router.get("/api/bid-cards/homeowner/{homeowner_id}")  # Line 176
@router.post("/api/conversations/transfer")             # Line 1159
```

### **Agent 2 (Backend Core + Admin Dashboard) Owns:**
```python
# jaa_routes.py - Bid card generation
@router.post("/api/jaa/process/{thread_id}")       # Line 587

# cda_routes.py - Contractor discovery  
@router.post("/api/cda/discover/{bid_card_id}")    # Line 612
@router.get("/api/cda/cache/{bid_card_id}")        # Line 639

# eaa_routes.py - Outreach campaigns
@router.post("/api/eaa/campaign/start")            # Line 661
@router.get("/api/eaa/campaign/{campaign_id}/status")  # Line 698
@router.post("/api/eaa/response/process")          # Line 723
@router.post("/api/eaa/onboarding/start")          # Line 755
@router.get("/api/eaa/analytics")                  # Line 784
@router.post("/api/eaa/webhook/email-response")    # Line 811
@router.post("/api/eaa/webhook/sms-response")      # Line 826

# Orchestration endpoints
@router.post("/api/timing/calculate")              # Line 842
@router.post("/api/campaigns/create-intelligent")  # Line 887
@router.get("/api/campaigns/{campaign_id}/check-in")   # Line 918
@router.get("/api/campaigns/{campaign_id}/metrics")    # Line 941
@router.post("/api/campaigns/{campaign_id}/escalate")  # Line 993

# admin_routes.py - Admin dashboard (CURRENTLY OWNED BY AGENT 2)
@router.websocket("/ws/admin")                     # Line 1224
@router.post("/api/admin/login")                   # Line 1354
@router.post("/api/admin/logout")                  # Line 1401
@router.get("/api/admin/session/validate")         # Line 1416
@router.get("/api/admin/bid-cards")                # Line 1434
@router.post("/api/admin/restart-agent")           # Line 1485
@router.get("/api/admin/dashboard")                # Line 1533
```

### **Agent 3 (Homeowner UX) Owns:**
```python
# homeowner_ui_routes.py - Homeowner features
@router.get("/api/profiles/{user_id}")             # Line 1666
@router.post("/api/inspiration/boards")            # Line 1065
@router.get("/api/iris/status")                    # Line 1143

# Demo pages
@router.get("/demo/wfa-rich-preview")              # Line 166
@router.get("/test/real-preview")                  # Line 218
```

### **Agent 4 (Contractor UX) Owns:**
```python
# contractor_ui_routes.py - Contractor features
@router.post("/api/contractor-chat/message")       # Line 537
# (Future contractor portal endpoints)
```

### **Agent 5 (Marketing) Owns:**
```python
# marketing_routes.py - Analytics & growth
# (Currently no endpoints - would add referral, analytics, etc.)
```

### **Agent 6 (QA/Testing/Monitoring) Owns:**
```python
# monitoring_routes.py - System health & monitoring
@router.get("/api/agents/status")                  # Line 1178
@router.get("/api/agents/{agent_name}/health")     # Line 1561
@router.get("/")                                   # Line 260 (health check)
@router.get("/api/debug/env")                      # Line 1052

# Note: Admin dashboard currently built by Agent 2
# Agent 6 will potentially take ownership after initial development
```

### **Shared/Utility Endpoints:**
```python
# websocket_routes.py - Real-time connections
@router.websocket("/ws/realtime")                  # Line 1684
```

## 📊 ENDPOINT COUNT BY AGENT

- **Agent 1**: 4 endpoints (CIA + frontend support)
- **Agent 2**: 22 endpoints (JAA + CDA + EAA + orchestration + admin dashboard)
- **Agent 3**: 5 endpoints (homeowner UI + IRIS)
- **Agent 4**: 1 endpoint (contractor chat - more coming)
- **Agent 5**: 0 endpoints (not implemented yet)
- **Agent 6**: 4 endpoints (monitoring only - admin will transfer later)

## 🎯 REFACTORING BENEFITS

1. **Agent 1** can add new CIA features without touching Agent 2's code
2. **Agent 2** can refactor backend logic without breaking frontend
3. **Agent 3** can enhance UX endpoints independently  
4. **Agent 4** can build contractor portal in isolation
5. **Agent 5** can add marketing features in new file
6. **Agent 6** can monitor/test without modifying core logic

## 🚀 MIGRATION PRIORITY

1. **First**: Move admin routes (newest, easiest to extract)
2. **Second**: Move EAA routes (most endpoints, clear boundaries)
3. **Third**: Move CIA routes (critical but only 2 endpoints)
4. **Fourth**: Move orchestration routes (complex but isolated)
5. **Last**: Move utility/shared endpoints