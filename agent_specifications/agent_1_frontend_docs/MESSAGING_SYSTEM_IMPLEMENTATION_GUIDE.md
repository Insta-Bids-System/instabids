# InstaBids Messaging System Implementation Guide

## Overview
The InstaBids messaging system provides secure, filtered communication between homeowners and contractors while protecting personal contact information. Built with privacy and security as core principles, it ensures no phone numbers, emails, or addresses are ever exchanged through the platform.

## System Architecture

### Core Components

1. **Database Schema (PostgreSQL/Supabase)**
   - `conversations` - Tracks conversations between homeowners and contractors
   - `messages` - Stores all messages with filtering metadata
   - `content_filter_rules` - Configurable filtering patterns
   - `broadcast_messages` - One-to-many communication
   - `broadcast_read_receipts` - Tracking for broadcast messages
   - `message_attachments` - File sharing support (future)

2. **LangGraph Messaging Agent**
   - Content filtering node
   - Conversation management node
   - Message persistence node
   - Notification node (WebSocket ready)

3. **REST API Endpoints**
   - `/api/messages/send` - Send filtered messages
   - `/api/messages/broadcast` - Send to multiple recipients
   - `/api/messages/conversations/{bid_card_id}` - Get conversations
   - `/api/messages/conversation/{conversation_id}/messages` - Get messages
   - `/api/messages/mark-read` - Mark messages as read
   - `/api/messages/unread-count` - Get unread counts

## Database Schema Details

### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_card_id UUID NOT NULL REFERENCES bid_cards(id),
    homeowner_id UUID NOT NULL,
    contractor_id UUID NOT NULL,
    contractor_alias VARCHAR(50) NOT NULL, -- "Contractor A", "B", etc.
    status VARCHAR(50) DEFAULT 'active',
    last_message_at TIMESTAMP WITH TIME ZONE,
    homeowner_unread_count INTEGER DEFAULT 0,
    contractor_unread_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(bid_card_id, contractor_id)
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    sender_type VARCHAR(20) NOT NULL,
    sender_id UUID NOT NULL,
    original_content TEXT NOT NULL,
    filtered_content TEXT NOT NULL,
    content_filtered BOOLEAN DEFAULT FALSE,
    filter_reasons JSONB DEFAULT '[]',
    message_type VARCHAR(50) DEFAULT 'text',
    metadata JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Content Filter Rules
```sql
CREATE TABLE content_filter_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_type VARCHAR(50) NOT NULL, -- 'regex', 'keyword', 'pattern'
    pattern TEXT NOT NULL,
    replacement TEXT,
    severity VARCHAR(20) DEFAULT 'medium',
    category VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Content Filtering System

### Default Filter Rules

1. **Phone Numbers**
   - US format: `555-123-4567` → `[PHONE REMOVED]`
   - With parentheses: `(555) 123-4567` → `[PHONE REMOVED]`
   - International: `+1 555 123 4567` → `[PHONE REMOVED]`

2. **Email Addresses**
   - Any email: `user@example.com` → `[EMAIL REMOVED]`

3. **Social Media**
   - Handles: `@username` → `[SOCIAL HANDLE REMOVED]`
   - Links: `instagram.com/profile` → `[SOCIAL LINK REMOVED]`

4. **Physical Addresses**
   - Street addresses: `123 Main St` → `[ADDRESS REMOVED]`

5. **Contact Requests**
   - Phrases: `call me at`, `text me at` → `[CONTACT REQUEST REMOVED]`

### Filter Implementation
```python
# Example from messaging_agent.py
def apply_filters(self, state: MessageState) -> MessageState:
    content = state["original_content"]
    filtered_content = content
    filter_reasons = []
    
    for rule in self.filter_rules:
        if rule["rule_type"] == "regex":
            pattern = re.compile(rule["pattern"], re.IGNORECASE)
            matches = pattern.findall(filtered_content)
            if matches:
                filtered_content = pattern.sub(rule["replacement"], filtered_content)
                # Track what was filtered
```

## API Usage Examples

### Send a Message
```javascript
// POST /api/messages/send
const response = await fetch('http://localhost:8008/api/messages/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        content: "I'm interested in your project. Call me at 555-123-4567",
        sender_type: "contractor",
        sender_id: "contractor-uuid",
        bid_card_id: "bid-card-uuid",
        conversation_id: null // Will create new conversation
    })
});

// Response
{
    "id": "message-uuid",
    "conversation_id": "conversation-uuid",
    "filtered_content": "I'm interested in your project. [CONTACT REQUEST REMOVED] [PHONE REMOVED]",
    "content_filtered": true,
    "filter_reasons": [
        {
            "category": "contact_request",
            "pattern": "call me at",
            "severity": "high",
            "matched_text": "call me at",
            "replacement": "[CONTACT REQUEST REMOVED]"
        },
        {
            "category": "phone",
            "pattern": "\\b\\d{3}[-.\s]?\\d{3}[-.\s]?\\d{4}\\b",
            "severity": "high",
            "matched_text": "555-123-4567",
            "replacement": "[PHONE REMOVED]"
        }
    ]
}
```

### Send Broadcast Message
```javascript
// POST /api/messages/broadcast
const response = await fetch('http://localhost:8008/api/messages/broadcast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        content: "Project update: Timeline changed. Contact me for details.",
        sender_type: "homeowner",
        sender_id: "homeowner-uuid",
        bid_card_id: "bid-card-uuid",
        recipient_type: "bidding_contractors" // or "all_contractors"
    })
});
```

### Get Conversations
```javascript
// GET /api/messages/conversations/{bid_card_id}?user_type=homeowner&user_id={user_id}
const response = await fetch(
    'http://localhost:8008/api/messages/conversations/bid-card-uuid?user_type=homeowner&user_id=user-uuid'
);

// Response
[
    {
        "id": "conversation-uuid",
        "contractor_alias": "Contractor A",
        "homeowner_unread_count": 2,
        "last_message_at": "2024-01-15T10:30:00Z"
    }
]
```

## Frontend Integration Guide

### React Components Needed

1. **ConversationList Component**
   ```typescript
   interface ConversationListProps {
       bidCardId: string;
       userType: 'homeowner' | 'contractor';
       userId: string;
       onSelectConversation: (conversationId: string) => void;
   }
   ```

2. **MessageThread Component**
   ```typescript
   interface MessageThreadProps {
       conversationId: string;
       currentUserId: string;
       userType: 'homeowner' | 'contractor';
   }
   ```

3. **MessageInput Component**
   ```typescript
   interface MessageInputProps {
       onSendMessage: (content: string) => void;
       placeholder?: string;
       showFilterWarning?: boolean;
   }
   ```

### State Management
```typescript
// Add to BidCardContext
interface BidCardContextType {
    // ... existing methods
    
    // Messaging methods
    sendMessage: (request: MessageSendRequest) => Promise<Message>;
    getConversations: (bidCardId: string) => Promise<Conversation[]>;
    getMessages: (conversationId: string, limit?: number) => Promise<Message[]>;
    markMessagesRead: (messageIds: string[]) => Promise<void>;
    sendBroadcast: (request: BroadcastRequest) => Promise<BroadcastResult>;
}
```

## Security Considerations

1. **Identity Protection**
   - Contractors identified only by aliases (Contractor A, B, C)
   - No real names exchanged in messages
   - Homeowner identity protected from contractors

2. **Content Filtering**
   - All messages filtered before storage
   - Original content stored for audit trail
   - Filter reasons tracked for transparency

3. **Access Control**
   - Messages only visible to conversation participants
   - Broadcast messages require sender authentication
   - Read receipts track message consumption

## Testing

### Unit Test Example
```python
def test_phone_filtering():
    message = "Call me at 555-123-4567"
    result = filter_content(message)
    assert result == "Call me at [PHONE REMOVED]"
```

### Integration Test Example
```javascript
// Test API endpoint
const testMessage = {
    content: "Email me at test@example.com",
    sender_type: "contractor",
    sender_id: "test-contractor",
    bid_card_id: "test-bid-card"
};

const response = await fetch('/api/messages/send', {
    method: 'POST',
    body: JSON.stringify(testMessage)
});

const result = await response.json();
expect(result.filtered_content).toBe("Email me at [EMAIL REMOVED]");
```

## Next Steps

1. **Build React Components**
   - Create ConversationList with unread badges
   - Build MessageThread with real-time updates
   - Add MessageInput with filter warnings

2. **Implement WebSocket Support**
   - Real-time message delivery
   - Online/offline status
   - Typing indicators

3. **Add File Attachments**
   - Support images and documents
   - Filter metadata from images
   - Scan documents for contact info

4. **Enhanced Features**
   - Message search
   - Conversation archiving
   - Blocked user management
   - Message templates

## Migration Applied
```sql
-- Migration: 003_messaging_system.sql
-- Status: ✅ Successfully applied
-- Tables created: 6
-- Indexes created: 6
-- Triggers created: 2
-- Filter rules inserted: 15
```

## File Locations
- **Database Migration**: `/ai-agents/migrations/003_messaging_system.sql`
- **Messaging Agent**: `/ai-agents/agents/messaging_agent.py`
- **API Routes**: `/ai-agents/routers/messaging_api.py`
- **Test File**: `/test_messaging_simple.py`
- **Test UI**: `/ai-agents/static/test-messaging.html`

## Support
For questions or issues with the messaging system, contact Agent 1 (Frontend) team.