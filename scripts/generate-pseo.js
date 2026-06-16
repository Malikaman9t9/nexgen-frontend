/**
 * pSEO Generator (Node.js)
 * Reads scripts/pseo-data.csv, loads pseo-template.html,
 * generates rich content for each modifier, writes to frontend 1/solutions/.
 *
 * Usage:
 *   node scripts/generate-pseo.js
 *
 * For Gemini-powered generation, use the Python version:
 *   python scripts/generate_pseo.py --api-key YOUR_KEY
 */

const fs = require('fs');
const path = require('path');

const TEMPLATE_PATH = 'frontend 1/pseo-template.html';
const CSV_PATH = 'scripts/pseo-data.csv';
const OUTPUT_DIR = 'frontend 1/solutions';

function slugify(text) {
  return text.toLowerCase().trim().replace(/\s+/g, '-').replace(/'/g, '').replace(/&/g, 'and');
}

function readCSV(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8').trim();
  const lines = raw.split('\n');
  const headers = lines[0].split(',').map(h => h.trim());
  const modifierIdx = headers.indexOf('Modifier');
  const modifiers = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const vals = line.split(',').map(v => v.trim());
    modifiers.push(vals[modifierIdx]);
  }
  return modifiers;
}

// Rich, unique fallback content for each modifier (better than generic paragraphs)
const CONTENT_CACHE = {};

function buildUniqueContent(modifier) {
  if (CONTENT_CACHE[modifier]) return CONTENT_CACHE[modifier];

  const paragraphs = [
    `Running a successful ${modifier} operation demands tools that adapt to your specific ecosystem. Our <b>white label seo report</b> generator is engineered from the ground up to help ${modifier} professionals deliver stunning, data-driven reports without drowning in manual formatting. Every <b>technical seo audit</b> goes beyond surface-level checks to uncover the metrics that actually matter for ${modifier} environments.`,
    `Unlike generic SEO tools, our <b>seo report generator</b> executes a comprehensive <b>core web vitals test</b> tailored to ${modifier} infrastructure. We analyze page speed performance, mobile responsiveness, and server configuration — then cross-reference these findings with industry benchmarks specific to ${modifier}. The result is a prioritized action plan that drives measurable improvements in search visibility and user experience.`,
    `Whether you need a quick <b>website seo checker</b> for a single prospect pitch or our powerful <b>bulk seo checker</b> to process hundreds of ${modifier} client URLs simultaneously, NexGenWebLab scales effortlessly. Export fully branded white label reports in seconds, build trust with professional-grade insights, and close more deals — all under your own agency brand without any technical overhead.`
  ];

  const content = `<section class="py-20 lg:py-32 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16 lg:mb-20" data-aos="fade-up">
        <h2 class="text-3xl md:text-4xl lg:text-5xl font-black tracking-tight text-slate-950 mb-6">White Label SEO Reports Tailored for ${modifier}</h2>
        <p class="text-lg md:text-xl text-slate-500 max-w-3xl mx-auto font-bold leading-relaxed">Industry-specific technical audits, AI-driven insights, and branded reports purpose-built for ${modifier}.</p>
      </div>
      <div class="max-w-4xl mx-auto space-y-6 text-lg text-slate-600 font-medium leading-relaxed" data-aos="fade-up">
        ${paragraphs.map(p => `<p>${p}</p>`).join('\n        ')}
      </div>
    </div>
  </section>`;

  CONTENT_CACHE[modifier] = content;
  return content;
}

function generatePage(modifier, template, geminiHtml) {
  const slug = slugify(modifier);
  const canonical = `https://nexgenweblab.com/solutions/${slug}`;

  let result = template;
  result = result.replace(/{{audience_modifier}}/g, modifier);
  result = result.replace(/{{meta_title}}/g, `White Label SEO Report for ${modifier} | Free Technical SEO Audit Tool`);
  result = result.replace(/{{meta_description}}/g, `Generate professional white label SEO reports for ${modifier}. Our technical SEO audit tool analyzes 117+ checkpoints and provides AI-driven growth strategies tailored to ${modifier}.`);
  result = result.replace(/{{canonical_url}}/g, canonical);
  result = result.replace(/{{schema_name}}/g, modifier);
  result = result.replace(/{{hero_heading}}/g, `The Most Powerful SEO Audit Tool for ${modifier}`);
  result = result.replace(/{{hero_subtext}}/g, `Execute deep technical SEO audits, track Core Web Vitals, and generate stunning white label reports in under 30 seconds — built specifically for ${modifier}.`);
  result = result.replace(/{{unique_gemini_content}}/g, geminiHtml);

  return result;
}

function updateSitemap(modifier, slug) {
  const sitemapPath = 'frontend 1/sitemap.xml';
  const url = `https://nexgenweblab.com/solutions/${slug}`;
  if (!fs.existsSync(sitemapPath)) return;

  let content = fs.readFileSync(sitemapPath, 'utf8');
  if (content.includes(url)) return;

  const entry = `  <url>
    <loc>${url}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
`;
  content = content.replace('</urlset>', entry + '</urlset>');
  fs.writeFileSync(sitemapPath, content);
  console.log(`  ✓ sitemap.xml updated: ${url}`);
}

function main() {
  // 1. Read CSV
  const modifiers = readCSV(CSV_PATH);
  console.log(`Loaded ${modifiers.length} modifiers from ${CSV_PATH}`);

  // 2. Load template
  const template = fs.readFileSync(TEMPLATE_PATH, 'utf8');
  console.log(`Loaded template (${template.length} chars)`);

  // 3. Ensure output dir
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // 4. Generate pages
  for (const modifier of modifiers) {
    const slug = slugify(modifier);
    console.log(`\nGenerating: ${modifier} → solutions/${slug}.html`);

    const html = buildUniqueContent(modifier);
    const page = generatePage(modifier, template, html);
    fs.writeFileSync(path.join(OUTPUT_DIR, `${slug}.html`), page);
    console.log(`  ✓ ${OUTPUT_DIR}/${slug}.html`);
    updateSitemap(modifier, slug);
  }

  console.log(`\nDone. Generated ${modifiers.length} pages in ${OUTPUT_DIR}/`);
  console.log('Commit and push to deploy. To use Gemini AI, run:\n  python scripts/generate_pseo.py --api-key YOUR_KEY');
}

main();
