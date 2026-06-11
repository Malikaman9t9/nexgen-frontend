-- ============================================================
-- Migration: Create blog_posts and admin_users tables
-- Run this in the Supabase SQL editor (https://supabase.com/dashboard)
-- ============================================================

-- 1. BLOG POSTS TABLE

CREATE TABLE IF NOT EXISTS blog_posts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  slug text NOT NULL UNIQUE,
  excerpt text,
  content text,
  cover_image_url text,
  author_name text DEFAULT 'NexGenWebLab Team',
  status text DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
  tags text[] DEFAULT '{}',
  published_at timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- 2. ADMIN USERS TABLE

CREATE TABLE IF NOT EXISTS admin_users (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email text NOT NULL,
  role text DEFAULT 'editor' CHECK (role IN ('editor', 'super_admin')),
  created_at timestamptz DEFAULT now()
);

-- 3. ENABLE ROW LEVEL SECURITY

ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- 4. RLS POLICIES — blog_posts

-- Anyone can read published posts (public blog)
CREATE POLICY "Anyone can read published posts"
  ON blog_posts
  FOR SELECT
  USING (status = 'published');

-- Admin users can read any post (including drafts)
CREATE POLICY "Admins can read all posts"
  ON blog_posts
  FOR SELECT
  USING (EXISTS (SELECT 1 FROM admin_users WHERE admin_users.id = auth.uid()));

-- Admin users can insert posts
CREATE POLICY "Admins can insert posts"
  ON blog_posts
  FOR INSERT
  WITH CHECK (EXISTS (SELECT 1 FROM admin_users WHERE admin_users.id = auth.uid()));

-- Admin users can update posts
CREATE POLICY "Admins can update posts"
  ON blog_posts
  FOR UPDATE
  USING (EXISTS (SELECT 1 FROM admin_users WHERE admin_users.id = auth.uid()));

-- Admin users can delete posts
CREATE POLICY "Admins can delete posts"
  ON blog_posts
  FOR DELETE
  USING (EXISTS (SELECT 1 FROM admin_users WHERE admin_users.id = auth.uid()));

-- 5. RLS POLICIES — admin_users

-- Admins can read their own record (for login verification)
CREATE POLICY "Admins can read own record"
  ON admin_users
  FOR SELECT
  USING (auth.uid() = id);

-- Super admins can manage all admin records (INSERT, UPDATE, DELETE)
CREATE POLICY "Super admins can manage admin users"
  ON admin_users
  FOR ALL
  USING (
    EXISTS (SELECT 1 FROM admin_users WHERE admin_users.id = auth.uid() AND admin_users.role = 'super_admin')
  );

-- 6. HELPER FUNCTION: Create first super admin (run after creating a user in auth.users)
-- Replace the email with your admin email
-- SELECT * FROM auth.users WHERE email = 'admin@example.com';  -- get the id first
-- INSERT INTO admin_users (id, email, role) VALUES ('<user-id>', 'admin@example.com', 'super_admin');
