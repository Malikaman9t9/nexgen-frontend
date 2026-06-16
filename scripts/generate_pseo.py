#!/usr/bin/env python3
"""
pSEO Generator — reads scripts/pseo-data.csv, calls Gemini API for each modifier,
replaces placeholders in frontend 1/pseo-template.html, and writes
static HTML files to frontend 1/solutions/{modifier}.html.

Usage:
  python scripts/generate_pseo.py

Requires:
  pip install google-genai
  Set GEMINI_API_KEY env var or pass via --api-key
"""

import argparse
import csv
import os
import re
import sys

# ── config ──────────────────────────────────────────────────────────
TEMPLATE_PATH = os.path.join("frontend 1", "pseo-template.html")
CSV_PATH = os.path.join("scripts", "pseo-data.csv")
OUTPUT_DIR = os.path.join("frontend 1", "solutions")

GEMINI_MODEL = "gemini-2.0-flash"

# ── helpers ─────────────────────────────────────────────────────────

def slugify(text):
    return text.lower().strip().replace(" ", "-").replace("'", "").replace("&", "and")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [row["Modifier"].strip() for row in csv.DictReader(f)]


def load_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(modifier):
    return f"""You are an expert SEO content writer. Generate exactly 3 SEO-optimized HTML paragraphs for a "White Label SEO Report Generator" landing page targeting **{modifier}**.

Rules:
- Each paragraph must be wrapped in <p> tags.
- Wrap the whole block in a <section class="py-20 lg:py-32 bg-white"> with inner container divs matching the site's Tailwind pattern (max-w-7xl mx-auto px-4 sm:px-6 lg:px-8).
- Include a centered <h2> heading before the paragraphs.
- Naturally include LSI keywords like: technical seo audit, white label seo report, seo report generator, core web vitals test, website seo checker, bulk seo checker.
- Tone: professional, persuasive, benefit-driven.
- Total length: roughly 250-350 words.

Output ONLY valid HTML — no markdown, no backticks, no extra commentary."""


def call_gemini(prompt, api_key):
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return resp.text.strip()
    except Exception as e:
        print(f"  [WARN] Gemini call failed: {e}", file=sys.stderr)
        return fallback_content()


def fallback_content(modifier=None):
    # If Gemini is unavailable, use a static fallback
    m = modifier or "this audience"
    return f"""<section class="py-20 lg:py-32 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16 lg:mb-20" data-aos="fade-up">
        <h2 class="text-3xl md:text-4xl lg:text-5xl font-black tracking-tight text-slate-950 mb-6">White Label SEO Reports for {m}</h2>
      </div>
      <div class="max-w-4xl mx-auto space-y-6 text-lg text-slate-600 font-medium leading-relaxed" data-aos="fade-up">
        <p>Running a successful {m} business means you need tools that adapt to your unique workflow. Our <b>white label seo report</b> generator is purpose-built to help agencies and professionals deliver stunning, data-driven reports to their clients without spending hours on manual formatting.</p>
        <p>Every <b>technical seo audit</b> powered by NexGenWebLab goes beyond surface-level checks. We execute a full <b>core web vitals test</b>, analyze on-page structures, and benchmark your site against industry competitors — all in under 30 seconds. The result is a comprehensive, actionable analysis that builds trust and drives results.</p>
        <p>Whether you need a quick <b>website seo checker</b> for a prospect pitch or a <b>bulk seo checker</b> to process hundreds of client URLs simultaneously, our platform scales to meet your needs. Generate branded reports, export to DOCX, and impress your clients with professional-grade insights — all under your own agency brand.</p>
      </div>
    </div>
  </section>"""


def generate_page(modifier, template, gemini_html):
    slug = slugify(modifier)
    canonical = f"https://nexgenweblab.com/solutions/{slug}"

    replacements = {
        "{{audience_modifier}}": modifier,
        "{{meta_title}}": f"White Label SEO Report for {modifier} | Free Technical SEO Audit Tool",
        "{{meta_description}}": f"Generate professional white label SEO reports for {modifier}. Our technical SEO audit tool analyzes 117+ checkpoints and provides AI-driven growth strategies tailored to {modifier}.",
        "{{canonical_url}}": canonical,
        "{{schema_name}}": modifier,
        "{{hero_heading}}": f"The Most Powerful SEO Audit Tool for {modifier}",
        "{{hero_subtext}}": f"Execute deep technical SEO audits, track Core Web Vitals, and generate stunning white label reports in under 30 seconds — built specifically for {modifier}.",
        "{{unique_gemini_content}}": gemini_html,
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


def update_sitemap(modifier, slug):
    """Append a new <url> entry to sitemap.xml if not already present."""
    sitemap_path = os.path.join("frontend 1", "sitemap.xml")
    url = f"https://nexgenweblab.com/solutions/{slug}"
    if not os.path.exists(sitemap_path):
        return
    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()
    if url in content:
        return  # already present
    # Insert before </urlset>
    entry = f"""  <url>
    <loc>{url}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
"""
    content = content.replace("</urlset>", entry + "</urlset>")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ sitemap.xml updated: {url}")


# ── main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="pSEO page generator")
    parser.add_argument("--api-key", help="Gemini API key (default: GEMINI_API_KEY env)")
    parser.add_argument("--no-gemini", action="store_true", help="Skip Gemini API, use fallback content")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    use_gemini = bool(api_key) and not args.no_gemini

    if not use_gemini and not args.no_gemini:
        print("[INFO] No GEMINI_API_KEY found. Use --api-key, set env var, or pass --no-gemini for fallback.", file=sys.stderr)
        sys.exit(1)

    # 1. Read CSV
    modifiers = read_csv(CSV_PATH)
    print(f"Loaded {len(modifiers)} modifiers from {CSV_PATH}")

    # 2. Load template
    template = load_template(TEMPLATE_PATH)
    print(f"Loaded template ({len(template)} chars)")

    # 3. Ensure output dir
    ensure_output_dir(OUTPUT_DIR)

    # 4. Generate pages
    for modifier in modifiers:
        slug = slugify(modifier)
        print(f"\nGenerating: {modifier} → solutions/{slug}.html")

        gemini_html = fallback_content(modifier)
        if use_gemini:
            prompt = build_prompt(modifier)
            print(f"  Calling Gemini API...")
            gemini_html = call_gemini(prompt, api_key)

        html = generate_page(modifier, template, gemini_html)
        out_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
        write_output(out_path, html)
        update_sitemap(modifier, slug)

    print(f"\nDone. Generated {len(modifiers)} pages in {OUTPUT_DIR}/")
    print("Run `npm run sync` to rebuild blog sitemap if needed, then commit & push.")


if __name__ == "__main__":
    main()
