-- SQL Script to create all missing tables for Instabids Intelligent Automation System
-- Run this in your Supabase SQL Editor

-- =====================================================
-- 1. BID CARD DISTRIBUTIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS bid_card_distributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_card_id UUID NOT NULL REFERENCES bid_cards(id),
    contractor_id UUID NOT NULL REFERENCES contractor_leads(id),
    
    -- Distribution Details
    sent_at TIMESTAMP DEFAULT NOW(),
    method VARCHAR(50) NOT NULL, -- 'email', 'sms', 'website'
    unique_url TEXT NOT NULL, -- Unique tracking URL for this contractor
    
    -- Tracking
    opened_at TIMESTAMP,
    first_opened_at TIMESTAMP,
    open_count INT DEFAULT 0,
    last_activity_at TIMESTAMP,
    
    -- Response Tracking
    responded_at TIMESTAMP,
    response_type VARCHAR(50), -- 'interested', 'not_interested', 'need_info'
    response_message TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_bid_distributions_bid ON bid_card_distributions(bid_card_id);
CREATE INDEX idx_bid_distributions_contractor ON bid_card_distributions(contractor_id);
CREATE INDEX idx_bid_distributions_url ON bid_card_distributions(unique_url);

-- =====================================================
-- 2. CAMPAIGN CONTRACTORS
-- =====================================================
CREATE TABLE IF NOT EXISTS campaign_contractors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES outreach_campaigns(id),
    contractor_id UUID NOT NULL REFERENCES contractor_leads(id),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'failed', 'responded'
    
    -- Outreach Details
    scheduled_for TIMESTAMP,
    sent_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    
    -- Response
    responded_at TIMESTAMP,
    response_channel VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Prevent duplicate assignments
    UNIQUE(campaign_id, contractor_id)
);

-- Indexes
CREATE INDEX idx_campaign_contractors_campaign ON campaign_contractors(campaign_id);
CREATE INDEX idx_campaign_contractors_contractor ON campaign_contractors(contractor_id);
CREATE INDEX idx_campaign_contractors_status ON campaign_contractors(status);

-- =====================================================
-- 3. CONTRACTOR RESPONSES
-- =====================================================
CREATE TABLE IF NOT EXISTS contractor_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contractor_id UUID NOT NULL REFERENCES contractor_leads(id),
    bid_card_id UUID REFERENCES bid_cards(id),
    distribution_id UUID REFERENCES bid_card_distributions(id),
    
    -- Response Details
    response_type VARCHAR(50) NOT NULL, -- 'email', 'form', 'phone', 'sms'
    response_channel VARCHAR(50), -- 'bid_card_link', 'direct_email', 'website_form'
    
    -- Content
    subject TEXT,
    message TEXT NOT NULL,
    
    -- Analysis
    sentiment VARCHAR(20), -- 'positive', 'negative', 'neutral'
    interest_level INT, -- 1-10 scale
    urgency_detected BOOLEAN DEFAULT FALSE,
    
    -- Follow-up
    requires_followup BOOLEAN DEFAULT TRUE,
    followup_completed BOOLEAN DEFAULT FALSE,
    followup_notes TEXT,
    
    -- Hot Lead Detection
    is_hot_lead BOOLEAN DEFAULT FALSE,
    hot_lead_score DECIMAL(3,2), -- 0.00 to 1.00
    hot_lead_reasons JSONB, -- Array of reasons
    
    -- Metadata
    received_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_responses_contractor ON contractor_responses(contractor_id);
CREATE INDEX idx_responses_bid_card ON contractor_responses(bid_card_id);
CREATE INDEX idx_responses_hot_leads ON contractor_responses(is_hot_lead) WHERE is_hot_lead = TRUE;
CREATE INDEX idx_responses_followup ON contractor_responses(requires_followup) WHERE requires_followup = TRUE;

-- =====================================================
-- 4. EMAIL TRACKING EVENTS
-- =====================================================
CREATE TABLE IF NOT EXISTS email_tracking_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    distribution_id UUID REFERENCES bid_card_distributions(id),
    contractor_id UUID REFERENCES contractor_leads(id),
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL, -- 'sent', 'delivered', 'opened', 'clicked', 'bounced'
    event_data JSONB, -- Provider-specific data (SendGrid, etc.)
    
    -- Click Tracking
    clicked_url TEXT,
    click_location JSONB, -- {x: 100, y: 200}
    
    -- User Agent Info
    user_agent TEXT,
    ip_address INET,
    device_type VARCHAR(50), -- 'desktop', 'mobile', 'tablet'
    
    -- Timestamp
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_email_events_distribution ON email_tracking_events(distribution_id);
CREATE INDEX idx_email_events_type ON email_tracking_events(event_type);
CREATE INDEX idx_email_events_time ON email_tracking_events(occurred_at);

-- =====================================================
-- 5. OUTREACH CAMPAIGNS (Already exists but adding for completeness)
-- =====================================================
-- This table already exists from migration 005, skipping creation

-- =====================================================
-- 6. MESSAGE TEMPLATES (Already exists but adding for completeness)
-- =====================================================
-- This table already exists from migration 005, skipping creation

-- =====================================================
-- 7. BID CARD VIEWS
-- =====================================================
CREATE TABLE IF NOT EXISTS bid_card_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_card_id UUID NOT NULL REFERENCES bid_cards(id),
    
    -- Viewer Info (if available)
    contractor_id UUID REFERENCES contractor_leads(id),
    visitor_id UUID, -- For anonymous tracking
    
    -- View Details
    viewed_at TIMESTAMP DEFAULT NOW(),
    duration_seconds INT,
    
    -- Source
    referrer_url TEXT,
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    -- Device Info
    user_agent TEXT,
    ip_address INET,
    device_type VARCHAR(50),
    browser VARCHAR(50),
    
    -- Behavior
    scroll_depth INT, -- Percentage
    clicks_count INT DEFAULT 0,
    form_started BOOLEAN DEFAULT FALSE,
    form_completed BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX idx_views_bid_card ON bid_card_views(bid_card_id);
CREATE INDEX idx_views_contractor ON bid_card_views(contractor_id);
CREATE INDEX idx_views_time ON bid_card_views(viewed_at);

-- =====================================================
-- 8. BID CARD ENGAGEMENT EVENTS
-- =====================================================
CREATE TABLE IF NOT EXISTS bid_card_engagement_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    view_id UUID NOT NULL REFERENCES bid_card_views(id),
    bid_card_id UUID NOT NULL REFERENCES bid_cards(id),
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL, -- 'click', 'form_start', 'form_submit', 'download', 'share'
    event_target TEXT, -- What was clicked/interacted with
    event_value TEXT, -- Additional data
    
    -- Timestamp
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_engagement_view ON bid_card_engagement_events(view_id);
CREATE INDEX idx_engagement_type ON bid_card_engagement_events(event_type);

-- =====================================================
-- 9. FOLLOWUP ATTEMPTS
-- =====================================================
CREATE TABLE IF NOT EXISTS followup_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contractor_id UUID NOT NULL REFERENCES contractor_leads(id),
    bid_card_id UUID REFERENCES bid_cards(id),
    response_id UUID REFERENCES contractor_responses(id),
    
    -- Attempt Details
    attempt_number INT NOT NULL DEFAULT 1,
    channel VARCHAR(50) NOT NULL, -- 'email', 'sms', 'phone'
    
    -- Content
    subject TEXT,
    message TEXT NOT NULL,
    personalization_data JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'failed'
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    
    -- Response
    got_response BOOLEAN DEFAULT FALSE,
    response_received_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_followup_contractor ON followup_attempts(contractor_id);
CREATE INDEX idx_followup_status ON followup_attempts(status);

-- =====================================================
-- 10. FOLLOWUP LOGS
-- =====================================================
CREATE TABLE IF NOT EXISTS followup_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Context
    log_type VARCHAR(50) NOT NULL, -- 'automation_run', 'email_sent', 'error', 'hot_lead'
    contractor_id UUID REFERENCES contractor_leads(id),
    bid_card_id UUID REFERENCES bid_cards(id),
    
    -- Log Details
    message TEXT NOT NULL,
    details JSONB,
    
    -- Error Tracking
    is_error BOOLEAN DEFAULT FALSE,
    error_code VARCHAR(50),
    error_stack TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_logs_type ON followup_logs(log_type);
CREATE INDEX idx_logs_contractor ON followup_logs(contractor_id);
CREATE INDEX idx_logs_errors ON followup_logs(is_error) WHERE is_error = TRUE;

-- =====================================================
-- 11. NOTIFICATIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Recipients
    user_id UUID, -- Future user reference
    notification_type VARCHAR(50) NOT NULL, -- 'hot_lead', 'response_received', 'campaign_complete'
    
    -- Content
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    action_url TEXT,
    
    -- Context
    contractor_id UUID REFERENCES contractor_leads(id),
    bid_card_id UUID REFERENCES bid_cards(id),
    campaign_id UUID REFERENCES outreach_campaigns(id),
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    
    -- Delivery
    channels JSONB, -- ['email', 'sms', 'in_app']
    delivered_channels JSONB, -- Tracks which channels succeeded
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_notifications_unread ON notifications(is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_type ON notifications(notification_type);

-- =====================================================
-- 12. MANUAL FOLLOWUP TASKS
-- =====================================================
CREATE TABLE IF NOT EXISTS manual_followup_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Task Details
    contractor_id UUID NOT NULL REFERENCES contractor_leads(id),
    bid_card_id UUID REFERENCES bid_cards(id),
    campaign_id UUID REFERENCES outreach_campaigns(id),
    
    -- Task Info
    task_type VARCHAR(50) NOT NULL, -- 'call_required', 'email_followup', 'site_visit'
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    
    -- Description
    title TEXT NOT NULL,
    description TEXT,
    notes TEXT,
    
    -- Assignment (for future use)
    assigned_to UUID,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'cancelled'
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_status ON manual_followup_tasks(status);
CREATE INDEX idx_tasks_priority ON manual_followup_tasks(priority);
CREATE INDEX idx_tasks_due ON manual_followup_tasks(due_date);

-- =====================================================
-- RESPONSE EVENTS (Additional tracking)
-- =====================================================
CREATE TABLE IF NOT EXISTS response_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    response_id UUID NOT NULL REFERENCES contractor_responses(id),
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL, -- 'received', 'processed', 'assigned', 'resolved'
    event_data JSONB,
    
    -- User/System that triggered event
    triggered_by VARCHAR(100),
    
    -- Timestamp
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- Update triggers for updated_at columns
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_bid_distributions_updated_at BEFORE UPDATE ON bid_card_distributions 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaign_contractors_updated_at BEFORE UPDATE ON campaign_contractors 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_manual_tasks_updated_at BEFORE UPDATE ON manual_followup_tasks 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Grant permissions
-- =====================================================
-- Grant appropriate permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- =====================================================
-- Enable Row Level Security (RLS) on new tables
-- =====================================================
ALTER TABLE bid_card_distributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_contractors ENABLE ROW LEVEL SECURITY;
ALTER TABLE contractor_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_tracking_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE bid_card_views ENABLE ROW LEVEL SECURITY;
ALTER TABLE bid_card_engagement_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE followup_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE followup_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE manual_followup_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE response_events ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- Create RLS policies (basic - adjust based on your needs)
-- =====================================================
-- For now, allow authenticated users to do everything
-- You should refine these based on your security requirements

CREATE POLICY "Allow all for authenticated users" ON bid_card_distributions
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON campaign_contractors
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON contractor_responses
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON email_tracking_events
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON bid_card_views
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON bid_card_engagement_events
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON followup_attempts
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON followup_logs
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON notifications
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON manual_followup_tasks
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON response_events
FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =====================================================
-- Summary
-- =====================================================
-- This script creates all missing tables needed for:
-- 1. Bid card distribution tracking
-- 2. Campaign management
-- 3. Response monitoring
-- 4. Email tracking
-- 5. Engagement analytics
-- 6. Follow-up automation
-- 7. Notification system
-- 8. Manual task management

-- After running this script, all the intelligent automation
-- components should have the database tables they need.