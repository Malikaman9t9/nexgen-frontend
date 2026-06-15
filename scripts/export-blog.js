const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function exportPosts() {
  const { data: posts, error } = await supabase
    .from('blog_posts')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Export failed:', error.message);
    process.exit(1);
  }

  const dir = path.resolve(__dirname, '..', '_data', 'blog');

  // Write individual JSON files
  for (const post of posts) {
    const slug = post.slug || post.id;
    const filePath = path.join(dir, `${slug}.json`);
    fs.writeFileSync(filePath, JSON.stringify(post, null, 2));
    console.log(`Exported: ${slug}.json`);
  }

  // Write index for quick reference
  const index = posts.map(p => ({
    id: p.id,
    slug: p.slug,
    title: p.title,
    status: p.status,
    created_at: p.created_at,
    author_name: p.author_name
  }));
  fs.writeFileSync(path.join(dir, '_index.json'), JSON.stringify(index, null, 2));

  console.log(`\nExported ${posts.length} posts to _data/blog/`);
}

exportPosts().catch(console.error);
