# Bid Card Tracking & Routing System

## Current vs Required Architecture

### Current System
- Bid cards have basic `id` field
- Email variant shows static URL: `https://instabids.com/bid-cards/${bidCard.id}`
- No tracking, no attribution, no routing

### Required System for External Distribution

## 1. Database Schema Updates

```sql
-- Add tracking fields to bid_cards table
ALTER TABLE bid_cards
ADD COLUMN IF NOT EXISTS public_id VARCHAR(50) UNIQUE,
ADD COLUMN IF NOT EXISTS share_token VARCHAR(100) UNIQUE,
ADD COLUMN IF NOT EXISTS created_by_user_id UUID REFERENCES auth.users(id),
ADD COLUMN IF NOT EXISTS homeowner_id UUID REFERENCES profiles(id),
ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS contractor_interest_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS share_settings JSONB DEFAULT '{}'::jsonb;

-- Create tracking table for bid card interactions
CREATE TABLE IF NOT EXISTS bid_card_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_card_id UUID REFERENCES bid_cards(id),
    interaction_type VARCHAR(50) NOT NULL, -- 'view', 'click', 'interest', 'bid_submitted'
    source_channel VARCHAR(50), -- 'email', 'sms', 'website', 'direct'
    referrer_code VARCHAR(100), -- Contractor referral code
    contractor_id UUID REFERENCES profiles(id),
    session_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create contractor tracking URLs table
CREATE TABLE IF NOT EXISTS bid_card_share_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_card_id UUID REFERENCES bid_cards(id),
    contractor_id UUID REFERENCES profiles(id),
    unique_token VARCHAR(100) UNIQUE NOT NULL,
    channel VARCHAR(50) NOT NULL, -- 'email', 'sms', 'website_embed'
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_bid_card_interactions_bid_card ON bid_card_interactions(bid_card_id);
CREATE INDEX idx_bid_card_interactions_contractor ON bid_card_interactions(contractor_id);
CREATE INDEX idx_bid_card_share_links_token ON bid_card_share_links(unique_token);
```

## 2. URL Structure & Routing

### Public Bid Card URLs
```
# Basic public URL (no tracking)
https://instabids.com/projects/{public_id}

# Tracked URL for contractor outreach
https://instabids.com/p/{share_token}?ref={contractor_code}&src={channel}

# Embeddable widget URL
https://instabids.com/widget/bid-card/{public_id}?contractor={contractor_id}
```

### URL Generation Logic
```python
import secrets
import hashlib
from datetime import datetime

def generate_bid_card_urls(bid_card_id: str, homeowner_id: str) -> dict:
    """Generate tracking URLs for bid card distribution"""
    
    # Generate public ID (shorter, readable)
    timestamp = datetime.now().strftime("%y%m%d")
    hash_part = hashlib.md5(f"{bid_card_id}{homeowner_id}".encode()).hexdigest()[:6]
    public_id = f"IB{timestamp}{hash_part}".upper()
    
    # Generate share token (secure, unguessable)
    share_token = secrets.token_urlsafe(32)
    
    return {
        "public_id": public_id,  # IB250130A3F2B1
        "share_token": share_token,
        "public_url": f"https://instabids.com/projects/{public_id}",
        "tracked_url": f"https://instabids.com/p/{share_token}"
    }

def generate_contractor_tracking_url(bid_card_id: str, contractor_id: str, channel: str) -> str:
    """Generate unique tracking URL for each contractor"""
    
    # Create unique token for this contractor/bid combo
    unique_token = secrets.token_urlsafe(16)
    
    # Store in bid_card_share_links table
    save_share_link(bid_card_id, contractor_id, unique_token, channel)
    
    # Return trackable URL
    return f"https://instabids.com/p/{unique_token}?src={channel}"
```

## 3. Contractor Onboarding Flow

### When Contractor Clicks Bid Card Link

```typescript
// pages/BidCardLanding.tsx
interface BidCardLandingProps {
  token: string;
  source?: string;
  ref?: string;
}

const BidCardLanding: React.FC = () => {
  const { token, source, ref } = useParams();
  const [bidCard, setBidCard] = useState(null);
  const [isContractor, setIsContractor] = useState(false);
  
  useEffect(() => {
    // Track the click
    trackInteraction(token, 'view', source, ref);
    
    // Load bid card data
    loadBidCardByToken(token);
    
    // Check if user is logged in
    checkContractorStatus();
  }, []);
  
  const handleExpressInterest = async () => {
    if (!isContractor) {
      // Redirect to contractor signup with return URL
      const returnUrl = encodeURIComponent(window.location.href);
      navigate(`/contractor/signup?return=${returnUrl}&bid=${bidCard.public_id}`);
    } else {
      // Submit interest/bid directly
      await submitContractorInterest(bidCard.id);
    }
  };
  
  return (
    <div>
      {/* Show bid card with special contractor CTAs */}
      <BidCard 
        bidCard={bidCard}
        variant="contractor"
        showQuoteButton={true}
        onSubmitQuote={handleExpressInterest}
      />
      
      {!isContractor && (
        <ContractorSignupPrompt 
          message="Join InstaBids to submit your quote"
          bidCardId={bidCard.public_id}
        />
      )}
    </div>
  );
};
```

### Contractor Quick Signup Flow

```typescript
// pages/ContractorQuickSignup.tsx
const ContractorQuickSignup: React.FC = () => {
  const { bid } = useParams();
  const [step, setStep] = useState(1);
  
  const handleQuickSignup = async (data) => {
    // Step 1: Basic info (name, phone, email)
    // Step 2: Trade & service area
    // Step 3: Quick verification (license/insurance Y/N)
    // Step 4: Submit quote for the specific bid
    
    const contractor = await createContractorAccount(data);
    
    // Auto-submit interest in the bid that brought them here
    if (bid) {
      await submitQuoteForBid(contractor.id, bid, data.quote);
    }
    
    // Redirect to contractor dashboard
    navigate('/contractor/dashboard');
  };
  
  return (
    <QuickSignupWizard 
      steps={[
        'Contact Info',
        'Trade & Area', 
        'Verification',
        'Submit Quote'
      ]}
      bidContext={bid}
      onComplete={handleQuickSignup}
    />
  );
};
```

## 4. Tracking & Analytics

### Backend Tracking Endpoints

```python
# api/tracking.py
from fastapi import APIRouter, Request
from typing import Optional

router = APIRouter()

@router.post("/track/bid-card/{token}")
async def track_bid_card_interaction(
    token: str,
    interaction_type: str,
    source: Optional[str] = None,
    ref: Optional[str] = None,
    request: Request = None
):
    """Track all bid card interactions"""
    
    # Get bid card by token
    link = get_share_link_by_token(token)
    if not link:
        return {"error": "Invalid token"}
    
    # Record interaction
    interaction = {
        "bid_card_id": link.bid_card_id,
        "interaction_type": interaction_type,
        "source_channel": source,
        "referrer_code": ref,
        "contractor_id": link.contractor_id,
        "session_data": {
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.now().isoformat()
        }
    }
    
    save_interaction(interaction)
    
    # Update click counts
    if interaction_type == "view":
        increment_click_count(token)
    elif interaction_type == "conversion":
        increment_conversion_count(token)
    
    return {"success": True}

@router.get("/analytics/bid-card/{bid_card_id}")
async def get_bid_card_analytics(bid_card_id: str):
    """Get analytics for a bid card"""
    
    return {
        "total_views": count_interactions(bid_card_id, "view"),
        "unique_contractors": count_unique_contractors(bid_card_id),
        "interest_expressed": count_interactions(bid_card_id, "interest"),
        "quotes_submitted": count_interactions(bid_card_id, "bid_submitted"),
        "by_channel": {
            "email": count_by_channel(bid_card_id, "email"),
            "sms": count_by_channel(bid_card_id, "sms"),
            "website": count_by_channel(bid_card_id, "website")
        },
        "conversion_funnel": {
            "viewed": 100,
            "clicked_cta": 67,
            "started_signup": 45,
            "completed_signup": 28,
            "submitted_quote": 12
        }
    }
```

## 5. Multi-Channel Distribution

### Email Integration
```python
def generate_email_bid_card(bid_card, contractor):
    """Generate tracked bid card for email"""
    
    # Get unique tracking URL for this contractor
    tracking_url = generate_contractor_tracking_url(
        bid_card.id, 
        contractor.id, 
        "email"
    )
    
    return {
        "html": render_bid_card_email(bid_card, tracking_url),
        "tracking_pixel": f"{API_URL}/track/open/{tracking_url}",
        "cta_url": tracking_url
    }
```

### SMS Integration
```python
def generate_sms_bid_card(bid_card, contractor):
    """Generate tracked bid card for SMS"""
    
    # Get short URL for SMS
    tracking_url = generate_contractor_tracking_url(
        bid_card.id,
        contractor.id, 
        "sms"
    )
    short_url = create_short_url(tracking_url)  # bit.ly integration
    
    return f"""New {bid_card.project_type} job in {bid_card.location}
Budget: {bid_card.budget_display}
Timeline: {bid_card.urgency}

View details & submit quote: {short_url}"""
```

### Website Widget
```html
<!-- Embeddable bid card widget -->
<div id="instabids-bid-card" 
     data-bid-id="IB250130A3F2B1"
     data-contractor-id="contractor_abc123">
</div>
<script src="https://instabids.com/widget.js"></script>
```

## 6. Security & Privacy

### Access Control
- Public URLs show limited info (no homeowner details)
- Full details require contractor authentication
- Homeowner contact info never exposed until bid accepted

### Token Security
- Share tokens expire after 30 days
- One-time use tokens for sensitive actions
- Rate limiting on tracking endpoints

### Data Privacy
- No PII in URLs
- Tracking data anonymized
- GDPR compliant tracking consent

## 7. Implementation Priority

1. **Phase 1**: Basic tracking URLs
   - Update database schema
   - Generate public_id and share_token
   - Create landing page for bid cards

2. **Phase 2**: Contractor onboarding
   - Quick signup flow
   - Auto-link to bid that brought them

3. **Phase 3**: Full tracking
   - Click tracking
   - Conversion tracking  
   - Analytics dashboard

4. **Phase 4**: Multi-channel
   - Email templates with tracking
   - SMS with short URLs
   - Embeddable widgets

This system ensures every bid card interaction is tracked while maintaining a smooth contractor onboarding experience.