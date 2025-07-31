# Agent 1: Technical Implementation Guide
**Purpose**: Detailed technical guide for CIA & JAA agent implementation  
**Last Updated**: January 30, 2025  
**Scope**: Customer Interface Agent, Job Assessment Agent, Technical patterns

## 🎯 **AGENT 1 TECHNICAL DOMAIN**

**My Technical Responsibility**:
- **CIA Agent Implementation** - Claude Opus 4 integration patterns
- **JAA Agent Implementation** - Bid card extraction and generation
- **Frontend Integration** - React components connecting to backend agents
- **Database Operations** - Supabase storage and retrieval patterns

---

## 🧠 **CIA AGENT TECHNICAL IMPLEMENTATION**

### **Core Agent Design**
**File**: `ai-agents/agents/cia/agent.py`

```python
# CIA Agent Personality & Configuration
AGENT_NAME = "Alex"  # Friendly project assistant
TONE = "Warm, professional, solution-oriented"
APPROACH = "Conversational but efficient"

# Claude Opus 4 Integration
MODEL = "claude-3-opus-20240229"
MAX_TOKENS = 4000
TEMPERATURE = 0.1  # Consistent, professional responses
```

### **LangGraph State Schema**
**File**: `ai-agents/agents/cia/state.py`

```python
from typing import TypedDict, List, Optional, Literal
from datetime import datetime

class PhotoAnalysis(TypedDict):
    description: str
    identified_issues: List[str]
    estimated_scope: str
    confidence: float

class ConversationState(TypedDict):
    # User & Session
    user_id: str
    session_id: str
    
    # Conversation
    messages: List[dict]
    current_phase: Literal["intro", "discovery", "details", "photos", "review", "complete"]
    
    # Collected Information (12 Key Data Points)
    project_type: Optional[str]
    project_description: Optional[str]
    timeline_start: Optional[str]
    timeline_end: Optional[str]
    urgency: Optional[Literal["emergency", "urgent", "flexible", "planning"]]
    budget_min: Optional[float]
    budget_max: Optional[float]
    
    # Property Details
    address: Optional[str]
    property_type: Optional[str]
    property_size: Optional[str]
    access_notes: Optional[str]
    
    # Preferences & Requirements
    materials_preferences: Optional[str]
    homeowner_communication_preference: Optional[str]
    homeowner_scheduling_preference: Optional[str]
    special_requirements: List[str]
    concerns_issues: List[str]
    
    # Photos & Analysis
    uploaded_photos: List[str]  # Supabase Storage URLs
    photo_analyses: List[PhotoAnalysis]
    
    # Status & Metadata
    created_at: datetime
    updated_at: datetime
    ready_for_jaa: bool
    missing_fields: List[str]
```

### **Image Processing Implementation**
**Real-time Claude Vision Integration**

```python
async def process_uploaded_image(image_url: str, state: ConversationState):
    """Process uploaded image with Claude Vision"""
    
    # 1. Analyze with Claude Vision API
    analysis = await analyze_image_with_claude(image_url)
    
    # 2. Update conversation state
    state["photo_analyses"].append(analysis)
    
    # 3. Generate contextual response
    response = generate_image_feedback(analysis)
    
    # 4. Update project understanding
    update_project_scope_from_image(state, analysis)
    
    return response

async def analyze_image_with_claude(image_url: str) -> PhotoAnalysis:
    """Use Claude Vision to analyze project images"""
    
    prompt = """
    Analyze this home improvement project image. Identify:
    1. Current condition and any issues
    2. Estimated scope of work needed
    3. Potential challenges or special requirements
    4. Overall project complexity (1-10 scale)
    
    Be specific and helpful for contractor planning.
    """
    
    # Claude Vision API call
    response = await claude_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}}
            ]
        }]
    )
    
    return parse_image_analysis(response.content[0].text)
```

### **Information Extraction Pattern**
**12 Key Data Points Collection**

```python
# The 12 critical data points CIA must extract:
REQUIRED_DATA_POINTS = [
    "project_type",          # lawn care, kitchen remodel, etc.
    "budget_range",          # min/max values from conversation
    "timeline_urgency",      # emergency, week, month, flexible
    "location",              # address, zip, city, state
    "project_description",   # detailed scope from conversation
    "property_details",      # type, size, access notes
    "materials_preferences", # specific materials mentioned
    "images_analysis",       # uploaded photos and vision analysis
    "special_requirements",  # permits, licenses, insurance
    "homeowner_preferences", # communication, scheduling, decision style
    "concerns_issues",       # damage, problems, urgency factors
    "contractor_requirements" # count needed, specialties, experience
]

def validate_conversation_completeness(state: ConversationState) -> tuple[bool, List[str]]:
    """Check if conversation has all required information for JAA"""
    
    missing_fields = []
    
    # Core project information
    if not state.get("project_type"):
        missing_fields.append("project_type")
    if not state.get("budget_min") or not state.get("budget_max"):
        missing_fields.append("budget_range")
    if not state.get("urgency"):
        missing_fields.append("timeline_urgency")
    
    # Location information
    if not state.get("address"):
        missing_fields.append("location")
    
    # Project details
    if not state.get("project_description"):
        missing_fields.append("project_description")
    
    ready_for_jaa = len(missing_fields) == 0
    return ready_for_jaa, missing_fields
```

---

## 🎯 **JAA AGENT TECHNICAL IMPLEMENTATION**

### **Simple JAA Solution** 
**Problem Solved**: "Just extract JSON conversation data into structured bid card"

**File**: `ai-agents/agents/jaa/simple_agent.py`

```python
class SimpleJAAAgent:
    """Simplified JAA that extracts conversation JSON into bid card schema"""
    
    def __init__(self):
        self.supabase = create_supabase_client()
        self.extractor = SimpleJAAExtractor()
    
    def process_conversation(self, cia_thread_id: str) -> dict:
        """
        3-step process:
        1. Load conversation JSON from Supabase
        2. Extract all 12 data points using SimpleJAAExtractor  
        3. Save to bid_cards table
        """
        
        try:
            # 1. Load CIA conversation
            conversation = self.load_conversation(cia_thread_id)
            
            # 2. Extract structured data
            bid_card_data = self.extractor.extract_all_data_points(conversation)
            
            # 3. Save to database
            bid_card_id = self.save_bid_card(bid_card_data)
            
            return {
                "success": True,
                "bid_card_number": bid_card_data["bid_card_number"],
                "bid_card_id": bid_card_id,
                "bid_card_data": bid_card_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_budget_correctly(self, conversation_data: dict) -> tuple[float, float]:
        """Extract budget as proper min/max values, not $4-$329 nonsense"""
        
        # Look for budget mentions in conversation
        budget_text = extract_budget_mentions(conversation_data)
        
        # Parse common patterns:
        # "$500-800", "around $25k", "budget is 50000"
        if "-" in budget_text:
            min_val, max_val = parse_range(budget_text)
        elif "around" in budget_text.lower():
            target = parse_single_value(budget_text)
            min_val, max_val = target * 0.8, target * 1.2
        else:
            value = parse_single_value(budget_text)
            min_val, max_val = value, value
        
        return float(min_val), float(max_val)
```

### **JAA Data Extraction Map**
**12 Data Points with Extraction Logic**

```python
class SimpleJAAExtractor:
    """Extract all 12 data points from CIA conversation JSON"""
    
    def extract_all_data_points(self, conversation_data: dict) -> dict:
        """Extract structured bid card data from conversation"""
        
        # Generate unique bid card number
        bid_card_number = f"BC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "bid_card_number": bid_card_number,
            
            # 1. Project Type
            "project_type": self.extract_project_type(conversation_data),
            
            # 2. Budget Range  
            "budget_min": self.extract_budget_min(conversation_data),
            "budget_max": self.extract_budget_max(conversation_data),
            
            # 3. Timeline/Urgency
            "urgency_level": self.extract_urgency(conversation_data),
            "timeline_start": self.extract_timeline_start(conversation_data),
            "timeline_end": self.extract_timeline_end(conversation_data),
            
            # 4. Location
            "address": self.extract_address(conversation_data),
            "zip_code": self.extract_zip_code(conversation_data),
            "city": self.extract_city(conversation_data),
            "state": self.extract_state(conversation_data),
            
            # 5. Project Description
            "project_description": self.extract_project_description(conversation_data),
            "current_condition": self.extract_current_condition(conversation_data),
            "desired_outcome": self.extract_desired_outcome(conversation_data),
            
            # 6. Property Details
            "property_type": self.extract_property_type(conversation_data),
            "property_size": self.extract_property_size(conversation_data),
            "access_notes": self.extract_access_notes(conversation_data),
            
            # 7. Materials/Preferences
            "materials_preferences": self.extract_materials(conversation_data),
            
            # 8. Images/Photos
            "images_count": self.extract_image_count(conversation_data),
            "images_urls": self.extract_image_urls(conversation_data),
            "images_analysis": self.extract_image_analysis(conversation_data),
            
            # 9. Special Requirements
            "special_requirements": self.extract_special_requirements(conversation_data),
            "permits_needed": self.extract_permits_needed(conversation_data),
            "licensed_contractor_required": self.extract_license_requirements(conversation_data),
            
            # 10. Homeowner Preferences
            "communication_preference": self.extract_communication_preference(conversation_data),
            "scheduling_preference": self.extract_scheduling_preference(conversation_data),
            "decision_style": self.extract_decision_style(conversation_data),
            
            # 11. Concerns/Issues
            "concerns_issues": self.extract_concerns(conversation_data),
            "damage_issues": self.extract_damage_issues(conversation_data),
            
            # 12. Contractor Requirements
            "complexity_score": self.calculate_complexity_score(conversation_data),
            "contractor_count_needed": self.calculate_contractor_count(conversation_data),
            "contractor_specialties_required": self.extract_specialties_required(conversation_data),
            "experience_level_required": self.calculate_experience_level(conversation_data),
            
            # Metadata
            "cia_thread_id": conversation_data.get("thread_id"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
```

### **Database Schema for JAA Output**
**Updated bid_cards table schema**

```sql
-- Enhanced bid_cards table with all 12 data points
CREATE TABLE bid_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference & Identity
    cia_thread_id VARCHAR(255), -- Links to CIA conversation
    bid_card_number VARCHAR(50) UNIQUE,
    
    -- 1. Project Type
    project_type VARCHAR(100),
    
    -- 2. Budget Range
    budget_min INTEGER,
    budget_max INTEGER,
    
    -- 3. Timeline/Urgency
    urgency_level VARCHAR(20) CHECK (urgency_level IN ('emergency', 'urgent', 'week', 'month', 'flexible')),
    timeline_start VARCHAR(100),
    timeline_end VARCHAR(100),
    
    -- 4. Location
    address TEXT,
    zip_code VARCHAR(10),
    city VARCHAR(100),
    state VARCHAR(50),
    
    -- 5. Project Description
    project_description TEXT,
    current_condition TEXT,
    desired_outcome TEXT,
    
    -- 6. Property Details
    property_type VARCHAR(100),
    property_size VARCHAR(100),
    access_notes TEXT,
    
    -- 7. Materials/Preferences
    materials_preferences TEXT,
    
    -- 8. Images/Photos
    images_count INTEGER DEFAULT 0,
    images_urls TEXT[], -- Array of Supabase storage URLs
    images_analysis JSONB,
    
    -- 9. Special Requirements
    special_requirements TEXT[],
    permits_needed BOOLEAN DEFAULT FALSE,
    licensed_contractor_required BOOLEAN DEFAULT FALSE,
    
    -- 10. Homeowner Preferences
    communication_preference VARCHAR(50),
    scheduling_preference VARCHAR(100),
    decision_style VARCHAR(50),
    
    -- 11. Concerns/Issues
    concerns_issues TEXT[],
    damage_issues TEXT[],
    
    -- 12. Contractor Requirements
    complexity_score INTEGER CHECK (complexity_score >= 1 AND complexity_score <= 10),
    contractor_count_needed INTEGER DEFAULT 3,
    contractor_specialties_required TEXT[],
    experience_level_required VARCHAR(50),
    
    -- Complete Bid Document
    bid_document JSONB, -- Generated professional bid card document
    
    -- Status & Metadata
    status VARCHAR(20) DEFAULT 'generated',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎨 **FRONTEND TECHNICAL IMPLEMENTATION**

### **CIAChat Component Architecture**
**File**: `web/src/components/chat/CIAChat.tsx`

```typescript
interface CIAChatProps {
  userId?: string;
  projectId?: string;
  onBidCardGenerated?: (bidCardId: string) => void;
}

interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  images?: string[];
  isTyping?: boolean;
}

interface ConversationState {
  sessionId: string;
  messages: ChatMessage[];
  isLoading: boolean;
  currentPhase: 'intro' | 'discovery' | 'details' | 'photos' | 'review' | 'complete';
  extractedData: Partial<ProjectData>;
  readyForJAA: boolean;
  missingFields: string[];
}

const CIAChat: React.FC<CIAChatProps> = ({ userId, projectId, onBidCardGenerated }) => {
  const [state, setState] = useState<ConversationState>(initialState);
  
  // Real-time chat with CIA agent
  const sendMessage = async (content: string, images?: File[]) => {
    setState(prev => ({ ...prev, isLoading: true }));
    
    try {
      // Upload images if provided
      const imageUrls = images ? await uploadImages(images) : [];
      
      // Send to CIA agent backend
      const response = await apiClient.post('/api/cia/chat', {
        user_id: userId,
        session_id: state.sessionId,
        message: content,
        images: imageUrls,
        project_id: projectId
      });
      
      // Update conversation state
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, 
          { id: crypto.randomUUID(), content, role: 'user', timestamp: new Date(), images: imageUrls },
          { id: crypto.randomUUID(), content: response.data.response, role: 'assistant', timestamp: new Date() }
        ],
        extractedData: response.data.extracted_data,
        readyForJAA: response.data.ready_for_jaa,
        missingFields: response.data.missing_fields,
        currentPhase: response.data.current_phase,
        isLoading: false
      }));
      
      // Auto-generate bid card when ready
      if (response.data.ready_for_jaa && onBidCardGenerated) {
        const bidCardResponse = await apiClient.post('/api/jaa/process', {
          session_id: state.sessionId
        });
        
        if (bidCardResponse.data.success) {
          onBidCardGenerated(bidCardResponse.data.bid_card_id);
        }
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };
  
  return (
    <div className="chat-container">
      <ChatMessages messages={state.messages} />
      <ProgressIndicator 
        currentPhase={state.currentPhase}
        extractedData={state.extractedData}
        missingFields={state.missingFields}
      />
      <MessageInput 
        onSendMessage={sendMessage}
        isLoading={state.isLoading}
        supportImages={true}
      />
    </div>
  );
};
```

### **File Upload Implementation**
**Real-time Image Upload with Drag & Drop**

```typescript
// File: web/src/lib/storage.ts
export const uploadToSupabase = async (files: File[]): Promise<string[]> => {
  const uploadPromises = files.map(async (file) => {
    const fileName = `${Date.now()}-${file.name}`;
    const filePath = `chat-images/${fileName}`;
    
    const { data, error } = await supabase.storage
      .from('project-images')
      .upload(filePath, file);
    
    if (error) throw error;
    
    const { data: { publicUrl } } = supabase.storage
      .from('project-images')
      .getPublicUrl(filePath);
    
    return publicUrl;
  });
  
  return Promise.all(uploadPromises);
};

// File: web/src/components/chat/ImageUpload.tsx
const ImageUpload: React.FC<ImageUploadProps> = ({ onUpload, maxFiles = 5 }) => {
  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles,
    onDrop: async (files) => {
      try {
        const urls = await uploadToSupabase(files);
        onUpload(urls);
      } catch (error) {
        console.error('Upload failed:', error);
      }
    }
  });
  
  return (
    <div {...getRootProps()} className={`upload-zone ${isDragActive ? 'active' : ''}`}>
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Drop images here...</p>
      ) : (
        <p>Drag & drop images, or click to select</p>
      )}
    </div>
  );
};
```

---

## 🔧 **API INTEGRATION PATTERNS**

### **CIA Agent API Endpoints**
**Backend**: `ai-agents/main.py`

```python
@app.post("/api/cia/chat")
async def cia_chat_endpoint(request: CIAChatRequest):
    """Main CIA conversation endpoint"""
    
    try:
        # Initialize CIA agent
        cia = CustomerInterfaceAgent(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Process conversation
        result = await cia.handle_conversation(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id,
            images=request.images,
            project_id=request.project_id
        )
        
        return {
            "success": True,
            "response": result["response"],
            "extracted_data": result["extracted_data"],
            "ready_for_jaa": result["ready_for_jaa"],
            "missing_fields": result["missing_fields"],
            "current_phase": result["current_phase"],
            "session_id": result["session_id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jaa/process")
async def jaa_process_endpoint(request: JAAProcessRequest):
    """Process CIA conversation with JAA to generate bid card"""
    
    try:
        # Initialize Simple JAA Agent  
        jaa = SimpleJAAAgent()
        
        # Process conversation
        result = jaa.process_conversation(request.session_id)
        
        if result['success']:
            return {
                "success": True,
                "bid_card_number": result["bid_card_number"],
                "bid_card_id": result["bid_card_id"],
                "bid_card_data": result["bid_card_data"],
                "unique_url": f"https://instabids.com/bid-cards/{result['bid_card_id']}"
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **Error Handling & Recovery**
**Graceful Failure Management**

```python
class CIAErrorRecovery:
    """Handle CIA conversation errors gracefully"""
    
    @staticmethod
    async def handle_claude_api_failure(state: ConversationState, error: Exception):
        """When Claude API fails"""
        
        # Log error
        logger.error(f"Claude API failure: {error}")
        
        # Provide fallback response
        fallback_response = "I'm having trouble connecting right now. Let me try a different approach. Could you tell me more about your project?"
        
        # Update state with error recovery
        state["messages"].append({
            "role": "assistant", 
            "content": fallback_response,
            "is_fallback": True
        })
        
        return state
    
    @staticmethod
    async def handle_incomplete_extraction(state: ConversationState):
        """When information extraction is incomplete"""
        
        missing_fields = validate_conversation_completeness(state)[1]
        
        if missing_fields:
            clarification_request = generate_clarification_request(missing_fields)
            
            state["messages"].append({
                "role": "assistant",
                "content": clarification_request,
                "requesting_clarification": True
            })
        
        return state
```

---

## 📊 **TESTING & VALIDATION PATTERNS**

### **CIA Agent Testing**
**File**: `ai-agents/test_cia_claude_extraction.py`

```python
def test_cia_conversation_flow():
    """Test complete CIA conversation with Claude Opus 4"""
    
    # Test data
    test_message = "I need lawn care, my grass is knee-high and I have a half-acre property in Melbourne, FL 32904. Budget is around $500-800 and I need it done ASAP."
    
    # Initialize CIA
    cia = CustomerInterfaceAgent(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Process message
    result = cia.handle_conversation(
        user_id="test_user",
        message=test_message,
        session_id="test_session"
    )
    
    # Validate extraction
    assert result["ready_for_jaa"] == True
    assert result["missing_fields"] == []
    assert result["extracted_data"]["project_type"] == "lawn care"
    assert result["extracted_data"]["urgency"] == "emergency"
    assert "Melbourne, FL 32904" in result["extracted_data"]["address"]
    
    print("✅ CIA Claude extraction test PASSED")

def test_jaa_bid_card_generation():
    """Test JAA creates proper bid cards from CIA conversations"""
    
    # Use session from CIA test
    jaa = SimpleJAAAgent()
    result = jaa.process_conversation("test_session")
    
    # Validate bid card creation
    assert result["success"] == True
    assert result["bid_card_data"]["budget_min"] == 500
    assert result["bid_card_data"]["budget_max"] == 800
    assert result["bid_card_data"]["urgency_level"] == "emergency"
    assert result["bid_card_data"]["project_type"] == "lawn care"
    
    print("✅ JAA bid card generation test PASSED")
```

### **Frontend Component Testing**
**File**: `web/src/components/chat/__tests__/CIAChat.test.tsx`

```typescript
describe('CIAChat Component', () => {
  test('sends messages to CIA agent', async () => {
    render(<CIAChat userId="test-user" />);
    
    const input = screen.getByPlaceholderText('Describe your project...');
    const sendButton = screen.getByRole('button', { name: 'Send' });
    
    // Type message
    fireEvent.change(input, { target: { value: 'I need kitchen remodel' } });
    fireEvent.click(sendButton);
    
    // Wait for response
    await waitFor(() => {
      expect(screen.getByText('Kitchen remodels are exciting projects!')).toBeInTheDocument();
    });
  });
  
  test('handles image uploads', async () => {
    render(<CIAChat userId="test-user" />);
    
    const file = new File(['test'], 'kitchen.jpg', { type: 'image/jpeg' });
    const dropzone = screen.getByText('Drag & drop images');
    
    // Upload image
    fireEvent.drop(dropzone, { dataTransfer: { files: [file] } });
    
    // Wait for upload and analysis
    await waitFor(() => {
      expect(screen.getByText('Thanks for the photos!')).toBeInTheDocument();
    });
  });
});
```

---

## 🎯 **SUCCESS METRICS & MONITORING**

### **CIA Performance Metrics**
```typescript
interface CIAMetrics {
  // Conversation Quality
  information_completeness_rate: number; // >95% target
  conversation_satisfaction_score: number; // >4.5/5 target
  average_conversation_length: number; // Efficiency metric
  dropout_rate: number; // <10% target
  
  // Technical Performance  
  average_response_time: number; // <2 seconds target
  claude_api_success_rate: number; // >99% target
  error_recovery_success_rate: number; // >95% target
  
  // Business Impact
  conversation_to_bid_card_rate: number; // >80% target
  information_accuracy_score: number; // >90% target
  user_return_rate: number; // Retention metric
}
```

### **JAA Performance Metrics**
```typescript
interface JAAMetrics {
  // Generation Success
  bid_card_generation_success_rate: number; // 100% target
  average_processing_time: number; // <5 seconds target
  data_extraction_accuracy: number; // >95% target
  
  // Data Quality
  budget_extraction_accuracy: number; // Critical metric
  timeline_extraction_accuracy: number; // Critical metric
  location_extraction_accuracy: number; // Critical metric
  
  // Business Impact
  contractor_engagement_rate: number; // Downstream metric
  bid_card_completion_rate: number; // Quality metric
}
```

---

## 🚀 **DEPLOYMENT & PRODUCTION PATTERNS**

### **Environment Configuration**
```bash
# Backend Environment (ai-agents/.env)
ANTHROPIC_API_KEY=your_anthropic_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key
API_PORT=8008

# Frontend Environment (web/.env)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_URL=http://localhost:8008
```

### **Production Deployment Commands**
```bash
# Backend Deployment
cd ai-agents
pip install -r requirements.txt
python main.py

# Frontend Deployment  
cd web
npm install
npm run build
npm run preview

# Health Checks
curl http://localhost:8008/health
curl http://localhost:5173
```

---

**🎯 Remember: This technical implementation guide covers my complete Agent 1 domain - CIA intelligence, JAA extraction, and frontend connections. Focus on intelligent conversation handling, accurate data extraction, and seamless user experience.**