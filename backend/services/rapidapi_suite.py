import requests
import json
from urllib.parse import quote

RAPIDAPI_HOST_MOZ = "moz-da-pa-low-cost.p.rapidapi.com"
RAPIDAPI_HOST_SEO_ANALYZER = "seo-analyzer3.p.rapidapi.com"
RAPIDAPI_HOST_FAST_AUDIT = "seo-fast-audit.p.rapidapi.com"
RAPIDAPI_HOST_KEYWORD = "google-keyword-insight1.p.rapidapi.com"
RAPIDAPI_HOST_SEMRUSH = "semrush-keyword-magic-tool.p.rapidapi.com"


def _headers(api_key, host):
    return {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": host,
        "Content-Type": "application/json",
    }


# ──────────────────────────────────────────────
# a. Moz DA PA API
# ──────────────────────────────────────────────

def get_moz_metrics(api_key, domains):
    if isinstance(domains, str):
        domains = [domains]
    try:
        url = f"https://{RAPIDAPI_HOST_MOZ}/v2/getDaPa"
        payload = {"domains": domains}
        resp = requests.post(url, json=payload, headers=_headers(api_key, RAPIDAPI_HOST_MOZ), timeout=15)
        resp.raise_for_status()
        return {"status": "ok", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


# ──────────────────────────────────────────────
# b. SEO Analyzer API
# ──────────────────────────────────────────────

def get_seo_analyzer(api_key, target_url):
    try:
        url = f"https://{RAPIDAPI_HOST_SEO_ANALYZER}/seo-audit-basic?url={quote(target_url)}"
        resp = requests.get(url, headers=_headers(api_key, RAPIDAPI_HOST_SEO_ANALYZER), timeout=20)
        resp.raise_for_status()
        return {"status": "ok", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


# ──────────────────────────────────────────────
# c. SEO Fast Audit API
# ──────────────────────────────────────────────

def get_web_shield_scan(api_key, target_url):
    try:
        url = f"https://{RAPIDAPI_HOST_FAST_AUDIT}/xss/b?url={quote(target_url)}"
        resp = requests.get(url, headers=_headers(api_key, RAPIDAPI_HOST_FAST_AUDIT), timeout=20)
        resp.raise_for_status()
        return {"status": "ok", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


def get_ssl_cert_verify(api_key, target_url):
    try:
        url = f"https://{RAPIDAPI_HOST_FAST_AUDIT}/ssl/verify?url={quote(target_url)}"
        resp = requests.get(url, headers=_headers(api_key, RAPIDAPI_HOST_FAST_AUDIT), timeout=15)
        resp.raise_for_status()
        return {"status": "ok", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


def get_robots_txt_check(api_key, target_url):
    try:
        url = f"https://{RAPIDAPI_HOST_FAST_AUDIT}/robots/check?url={quote(target_url)}"
        resp = requests.get(url, headers=_headers(api_key, RAPIDAPI_HOST_FAST_AUDIT), timeout=15)
        resp.raise_for_status()
        return {"status": "ok", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


def get_sitemap_detector(api_key, target_url):
    try:
        url = f"https://{RAPIDAPI_HOST_FAST_AUDIT}/sitemap/detect?url={quote(target_url)}"
        resp = requests.get(url, headers=_headers(api_key, RAPIDAPI_HOST_FAST_AUDIT), timeout=15)
        resp.raise_for_status()
        return {"status": "ok", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


# ──────────────────────────────────────────────
# d. Google Keyword Insight API
# ──────────────────────────────────────────────

def get_keyword_research(api_key, keyword, country_code="us", lang_code="en"):
    try:
        url = (
            f"https://{RAPIDAPI_HOST_KEYWORD}/keyword-research"
            f"?keyword={quote(keyword)}&countryCode={country_code}&langCode={lang_code}"
        )
        resp = requests.get(url, headers=_headers(api_key, RAPIDAPI_HOST_KEYWORD), timeout=20)
        resp.raise_for_status()
        return {"status": "ok", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


def get_top_keyword(api_key, keyword, country_code="us", lang_code="en"):
    try:
        url = (
            f"https://{RAPIDAPI_HOST_KEYWORD}/top-keyword"
            f"?keyword={quote(keyword)}&countryCode={country_code}&langCode={lang_code}"
        )
        resp = requests.get(url, headers=_headers(api_key, RAPIDAPI_HOST_KEYWORD), timeout=20)
        resp.raise_for_status()
        return {"status": "ok", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


# ──────────────────────────────────────────────
# e. Semrush Keyword Magic Tool
# ──────────────────────────────────────────────

def get_semrush_global_volume(api_key, keyword, database="us"):
    try:
        url = (
            f"https://{RAPIDAPI_HOST_SEMRUSH}/global-volume"
            f"?keyword={quote(keyword)}&database={database}"
        )
        resp = requests.get(url, headers=_headers(api_key, RAPIDAPI_HOST_SEMRUSH), timeout=20)
        resp.raise_for_status()
        return {"status": "ok", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}
