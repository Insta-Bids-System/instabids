# InstaBids Development Workflow

**Maintained by**: Agent 6 (Quality Gatekeeper)  
**Created**: August 1, 2025  
**Purpose**: Standardized development process for all agents working on InstaBids codebase

## 🎯 **CRITICAL: READ BEFORE CODING**

This workflow ensures all agents work effectively together and maintain code quality across the InstaBids system.

---

## 📋 **PRE-DEVELOPMENT CHECKLIST**

### **🔍 Step 1: Understand Your Context**
Before writing any code, complete these steps:

1. **Read Your Agent Specification**
   - Location: `agent_specifications/CLAUDE_AGENT_{N}*.md`
   - Understand your role and responsibilities
   - Know what you should and shouldn't work on

2. **Review Current System State**
   - **MUST READ**: `CLAUDE.md` - Current build status and known issues
   - **Architecture**: `SYSTEM_INTERDEPENDENCY_MAP.md` - How components connect
   - **File Structure**: `CODEBASE_OVERVIEW.md` - Where everything is located

3. **Check Existing Implementation**
   - Look for existing components before creating new ones
   - Read relevant agent `README.md` files for context
   - Check `test_*.py` files to understand expected behavior

### **🧪 Step 2: Verify System is Working**
Always test the current system before making changes:

```bash
# Start backend server
cd ai-agents && python main.py  # Port 8008

# Start frontend (if needed)
cd web && npm run dev           # Port 5173

# Test core functionality
python test_complete_system_validation.py

# Check admin dashboard
http://localhost:5173/admin/login  # admin@instabids.com / admin123
```

### **📊 Step 3: Use Admin Dashboard for Context**
- Monitor system health and agent status
- See current bid cards and campaign activity  
- Understand real-time system behavior
- Access: http://localhost:5173/admin/login

---

## 🛠️ **DEVELOPMENT PROCESS**

### **🎯 Code Development Standards**

#### **Backend Development (`ai-agents/`)**
```python
# Follow existing patterns
class YourAgent:
    """Clear docstring describing agent purpose"""
    
    def __init__(self):
        # Use existing database patterns
        self.supabase = create_client(supabase_url, supabase_anon_key)
        
    def main_method(self, input_data):
        """Process input and return structured output"""
        try:
            # Main logic here
            result = self._process_data(input_data)
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

#### **Frontend Development (`web/`)**
```typescript
// Use TypeScript and existing patterns
interface YourComponentProps {
  data: any;
  onUpdate: (data: any) => void;
}

export const YourComponent: React.FC<YourComponentProps> = ({ 
  data, 
  onUpdate 
}) => {
  // Use existing hooks
  const { apiCall } = useApi();
  const { wsMessage } = useWebSocket();
  
  return (
    <div className="existing-tailwind-classes">
      {/* Component JSX */}
    </div>
  );
};
```

### **🗄️ Database Operations**
Always use the shared database utility:

```python
# CORRECT - Use shared database functions
from database_simple import (
    create_bid_card,
    get_contractors,
    update_campaign_status
)

# Use these functions instead of direct Supabase calls
result = create_bid_card(bid_data)
contractors = get_contractors(filters)
```

### **🧪 Testing Requirements**
Every change must include appropriate tests:

```python
# Create test file: test_your_feature.py
def test_your_functionality():
    """Test your specific functionality"""
    # Arrange
    test_data = {"example": "data"}
    
    # Act
    result = your_function(test_data)
    
    # Assert
    assert result["status"] == "success"
    assert "data" in result
```

---

## 🔧 **AGENT-SPECIFIC WORKFLOWS**

### **Agent 1 (Frontend Flow)**
```bash
# Your focus: React components and user interfaces
cd web/
npm run dev

# Key directories:
# - src/components/ - React components
# - src/pages/ - Page components  
# - src/hooks/ - React hooks

# Test your changes:
# - Check all user flows work
# - Verify mobile responsiveness
# - Test admin dashboard integration
```

### **Agent 2 (Backend Core)**
```bash
# Your focus: AI agents and backend logic
cd ai-agents/
python main.py

# Key directories:
# - agents/ - AI agent implementations
# - main.py - FastAPI server
# - database_simple.py - Database operations

# Test your changes:
python test_complete_system_validation.py
```

### **Agent 3 (Homeowner UX)**
```bash
# Your focus: Homeowner experience and CIA integration
# Frontend: web/src/components/chat/
# Backend: ai-agents/agents/cia/

# Test homeowner flows:
# - Chat interface with CIA
# - Multi-project memory
# - Design inspiration with IRIS
```

### **Agent 4 (Contractor UX)**
```bash
# Your focus: Contractor experience and COIA integration
# Frontend: web/src/components/contractor/
# Backend: ai-agents/agents/coia/

# Test contractor flows:
# - Onboarding process
# - Account creation
# - Profile management
```

### **Agent 5 (Marketing & Growth)**
```bash
# Your focus: EAA outreach and campaign management
# Backend: ai-agents/agents/eaa/
# Frontend: Campaign monitoring components

# Test marketing flows:
# - Email campaigns with MCP integration
# - SMS outreach
# - Website form automation via WFA
```

### **Agent 6 (Quality Assurance)**
```bash
# Your focus: Code quality, testing, documentation
# All directories - system-wide oversight

# Quality tasks:
# - Run all test suites
# - Maintain documentation
# - Monitor system health
# - Consolidate duplicate code
```

---

## 🧪 **TESTING WORKFLOW**

### **Before Making Changes**
```bash
# Test current system works
python test_complete_system_validation.py
python test_complete_admin_system.py

# Test specific components you'll modify
python test_cia_claude_extraction.py  # If working on CIA
python test_actual_mcp_emails.py      # If working on EAA
```

### **During Development**
```bash
# Create tests for your changes
# Follow naming convention: test_{component}_{feature}.py

# Example:
# test_cia_new_feature.py
# test_eaa_campaign_improvements.py
```

### **After Changes**
```bash
# Run your specific tests
python test_your_changes.py

# Run integration tests
python test_complete_system_validation.py

# Check admin dashboard shows no errors
http://localhost:5173/admin/login
```

---

## 📊 **QUALITY CHECKPOINTS**

### **🔍 Code Review Checklist**
Before considering your work complete:

- [ ] **Functionality**: Does your code work as intended?
- [ ] **Testing**: Are there tests that prove it works?
- [ ] **Integration**: Does it work with the rest of the system?
- [ ] **Documentation**: Is it documented for other agents?
- [ ] **Performance**: Does it maintain system performance?
- [ ] **Error Handling**: Does it handle errors gracefully?

### **🧪 System Integration Check**
Your changes must not break:

1. **Core Agent Pipeline**: CIA → JAA → CDA → EAA → WFA → COIA
2. **Admin Dashboard**: Real-time monitoring and updates
3. **Database Operations**: All CRUD operations still work
4. **Email/Form Automation**: MCP integration and Playwright automation
5. **Multi-Project Memory**: Context and memory persistence

### **📋 Documentation Requirements**
Update documentation when you:

- Add new features or components
- Change existing functionality
- Fix bugs or issues
- Modify database schema
- Add new API endpoints

---

## 🚨 **CRITICAL RULES**

### **❌ DON'T DO THIS**
1. **Don't create duplicate code** - Check for existing implementations first
2. **Don't break existing functionality** - Always test before submitting
3. **Don't ignore interdependencies** - Check impact on other agents
4. **Don't skip testing** - Every change needs appropriate tests
5. **Don't work in isolation** - Consider system-wide impact

### **✅ DO THIS**
1. **Follow existing patterns** - Consistency is key
2. **Use shared utilities** - `database_simple.py`, existing hooks
3. **Write clear documentation** - Help other agents understand your work
4. **Test thoroughly** - Verify your changes work in context
5. **Monitor system health** - Use admin dashboard to verify impact

---

## 🔄 **COLLABORATION WORKFLOW**

### **🤝 Working with Other Agents**
1. **Check interdependency map** before making changes that affect other agents
2. **Use admin dashboard** to monitor impact of your changes
3. **Run integration tests** to verify system still works together
4. **Update shared documentation** when you change shared components

### **📞 Getting Help**
If you're stuck or need context:

1. **Read documentation first**: `CLAUDE.md`, your agent spec, relevant README files
2. **Check existing code**: Look for similar implementations
3. **Use admin dashboard**: Monitor system behavior and health
4. **Run tests**: Understand expected behavior through test files

---

## 📈 **QUALITY IMPROVEMENT PROCESS**

### **🔧 Regular Maintenance Tasks**
All agents should contribute to:

1. **Code Quality**: Follow standards, remove duplication
2. **Testing**: Maintain and improve test coverage
3. **Documentation**: Keep documentation current and helpful
4. **Performance**: Monitor and optimize system performance
5. **Security**: Ensure secure coding practices

### **📊 Monitoring System Health**
Use these tools to maintain quality:

- **Admin Dashboard**: Real-time system monitoring
- **Test Suites**: Automated quality verification
- **Documentation**: Keep system knowledge current
- **Performance Metrics**: Monitor system performance

---

## 🎯 **SUCCESS CRITERIA**

Your development work is successful when:

1. **Functionality Works**: Your feature/fix works as intended
2. **Tests Pass**: All relevant tests pass, including integration tests
3. **Documentation Updated**: Other agents can understand and build on your work
4. **System Stable**: Admin dashboard shows healthy system state
5. **No Regressions**: Existing functionality continues to work

---

## 📚 **QUICK REFERENCE**

### **📁 Key Files to Know**
- `CLAUDE.md` - Current system status and build instructions
- `SYSTEM_INTERDEPENDENCY_MAP.md` - Architecture and dependencies
- `CODEBASE_OVERVIEW.md` - Complete file structure
- Your agent spec in `agent_specifications/`
- `ai-agents/main.py` - FastAPI server with all endpoints
- `ai-agents/database_simple.py` - Shared database operations

### **🧪 Key Commands**
```bash
# Start development environment
cd ai-agents && python main.py     # Backend
cd web && npm run dev              # Frontend

# Test your changes
python test_your_component.py      # Specific tests
python test_complete_system_validation.py  # Integration

# Monitor system
http://localhost:5173/admin/login  # Admin dashboard
```

### **🎯 Quality Contacts**
- **Agent 6** maintains overall system quality and can help with:
  - System architecture questions
  - Integration issues
  - Testing guidance
  - Documentation standards

---

This development workflow ensures all agents can work effectively together while maintaining the high quality and reliability of the InstaBids system.