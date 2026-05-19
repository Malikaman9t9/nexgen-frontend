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
    "referral_traffic": "N/A",
    "email_traffic": "N/A",
    "monthly_visits_list": [],
    "top_countries": [],
    "top_referrals": [],
    "top_keywords": [],
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
            timeout=30,
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
        
        monthly_data = traffic.get("Visits") or {}
        monthly_visits_list = []
        if isinstance(monthly_data, dict) and len(monthly_data) > 0:
            months_map = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
            for date_str, visits in monthly_data.items():
                try:
                    month_part = date_str[5:7] if len(date_str) >= 7 else "01"
                    month_label = months_map.get(month_part, month_part)
                    monthly_visits_list.append({
                        "month": month_label,
                        "visits": int(visits) if visits else 0
                    })
                except Exception as e:
                    print(f"Error parsing date {date_str}: {e}")
            if len(monthly_visits_list) > 1:
                monthly_visits_list = sorted(monthly_visits_list, key=lambda x: x.get("month", ""))[-6:]
            elif monthly_visits_list:
                monthly_visits_list = monthly_visits_list[:1]

        top_countries = []
        country_shares = raw.get("Traffic", {}).get("TopCountryShares") or {}
        if isinstance(country_shares, dict):
            country_names = {"US": "United States", "GB": "United Kingdom", "DE": "Germany", "FR": "France", "IN": "India", "JP": "Japan", "CN": "China", "BR": "Brazil", "CA": "Canada", "AU": "Australia", "ES": "Spain", "IT": "Italy", "MX": "Mexico", "NL": "Netherlands", "RU": "Russia", "KR": "South Korea", "SE": "Sweden"}
            for code, share in list(country_shares.items())[:5]:
                top_countries.append({
                    "country": country_names.get(code, code),
                    "visits": int(share * 1000000) if share else 0,
                    "share": f"{share * 100:.1f}%" if share else "0%"
                })

        top_keywords = []
        seo_insights = raw.get("SEOInsights") or {}
        seo_kws = seo_insights.get("TopKeywords") if isinstance(seo_insights, dict) else seo_insights
        if isinstance(seo_kws, list):
            rank = 1
            for kw in seo_kws[:10]:
                if isinstance(kw, dict):
                    try:
                        kw_name = kw.get("Name", "Unknown")
                        kw_volume = kw.get("Volume", 0)
                        if isinstance(kw_volume, (int, float)):
                            top_keywords.append({
                                "keyword": kw_name,
                                "visits": int(kw_volume),
                                "position": rank
                            })
                            rank += 1
                    except:
                        pass

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

        rank_data = raw.get("Rank") or {}
        rank = rank_data.get("GlobalRank")
        visits_data = traffic.get("Visits", {})
        if isinstance(visits_data, dict) and visits_data:
            try:
                total_visits = sum(int(v) for v in visits_data.values() if v)
                avg_visits = total_visits // len(visits_data) if visits_data else 0
            except:
                avg_visits = None
        else:
            avg_visits = None

        if rank is None and avg_visits is None and not engagement and not monthly_visits_list:
            return {**FALLBACK, "status": "Low traffic data"}

        return {
            "status": "Live Data",
            "global_rank": safe_rank(rank) if rank else "N/A",
            "monthly_visits": safe_visits(avg_visits) if avg_visits else "N/A",
            "bounce_rate": safe_pct(engagement.get("BounceRate")),
            "pages_per_visit": safe_float_str(engagement.get("PagesPerVisit")),
            "avg_duration": safe_time(engagement.get("TimeOnSite")),
            "search_traffic": safe_pct(sources.get("Search")),
            "direct_traffic": safe_pct(sources.get("Direct")),
            "social_traffic": safe_pct(sources.get("Social")),
            "referral_traffic": safe_pct(sources.get("Referrals")),
            "email_traffic": safe_pct(sources.get("Mail")),
            "monthly_visits_list": monthly_visits_list,
            "top_countries": top_countries,
            "top_referrals": [],
            "top_keywords": top_keywords,
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