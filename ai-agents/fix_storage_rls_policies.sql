-- Fix Storage RLS Policies for project-images bucket
-- Run this in Supabase SQL Editor

-- Enable RLS on storage.objects if not already enabled
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to recreate them)
DROP POLICY IF EXISTS "Allow public read access to project-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated users to upload to project-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow service role full access to project-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow users to update their own images in project-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow users to delete their own images in project-images" ON storage.objects;

-- 1. Allow anyone to read images from project-images bucket (PUBLIC ACCESS)
CREATE POLICY "Allow public read access to project-images" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'project-images');

-- 2. Allow authenticated users to upload images to project-images bucket
CREATE POLICY "Allow authenticated users to upload to project-images" 
ON storage.objects FOR INSERT 
WITH CHECK (
    bucket_id = 'project-images' 
    AND auth.role() = 'authenticated'
);

-- 3. Allow service role to do anything (for backend operations)
CREATE POLICY "Allow service role full access to project-images" 
ON storage.objects 
USING (
    bucket_id = 'project-images' 
    AND auth.role() = 'service_role'
);

-- 4. Allow users to update their own uploaded images
CREATE POLICY "Allow users to update their own images in project-images" 
ON storage.objects FOR UPDATE 
USING (
    bucket_id = 'project-images' 
    AND auth.uid()::text = (storage.foldername(name))[1]
)
WITH CHECK (
    bucket_id = 'project-images' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);

-- 5. Allow users to delete their own uploaded images
CREATE POLICY "Allow users to delete their own images in project-images" 
ON storage.objects FOR DELETE 
USING (
    bucket_id = 'project-images' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Also create policies for anonymous/service operations (for the CIA agent)
-- This allows the backend to upload on behalf of users
CREATE POLICY "Allow anon uploads to project-images" 
ON storage.objects FOR INSERT 
WITH CHECK (
    bucket_id = 'project-images'
);

-- Verify the policies were created
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'objects' 
AND schemaname = 'storage'
ORDER BY policyname;