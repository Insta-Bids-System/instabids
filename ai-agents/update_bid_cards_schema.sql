-- Update bid_cards table to include all 12 data points from CIA conversations
-- Run this after the initial create_bid_cards_table.sql

-- Add location fields (Data Point #4)
ALTER TABLE bid_cards 
ADD COLUMN IF NOT EXISTS location_address VARCHAR(255),
ADD COLUMN IF NOT EXISTS location_zip_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS location_city VARCHAR(100),
ADD COLUMN IF NOT EXISTS location_state VARCHAR(50);

-- Add project description (Data Point #5)
ALTER TABLE bid_cards
ADD COLUMN IF NOT EXISTS project_description TEXT;

-- Add property details (Data Point #6)
ALTER TABLE bid_cards
ADD COLUMN IF NOT EXISTS property_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS property_size VARCHAR(100),
ADD COLUMN IF NOT EXISTS property_access_notes TEXT;

-- Add materials/preferences (Data Point #7)
ALTER TABLE bid_cards
ADD COLUMN IF NOT EXISTS materials_preferences JSONB DEFAULT '[]'::jsonb;

-- Add homeowner preferences (Data Point #10)
ALTER TABLE bid_cards
ADD COLUMN IF NOT EXISTS homeowner_communication_preference VARCHAR(50),
ADD COLUMN IF NOT EXISTS homeowner_scheduling_preference VARCHAR(50),
ADD COLUMN IF NOT EXISTS homeowner_decision_style VARCHAR(50);

-- Add concerns/issues (Data Point #11)
ALTER TABLE bid_cards
ADD COLUMN IF NOT EXISTS concerns_issues JSONB DEFAULT '[]'::jsonb;

-- Update contractor requirements to be more detailed (Data Point #12)
ALTER TABLE bid_cards
ADD COLUMN IF NOT EXISTS contractor_specialties_required JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS contractor_experience_level VARCHAR(50);

-- Add indexes for new searchable fields
CREATE INDEX IF NOT EXISTS idx_bid_cards_location_zip ON bid_cards(location_zip_code);
CREATE INDEX IF NOT EXISTS idx_bid_cards_location_city ON bid_cards(location_city);
CREATE INDEX IF NOT EXISTS idx_bid_cards_property_type ON bid_cards(property_type);

-- Add comments for clarity
COMMENT ON COLUMN bid_cards.location_address IS 'Full address from CIA conversation';
COMMENT ON COLUMN bid_cards.location_zip_code IS 'Extracted zip code for contractor matching';
COMMENT ON COLUMN bid_cards.location_city IS 'City name for regional contractor search';
COMMENT ON COLUMN bid_cards.location_state IS 'State for contractor licensing requirements';
COMMENT ON COLUMN bid_cards.project_description IS 'Extracted description of work needed';
COMMENT ON COLUMN bid_cards.property_type IS 'single family, condo, apartment, commercial';
COMMENT ON COLUMN bid_cards.property_size IS 'Size in acres or sq ft';
COMMENT ON COLUMN bid_cards.property_access_notes IS 'Gate codes, HOA restrictions, etc';
COMMENT ON COLUMN bid_cards.materials_preferences IS 'Array of preferred materials';
COMMENT ON COLUMN bid_cards.homeowner_communication_preference IS 'text, phone, email, any';
COMMENT ON COLUMN bid_cards.homeowner_scheduling_preference IS 'weekends, evenings, mornings, flexible';
COMMENT ON COLUMN bid_cards.homeowner_decision_style IS 'quick_decision, comparison_shopper, standard';
COMMENT ON COLUMN bid_cards.concerns_issues IS 'Array of specific concerns mentioned';
COMMENT ON COLUMN bid_cards.contractor_specialties_required IS 'Array of required specialties';
COMMENT ON COLUMN bid_cards.contractor_experience_level IS 'standard, experienced, expert';

-- Update the bid_document to ensure it contains all extracted data
COMMENT ON COLUMN bid_cards.bid_document IS 'Complete bid card data including all 12 extracted data points';