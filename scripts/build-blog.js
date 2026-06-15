const fs = require('fs');
const path = require('path');

const blogDir = path.resolve(__dirname, '..', '_data', 'blog');
const outDir = path.resolve(__dirname, '..', 'frontend 1', 'blog');

// Read index to get all posts
const index = JSON.parse(fs.readFileSync(path.join(blogDir, '_index.json'), 'utf8'));

// Template for blog post pages
function buildPostHtml(post) {
  const tags = (post.tags || []).map(t =>
    `<span class="tag-pill inline-block bg-primary/5 text-primary text-xs font-bold px-3 py-1.5 rounded-full">${t}</span>`
  ).join('');

  const imgHtml = post.featured_image || post.cover_image_url
    ? `<div id="post-cover" class="mb-10 rounded-[2rem] overflow-hidden shadow-lg"><img src="${post.featured_image || post.cover_image_url}" alt="${post.title}" class="w-full h-auto max-h-[500px] object-cover"></div>`
    : '';

  const date = new Date(post.published_at || post.created_at)
    .toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  return `<!DOCTYPE html>
<html lang="en-US" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${post.title} — NexGenWebLab</title>
  <meta name="description" content="${(post.excerpt || '').replace(/"/g, '&quot;')}">
  <link rel="canonical" href="https://nexgenweblab.com/blog/${post.slug}">
  <link rel="icon" type="image/png" href="/assets/images/favicon.png?v=2">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = { theme: { extend: { fontFamily: { sans: ['Inter', 'sans-serif'] }, colors: { primary: '#6D28D9', secondary: '#DB2777' } } } }
  </script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "${post.title}",
    "description": "${(post.excerpt || '').replace(/"/g, '&quot;')}",
    "url": "https://nexgenweblab.com/blog/${post.slug}",
    "datePublished": "${post.published_at || post.created_at}",
    "dateModified": "${post.updated_at || post.created_at}",
    "author": { "@type": "Person", "name": "${post.author_name || 'NexGenWebLab Team'}" },
    "publisher": { "@type": "Organization", "name": "NexGenWebLab", "url": "https://nexgenweblab.com" }${post.featured_image || post.cover_image_url ? `,\n    "image": "${post.featured_image || post.cover_image_url}"` : ''}${(post.tags || []).length ? `,\n    "keywords": "${(post.tags || []).join(', ')}"` : ''}
  }
  </script>
  <style>
    .hero-gradient { background: radial-gradient(circle at top right, rgba(109, 40, 217, 0.08), transparent), radial-gradient(circle at bottom left, rgba(219, 39, 119, 0.05), transparent); }
    .blog-content h1, .blog-content h2, .blog-content h3, .blog-content h4 { font-weight: 800; line-height: 1.2; margin-top: 1.5em; margin-bottom: 0.6em; color: #0f172a; }
    .blog-content h1 { font-size: 2rem; }
    .blog-content h2 { font-size: 1.6rem; }
    .blog-content h3 { font-size: 1.3rem; }
    .blog-content p { margin-bottom: 1.2em; line-height: 1.8; color: #334155; font-size: 1.05rem; }
    .blog-content ul, .blog-content ol { margin-bottom: 1.2em; padding-left: 1.6em; }
    .blog-content li { margin-bottom: 0.3em; color: #334155; font-size: 1.05rem; line-height: 1.7; }
    .blog-content blockquote { border-left: 4px solid #6D28D9; padding: 0.8em 1.2em; margin: 1.5em 0; background: #f8fafc; border-radius: 0 12px 12px 0; color: #475569; font-style: italic; }
    .blog-content a { color: #6D28D9; font-weight: 600; text-decoration: underline; }
    .blog-content a:hover { color: #5B21B6; }
    .blog-content img { max-width: 100%; border-radius: 16px; margin: 1.5em 0; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
    .blog-content pre { background: #1e293b; color: #e2e8f0; padding: 1.2em; border-radius: 12px; overflow-x: auto; margin: 1.2em 0; font-size: 0.95rem; }
    .blog-content code { background: #f1f5f9; padding: 2px 8px; border-radius: 6px; font-size: 0.9em; color: #6D28D9; }
    .blog-content hr { margin: 2em 0; border-color: #e2e8f0; }
  </style>
</head>
<body class="bg-white text-slate-900 antialiased selection:bg-primary selection:text-white flex flex-col min-h-screen hero-gradient">
  <div id="root"></div>
  <script src="/assets/js/site.js"></script>
  <main class="flex-grow pt-16 md:pt-28">
    <article class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 md:pb-20">
      <div data-aos="fade-up">
        <a href="/blog" class="inline-flex items-center gap-2 text-sm font-bold text-primary hover:text-secondary transition-colors mb-8">
          <i class="fa-solid fa-arrow-left"></i> Back to Blog
        </a>
      </div>

      ${imgHtml}

      <header data-aos="fade-up" data-aos-delay="50">
        <div class="flex flex-wrap items-center gap-3 text-sm text-slate-400 font-bold mb-4">
          <span><i class="far fa-calendar mr-1.5"></i>${date}</span>
          <span><i class="far fa-user mr-1.5"></i>${post.author_name || 'NexGenWebLab Team'}</span>
        </div>
        <h1 class="text-3xl md:text-5xl lg:text-6xl font-black text-slate-950 tracking-tighter leading-[1.08] mb-6">${post.title}</h1>
        ${tags ? `<div class="flex flex-wrap gap-2 mb-8">${tags}</div>` : ''}
      </header>

      <div class="blog-content max-w-none" data-aos="fade-up" data-aos-delay="100">${post.content || ''}</div>

      <div class="mt-16 pt-8 border-t border-slate-200" data-aos="fade-up">
        <a href="/blog" class="inline-flex items-center gap-2 text-sm font-bold text-primary hover:text-secondary transition-colors">
          <i class="fa-solid fa-arrow-left"></i> Back to Blog
        </a>
      </div>
    </article>
  </main>
  <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
  <script>AOS.init({ duration: 800, easing: 'ease-out-cubic', once: true, offset: 80 });</script>
</body>
</html>`;
}

// Build static files for published posts
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

let built = 0;
for (const entry of index) {
  if (entry.status !== 'published') continue;
  const filePath = path.join(blogDir, `${entry.slug}.json`);
  if (!fs.existsSync(filePath)) continue;
  const post = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const html = buildPostHtml(post);
  const outFile = path.join(outDir, `${entry.slug}.html`);
  fs.writeFileSync(outFile, html);
  built++;
}

console.log(`Built ${built} static blog pages to frontend 1/blog/`);

// Update sitemap with blog post URLs
var sitemapPath = path.resolve(__dirname, '..', 'frontend 1', 'sitemap.xml');
var sitemap = fs.readFileSync(sitemapPath, 'utf8');

// Remove any existing blog post entries
sitemap = sitemap.replace(/\n\s*<url>\s*<loc>https:\/\/nexgenweblab\.com\/blog\/[^<]+<\/loc>.*?<\/url>/gs, '');

// Insert new blog post entries before </urlset>
var blogUrls = '';
for (const entry of index) {
  if (entry.status !== 'published') continue;
  var date = (entry.published_at || entry.created_at || '').split('T')[0];
  blogUrls += `  <url>
    <loc>https://nexgenweblab.com/blog/${entry.slug}</loc>
    <lastmod>${date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
`;
}
sitemap = sitemap.replace('</urlset>', blogUrls + '</urlset>');
fs.writeFileSync(sitemapPath, sitemap);
console.log(`Updated sitemap.xml with ${built} blog URLs`);
