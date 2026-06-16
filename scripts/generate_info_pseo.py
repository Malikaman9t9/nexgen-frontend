#!/usr/bin/env python3
"""
SEO Info Hub Generator — reads "Keywords for Nex Gen Web Lab.xlsx",
calls Gemini API, generates purely informational HTML pages in frontend 1/learn/.

Usage:
  python scripts/generate_info_pseo.py --api-key YOUR_KEY
  python scripts/generate_info_pseo.py --no-gemini   (fallback content)

Requires: pandas, openpyxl, google-genai
  pip install pandas openpyxl google-genai
"""

import argparse
import os
import sys
import pandas as pd

TEMPLATE_PATH = os.path.join("frontend 1", "info-template.html")
EXCEL_PATH = "Keywords for Nex Gen Web Lab.xlsx"
OUTPUT_DIR = os.path.join("frontend 1", "learn")
GEMINI_MODEL = "gemini-2.0-flash"
SKIP_FIRST_N = 3  # first 3 keywords are used in a blog post


def slugify(text):
    return text.lower().strip().replace(" ", "-").replace("'", "").replace("&", "and").replace("?", "").replace("/", "-")


def read_keywords(path):
    df = pd.read_excel(path)
    return df["Keywords"].dropna().astype(str).tolist()


def load_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(keyword):
    return f"""You are an expert technical writer creating an informational SEO guide. Write a purely educational article about "{keyword}".

Structure the content with these sections (use <h2> and <h3> tags):
1. What is {keyword}? — A clear, concise definition.
2. Why is {keyword} Important? — Explain its significance in SEO and web development.
3. Key Components / Factors — Break down the main elements.
4. Best Practices — Actionable, practical advice.
5. Common Mistakes to Avoid — Pitfalls readers should watch out for.

CRITICAL RULES:
- Output ONLY valid HTML. No markdown, no backticks, no extra commentary.
- Use <h2> for main sections, <h3> for subsections, <p> for paragraphs.
- Each section should be 2-4 paragraphs.
- Use <ul>/<li> for lists where appropriate.
- Total length: approximately 400 words.
- Do NOT include any sales pitches, promotional content, or calls to action.
- Do NOT mention any third-party tools, competitors, or external websites.
- Keep it purely informational and educational."""


def call_gemini(prompt, api_key):
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return resp.text.strip()
    except Exception as e:
        print(f"  [WARN] Gemini call failed: {e}", file=sys.stderr)
        return None


def fallback_content(keyword):
    return f"""<h2>What is {keyword}?</h2>
<p>{keyword} refers to the systematic process of evaluating and optimizing websites to improve their visibility in search engine results. It encompasses a wide range of technical and creative elements that work together to help search engines better understand, crawl, and rank web content. Understanding {keyword} is fundamental for anyone looking to establish a strong online presence.</p>

<h2>Why is {keyword} Important?</h2>
<p>In today's competitive digital landscape, {keyword} plays a crucial role in determining how well a website performs in organic search results. Search engines continuously refine their algorithms to prioritize high-quality, relevant content that provides genuine value to users. Without a solid understanding of {keyword}, websites risk being overlooked by their target audience.</p>
<p>The importance of {keyword} extends beyond just rankings. It directly impacts user experience, site performance, and ultimately, business outcomes. Websites that prioritize these principles tend to have lower bounce rates, higher engagement, and better conversion metrics.</p>

<h2>Key Components</h2>
<p>Several core components make up an effective {keyword} strategy. These include technical infrastructure, content quality, user experience signals, and off-page factors. Each component requires careful attention and ongoing optimization to maintain and improve search visibility.</p>
<ul>
<li><strong>Technical Foundation:</strong> Ensuring proper crawlability, indexation, and site architecture.</li>
<li><strong>Content Quality:</strong> Creating valuable, original content that addresses user intent.</li>
<li><strong>User Experience:</strong> Optimizing page speed, mobile responsiveness, and navigation.</li>
<li><strong>Authority Signals:</strong> Building trust through ethical practices and quality signals.</li>
</ul>

<h2>Best Practices</h2>
<p>Implementing {keyword} effectively requires a methodical approach. Start with a thorough audit of your current situation, identify areas for improvement, and prioritize changes based on potential impact. Regular monitoring and adjustment are essential as search engine algorithms and user behaviors evolve over time.</p>
<p>Focus on creating comprehensive, well-structured content that genuinely helps your audience. Ensure your technical foundation is solid, with clean code, fast loading times, and proper metadata. Build relationships and earn quality references naturally through exceptional work and valuable resources.</p>

<h2>Common Mistakes to Avoid</h2>
<p>One of the most frequent errors is focusing on quick fixes rather than sustainable long-term strategies. Shortcuts and manipulative tactics may provide temporary gains but often lead to penalties and reputational damage. Another common mistake is neglecting the user experience in favor of search engine signals.</p>
<p>Additionally, failing to keep pace with industry changes can leave your strategies outdated. The digital landscape evolves continuously, and what worked yesterday may not be effective tomorrow. Regular education, testing, and adaptation are essential components of any successful approach to {keyword}.</p>"""


def generate_page(keyword, template, gemini_html):
    slug = slugify(keyword)
    canonical = f"https://nexgenweblab.com/learn/{slug}"

    replacements = {
        "{{keyword_title}}": keyword,
        "{{meta_title}}": f"{keyword} — Complete Guide | NexGenWebLab",
        "{{meta_description}}": f"Learn everything about {keyword}. A comprehensive, informational guide covering what it is, why it matters, best practices, and common mistakes.",
        "{{canonical_url}}": canonical,
        "{{gemini_informational_content}}": gemini_html,
    }

    result = template
    for key, val in replacements.items():
        result = result.replace(key, val)
    return result


def ensure_output_dir(path):
    os.makedirs(path, exist_ok=True)


def write_output(path, html):
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ {path}")


def update_sitemap(keyword, slug):
    sitemap_path = os.path.join("frontend 1", "sitemap.xml")
    url = f"https://nexgenweblab.com/learn/{slug}"
    if not os.path.exists(sitemap_path):
        return
    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()
    if url in content:
        return
    entry = f"""  <url>
    <loc>{url}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
"""
    content = content.replace("</urlset>", entry + "</urlset>")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ sitemap.xml updated: {url}")


def main():
    parser = argparse.ArgumentParser(description="SEO Info Hub generator")
    parser.add_argument("--api-key", help="Gemini API key (default: GEMINI_API_KEY env)")
    parser.add_argument("--no-gemini", action="store_true", help="Use fallback content, skip Gemini")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    use_gemini = bool(api_key) and not args.no_gemini

    # 1. Read Excel
    keywords = read_keywords(EXCEL_PATH)
    keywords = keywords[SKIP_FIRST_N:]  # skip first 3
    print(f"Loaded {len(keywords)} keywords (skipped first {SKIP_FIRST_N})")

    # 2. Load template
    template = load_template(TEMPLATE_PATH)
    print(f"Loaded template ({len(template)} chars)")

    # 3. Ensure output dir
    ensure_output_dir(OUTPUT_DIR)

    # 4. Generate pages
    for keyword in keywords:
        slug = slugify(keyword)
        print(f"\nGenerating: {keyword} → learn/{slug}.html")

        html_content = fallback_content(keyword)
        if use_gemini:
            prompt = build_prompt(keyword)
            print("  Calling Gemini API...")
            result = call_gemini(prompt, api_key)
            if result:
                html_content = result

        page = generate_page(keyword, template, html_content)
        out_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
        write_output(out_path, page)
        update_sitemap(keyword, slug)

    print(f"\nDone. Generated {len(keywords)} pages in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
