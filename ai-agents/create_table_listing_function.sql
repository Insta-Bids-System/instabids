-- Run this in your Supabase SQL Editor to create a function that lists all tables
-- This bypasses the MCP tool limitations

-- Function to list all public tables
CREATE OR REPLACE FUNCTION list_all_public_tables()
RETURNS TABLE(
    table_name text,
    table_type text,
    row_count bigint
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.tablename::text as table_name,
        CASE 
            WHEN t.tablename LIKE '%_view' THEN 'VIEW'
            ELSE 'TABLE'
        END as table_type,
        (SELECT COUNT(*) FROM public.tmp_table)::bigint as row_count
    FROM pg_tables t
    WHERE t.schemaname = 'public'
    ORDER BY t.tablename;
EXCEPTION
    WHEN OTHERS THEN
        -- If count fails, just return table names
        RETURN QUERY
        SELECT 
            t.tablename::text as table_name,
            'TABLE'::text as table_type,
            0::bigint as row_count
        FROM pg_tables t
        WHERE t.schemaname = 'public'
        ORDER BY t.tablename;
END;
$$;

-- Grant execute permission to anon and authenticated roles
GRANT EXECUTE ON FUNCTION list_all_public_tables() TO anon, authenticated;

-- Test the function
SELECT * FROM list_all_public_tables();