-- Fix the analytics view to not reference timeline column
-- Since timeline is stored in project_details JSON, we'll extract it or use urgency

DROP VIEW IF EXISTS bid_card_analytics;

CREATE OR REPLACE VIEW bid_card_analytics AS
SELECT 
  bc.id,
  bc.project_type,
  bc.urgency as timeline_urgency,
  bc.created_at,
  COUNT(DISTINCT bcv.id) as total_views,
  COUNT(DISTINCT bcv.contractor_lead_id) as unique_contractor_views,
  COUNT(DISTINCT CASE WHEN bcv.clicked_cta THEN bcv.contractor_lead_id END) as contractors_interested,
  AVG(bcv.view_duration_seconds) as avg_view_duration,
  MAX(bcv.created_at) as last_viewed_at
FROM bid_cards bc
LEFT JOIN bid_card_views bcv ON bc.id = bcv.bid_card_id
GROUP BY bc.id, bc.project_type, bc.urgency, bc.created_at;