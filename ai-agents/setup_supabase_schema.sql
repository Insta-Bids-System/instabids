-- Supabase Schema Setup for CIA -> JAA Workflow
-- Run this in the Supabase SQL Editor

-- Create conversations table for CIA agent
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    state JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create bid_cards table for JAA agent  
CREATE TABLE IF NOT EXISTS bid_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cia_session_id VARCHAR(255) REFERENCES conversations(session_id),
    bid_card_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Project Assessment
    project_type VARCHAR(100),
    urgency_level VARCHAR(20) CHECK (urgency_level IN ('emergency', 'week', 'month', 'flexible')),
    complexity_score INTEGER CHECK (complexity_score >= 1 AND complexity_score <= 10),
    contractor_count_needed INTEGER DEFAULT 3,
    
    -- Financial
    budget_min INTEGER,
    budget_max INTEGER,
    
    -- Generated Content
    bid_document JSONB, -- Complete bid card data
    requirements_extracted JSONB, -- Structured requirements
    
    -- Status
    status VARCHAR(20) DEFAULT 'generated',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_bid_cards_session_id ON bid_cards(cia_session_id);
CREATE INDEX IF NOT EXISTS idx_bid_cards_urgency ON bid_cards(urgency_level);
CREATE INDEX IF NOT EXISTS idx_bid_cards_created_at ON bid_cards(created_at);

-- Add Row Level Security (RLS) policies
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE bid_cards ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (can be restricted later)
CREATE POLICY IF NOT EXISTS "Enable all operations on conversations" ON conversations
    FOR ALL USING (true);

CREATE POLICY IF NOT EXISTS "Enable all operations on bid_cards" ON bid_cards  
    FOR ALL USING (true);

-- Verify tables were created
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('conversations', 'bid_cards')
AND table_schema = 'public'
ORDER BY table_name, ordinal_position;