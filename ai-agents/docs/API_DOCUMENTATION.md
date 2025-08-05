# InstaBids Backend API Documentation

## Overview
The InstaBids backend provides intelligent contractor outreach orchestration with timing calculations, campaign management, and automated check-ins.

**Base URL**: `http://localhost:8008`

## Authentication
Currently using Supabase RLS. Backend operations require service role key or disabled RLS on campaign tables.

## Endpoints

### 1. Timing & Probability Calculation

#### Calculate Outreach Strategy
```http
POST /api/timing/calculate
```

Calculates how many contractors to contact based on timeline and business requirements.

**Request Body:**
```json
{
  "bids_needed": 4,
  "timeline_hours": 24,
  "tier1_available": 10,
  "tier2_available": 30,
  "tier3_available": 100,
  "project_type": "Kitchen Remodel",
  "location": {
    "city": "Denver",
    "state": "CO"
  }
}
```

**Response:**
```json
{
  "success": true,
  "total_contractors": 8,
  "expected_responses": 4.0,
  "confidence": 100,
  "urgency": "standard",
  "tier_breakdown": {
    "tier1": {
      "to_contact": 0,
      "expected_responses": 0.0,
      "response_rate": 0.9
    },
    "tier2": {
      "to_contact": 8,
      "expected_responses": 4.0,
      "response_rate": 0.5
    },
    "tier3": {
      "to_contact": 0,
      "expected_responses": 0.0,
      "response_rate": 0.33
    }
  },
  "check_in_times": [
    "2024-01-31T18:00:00",
    "2024-02-01T00:00:00",
    "2024-02-01T06:00:00"
  ],
  "recommendations": [
    "Standard timeline allows for optimal contractor selection"
  ]
}
```

### 2. Campaign Management

#### Create Intelligent Campaign
```http
POST /api/campaigns/create-intelligent
```

Creates a campaign with automatic timing and contractor selection.

**Request Body:**
```json
{
  "bid_card_id": "123e4567-e89b-12d3-a456-426614174000",
  "project_type": "Kitchen Remodel",
  "timeline_hours": 24,
  "urgency_level": "standard",
  "bids_needed": 4,
  "location": {
    "city": "Denver",
    "state": "CO"
  }
}
```

**Response:**
```json
{
  "success": true,
  "campaign_id": "456e7890-e89b-12d3-a456-426614174000",
  "total_contractors": 8,
  "strategy": {
    "urgency": "standard",
    "expected_responses": 4.0,
    "confidence": 100
  }
}
```

#### Check Campaign Status
```http
GET /api/campaigns/{campaign_id}/check-in
```

Checks if campaign needs escalation based on current performance.

**Response:**
```json
{
  "success": true,
  "campaign_id": "456e7890-e89b-12d3-a456-426614174000",
  "bids_received": 2,
  "bids_expected": 4,
  "on_track": false,
  "escalation_needed": true,
  "escalation_level": "medium",
  "additional_contractors_needed": 4
}
```

#### Get Campaign Metrics
```http
GET /api/campaigns/{campaign_id}/metrics
```

Returns detailed performance metrics for a campaign.

**Response:**
```json
{
  "success": true,
  "campaign_id": "456e7890-e89b-12d3-a456-426614174000",
  "status": "active",
  "created_at": "2024-01-31T12:00:00",
  "metrics": {
    "total_contractors": 8,
    "messages_sent": 8,
    "open_rate": 62.5,
    "response_rate": 25.0,
    "bids_received": 2
  },
  "check_ins": [
    {
      "time": "2024-01-31T18:00:00",
      "bids_at_time": 1,
      "on_track": false,
      "action_taken": "escalated"
    }
  ]
}
```

#### Escalate Campaign
```http
POST /api/campaigns/{campaign_id}/escalate
```

Manually escalates a campaign by adding more contractors.

**Request Body:**
```json
{
  "additional_contractors": 5,
  "tier_preference": "tier2"
}
```

**Response:**
```json
{
  "success": true,
  "campaign_id": "456e7890-e89b-12d3-a456-426614174000",
  "contractors_added": 5,
  "new_total": 13
}
```

### 3. Error Handling

All endpoints follow a consistent error format:

```json
{
  "success": false,
  "error_id": "ERR_20240131_120000_database",
  "error": "new row violates row-level security policy",
  "category": "permission",
  "severity": "high",
  "recovery_strategy": {
    "action": "fix_permissions",
    "suggestion": "Database permissions need to be updated. Contact admin.",
    "can_retry": false
  },
  "user_message": "Database security policy is blocking this operation. Please contact support."
}
```

## Urgency Levels

The system uses intelligent timing based on urgency:

- **emergency**: < 1 hour timeline
- **urgent**: 1-12 hours timeline  
- **standard**: 12-72 hours timeline
- **group_bidding**: 72-120 hours timeline
- **flexible**: > 120 hours timeline

## Business Rules

### Contractor Response Rates
- **Tier 1 (Internal)**: 90% response rate
- **Tier 2 (Prospects)**: 50% response rate
- **Tier 3 (Cold)**: 33% response rate

### Check-in Schedule
- **25%** of timeline: First check-in
- **50%** of timeline: Second check-in
- **75%** of timeline: Final check-in

### Escalation Thresholds
- Escalate if bids received < 75% of expected at check-in
- Add more contractors based on remaining time and deficit

## Testing

Run the test suite:
```bash
python test_api_endpoints.py
```

## Common Issues

### RLS Policy Error
If you get "new row violates row-level security policy":
1. Run migration: `009_disable_rls_campaigns.sql`
2. Or update service role key in `.env`

### Invalid API Key
Ensure `SUPABASE_SERVICE_ROLE_KEY` is set correctly in `.env`