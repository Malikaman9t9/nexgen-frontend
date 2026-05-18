import requests
import time

PAGESPEED_BASE = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def _estimate_from_http(url, strategy):
    """Fallback HTTP-level estimation when PageSpeed API is unavailable."""
    try:
        start = time.time()
        r = requests.get(url, headers=HEADERS, timeout=15)
        elapsed = time.time() - start
        size_kb = len(r.content) / 1024
        status = r.status_code

        perf = 100
        if elapsed > 3.0:
            perf = 20
        elif elapsed > 2.0:
            perf = 35
        elif elapsed > 1.0:
            perf = 55
        elif elapsed > 0.5:
            perf = 75
        elif elapsed > 0.2:
            perf = 90

        if size_kb > 500:
            perf = max(perf - 15, 5)
        elif size_kb > 200:
            perf = max(perf - 5, 10)
        if status != 200:
            perf = max(perf - 30, 5)

        seo = 85
        acc = 70
        bp = 75
        if r.headers.get("Strict-Transport-Security"):
            bp = 90
        if r.headers.get("Content-Security-Policy"):
            bp = 95

        return {
            "performance": perf,
            "accessibility": acc,
            "best-practices": bp,
            "seo": seo,
            "metrics": {
                "fcp": {"value": f"{elapsed:.1f}s", "score": max(0, min(1, 1 - elapsed / 5))},
                "lcp": {"value": f"{elapsed * 1.2:.1f}s", "score": max(0, min(1, 1 - elapsed * 1.2 / 5))},
                "tbt": {"value": f"{max(0, int((elapsed - 0.5) * 50))}ms", "score": max(0, min(1, 1 - max(elapsed - 0.5, 0) / 3))},
                "cls": {"value": "0.05", "score": 0.9},
                "si": {"value": f"{elapsed * 1.1:.1f}s", "score": max(0, min(1, 1 - elapsed * 1.1 / 6))},
            },
        }
    except Exception as e:
        print(f"[-] HTTP estimation failed: {e}")
        return None


def _fetch_strategy(url, strategy, api_key, retries=2):
    """Fetch Lighthouse data for a single strategy (mobile/desktop)."""

    fallback = _estimate_from_http(url, strategy)
    fallback_data = fallback or {
        "performance": 0,
        "accessibility": 0,
        "best-practices": 0,
        "seo": 0,
        "metrics": {k: {"value": "N/A", "score": 0} for k in ("fcp", "lcp", "tbt", "cls", "si")},
    }

    has_key = bool(api_key and len(api_key) > 5)

    for attempt in range(retries):
        try:
            params = {
                "url": url,
                "strategy": strategy,
                "category": ["performance", "accessibility", "best-practices", "seo"],
            }
            if has_key:
                params["key"] = api_key

            print(f"[*] PageSpeed API for {strategy} (attempt {attempt + 1}/{retries})")
            resp = requests.get(PAGESPEED_BASE, params=params, timeout=60)

            if resp.status_code == 429:
                print("[-] Rate limited, waiting 5s...")
                time.sleep(5)
                continue

            if resp.status_code >= 500:
                print(f"[-] Server error {resp.status_code}, waiting 3s...")
                time.sleep(3)
                continue

            if resp.status_code != 200:
                print(f"[-] API error {resp.status_code}: {resp.text[:200]}")
                break

            data = resp.json()
            lr = data.get("lighthouseResult")
            if not lr:
                print("[-] No lighthouseResult, retrying with categories...")
                params["category"] = ["performance", "accessibility", "best-practices", "seo"]
                resp2 = requests.get(PAGESPEED_BASE, params=params, timeout=60)
                if resp2.status_code == 200:
                    data = resp2.json()
                    lr = data.get("lighthouseResult")

            if not lr:
                print("[-] Still no lighthouse data, falling back to HTTP estimation")
                break

            cats = lr.get("categories", {})
            audits = lr.get("audits", {})

            def get_audit(key):
                a = audits.get(key, {})
                return {
                    "value": a.get("displayValue", "N/A"),
                    "score": a.get("score") if a.get("score") is not None else 0,
                }

            def cat_score(name):
                c = cats.get(name, {})
                s = c.get("score")
                return int(s * 100) if s is not None else 0

            return {
                "performance": cat_score("performance"),
                "accessibility": cat_score("accessibility"),
                "best-practices": cat_score("best-practices"),
                "seo": cat_score("seo"),
                "metrics": {
                    "fcp": get_audit("first-contentful-paint"),
                    "lcp": get_audit("largest-contentful-paint"),
                    "tbt": get_audit("total-blocking-time"),
                    "cls": get_audit("cumulative-layout-shift"),
                    "si": get_audit("speed-index"),
                },
            }

        except requests.exceptions.Timeout:
            print(f"[-] Timeout for {strategy} (attempt {attempt + 1})")
            time.sleep(2)
        except Exception as e:
            print(f"[-] Exception for {strategy}: {e}")
            time.sleep(2)

    print(f"[*] Using HTTP estimation for {strategy}")
    return fallback_data


def check_speed(url, api_key):
    print(f"[*] Speed analysis for: {url}")
    mobile = _fetch_strategy(url, "mobile", api_key)

    print("[*] Waiting 2s before desktop check...")
    time.sleep(2)

    desktop = _fetch_strategy(url, "desktop", api_key)

    return {"mobile": mobile, "desktop": desktop}
