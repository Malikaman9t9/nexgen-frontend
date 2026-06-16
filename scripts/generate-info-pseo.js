/**
 * SEO Info Hub Generator (Node.js)
 * Reads "Keywords for Nex Gen Web Lab.xlsx", generates informational
 * HTML pages in frontend 1/learn/, updates sitemap.xml.
 *
 * Usage: node scripts/generate-info-pseo.js
 */

const fs = require('fs');
const path = require('path');
const XLSX = require('xlsx');

const TEMPLATE_PATH = 'frontend 1/info-template.html';
const EXCEL_PATH = 'Keywords for Nex Gen Web Lab.xlsx';
const OUTPUT_DIR = 'frontend 1/learn';
const SKIP_FIRST_N = 3;

function slugify(text) {
  return text.toLowerCase().trim()
    .replace(/\s+/g, '-')
    .replace(/'/g, '').replace(/&/g, 'and')
    .replace(/[?\/]/g, '')
    .replace(/-+/g, '-');
}

function readKeywords(filePath) {
  const wb = XLSX.readFile(filePath);
  const ws = wb.Sheets[wb.SheetNames[0]];
  const data = XLSX.utils.sheet_to_json(ws);
  return data.map(row => row['Keywords'].toString().trim()).filter(Boolean);
}

function loadTemplate(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

function fallbackContent(keyword) {
  return `<h2>What is ${keyword}?</h2>
<p>${keyword} refers to the systematic process of evaluating and optimizing websites to improve their visibility in search engine results. It encompasses a wide range of technical and creative elements that work together to help search engines better understand, crawl, and rank web content. Understanding ${keyword} is fundamental for anyone looking to establish a strong online presence.</p>

<h2>Why is ${keyword} Important?</h2>
<p>In today's competitive digital landscape, ${keyword} plays a crucial role in determining how well a website performs in organic search results. Search engines continuously refine their algorithms to prioritize high-quality, relevant content that provides genuine value to users. Without a solid understanding of ${keyword}, websites risk being overlooked by their target audience.</p>
<p>The importance of ${keyword} extends beyond just rankings. It directly impacts user experience, site performance, and ultimately, business outcomes. Websites that prioritize these principles tend to have lower bounce rates, higher engagement, and better conversion metrics.</p>

<h2>Key Components</h2>
<p>Several core components make up an effective ${keyword} strategy. These include technical infrastructure, content quality, user experience signals, and off-page factors. Each component requires careful attention and ongoing optimization to maintain and improve search visibility.</p>
<ul>
<li><strong>Technical Foundation:</strong> Ensuring proper crawlability, indexation, and site architecture.</li>
<li><strong>Content Quality:</strong> Creating valuable, original content that addresses user intent.</li>
<li><strong>User Experience:</strong> Optimizing page speed, mobile responsiveness, and navigation.</li>
<li><strong>Authority Signals:</strong> Building trust through ethical practices and quality signals.</li>
</ul>

<h2>Best Practices</h2>
<p>Implementing ${keyword} effectively requires a methodical approach. Start with a thorough audit of your current situation, identify areas for improvement, and prioritize changes based on potential impact. Regular monitoring and adjustment are essential as search engine algorithms and user behaviors evolve over time.</p>
<p>Focus on creating comprehensive, well-structured content that genuinely helps your audience. Ensure your technical foundation is solid, with clean code, fast loading times, and proper metadata. Build relationships and earn quality references naturally through exceptional work and valuable resources.</p>

<h2>Common Mistakes to Avoid</h2>
<p>One of the most frequent errors is focusing on quick fixes rather than sustainable long-term strategies. Shortcuts and manipulative tactics may provide temporary gains but often lead to penalties and reputational damage. Another common mistake is neglecting the user experience in favor of search engine signals.</p>
<p>Additionally, failing to keep pace with industry changes can leave your strategies outdated. The digital landscape evolves continuously, and what worked yesterday may not be effective tomorrow. Regular education, testing, and adaptation are essential components of any successful approach to ${keyword}.</p>`;
}

function generatePage(keyword, template, htmlContent) {
  const slug = slugify(keyword);
  const canonical = `https://nexgenweblab.com/learn/${slug}`;

  let result = template;
  result = result.replace(/{{keyword_title}}/g, keyword);
  result = result.replace(/{{meta_title}}/g, `${keyword} — Complete Guide | NexGenWebLab`);
  result = result.replace(/{{meta_description}}/g, `Learn everything about ${keyword}. A comprehensive, informational guide covering what it is, why it matters, best practices, and common mistakes.`);
  result = result.replace(/{{canonical_url}}/g, canonical);
  result = result.replace(/{{gemini_informational_content}}/g, htmlContent);

  return result;
}

function updateSitemap(keyword, slug) {
  const sitemapPath = 'frontend 1/sitemap.xml';
  const url = `https://nexgenweblab.com/learn/${slug}`;
  if (!fs.existsSync(sitemapPath)) return;

  let content = fs.readFileSync(sitemapPath, 'utf8');
  if (content.includes(url)) return;

  const entry = `  <url>
    <loc>${url}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
`;
  content = content.replace('</urlset>', entry + '</urlset>');
  fs.writeFileSync(sitemapPath, content);
  console.log(`  ✓ sitemap.xml updated: ${url}`);
}

function main() {
  // 1. Read Excel
  const keywords = readKeywords(EXCEL_PATH);
  const skipped = keywords.slice(SKIP_FIRST_N);
  console.log(`Loaded ${keywords.length} keywords, skipped first ${SKIP_FIRST_N}, generating ${skipped.length} pages`);

  // 2. Load template
  const template = loadTemplate(TEMPLATE_PATH);
  console.log(`Loaded template (${template.length} chars)`);

  // 3. Ensure output dir
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // 4. Generate pages
  for (const keyword of skipped) {
    const slug = slugify(keyword);
    console.log(`\nGenerating: ${keyword} → learn/${slug}.html`);

    const htmlContent = fallbackContent(keyword);
    const page = generatePage(keyword, template, htmlContent);
    const outPath = path.join(OUTPUT_DIR, `${slug}.html`);
    fs.writeFileSync(outPath, page);
    console.log(`  ✓ ${outPath}`);
    updateSitemap(keyword, slug);
  }

  console.log(`\nDone. Generated ${skipped.length} pages in ${OUTPUT_DIR}/`);
  console.log('To use Gemini AI:\n  python scripts/generate_info_pseo.py --api-key YOUR_KEY');
}

main();
