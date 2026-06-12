const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';
const BASE_URL = 'https://nexgenweblab.com';

const STATIC_PAGES = [
  { loc: '/', priority: '1.0', changefreq: 'weekly' },
  { loc: '/about', priority: '0.8', changefreq: 'monthly' },
  { loc: '/pricing', priority: '0.9', changefreq: 'weekly' },
  { loc: '/contact', priority: '0.7', changefreq: 'monthly' },
  { loc: '/blog', priority: '0.9', changefreq: 'daily' },
  { loc: '/privacy', priority: '0.4', changefreq: 'yearly' },
  { loc: '/terms', priority: '0.4', changefreq: 'yearly' },
  { loc: '/sitemap', priority: '0.5', changefreq: 'monthly' },
];

function urlXml(page) {
  return [
    '  <url>',
    '    <loc>' + BASE_URL + page.loc + '</loc>',
    '    <changefreq>' + page.changefreq + '</changefreq>',
    '    <priority>' + page.priority + '</priority>',
    '  </url>'
  ].join('\n');
}

function buildSitemap(blogPosts) {
  var urls = STATIC_PAGES.map(urlXml);

  for (var i = 0; i < blogPosts.length; i++) {
    var post = blogPosts[i];
    var slug = post.slug ? encodeURIComponent(post.slug) : '';
    if (!slug) continue;
    urls.push('  <url>');
    urls.push('    <loc>' + BASE_URL + '/blog/' + slug + '</loc>');
    urls.push('    <changefreq>monthly</changefreq>');
    urls.push('    <priority>0.7</priority>');
    urls.push('  </url>');
  }

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    urls.join('\n'),
    '</urlset>'
  ].join('\n');
}

module.exports = async function handler(req, res) {
  try {
    var response = await fetch(SUPABASE_URL + '/rest/v1/blog_posts?select=slug,updated_at&status=eq.published&order=created_at.desc', {
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': 'Bearer ' + SUPABASE_ANON_KEY
      }
    });

    var blogPosts = [];
    if (response.ok) {
      blogPosts = await response.json();
    }

    var xml = buildSitemap(blogPosts);
    res.setHeader('Content-Type', 'application/xml');
    res.setHeader('Cache-Control', 'public, max-age=3600, s-maxage=3600');
    res.status(200).send(xml);
  } catch (err) {
    var fallbackXml = buildSitemap([]);
    res.setHeader('Content-Type', 'application/xml');
    res.status(200).send(fallbackXml);
  }
};
