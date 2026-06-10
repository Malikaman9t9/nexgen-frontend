import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

REQUEST_TIMEOUT = 15


def get_basic_onpage(url):
    print(f"[*] Extracting on-page SEO factors for: {url}")
    try:
        start_time = time.time()
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response_time = round(time.time() - start_time, 2)

        if response.status_code != 200:
            print(f"[-] HTTP {response.status_code} for {url}")
            return None

        html_text = response.text
        html_size_kb = round(len(response.content) / 1024, 2)
        soup = BeautifulSoup(html_text, "html.parser")

        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else "Missing Title"

        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc.get("content", "Missing") if meta_desc else "Missing"

        h1_tags = [h1.text.strip() for h1 in soup.find_all("h1")]
        h2_count = len(soup.find_all("h2"))
        h3_count = len(soup.find_all("h3"))

        images = soup.find_all("img")
        images_missing_alt = [img for img in images if not img.get("alt")]

        domain = urlparse(url).netloc
        links = soup.find_all("a", href=True)
        internal_links = [
            l["href"] for l in links if domain in l["href"] or l["href"].startswith("/")
        ]
        external_links = [
            l["href"]
            for l in links
            if domain not in l["href"] and l["href"].startswith("http")
        ]

        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag.get("href", "Missing") if canonical_tag else "Missing"

        robots_tag = soup.find("meta", attrs={"name": "robots"})
        robots_content = robots_tag.get("content", "").lower() if robots_tag else "index, follow"
        has_noindex = "noindex" in robots_content

        html_tag = soup.find("html")
        lang = html_tag.get("lang", "Missing") if html_tag else "Missing"

        og_title = soup.find("meta", attrs={"property": "og:title"})
        og_content = og_title.get("content", "Missing") if og_title else "Missing"

        text_content = soup.get_text(separator=" ")
        word_count = len(text_content.split())

        schema = soup.find("script", type="application/ld+json")
        schema_status = "Found" if schema else "Missing"

        is_https = url.startswith("https")

        css_files = [
            l["href"] for l in soup.find_all("link", rel="stylesheet") if l.get("href")
        ]
        js_files = [s["src"] for s in soup.find_all("script") if s.get("src")]
        unminified_css = sum(1 for c in css_files if ".min.css" not in c)
        unminified_js = sum(1 for j in js_files if ".min.js" not in j)

        dir_listing_secured = True
        try:
            test_paths = ["/wp-includes/", "/assets/", "/uploads/", "/images/"]
            for path in test_paths:
                test_dir = urljoin(url, path)
                dir_resp = requests.get(test_dir, headers=HEADERS, timeout=5)
                if dir_resp.status_code == 200 and "Index of" in dir_resp.text:
                    dir_listing_secured = False
                    break
        except Exception:
            pass

        return {
            "title": title,
            "title_count": len(title) if title != "Missing Title" else 0,
            "description": description,
            "desc_count": len(description) if description != "Missing" else 0,
            "h1": h1_tags if h1_tags else ["Missing"],
            "h2_count": h2_count,
            "h3_count": h3_count,
            "total_images": len(images),
            "missing_alt": len(images_missing_alt),
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "canonical": canonical,
            "meta_robots": robots_content,
            "has_noindex": has_noindex,
            "lang": lang,
            "og_title": og_content,
            "word_count": word_count,
            "schema": schema_status,
            "is_https": "Yes" if is_https else "No",
            "response_time": response_time,
            "html_size_kb": html_size_kb,
            "unminified_css": unminified_css,
            "unminified_js": unminified_js,
            "dir_listing_secured": "Yes" if dir_listing_secured else "No",
        }

    except requests.exceptions.Timeout:
        print(f"[-] Timeout scraping {url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"[-] Connection error scraping {url}")
        return None
    except Exception as e:
        print(f"[-] Scraping failed: {e}")
        return None
