# Supabase Storage Setup Guide

## Quick Fix Instructions

You need to manually set up the storage bucket through the Supabase Dashboard because RLS policies are blocking programmatic creation.

### Step 1: Create the Storage Bucket

1. Go to your Supabase Dashboard: https://app.supabase.com/project/yuysysshjqiozxlihudz
2. Click on **Storage** in the left sidebar
3. Click **New bucket** button
4. Enter:
   - Bucket name: `project-images`
   - Public bucket: ✅ Check this box (IMPORTANT!)
   - Allowed MIME types: Leave empty (allows all image types)
   - Max file size: 10MB (or leave default)
5. Click **Create bucket**

### Step 2: Set Up RLS Policies

After creating the bucket:

1. Stay in the Storage section
2. Click on the `project-images` bucket
3. Click on **Policies** tab
4. You'll see "No policies set up yet"
5. Click **New policy** and create these policies:

#### Policy 1: Public Read Access
- **Name**: `Allow public read`
- **Policy command**: `SELECT`
- **Target roles**: Leave empty (applies to all)
- **Policy definition**: 
  ```sql
  true
  ```
  This allows anyone to view images

#### Policy 2: Allow Uploads from Backend
- **Name**: `Allow authenticated uploads`
- **Policy command**: `INSERT`
- **Target roles**: Leave empty
- **Policy definition**:
  ```sql
  true
  ```
  This allows the backend to upload images

#### Policy 3: Allow Updates
- **Name**: `Allow updates`
- **Policy command**: `UPDATE`
- **Target roles**: Leave empty
- **Policy definition**:
  ```sql
  true
  ```

#### Policy 4: Allow Deletes
- **Name**: `Allow deletes`
- **Policy command**: `DELETE`
- **Target roles**: Leave empty
- **Policy definition**:
  ```sql
  true
  ```

### Step 3: Test It Works

Run this test script after setting up:

```bash
cd ai-agents
python test_storage_upload.py
```

## Alternative: SQL Commands

If you prefer, you can run all policies at once in the SQL Editor:

1. Go to **SQL Editor** in Supabase Dashboard
2. Paste and run:

```sql
-- Enable RLS on storage tables
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage.buckets ENABLE ROW LEVEL SECURITY;

-- Create bucket (if not exists)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('project-images', 'project-images', true, 10485760, null)
ON CONFLICT (id) DO NOTHING;

-- Allow all operations on project-images bucket
CREATE POLICY "Allow all operations on project-images" ON storage.objects
FOR ALL USING (bucket_id = 'project-images');
```

## Why This is Happening

Supabase has Row Level Security (RLS) enabled by default on storage tables. This prevents unauthorized access but also blocks programmatic bucket creation unless you're using the Dashboard or have special permissions.

The manual setup only needs to be done once. After that, the CIA agent will be able to upload images without token limit issues!