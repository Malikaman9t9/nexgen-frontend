import requests
from urllib.parse import urlparse

FALLBACK = {
    "status": "Unavailable",
    "global_rank": "N/A",
    "monthly_visits": "N/A",
    "bounce_rate": "N/A",
    "pages_per_visit": "N/A",
    "avg_duration": "N/A",
    "search_traffic": "N/A",
    "direct_traffic": "N/A",
    "social_traffic": "N/A",
    "raw_data": {},
}


def get_traffic_data(url, api_key):
    print(f"[*] Fetching traffic insights for: {url}")

    if not api_key or api_key == "" or api_key == "YOUR_RAPIDAPI_KEY":
        print("[-] Traffic API key not configured or is a placeholder.")
        return {**FALLBACK, "status": "API Key Missing"}

    parsed = urlparse(url)
    domain = (parsed.netloc or parsed.path).replace("www.", "").strip("/")

    try:
        response = requests.get(
            "https://similarweb-insights.p.rapidapi.com/all-insights",
            headers={
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": "similarweb-insights.p.rapidapi.com",
            },
            params={"domain": domain},
            timeout=20,
        )

        if response.status_code == 429:
            print("[-] Traffic API rate limited")
            return {**FALLBACK, "status": "Rate limited"}

        if response.status_code != 200:
            print(f"[-] Traffic API error: {response.status_code}")
            return {**FALLBACK, "status": f"API error {response.status_code}"}

        raw = response.json()

        if "message" in raw and "not found" in raw.get("message", "").lower():
            return {**FALLBACK, "status": "No traffic data"}

        traffic = raw.get("Traffic") or {}
        engagement = traffic.get("Engagement") or {}
        sources = traffic.get("Sources") or {}

        def safe_pct(val):
            try:
                return f"{float(val) * 100:.1f}%" if val is not None else "N/A"
            except (ValueError, TypeError):
                return "N/A"

        def safe_time(sec):
            try:
                s = int(float(sec))
                return f"{s // 60:02d}:{s % 60:02d}"
            except (ValueError, TypeError):
                return "N/A"

        def safe_rank(val):
            try:
                return f"#{int(float(val)):,}" if val is not None else "N/A"
            except (ValueError, TypeError):
                return "N/A"

        def safe_visits(val):
            try:
                v = float(val)
                if v >= 1_000_000:
                    return f"{v / 1_000_000:.1f}M"
                if v >= 1_000:
                    return f"{v / 1_000:.1f}K"
                return str(int(v))
            except (ValueError, TypeError):
                return "N/A"

        def safe_float_str(val):
            try:
                return f"{float(val):.1f}" if val is not None else "N/A"
            except (ValueError, TypeError):
                return "N/A"

        rank = raw.get("GlobalRank", raw.get("Rank"))
        visits = raw.get("EstimatedMonthlyVisits", raw.get("Visits"))

        if rank is None and visits is None and not engagement:
            return {**FALLBACK, "status": "Low traffic data"}

        return {
            "status": "Live Data",
            "global_rank": safe_rank(rank),
            "monthly_visits": safe_visits(visits),
            "bounce_rate": safe_pct(engagement.get("BounceRate")),
            "pages_per_visit": safe_float_str(engagement.get("PagesPerVisit")),
            "avg_duration": safe_time(engagement.get("TimeOnSite")),
            "search_traffic": safe_pct(sources.get("Search")),
            "direct_traffic": safe_pct(sources.get("Direct")),
            "social_traffic": safe_pct(sources.get("Social")),
            "raw_data": raw,
        }

    except requests.exceptions.Timeout:
        print("[-] Traffic API timed out")
        return {**FALLBACK, "status": "Timeout"}
    except requests.exceptions.ConnectionError:
        print("[-] Traffic API connection failed")
        return {**FALLBACK, "status": "Connection failed"}
    except Exception as e:
        print(f"[-] Traffic API exception: {e}")
        return {**FALLBACK, "status": "Error"}
