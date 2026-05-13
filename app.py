import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
import time
import pandas as pd
from urllib.parse import urlparse
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from modules.onpage_scraper import get_basic_onpage
from modules.speed_checker import check_speed
from modules.ai_analyzer import get_ai_suggestions
from modules.report_export import generate_word_report
from modules.traffic_checker import get_traffic_data

# ==============================================================================
# 1. INITIALIZATION
# ==============================================================================
load_dotenv()

SPEED_API_KEY = os.getenv("SPEED_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

st.set_page_config(
    page_title="NexGenWebLab | SEO Auditor",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Supabase client (optional — app works without it) ---
supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Verify the connection is live
        supabase.auth.get_session()
    except Exception as e:
        st.warning(
            f"Database unavailable — running in demo mode. "
            f"Log-in and plan features are disabled."
        )
        supabase = None
else:
    st.warning(
        "Supabase credentials not configured — running in demo mode. "
        "Set SUPABASE_URL and SUPABASE_KEY in your environment to enable authentication."
    )

# ==============================================================================
# 2. AUTHENTICATION GATE
# ==============================================================================
if "user" not in st.session_state:
    st.session_state["user"] = None

if supabase and st.session_state["user"] is None:
    access_token = st.query_params.get("access_token", "")
    refresh_token = st.query_params.get("refresh_token", "")

    if access_token and refresh_token:
        try:
            supabase.auth.set_session(access_token, refresh_token)
            user_res = supabase.auth.get_user()
            if user_res and user_res.user:
                st.session_state["user"] = user_res.user
                st.query_params.clear()
                st.rerun()
        except Exception:
            pass

if supabase and st.session_state["user"] is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", border=False):
            st.markdown("""
                <div style="text-align:center;margin-bottom:32px;">
                    <div style="width:56px;height:56px;background:linear-gradient(135deg,#6D28D9,#DB2777);border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">
                        <i class="fa-solid fa-shield-halved" style="color:#fff;font-size:24px;"></i>
                    </div>
                    <h2 style="font-size:24px;font-weight:800;color:#0f172a;margin:0 0 4px;">Welcome Back</h2>
                    <p style="color:#64748b;font-size:14px;font-weight:500;margin:0;">Sign in to your SEO dashboard</p>
                </div>
            """, unsafe_allow_html=True)
            login_email = st.text_input("Email", placeholder="you@agency.com", label_visibility="collapsed")
            login_password = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed")
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            if submitted:
                try:
                    response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                    st.session_state["user"] = response.user
                    st.query_params.clear()
                    st.rerun()
                except Exception:
                    st.error("Invalid email or password.")

        st.markdown("""
            <div style="text-align:center;margin-top:24px;padding-top:24px;border-top:1px solid #e2e8f0;">
                <p style="color:#475569;font-size:14px;font-weight:500;margin:0 0 4px;">Don't have an account?</p>
                <a href="https://nexgenweblab.com/auth" style="color:#6D28D9;font-weight:700;text-decoration:none;">Create free account →</a>
            </div>
        """, unsafe_allow_html=True)
    st.stop()

# If running without Supabase, create a demo user session
if st.session_state["user"] is None:
    class DemoUser:
        email = "demo@nexgenweblab.com"
        user_metadata = {"plan": "free"}
    st.session_state["user"] = DemoUser()

# ==============================================================================
# 3. USER & PLAN
# ==============================================================================
current_user = st.session_state["user"]
metadata = current_user.user_metadata or {}
plan_type = metadata.get("plan", "free")
is_pro = plan_type == "pro"
plan_label = "Enterprise Pro" if is_pro else "Starter"
user_email = current_user.email

# ==============================================================================
# 4. CSS
# ==============================================================================
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
    [data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stToolbarActions"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    * { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 2rem; max-width: 1320px; }
    body, .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #fff; border-right: 1px solid #e2e8f0; padding-top: 1rem; }

    .hero-container { text-align: center; padding: 40px 10px 20px; }
    .hero-title { font-size: 42px; font-weight: 900; color: #0f172a; line-height: 1.1; margin-bottom: 12px; letter-spacing: -0.02em; }
    .hero-title span { background: linear-gradient(135deg, #6D28D9, #DB2777); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-subtitle { font-size: 16px; color: #64748b; max-width: 560px; margin: 0 auto 28px; font-weight: 500; line-height: 1.6; }

    .url-bar-wrapper { background: #fff; border: 1px solid #e2e8f0; border-radius: 24px; padding: 8px; box-shadow: 0 20px 50px -12px rgba(0,0,0,0.08); margin-bottom: 8px; }
    [data-testid="stForm"] div[data-testid="stHorizontalBlock"] { gap: 0 !important; align-items: stretch !important; padding: 0 !important; }
    .url-prefix { height: 64px !important; line-height: 64px !important; display: flex !important; align-items: center !important; justify-content: center !important; background: #f1f5f9 !important; color: #64748b !important; font-size: 15px !important; font-weight: 700 !important; border: 2px solid #e2e8f0 !important; border-right: none !important; border-radius: 16px 0 0 16px !important; padding: 0 24px !important; white-space: nowrap; }
    [data-testid="stForm"] .stTextInput input { height: 64px !important; font-size: 18px !important; padding-left: 20px !important; font-weight: 700 !important; color: #0f172a !important; border-radius: 0 !important; border: 2px solid #e2e8f0 !important; border-left: none !important; background: #f8fafc !important; }
    [data-testid="stForm"] .stTextInput input:focus { background: #fff !important; border-color: #6D28D9 !important; }
    [data-testid="stForm"] button[kind="primary"] { height: 64px !important; border-radius: 0 16px 16px 0 !important; font-size: 16px !important; font-weight: 800 !important; background: linear-gradient(135deg, #6D28D9, #DB2777) !important; color: white !important; border: none !important; width: 100% !important; letter-spacing: 0.02em !important; }
    [data-testid="stForm"] button[kind="primary"]:hover { transform: scale(1.02) !important; transition: transform 0.2s !important; box-shadow: 0 8px 20px rgba(109,40,217,0.25) !important; }
    @media (min-width: 768px) {
        .url-prefix { height: 80px !important; line-height: 80px !important; font-size: 16px !important; padding: 0 28px !important; }
        [data-testid="stForm"] .stTextInput input { height: 80px !important; font-size: 20px !important; }
        [data-testid="stForm"] button[kind="primary"] { height: 80px !important; font-size: 18px !important; }
    }

    div.stButton > button[kind="secondary"] { border-radius: 10px !important; font-weight: 600 !important; border: 1px solid #e2e8f0 !important; color: #475569 !important; background-color: #fff !important; font-size: 14px !important; height: 44px !important; }
    div.stButton > button[kind="secondary"]:hover { border-color: #6D28D9 !important; color: #6D28D9 !important; }

    .score-container { background: #fff; border-radius: 20px; padding: 32px; border: 1px solid #e2e8f0; margin-bottom: 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
    .issue-card { border-radius: 16px; padding: 24px; background: linear-gradient(135deg, #f8fafc, #fff); border: 1px solid #e2e8f0; display: flex; flex-direction: column; justify-content: center; height: 100%; }
    .issue-count { font-size: 44px; font-weight: 900; line-height: 1; margin-bottom: 6px; letter-spacing: -0.03em; }
    .issue-label { font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: none; margin-bottom: 24px; background: #f1f5f9; padding: 6px; border-radius: 14px; }
    .stTabs [data-baseweb="tab"] { height: 42px; font-size: 14px; font-weight: 600; color: #64748b; background: transparent; border-radius: 10px; border: none; padding: 0 18px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6D28D9, #DB2777) !important; color: white !important; box-shadow: 0 2px 8px rgba(109,40,217,0.2); }

    .audit-item { background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; margin-bottom: 14px; position: relative; overflow: hidden; display: flex; flex-direction: column; min-height: 210px; }
    .audit-item::before { content:''; position: absolute; left: 0; top: 0; height: 100%; width: 4px; border-radius: 0 2px 2px 0; }
    .status-danger::before { background: linear-gradient(180deg, #ef4444, #dc2626); }
    .status-warning::before { background: linear-gradient(180deg, #f59e0b, #d97706); }
    .status-success::before { background: linear-gradient(180deg, #10b981, #059669); }
    .status-info::before { background: linear-gradient(180deg, #3b82f6, #2563eb); }
    .audit-header { display: flex; align-items: flex-start; }
    .audit-header i { font-size: 18px; margin-right: 14px; width: 22px; text-align: center; margin-top: 2px; }
    .audit-item-title { font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
    .audit-item-desc { font-size: 13px; color: #64748b; font-weight: 500; }
    .actual-data-box { margin-top: 14px; margin-bottom: 4px; margin-left: 36px; padding: 10px 14px; background: #f8fafc; border-radius: 8px; font-size: 12px; color: #334155; word-break: break-word; border: 1px solid #e2e8f0; font-family: 'SF Mono', 'Fira Code', monospace; flex-grow: 1; }
    details.seo-tip { margin-top: 10px; margin-left: 36px; border-top: 1px dashed #e2e8f0; padding-top: 10px; }
    details.seo-tip summary { font-size: 12px; font-weight: 600; color: #6D28D9; cursor: pointer; outline: none; list-style: none; }
    details.seo-tip summary::after { content: ' +'; font-weight: 700; }
    details.seo-tip[open] summary::after { content: ' -'; }
    details.seo-tip p { margin: 8px 0 0 0; font-size: 12px; color: #475569; background: #f1f5f9; padding: 10px 14px; border-left: 3px solid #6D28D9; border-radius: 6px; }

    .speed-metric-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; height: 52px; }
    .speed-metric-card:hover { border-color: #cbd5e1; }

    .stProgress > div > div > div > div { background: linear-gradient(90deg, #6D28D9, #DB2777) !important; }

    .upgrade-banner { display: block; text-align: center; background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; padding: 11px; border-radius: 10px; font-weight: 700; text-decoration: none; margin-bottom: 14px; font-size: 13px; box-shadow: 0 4px 12px rgba(109,40,217,0.2); }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. HELPERS
# ==============================================================================
def render_donut(score):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 90 else "#10b981"
    fig = go.Figure(go.Pie(
        values=[max(score, 0), max(100 - score, 0)],
        labels=["Score", "Remaining"],
        hole=0.8,
        marker_colors=[color, "#f1f5f9"],
        textinfo="none",
        hoverinfo="none",
    ))
    fig.update_layout(
        annotations=[dict(text=str(int(score)), x=0.5, y=0.5, font_size=45, font_weight=900, font_color="#0f172a", showarrow=False)],
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=180,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_gauge(score):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 90 else "#10b981"
    fig = go.Figure(go.Pie(
        values=[max(score, 0), max(100 - score, 0)],
        labels=["Score", "Remaining"],
        hole=0.75,
        marker_colors=[color, "#f1f5f9"],
        textinfo="none",
        hoverinfo="none",
    ))
    fig.update_layout(
        annotations=[dict(text=str(int(score)), x=0.5, y=0.5, font_size=24, font_weight=800, font_color="#0f172a", showarrow=False)],
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=10),
        height=110,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def audit_status(v, check_type):
    tips = {
        "title": "Keep title between 30-60 characters.",
        "meta": "Meta description should be 150-160 characters.",
        "h1": "Each page must have exactly one H1 tag.",
        "images": "Add descriptive ALT attributes to all images.",
        "word_count": "Aim for 300+ words per page.",
        "schema": "Implement JSON-LD structured data markup.",
        "https": "Ensure SSL certificate is active and valid.",
        "html_size": "Keep HTML under 100KB for optimal performance.",
        "response_time": "Server response time should be under 0.2s.",
        "minified_css": "Minify all CSS files to reduce load time.",
        "minified_js": "Minify all JavaScript files.",
        "canonical": "Set a self-referencing canonical URL.",
        "meta_robots": "Configure proper meta robots directives.",
        "lang": "Declare the language attribute on the HTML tag.",
        "og": "Set Open Graph meta tags for social sharing.",
        "dir_listing": "Disable directory listing on your server.",
        "internal_links": "Ensure a strong internal linking structure.",
        "external_links": "Link to authoritative external sources.",
    }

    try:
        if check_type == "title":
            if isinstance(v, dict) and "Missing" not in v.get("title", "Missing"):
                return ("fa-solid fa-heading", f"Title Tag ({v.get('title_count', 0)} chars)", "success", tips["title"], v.get("title", "N/A"))
            return ("fa-solid fa-heading", "Missing Title Tag", "danger", tips["title"], "N/A")

        if check_type == "meta":
            if isinstance(v, dict) and "Missing" not in v.get("description", "Missing"):
                return ("fa-solid fa-paragraph", f"Meta Description ({v.get('desc_count', 0)} chars)", "success", tips["meta"], v.get("description", "N/A"))
            return ("fa-solid fa-paragraph", "Missing Meta Description", "danger", tips["meta"], "N/A")

        if check_type == "h1":
            if v and isinstance(v, list) and "Missing" not in v:
                return ("fa-solid fa-h", "H1 Tag Present", "success", tips["h1"], ", ".join(v[:3]))
            return ("fa-solid fa-h", "Missing H1 Heading", "danger", tips["h1"], "N/A")

        if check_type == "images":
            n = int(v) if v else 0
            if n > 0:
                return ("fa-solid fa-image", f"{n} image(s) missing ALT", "warning", tips["images"], f"{n} images without ALT")
            return ("fa-solid fa-image", "All images have ALT attributes", "success", tips["images"], "Optimized")

        if check_type == "word_count":
            n = int(v) if v else 0
            if n < 300:
                return ("fa-solid fa-file-lines", f"Low content ({n} words)", "warning", tips["word_count"], f"{n} words")
            return ("fa-solid fa-file-lines", f"Good content ({n} words)", "success", tips["word_count"], f"{n} words")

        if check_type == "schema":
            if v and "Missing" not in str(v):
                return ("fa-solid fa-diagram-next", "Schema Markup Found", "success", tips["schema"], str(v))
            return ("fa-solid fa-diagram-next", "Missing Schema Markup", "danger", tips["schema"], "N/A")

        if check_type == "https":
            if str(v) == "Yes":
                return ("fa-solid fa-lock", "HTTPS Secure", "success", tips["https"], "SSL active")
            return ("fa-solid fa-lock-open", "Not Secure (HTTP)", "danger", tips["https"], "No SSL")

        if check_type == "response_time":
            t = float(v) if v else 0
            if t > 0.5:
                return ("fa-solid fa-stopwatch", f"Slow response ({t:.2f}s)", "warning", tips["response_time"], f"{t:.2f}s")
            return ("fa-solid fa-stopwatch", f"Fast response ({t:.2f}s)", "success", tips["response_time"], f"{t:.2f}s")

        if check_type == "html_size":
            s = float(v) if v else 0
            if s > 100:
                return ("fa-solid fa-code", f"Large HTML ({s:.1f} KB)", "warning", tips["html_size"], f"{s:.1f} KB")
            return ("fa-solid fa-code", f"Optimal HTML ({s:.1f} KB)", "success", tips["html_size"], f"{s:.1f} KB")

        if check_type == "minified_css":
            n = int(v) if v else 0
            if n > 0:
                return ("fa-solid fa-file-code", f"{n} unminified CSS file(s)", "warning", tips["minified_css"], f"{n} files")
            return ("fa-solid fa-file-code", "CSS minified", "success", tips["minified_css"], "Optimized")

        if check_type == "minified_js":
            n = int(v) if v else 0
            if n > 0:
                return ("fa-solid fa-file-code", f"{n} unminified JS file(s)", "warning", tips["minified_js"], f"{n} files")
            return ("fa-solid fa-file-code", "JS minified", "success", tips["minified_js"], "Optimized")

        if check_type == "dir_listing":
            if str(v) == "Yes":
                return ("fa-solid fa-folder-minus", "Directory listing secured", "success", tips["dir_listing"], "Secured")
            return ("fa-solid fa-folder-tree", "Directory listing exposed", "danger", tips["dir_listing"], "Exposed!")

        label_map = {
            "canonical": ("fa-solid fa-link", "Canonical URL", "info", tips["canonical"]),
            "meta_robots": ("fa-solid fa-robot", "Meta Robots", "info", tips["meta_robots"]),
            "lang": ("fa-solid fa-language", "HTML Language", "info", tips["lang"]),
            "og": ("fa-solid fa-share-nodes", "Open Graph Tags", "info", tips["og"]),
            "internal_links": ("fa-solid fa-link", "Internal Links", "info", tips["internal_links"]),
            "external_links": ("fa-solid fa-external-link", "External Links", "info", tips["external_links"]),
        }
        if check_type in label_map:
            icon, label, status, tip = label_map[check_type]
            return (icon, label, status, tip, str(v) if v else "N/A")

        return ("fa-solid fa-circle-info", "SEO Factor", "info", "N/A", str(v))

    except Exception as e:
        return ("fa-solid fa-triangle-exclamation", "Error", "danger", str(e), "N/A")


def render_audit_card(label, data):
    icon, message, status, tip, actual = data
    return f"""<div class="audit-item status-{status}"><div class="audit-header"><i class="{icon}" style="color:var(--text-color);"></i><div class="audit-item-content"><span class="audit-item-title">{label}</span><span class="audit-item-desc">{message}</span></div></div><div class="actual-data-box">{actual}</div><details class="seo-tip"><summary>How to fix</summary><p>{tip}</p></details></div>""".replace("\n", "")


def render_metric(label, data_obj):
    score = data_obj.get("score", 0)
    value = data_obj.get("value", "N/A")
    if score >= 0.9:
        color, icon = "#10b981", "fa-solid fa-circle-check"
    elif score >= 0.5:
        color, icon = "#f59e0b", "fa-solid fa-square-minus"
    else:
        color, icon = "#ef4444", "fa-solid fa-triangle-exclamation"
    return f"""<div class="speed-metric-card"><div style="display:flex;align-items:center;"><i class="{icon}" style="color:{color};font-size:16px;margin-right:12px;width:16px;"></i><span style="font-size:14px;font-weight:700;color:#334155;">{label}</span></div><span style="font-size:16px;font-weight:900;color:{color};">{value}</span></div>""".replace("\n", "")


def calculate_scores(onpage, speed):
    critical = warnings = passed = 0

    if not onpage:
        return 0, 0, 0, 0

    h_alt = onpage.get("missing_alt", 0)
    w_count = onpage.get("word_count", 0)
    html_s = onpage.get("html_size_kb", 0.0)
    resp_t = onpage.get("response_time", 0.0)
    un_css = onpage.get("unminified_css", 0)
    un_js = onpage.get("unminified_js", 0)

    checks = [
        ("title", lambda: "Missing" in onpage.get("title", "Missing")),
        ("description", lambda: "Missing" in onpage.get("description", "Missing")),
        ("h1", lambda: not onpage.get("h1", []) or "Blocked" in str(onpage.get("h1", []))),
        ("schema", lambda: not onpage.get("schema") or "Blocked" in str(onpage.get("schema", ""))),
        ("https", lambda: onpage.get("is_https", "No") == "No"),
        ("dir", lambda: onpage.get("dir_listing_secured", "No") == "No"),
    ]
    for _, is_critical in checks:
        if is_critical():
            critical += 1
        else:
            passed += 1

    warn_checks = [
        h_alt > 0,
        w_count < 300,
        html_s > 100,
        resp_t > 0.5,
        un_css > 0,
        un_js > 0,
    ]
    for w in warn_checks:
        if w:
            warnings += 1
        else:
            passed += 1

    onpage_score = max(100 - (critical * 9) - (warnings * 3), 0)
    m_perf = speed["mobile"].get("performance", 50) if speed else 50
    d_perf = speed["desktop"].get("performance", 50) if speed else 50
    final = int((onpage_score + (m_perf + d_perf) / 2) / 2)

    return final, critical, warnings, passed


# ==============================================================================
# 6. SIDEBAR
# ==============================================================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=250)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#f8fafc,#fff);padding:16px;border-radius:14px;border:1px solid #e2e8f0;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#6D28D9,#DB2777);color:white;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;box-shadow:0 4px 8px rgba(109,40,217,0.2);">
                {user_email[0].upper()}
            </div>
            <div style="overflow:hidden;flex:1;">
                <div style="font-size:13px;font-weight:700;color:#0f172a;text-overflow:ellipsis;white-space:nowrap;overflow:hidden;">{user_email}</div>
                <div style="font-size:11px;color:{'#10b981' if is_pro else '#94a3b8'};font-weight:600;margin-top:3px;display:flex;align-items:center;gap:4px;">
                    <i class="fa-solid fa-{'crown' if is_pro else 'user'}"></i> {plan_label}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not is_pro:
        st.markdown('<a href="https://nexgenweblab.com/upgrade" target="_blank" class="upgrade-banner"><i class="fa-solid fa-bolt"></i> Upgrade to Pro</a>', unsafe_allow_html=True)

    if st.button("Log Out", use_container_width=True, type="secondary"):
        if supabase:
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
        st.session_state["user"] = None
        st.query_params.clear()
        st.rerun()

    st.markdown("<hr style='border-top:1px solid #e2e8f0;margin:20px 0;'>", unsafe_allow_html=True)

    bulk_icon = "file-earmark-spreadsheet" if is_pro else "lock-fill"
    menu = option_menu(
        menu_title=None,
        options=["Site Auditor", "Bulk Analysis"],
        icons=["search", bulk_icon],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#94a3b8", "font-size": "18px"},
            "nav-link": {
                "font-size": "15px", "text-align": "left", "margin": "0px",
                "color": "#475569", "font-weight": "600", "height": "50px", "border-radius": "10px",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, rgba(109, 40, 217, 0.07), rgba(219, 39, 119, 0.07))",
                "color": "#6D28D9", "border-left": "4px solid #DB2777",
            },
        },
    )
    st.markdown("<hr style='border-top:1px dashed #e2e8f0;margin:20px 0;'>", unsafe_allow_html=True)
    if st.button("Start New Audit", type="secondary", use_container_width=True):
        st.rerun()

# ==============================================================================
# 7. MAIN CONTENT
# ==============================================================================
if menu == "Site Auditor":
    st.markdown("""<div class="hero-container"><div class="hero-title">Professional <span>SEO Auditor</span></div><div class="hero-subtitle">Analyze technical roadblocks, measure Core Web Vitals, and get AI-driven growth strategies for any website.</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="url-bar-wrapper">', unsafe_allow_html=True)
    with st.form("audit_form", border=False):
        col_p, col_d, col_b = st.columns([1.2, 6.3, 2.5])
        with col_p:
            st.markdown('<div class="url-prefix">https://</div>', unsafe_allow_html=True)
        with col_d:
            domain_input = st.text_input("Domain", placeholder="yourdomain.com", label_visibility="collapsed")
        with col_b:
            run_btn = st.form_submit_button("Analyze Now", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if run_btn and domain_input:
        clean = domain_input.strip().replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
        target = f"https://{clean}"

        st.session_state["last_url"] = target
        st.session_state["last_domain"] = clean

        bar = st.progress(0, text="Initializing audit engine...")

        bar.progress(15, text="Crawling page architecture...")
        onpage = get_basic_onpage(target)
        if not onpage:
            onpage = {
                "title": "Data Blocked", "title_count": 0,
                "description": "Data Blocked", "desc_count": 0,
                "h1": ["Blocked"], "missing_alt": 0, "word_count": 0,
                "schema": "Blocked", "is_https": "Yes" if target.startswith("https") else "No",
                "html_size_kb": 0, "response_time": 0, "unminified_css": 0,
                "unminified_js": 0, "dir_listing_secured": "Unknown",
            }
        st.session_state["onpage_data"] = onpage

        bar.progress(45, text="Running Core Web Vitals test...")
        st.session_state["speed_data"] = check_speed(target, SPEED_API_KEY)

        if is_pro:
            bar.progress(70, text="Fetching traffic intelligence...")
            st.session_state["traffic_data"] = get_traffic_data(target, RAPIDAPI_KEY)
        else:
            bar.progress(70, text="Traffic analytics (Pro feature)")
            st.session_state["traffic_data"] = None

        bar.progress(85, text="Generating AI recommendations...")
        m_p = st.session_state["speed_data"]["mobile"].get("performance", 0)
        d_p = st.session_state["speed_data"]["desktop"].get("performance", 0)
        ai_result = get_ai_suggestions(
            {**onpage, "mobile_speed": m_p, "desktop_speed": d_p}, GEMINI_API_KEY
        )
        st.session_state["ai_data"] = ai_result

        bar.progress(100, text="Audit complete.")
        time.sleep(0.3)
        bar.empty()

    if "onpage_data" in st.session_state and st.session_state["onpage_data"]:
        onpage = st.session_state["onpage_data"]
        speed = st.session_state["speed_data"]
        traffic = st.session_state["traffic_data"]
        ai_data_full = st.session_state["ai_data"]
        ai_recommendations = ai_data_full.get("recommendations", []) if isinstance(ai_data_full, dict) else []
        ai_status = ai_data_full.get("status", "") if isinstance(ai_data_full, dict) else ""

        ov_score, crit, warn, passed = calculate_scores(onpage, speed)

        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;">
            <h3 style="color:#0f172a;font-weight:800;font-size:20px;margin:0;">Audit Overview</h3>
            <span style="font-size:13px;color:#64748b;font-weight:500;">Comprehensive technical analysis</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([1, 2.2], gap="large")
        with c1:
            st.plotly_chart(render_donut(ov_score), use_container_width=True, config={"displayModeBar": False}, key="donut_main")
        with c2:
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                st.markdown(f'<div class="issue-card" style="border-top:4px solid #ef4444;"><div class="issue-count" style="color:#ef4444;">{crit}</div><div class="issue-label">Critical</div></div>', unsafe_allow_html=True)
            with ic2:
                st.markdown(f'<div class="issue-card" style="border-top:4px solid #f59e0b;"><div class="issue-count" style="color:#f59e0b;">{warn}</div><div class="issue-label">Warnings</div></div>', unsafe_allow_html=True)
            with ic3:
                st.markdown(f'<div class="issue-card" style="border-top:4px solid #10b981;"><div class="issue-count" style="color:#10b981;">{passed}</div><div class="issue-label">Passed</div></div>', unsafe_allow_html=True)

        st.markdown("<hr style='border-top:1px solid #e2e8f0;margin:40px 0;'>", unsafe_allow_html=True)

        t1, t2, t3, t4 = st.tabs(["On-Page Data", "Speed Vitals", "AI Strategy", "Export"])

        with t1:
            hc1, hc2 = st.columns(2, gap="large")
            with hc1:
                st.markdown("<h5 style='color:#0f172a;margin-bottom:10px;border-bottom:2px solid #e2e8f0;padding-bottom:10px;'>Content & Performance</h5>", unsafe_allow_html=True)
            with hc2:
                st.markdown("<h5 style='color:#0f172a;margin-bottom:10px;border-bottom:2px solid #e2e8f0;padding-bottom:10px;'>Technical & Advanced</h5>", unsafe_allow_html=True)

            pairs = [
                (("Title Tag", audit_status(onpage, "title")), ("Canonical", audit_status(onpage.get("canonical", "Missing"), "canonical"))),
                (("Meta Description", audit_status(onpage, "meta")), ("Meta Robots", audit_status(onpage.get("meta_robots", "Missing"), "meta_robots"))),
                (("H1 Heading", audit_status(onpage.get("h1", []), "h1")), ("HTML Language", audit_status(onpage.get("lang", "Missing"), "lang"))),
                (("Content Length", audit_status(onpage.get("word_count", 0), "word_count")), ("Open Graph", audit_status(onpage.get("og_title", "Missing"), "og"))),
                (("Image ALT", audit_status(onpage.get("missing_alt", 0), "images")), ("Schema Markup", audit_status(onpage.get("schema", []), "schema"))),
                (("Server Response", audit_status(onpage.get("response_time", 0.0), "response_time")), ("SSL (HTTPS)", audit_status(onpage.get("is_https", "No"), "https"))),
                (("HTML Size", audit_status(onpage.get("html_size_kb", 0.0), "html_size")), ("Directory Listing", audit_status(onpage.get("dir_listing_secured", "No"), "dir_listing"))),
                (("CSS Minification", audit_status(onpage.get("unminified_css", 0), "minified_css")), ("Internal Links", audit_status(onpage.get("internal_links", 0), "internal_links"))),
                (("JS Minification", audit_status(onpage.get("unminified_js", 0), "minified_js")), ("External Links", audit_status(onpage.get("external_links", 0), "external_links"))),
            ]
            for left, right in pairs:
                ca, cb = st.columns(2, gap="large")
                with ca:
                    st.markdown(render_audit_card(*left), unsafe_allow_html=True)
                with cb:
                    st.markdown(render_audit_card(*right), unsafe_allow_html=True)

        with t2:
            if speed:
                estimated = speed["mobile"].get("performance", 0) == 0 and speed["desktop"].get("performance", 0) == 0
                badge = (
                    '<span style="font-size:11px;background:#f1f5f9;color:#64748b;padding:4px 12px;border-radius:20px;font-weight:600;">HTTP estimated</span>'
                    if estimated else
                    '<span style="font-size:11px;background:#ecfdf5;color:#059669;padding:4px 12px;border-radius:20px;font-weight:600;"><i class="fa-solid fa-check-circle"></i> Google PageSpeed API</span>'
                )

                for device, label in [("mobile", "Mobile"), ("desktop", "Desktop")]:
                    st.markdown(f"<h5 style='color:#0f172a;margin-bottom:20px;font-size:15px;font-weight:700;'>{label} Device</h5>", unsafe_allow_html=True)
                    cols = st.columns(4)
                    for i, k in enumerate(["performance", "accessibility", "best-practices", "seo"]):
                        with cols[i]:
                            st.plotly_chart(render_gauge(speed[device].get(k, 0)), use_container_width=True, config={"displayModeBar": False}, key=f"{device}_{k}")
                            st.markdown(f"<div style='text-align:center;font-size:14px;font-weight:700;color:#475569;margin-top:-15px;'>{k.replace('-', ' ').title()}</div>", unsafe_allow_html=True)

                    st.markdown("<div style='margin-top:35px;'></div>", unsafe_allow_html=True)
                    metrics = speed[device].get("metrics", {})
                    mc1, mc2 = st.columns(2, gap="large")
                    with mc1:
                        st.markdown(render_metric("First Contentful Paint (FCP)", metrics.get("fcp", {})), unsafe_allow_html=True)
                        st.markdown(render_metric("Total Blocking Time (TBT)", metrics.get("tbt", {})), unsafe_allow_html=True)
                        st.markdown(render_metric("Speed Index", metrics.get("si", {})), unsafe_allow_html=True)
                    with mc2:
                        st.markdown(render_metric("Largest Contentful Paint (LCP)", metrics.get("lcp", {})), unsafe_allow_html=True)
                        st.markdown(render_metric("Cumulative Layout Shift (CLS)", metrics.get("cls", {})), unsafe_allow_html=True)

                    st.markdown("<hr style='border-top:1px solid #e2e8f0;margin:40px 0;'>", unsafe_allow_html=True)

                # Traffic tab — always show if Pro
                if is_pro and traffic and traffic.get("status") == "Live Data":
                    st.markdown("<h5 style='color:#0f172a;margin-bottom:20px;font-size:15px;font-weight:700;'>Traffic Analytics</h5>", unsafe_allow_html=True)
                    raw = traffic.get("raw_data", {})
                    tg1, tg2 = st.columns(2)
                    with tg1:
                        visits = raw.get("EstimatedMonthlyVisits", 5000)
                        months = [(datetime.now() - timedelta(days=30 * i)).strftime("%b") for i in range(5, -1, -1)]
                        sim = [int(visits * (0.9 + 0.02 * i)) for i in range(6)]
                        fig = px.line(x=months, y=sim, labels={"x": "Month", "y": "Visits"})
                        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=250)
                        st.plotly_chart(fig, use_container_width=True, key="traffic_trend")
                    with tg2:
                        sources = raw.get("Traffic", {}).get("Sources", {})
                        fig2 = px.pie(
                            values=[sources.get("Search", 1), sources.get("Direct", 1), sources.get("Social", 1)],
                            names=["Search", "Direct", "Social"],
                            hole=0.5,
                        )
                        fig2.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=250)
                        st.plotly_chart(fig2, use_container_width=True, key="traffic_source")
                elif is_pro and traffic and traffic.get("status") == "API Key Missing":
                    st.warning("Traffic analytics not available: RAPIDAPI_KEY is not configured. Please set the API key in your environment.")
                elif not is_pro:
                    st.markdown("""
                    <div style="text-align:center;padding:40px 20px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;margin-top:20px;">
                        <i class="fa-solid fa-lock" style="font-size:48px;color:#DB2777;margin-bottom:20px;"></i>
                        <h3 style="color:#0f172a;font-weight:800;margin-bottom:10px;">Traffic Analytics is a Pro Feature</h3>
                        <p style="color:#64748b;margin-bottom:25px;max-width:500px;margin:0 auto 25px;">Unlock live traffic estimates, competitor analysis, and traffic sources by upgrading to Enterprise Pro.</p>
                        <a href="https://nexgenweblab.com/upgrade" target="_blank" style="background:linear-gradient(135deg,#6D28D9,#DB2777);color:white;padding:12px 25px;border-radius:8px;font-weight:bold;text-decoration:none;display:inline-block;">Upgrade to Pro ($9.99/mo)</a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Traffic data not available for this domain.")

        with t3:
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
                <h4 style="color:#0f172a;font-weight:800;font-size:18px;margin:0;">AI Action Plan</h4>
                <span style="font-size:12px;color:#64748b;font-weight:500;">Powered by Google Gemini</span>
            </div>
            """, unsafe_allow_html=True)

            if ai_status == "no_api_key":
                st.info("AI recommendations are not available because GEMINI_API_KEY is not configured. Please set the API key in your environment.")
            elif ai_recommendations:
                for item in ai_recommendations:
                    text = str(item.get("text", "")).replace("```json", "").replace("```html", "").replace("```", "").strip()
                    st.markdown(f"""<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px;margin-bottom:12px;border-left:4px solid #6D28D9;"><div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;"><div style="width:32px;height:32px;background:linear-gradient(135deg,rgba(109,40,217,0.1),rgba(219,39,119,0.1));border-radius:8px;display:flex;align-items:center;justify-content:center;"><i class="{item.get("icon", "fa-solid fa-lightbulb")}" style="color:#DB2777;font-size:14px;"></i></div><h5 style="color:#0f172a;font-weight:700;font-size:15px;margin:0;">{item.get("title", "Recommendation")}</h5></div><div style="color:#475569;font-size:14px;line-height:1.6;padding-left:42px;">{text}</div></div>""", unsafe_allow_html=True)
            elif ai_status == "error":
                st.error("Failed to generate AI recommendations. Please try again later.")
            elif not ai_recommendations and not ai_status:
                st.info("Run an audit to generate AI recommendations.")

        with t4:
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <h4 style="color:#0f172a;font-weight:800;font-size:18px;margin:0;">White Label Report</h4>
                <span style="font-size:12px;color:#64748b;font-weight:500;">DOCX export</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b;font-size:14px;margin-bottom:24px;'>Generate a professional SEO audit document with your own branding.</p>", unsafe_allow_html=True)

            wc1, wc2 = st.columns(2)
            agency = wc1.text_input("Agency name", value="NexGenWebLab Pro")
            author = wc2.text_input("Prepared by", value="SEO Team")
            client = st.text_input("Client / Project", value=st.session_state.get("last_domain", "client-domain").upper())

                doc_bytes = generate_word_report(
                    st.session_state["last_url"], onpage, speed, ai_recommendations, agency, client, author,
                )

            st.download_button(
                label="Download DOCX Report",
                data=doc_bytes,
                file_name=f"{st.session_state.get('last_domain', 'client')}_SEO_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )

elif menu == "Bulk Analysis":
    st.markdown("""<div class="hero-container"><div class="hero-title">Bulk <span>Outreach</span> Engine</div></div>""", unsafe_allow_html=True)

    if not is_pro:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;margin-top:20px;">
            <i class="fa-solid fa-file-earmark-lock" style="font-size:60px;color:#DB2777;margin-bottom:20px;"></i>
            <h2 style="color:#0f172a;font-weight:800;margin-bottom:10px;">Bulk Engine Locked</h2>
            <p style="color:#64748b;margin-bottom:30px;font-size:18px;max-width:600px;margin-left:auto;margin-right:auto;">Bulk analysis is exclusive to Enterprise Pro. Audit hundreds of URLs at once.</p>
            <a href="https://nexgenweblab.com/upgrade" target="_blank" style="background:linear-gradient(135deg,#6D28D9,#DB2777);color:white;padding:15px 30px;border-radius:8px;font-weight:bold;text-decoration:none;font-size:16px;display:inline-block;">Unlock Enterprise Pro</a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='score-container'>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload .xlsx file with URLs in the first column", type=["xlsx"])
        st.markdown("</div>", unsafe_allow_html=True)

        if uploaded:
            try:
                df = pd.read_excel(uploaded, header=None)
                urls = []
                for col in df.columns:
                    for cell in df[col].dropna().astype(str):
                        cell = cell.strip()
                        if cell.startswith("http") and cell not in urls:
                            urls.append(cell)

                if not urls:
                    st.error("No valid URLs (starting with http/https) found. Please ensure your Excel file contains URLs in any column, each starting with 'http' or 'https'.")
                else:
                    st.success(f"Found {len(urls)} unique URL(s).")

                    if st.button("Generate Bulk Reports", type="primary"):
                        st.info("Processing URLs... this may take a few minutes.")
                        progress = st.progress(0, text="Starting...")
                        results = []

                        for i, url in enumerate(urls):
                            pct = int((i + 1) / len(urls) * 100)
                            progress.progress(pct, text=f"Auditing {i+1}/{len(urls)}: {url[:50]}...")

                            onpage = get_basic_onpage(url)
                            speed = check_speed(url, SPEED_API_KEY)

                            if onpage:
                                m_p = speed.get("mobile", {}).get("performance", 0) if speed else 0
                                d_p = speed.get("desktop", {}).get("performance", 0) if speed else 0
                                ai_result = get_ai_suggestions({**onpage, "mobile_speed": m_p, "desktop_speed": d_p}, GEMINI_API_KEY)
                                ai_recommendations = ai_result.get("recommendations", []) if isinstance(ai_result, dict) else []
                                ai_status = ai_result.get("status", "") if isinstance(ai_result, dict) else ""
                            else:
                                ai = []

                            results.append({
                                "url": url,
                                "onpage": onpage,
                                "speed": speed,
                                "ai_recommendations": ai_recommendations,
                                "ai_status": ai_status,
                            })

                        progress.empty()

                        st.success(f"Audited {len(results)} URL(s). Download individual reports below.")
                        st.markdown("<hr style='border-top:1px solid #e2e8f0;margin:30px 0;'>", unsafe_allow_html=True)

                        for r in results:
                            if r["onpage"]:
                                domain = urlparse(r["url"]).netloc.replace("www.", "")
                                doc = generate_word_report(
                                    r["url"],
                                    r["onpage"],
                                    r["speed"],
                                    r["ai_recommendations"],
                                    "NexGenWebLab Pro",
                                    domain.upper(),
                                    "SEO Team",
                                )
                                st.download_button(
                                    label=f"Download {domain}_SEO_Report.docx",
                                    data=doc,
                                    file_name=f"{domain}_SEO_Report.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True,
                                )
                            else:
                                st.warning(f"Could not audit: {r['url']}")

            except Exception as e:
                st.error(f"Error processing file: {e}")
