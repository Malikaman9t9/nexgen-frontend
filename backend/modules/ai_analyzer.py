import google.generativeai as genai
import json
import re

FALLBACK_RECOMMENDATIONS = [
    {"title": "Improve Loading Speed", "text": "Optimize your Core Web Vitals by deferring unused Javascript and compressing images to modern WebP format.", "icon": "zap"},
    {"title": "Enhance Content Depth", "text": "Ensure your primary pages have sufficient word count and semantic H1/H2 structures for better entity recognition.", "icon": "file-text"},
    {"title": "Optimize Meta Tags", "text": "Write compelling Title tags (30-60 chars) and Meta Descriptions to improve organic search click-through rates.", "icon": "heading"},
    {"title": "Image Accessibility", "text": "Add descriptive ALT attributes to all images to assist search engine crawlers and visually impaired users.", "icon": "image"}
]

def get_ai_suggestions(seo_data, api_key):
    print("[*] Generating AI Strategic Recommendations...")
    
    # Validate API key
    if not api_key or api_key == "" or "your_" in api_key.lower() or api_key == "YOUR_GEMINI_API_KEY":
        print("[-] No valid API key provided, using fallback data.")
        return {"status": "no_api_key", "recommendations": FALLBACK_RECOMMENDATIONS}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        Act as an SEO Expert. Review this website data and provide 4 strict actionable tips.
        Format strictly as a JSON array. Do not add any backticks or markdown outside the array.
        [
          {{"title": "String", "text": "String", "icon": "fa-solid fa-check"}}
        ]
        Data: {seo_data}
        """

        response = model.generate_content(prompt)
        text = response.text

        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            # Ensure we return proper structure
            if isinstance(parsed, list):
                return {"status": "success", "recommendations": parsed}
            else:
                return {"status": "error", "recommendations": FALLBACK_RECOMMENDATIONS}
        return {"status": "error", "recommendations": FALLBACK_RECOMMENDATIONS}

    except Exception as e:
        print(f"[-] AI Generation Failed: {e}")
        return {"status": "error", "recommendations": FALLBACK_RECOMMENDATIONS}

FALLBACK_PARAGRAPHS = {
    "executive_summary": "This SEO audit evaluates the website's technical foundation, on-page optimization, and performance metrics. The analysis reveals opportunities to improve search visibility through targeted enhancements in site structure, content quality, and user experience. Key findings highlight areas where strategic improvements can drive measurable organic growth.",
    "onpage_analysis": "The on-page SEO assessment examines critical elements such as title tags, meta descriptions, heading structure, content depth, and technical markup. Proper optimization of these factors helps search engines understand and rank the page effectively for relevant queries.",
    "speed_analysis": "Page speed and Core Web Vitals are essential ranking factors that directly impact user experience. The analysis evaluates loading performance across mobile and desktop devices, identifying opportunities to reduce latency and improve interactivity metrics.",
    "traffic_analysis": "Traffic data provides insight into the site's current visibility and audience engagement patterns. Understanding traffic sources, user behavior metrics, and geographic distribution helps inform a data-driven SEO strategy."
}

def get_ai_paragraphs(seo_data, api_key):
    print("[*] Generating AI Analysis Paragraphs...")

    if not api_key or api_key == "" or "your_" in api_key.lower() or api_key == "YOUR_GEMINI_API_KEY":
        print("[-] No valid API key provided, using fallback paragraphs.")
        return {"status": "no_api_key", "paragraphs": FALLBACK_PARAGRAPHS}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        Act as an SEO Expert and technical writer. Review this website audit data and write professional, detailed paragraphs.
        Return ONLY a valid JSON object with these 4 keys — no markdown, no backticks:
        {{
          "executive_summary": "Two strong paragraphs summarizing the overall SEO health, key strengths, and critical areas for improvement.",
          "onpage_analysis": "One paragraph analyzing the on-page SEO factors from the data provided.",
          "speed_analysis": "One paragraph interpreting the Core Web Vitals and page speed scores.",
          "traffic_analysis": "One paragraph explaining the traffic metrics and what they indicate about search visibility."
        }}
        Write in a clear, authoritative tone suitable for a professional SEO report. Each paragraph should be 3-5 sentences.
        Data: {seo_data}
        """

        response = model.generate_content(prompt)
        text = response.text

        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            required = ["executive_summary", "onpage_analysis", "speed_analysis", "traffic_analysis"]
            if all(k in parsed for k in required):
                return {"status": "success", "paragraphs": parsed}
        return {"status": "error", "paragraphs": FALLBACK_PARAGRAPHS}

    except Exception as e:
        print(f"[-] AI Paragraphs Generation Failed: {e}")
        return {"status": "error", "paragraphs": FALLBACK_PARAGRAPHS}
