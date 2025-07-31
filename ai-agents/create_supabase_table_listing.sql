-- Complete SQL script to enable table listing in Supabase
-- Run this in your Supabase SQL Editor

-- Create a function that lists all tables with details
CREATE OR REPLACE FUNCTION public.list_all_database_tables()
RETURNS TABLE(
    schema_name text,
    table_name text,
    table_type text,
    is_instabids_table boolean
)
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT 
        n.nspname as schema_name,
        c.relname as table_name,
        CASE c.relkind
            WHEN 'r' THEN 'TABLE'
            WHEN 'v' THEN 'VIEW'
            WHEN 'm' THEN 'MATERIALIZED VIEW'
            WHEN 'f' THEN 'FOREIGN TABLE'
            ELSE 'OTHER'
        END as table_type,
        CASE 
            WHEN c.relname IN (
                'bid_cards', 'bid_card_distributions', 'bid_card_views',
                'contractor_leads', 'contractor_outreach_attempts', 
                'contractor_engagement_summary', 'contractor_responses',
                'outreach_campaigns', 'campaign_contractors',
                'agent_conversations', 'profiles', 'projects',
                'homeowners', 'contractors', 'bids', 'messages',
                'potential_contractors', 'email_tracking_events',
                'followup_attempts', 'followup_logs', 'notifications'
            ) THEN true
            ELSE false
        END as is_instabids_table
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    AND c.relkind IN ('r', 'v', 'm', 'f')
    ORDER BY n.nspname, c.relname;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION public.list_all_database_tables() TO anon, authenticated;

-- Create a simpler version that just lists public tables
CREATE OR REPLACE FUNCTION public.list_public_tables()
RETURNS TABLE(table_name text)
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT tablename::text
    FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION public.list_public_tables() TO anon, authenticated;

-- Test the functions
SELECT * FROM list_all_database_tables() WHERE schema_name = 'public';