-- Add tracking fields to bid_cards table for contractor acquisition
-- This enables tracking which bid cards lead to contractor signups

-- Add public token for shareable URLs and basic tracking
ALTER TABLE bid_cards
ADD COLUMN IF NOT EXISTS public_token VARCHAR(20) UNIQUE,
ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS click_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS contractor_signups INTEGER DEFAULT 0;

-- Create simple tracking table for contractor acquisition
CREATE TABLE IF NOT EXISTS bid_card_clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_card_id UUID REFERENCES bid_cards(id),
    bid_card_token VARCHAR(20),
    source_channel VARCHAR(50), -- 'email', 'sms', 'website', 'direct'
    clicked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    resulted_in_signup BOOLEAN DEFAULT FALSE,
    new_contractor_id UUID REFERENCES profiles(id),
    signup_completed_at TIMESTAMP WITH TIME ZONE
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_bid_card_clicks_token ON bid_card_clicks(bid_card_token);
CREATE INDEX IF NOT EXISTS idx_bid_card_clicks_bid_card ON bid_card_clicks(bid_card_id);
CREATE INDEX IF NOT EXISTS idx_bid_cards_public_token ON bid_cards(public_token);

-- Add trigger to auto-generate public_token if not provided
CREATE OR REPLACE FUNCTION generate_bid_card_token()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.public_token IS NULL THEN
        -- Use bid_card_number if exists, otherwise generate from ID
        IF NEW.bid_card_number IS NOT NULL THEN
            NEW.public_token = NEW.bid_card_number;
        ELSE
            NEW.public_token = 'BC' || SUBSTRING(NEW.id::TEXT, 1, 8);
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ensure_bid_card_token
    BEFORE INSERT OR UPDATE ON bid_cards
    FOR EACH ROW
    EXECUTE FUNCTION generate_bid_card_token();

-- Add comments for documentation
COMMENT ON COLUMN bid_cards.public_token IS 'Public token for shareable URLs (e.g. BC0730123456)';
COMMENT ON COLUMN bid_cards.view_count IS 'Total number of times bid card was viewed';
COMMENT ON COLUMN bid_cards.click_count IS 'Total number of CTA clicks from bid card';
COMMENT ON COLUMN bid_cards.contractor_signups IS 'Number of contractors who signed up from this bid card';
COMMENT ON TABLE bid_card_clicks IS 'Tracks contractor acquisition from bid card distribution';