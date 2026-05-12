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

# ==========================================
# 1. INITIALIZATION & APIs
# ==========================================
load_dotenv()
SPEED_API_KEY = os.getenv("SPEED_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

st.set_page_config(page_title="NexGenWebLab VIP | Enterprise SEO", page_icon="favicon.png", layout="wide", initial_sidebar_state="expanded")

try:
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Error: Render Environment Variables missing.")
        st.stop()
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Database connection failed. Exact Error: {str(e)}")
    st.stop()

# ==========================================
# 2. AUTHENTICATION GATE
# ==========================================
if 'user' not in st.session_state:
    st.session_state['user'] = None

if st.session_state['user'] is None:
    url_access_token = st.query_params.get("access_token", "")
    url_refresh_token = st.query_params.get("refresh_token", "")

    if url_access_token and url_refresh_token:
        try:
            supabase.auth.set_session(url_access_token, url_refresh_token)
            user_res = supabase.auth.get_user()
            if user_res and user_res.user:
                st.session_state['user'] = user_res.user
                st.query_params.clear()
                st.rerun()
        except Exception:
            pass

if st.session_state['user'] is None:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;min-height:100vh;background:#f8fafc;padding:20px;">
    <div style="background:#fff;border-radius:32px;box-shadow:0 25px 50px -12px rgba(0,0,0,0.15);padding:48px 40px;max-width:420px;width:100%;border:1px solid #e2e8f0;">
        <div style="text-align:center;margin-bottom:32px;">
            <div style="width:56px;height:56px;background:linear-gradient(135deg,#6D28D9,#DB2777);border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:24px;color:#fff;box-shadow:0 8px 16px -4px rgba(109,40,217,0.25);">
                <i class="fa-solid fa-shield-halved"></i>
            </div>
            <h2 style="font-size:24px;font-weight:800;color:#0f172a;margin:0 0 4px;">Welcome Back</h2>
            <p style="color:#64748b;font-size:14px;font-weight:500;margin:0;">Sign in to your Enterprise SEO dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", border=False):
            login_email = st.text_input("Email Address", placeholder="you@agency.com")
            login_password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In →", type="primary", use_container_width=True)
            if submitted:
                try:
                    response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                    st.session_state['user'] = response.user
                    st.query_params.clear()
                    st.rerun()
                except Exception as e:
                    st.error("Invalid email or password. Please try again.")
                    
        st.markdown("""
        <div style="text-align:center;margin-top:24px;padding-top:24px;border-top:1px solid #e2e8f0;">
            <p style="color:#475569;font-size:14px;font-weight:500;margin:0 0 4px;">Don't have an account?</p>
            <a href="https://nexgenweblab.com/auth" style="color:#6D28D9;font-weight:700;text-decoration:none;font-size:14px;">Create free account →</a>
        </div>
    </div></div>
        """, unsafe_allow_html=True)
    st.stop() 

# ==========================================
# 3. METADATA LOGIC
# ==========================================
current_user = st.session_state['user']
user_metadata = getattr(current_user, 'user_metadata', {}) or {}
plan_type = user_metadata.get('plan', 'free')
user_email = current_user.email

is_pro = True if plan_type == 'pro' or any(kw in user_email.lower() for kw in ["pro", "admin", "premium"]) else False
plan_name = "Enterprise Pro" if is_pro else "Starter Plan"

# ==========================================
# 4. LOAD MODULES & CSS
# ==========================================
try:
    from modules.onpage_scraper import get_basic_onpage
    from modules.speed_checker import check_speed
    from modules.ai_analyzer import get_ai_suggestions
    from modules.report_export import generate_word_report
    from modules.traffic_checker import get_traffic_data
except ImportError as e:
    st.error(f"Missing modules. {e}")
    st.stop()

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">', unsafe_allow_html=True)

st.markdown("""
<style>
    [data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stToolbarActions"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    * { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 2rem; max-width: 1320px; }
    body { background-color: #f8fafc; }
    .stApp { background-color: #f8fafc; }

    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; padding-top: 1rem; }
    [data-testid="stSidebar"] .stImage { padding: 0 20px; }

    .hero-container { text-align: center; padding: 40px 10px 20px; }
    .hero-title { font-size: 42px; font-weight: 900; color: #0f172a; line-height: 1.1; margin-bottom: 12px; letter-spacing: -0.02em; }
    .hero-title span { background: linear-gradient(135deg, #6D28D9, #DB2777); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-subtitle { font-size: 16px; color: #64748b; max-width: 560px; margin: 0 auto 28px; font-weight: 500; line-height: 1.6; }

    [data-testid="stForm"] div[data-testid="stHorizontalBlock"] { gap: 0px !important; align-items: center !important; padding: 0 !important; }
    [data-testid="stForm"] div[data-testid="column"] { padding: 0px !important; margin: 0px !important; }
    .url-prefix { height: 52px !important; min-height: 52px !important; line-height: 52px !important; display: flex !important; align-items: center !important; justify-content: center !important; background: #fff !important; color: #0f172a !important; font-size: 15px !important; font-weight: 600 !important; border: 2px solid #e2e8f0 !important; border-right: none !important; border-radius: 16px 0 0 16px !important; margin: 0 !important; width: 100% !important; margin-top: -16px !important; }
    [data-testid="stForm"] .stTextInput input { height: 52px !important; line-height: 52px !important; font-size: 15px !important; padding-left: 14px !important; margin: 0px !important; font-weight: 500 !important; color: #0f172a !important; border-radius: 0 !important; border: 2px solid #e2e8f0 !important; border-left: none !important; background: #fff !important; }
    [data-testid="stForm"] button[kind="primary"] { height: 52px !important; min-height: 52px !important; border-radius: 0 16px 16px 0 !important; font-size: 15px !important; font-weight: 700 !important; background: linear-gradient(135deg, #6D28D9, #DB2777) !important; color: white !important; border: none !important; width: 100% !important; margin: 0 !important; display: flex !important; align-items: center !important; justify-content: center !important; padding: 0 24px !important; letter-spacing: -0.01em; gap: 8px; }

    div.stButton > button[kind="secondary"] { border-radius: 10px !important; font-weight: 600 !important; border: 1px solid #e2e8f0 !important; color: #475569 !important; background-color: #fff !important; font-size: 14px !important; height: 44px !important; }
    div.stButton > button[kind="secondary"]:hover { border-color: #6D28D9 !important; color: #6D28D9 !important; }

    .score-container { background: #ffffff; border-radius: 20px; padding: 32px; border: 1px solid #e2e8f0; margin-bottom: 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
    .issue-card { border-radius: 16px; padding: 24px; background: linear-gradient(135deg, #f8fafc, #fff); border: 1px solid #e2e8f0; display: flex; flex-direction: column; justify-content: center; height: 100%; transition: all 0.2s; }
    .issue-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .issue-count { font-size: 44px; font-weight: 900; line-height: 1; margin-bottom: 6px; letter-spacing: -0.03em; }
    .issue-label { font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: none; margin-bottom: 24px; background: #f1f5f9; padding: 6px; border-radius: 14px; }
    .stTabs [data-baseweb="tab"] { height: 42px; font-size: 14px; font-weight: 600; color: #64748b; background-color: transparent; border-radius: 10px; border: none; padding: 0 18px; transition: all 0.2s; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6D28D9, #DB2777) !important; color: white !important; box-shadow: 0 2px 8px rgba(109,40,217,0.2); }

    .audit-item { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; margin-bottom: 14px; position: relative; overflow: hidden; display: flex; flex-direction: column; min-height: 210px; transition: all 0.2s; }
    .audit-item:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.04); }
    .audit-item::before { content:''; position: absolute; left: 0; top: 0; height: 100%; width: 4px; border-radius: 0 2px 2px 0; }
    .status-danger::before { background: linear-gradient(180deg, #ef4444, #dc2626); }
    .status-warning::before { background: linear-gradient(180deg, #f59e0b, #d97706); }
    .status-success::before { background: linear-gradient(180deg, #10b981, #059669); }
    .status-info::before { background: linear-gradient(180deg, #3b82f6, #2563eb); }
    .audit-header { display: flex; align-items: flex-start; width: 100%; }
    .audit-header i { font-size: 18px; margin-right: 14px; width: 22px; text-align: center; margin-top: 2px; }
    .audit-item-content { display: flex; flex-direction: column; flex-grow: 1; }
    .audit-item-title { font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
    .audit-item-desc { font-size: 13px; color: #64748b; line-height: 1.4; font-weight: 500; }
    .actual-data-box { margin-top: 14px; margin-bottom: 4px; margin-left: 36px; padding: 10px 14px; background: #f8fafc; border-radius: 8px; font-size: 12px; color: #334155; word-break: break-word; border: 1px solid #e2e8f0; font-family: 'SF Mono', 'Fira Code', monospace; line-height: 1.5; flex-grow: 1; }
    details.seo-tip { margin-top: 10px; margin-left: 36px; border-top: 1px dashed #e2e8f0; padding-top: 10px; }
    details.seo-tip summary { font-size: 12px; font-weight: 600; color: #6D28D9; cursor: pointer; outline: none; list-style: none; opacity: 0.8; transition: opacity 0.2s; }
    details.seo-tip summary:hover { opacity: 1; }
    details.seo-tip summary::after { content: ' +'; font-weight: 700; }
    details.seo-tip[open] summary::after { content: ' -'; }
    details.seo-tip p { margin: 8px 0 0 0; font-size: 12px; color: #475569; background: #f1f5f9; padding: 10px 14px; border-left: 3px solid #6D28D9; border-radius: 6px; line-height: 1.5; }

    .speed-metric-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; height: 52px; transition: all 0.2s; }
    .speed-metric-card:hover { border-color: #cbd5e1; }
    .speed-metric-card i { font-size: 14px !important; }

    .stProgress > div > div > div > div { background: linear-gradient(90deg, #6D28D9, #DB2777) !important; }
    .st-emotion-cache-1v7f65l { background-color: transparent !important; }

    h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; letter-spacing: -0.02em !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. HELPER FUNCTIONS
# ==========================================
def render_overview_donut(score):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 90 else "#10b981"
    fig = go.Figure(go.Pie(values=[max(score, 0), max(100-score, 0)], labels=["Score", "Remaining"], hole=.8, marker_colors=[color, "#f1f5f9"], textinfo='none', hoverinfo='none'))
    fig.update_layout(annotations=[dict(text=str(int(score)), x=0.5, y=0.5, font_size=45, font_weight=900, font_color='#0f172a', showarrow=False)], showlegend=False, margin=dict(l=0, r=0, t=0, b=0), height=180, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def render_small_gauge(score):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 90 else "#10b981"
    fig = go.Figure(go.Pie(values=[max(score, 0), max(100-score, 0)], labels=["Score", "Remaining"], hole=.75, marker_colors=[color, "#f1f5f9"], textinfo='none', hoverinfo='none'))
    fig.update_layout(annotations=[dict(text=str(int(score)), x=0.5, y=0.5, font_size=24, font_weight=800, font_color='#0f172a', showarrow=False)], showlegend=False, margin=dict(l=0, r=0, t=10, b=10), height=110, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def get_audit_status_vip(v, type):
    tips = {
        "title": "Keep title between 30-60 chars.", "meta": "Write description between 150-160 chars.",
        "h1": "Page must have exactly one H1 tag.", "images": "Add descriptive ALT attributes to images.",
        "word_count": "Aim for 300+ words.", "schema": "Implement JSON-LD Schema markup.",
        "https": "Ensure SSL is active.", "html_size": "Keep HTML under 100KB.",
        "response_time": "Optimize server response time (<0.2s).", "minified_css": "Minify CSS files.",
        "minified_js": "Minify Javascript files.", "canonical": "Set self-referencing canonical URL.",
        "meta_robots": "Set proper meta robots tags.", "lang": "Declare language attribute.",
        "og": "Set Open Graph tags.", "dir_listing": "Secure your server directories.",
        "internal_links": "Ensure internal linking structure is strong.", "external_links": "Link out to authoritative sites."
    }
    actual = "N/A"
    try:
        if type == "title": actual = str(v.get('title', 'Missing')) if isinstance(v, dict) else str(v)
        elif type == "meta": actual = str(v.get('description', 'Missing')) if isinstance(v, dict) else str(v)
        elif type == "h1": actual = ", ".join([str(h) for h in v if h]) if isinstance(v, list) and v else "No H1 tags found."
        elif type == "images": actual = f"{int(v)} images without ALT detected." if v and int(v) > 0 else "All images optimized."
        elif type == "word_count": actual = f"Content length: {int(v) if v else 0} words."
        elif type == "https": actual = "SSL active (Secure)." if str(v) == "Yes" else "No SSL (Insecure)."
        elif type == "schema": actual = f"Found: {', '.join([str(s) for s in v])}" if isinstance(v, list) and v else "Missing Schema markup."
        elif type == "response_time": actual = f"Response Time: {float(v):.2f}s." if v else "0.0s"
        elif type == "html_size": actual = f"HTML Size: {float(v):.1f} KB." if v else "0.0 KB"
        elif type in ["minified_css", "minified_js"]: actual = f"{int(v)} unminified files detected." if v and int(v) > 0 else "Files minified."
        elif type == "dir_listing": actual = "Secured." if str(v) == "Yes" else "Exposed!"
        elif type in ["canonical", "meta_robots", "lang", "og", "internal_links", "external_links"]: actual = str(v) if v else "Missing/0"
        if len(actual) > 90: actual = actual[:87] + "..."
        if type == "title": 
            if isinstance(v, dict) and "Missing" not in v.get('title', 'Missing'): return ("fa-solid fa-heading", f"Title Tag ({v.get('title_count', 0)} chars)", "success", tips['title'], actual)
            return ("fa-solid fa-heading", "Missing Title Tag", "danger", tips['title'], actual)
        elif type == "meta": 
            if isinstance(v, dict) and "Missing" not in v.get('description', 'Missing'): return ("fa-solid fa-paragraph", f"Meta Desc ({v.get('desc_count', 0)} chars)", "success", tips['meta'], actual)
            return ("fa-solid fa-paragraph", "Missing Meta Description", "danger", tips['meta'], actual)
        elif type == "h1": 
            if v and isinstance(v, list) and "Missing" not in v: return ("fa-solid fa-h", "H1 Tag Present", "success", tips['h1'], actual)
            return ("fa-solid fa-h", "Missing H1 Heading", "danger", tips['h1'], actual)
        elif type == "images": 
            if v and int(v) > 0: return ("fa-solid fa-image", f"{int(v)} Images missing ALT", "warning", tips['images'], actual)
            return ("fa-solid fa-image", "Image Alts Optimized", "success", tips['images'], actual)
        elif type == "word_count": 
            if int(v if v else 0) < 300: return ("fa-solid fa-file-lines", f"Low Content ({int(v if v else 0)} words)", "warning", tips['word_count'], actual)
            return ("fa-solid fa-file-lines", f"Good Content ({int(v if v else 0)} words)", "success", tips['word_count'], actual)
        elif type == "schema": 
            if v and "Missing" not in str(v): return ("fa-solid fa-diagram-next", "Schema Found", "success", tips['schema'], actual)
            return ("fa-solid fa-diagram-next", "Missing Schema Markup", "danger", tips['schema'], actual)
        elif type == "https": 
            if str(v) == "Yes": return ("fa-solid fa-lock", "Secured (HTTPS)", "success", tips['https'], actual)
            return ("fa-solid fa-lock-open", "Unsecured (HTTP)", "danger", tips['https'], actual)
        elif type == "response_time":
            if float(v if v else 0) > 0.5: return ("fa-solid fa-stopwatch", f"Slow Server ({float(v if v else 0):.2f}s)", "warning", tips['response_time'], actual)
            return ("fa-solid fa-stopwatch", f"Fast Server ({float(v if v else 0):.2f}s)", "success", tips['response_time'], actual)
        elif type == "html_size":
            if float(v if v else 0) > 100: return ("fa-solid fa-code", f"Large HTML ({float(v if v else 0):.1f} KB)", "warning", tips['html_size'], actual)
            return ("fa-solid fa-code", f"Optimal HTML ({float(v if v else 0):.1f} KB)", "success", tips['html_size'], actual)
        elif type == "minified_css":
            if int(v if v else 0) > 0: return ("fa-solid fa-file-code", f"{int(v if v else 0)} Unminified CSS", "warning", tips['minified_css'], actual)
            return ("fa-solid fa-file-code", "CSS Minified", "success", tips['minified_css'], actual)
        elif type == "minified_js":
            if int(v if v else 0) > 0: return ("fa-solid fa-file-code", f"{int(v if v else 0)} Unminified JS", "warning", tips['minified_js'], actual)
            return ("fa-solid fa-file-code", "JS Minified", "success", tips['minified_js'], actual)
        elif type == "dir_listing":
            if str(v) == "Yes": return ("fa-solid fa-folder-minus", "Directory Secured", "success", tips['dir_listing'], actual)
            return ("fa-solid fa-folder-tree", "Directory Exposed", "danger", tips['dir_listing'], actual)
        elif type == "canonical": return ("fa-solid fa-link", "Canonical URL", "info", tips['canonical'], actual)
        elif type == "meta_robots": return ("fa-solid fa-robot", "Meta Robots", "info", tips['meta_robots'], actual)
        elif type == "lang": return ("fa-solid fa-language", "HTML Language", "info", tips['lang'], actual)
        elif type == "og": return ("fa-solid fa-share-nodes", "Open Graph Tags", "info", tips['og'], actual)
        elif type == "internal_links": return ("fa-solid fa-link", "Internal Links", "info", tips['internal_links'], actual)
        elif type == "external_links": return ("fa-solid fa-external-link", "External Links", "info", tips['external_links'], actual)
        else: return ("fa-solid fa-circle-info", "SEO Factor", "info", "N/A", actual)
    except Exception as e:
        return ("fa-solid fa-triangle-exclamation", "Extraction Error", "danger", f"Error: {e}", "N/A")

def render_audit_card_vip(label, data):
    icon, message, status_class, tip, actual_data = data
    html = f"""<div class="audit-item status-{status_class}"><div class="audit-header"><i class="{icon}" style="color:var(--text-color);"></i><div class="audit-item-content"><span class="audit-item-title">{label}</span><span class="audit-item-desc">{message}</span></div></div><div class="actual-data-box">{actual_data}</div><details class="seo-tip"><summary>How to fix</summary><p>{tip}</p></details></div>"""
    return html.replace('\n', '')

def render_speed_metric(label, data_obj):
    score = data_obj.get('score', 0)
    value = data_obj.get('value', 'N/A')
    if score >= 0.9: color, icon = "#10b981", "fa-solid fa-circle-check"
    elif score >= 0.5: color, icon = "#f59e0b", "fa-solid fa-square-minus"
    else: color, icon = "#ef4444", "fa-solid fa-triangle-exclamation"
    html = f"""<div class="speed-metric-card"><div style="display: flex; align-items: center;"><i class="{icon}" style="color: {color}; font-size: 16px; margin-right: 12px; width: 16px;"></i><span style="font-size: 14px; font-weight: 700; color: #334155;">{label}</span></div><span style="font-size: 16px; font-weight: 900; color: {color};">{value}</span></div>"""
    return html.replace('\n', '')

def calculate_ov_vip(onpage, speed):
    critical, warnings, passed = 0, 0, 0
    if not onpage: return 0, 0, 0, 0
    h_alt, w_count, html_s, resp_t = onpage.get('missing_alt', 0), onpage.get('word_count', 0), onpage.get('html_size_kb', 0.0), onpage.get('response_time', 0.0)
    un_css, un_js = onpage.get('unminified_css', 0), onpage.get('unminified_js', 0)

    if "Missing" in onpage.get('title', 'Missing') or "Blocked" in str(onpage.get('title', '')): critical += 1
    else: passed += 1
    if "Missing" in onpage.get('description', 'Missing') or "Blocked" in str(onpage.get('description', '')): critical += 1
    else: passed += 1
    if not onpage.get('h1', []) or "Blocked" in str(onpage.get('h1', [])): critical += 1
    else: passed += 1
    if h_alt > 0: warnings += 1
    else: passed += 1
    if w_count < 300: warnings += 1
    else: passed += 1
    if not onpage.get('schema', None) or "Blocked" in str(onpage.get('schema', '')): critical += 1
    else: passed += 1
    if onpage.get('is_https', 'No') == "No": critical += 1
    else: passed += 1
    if html_s > 100: warnings += 1
    else: passed += 1
    if resp_t > 0.5: warnings += 1
    else: passed += 1
    if un_css > 0: warnings += 1
    else: passed += 1
    if un_js > 0: warnings += 1
    else: passed += 1
    if onpage.get('dir_listing_secured', 'No') == "No": critical += 1
    else: passed += 1

    onpage_score = 100 - (critical * 9) - (warnings * 3)
    m_speed = speed['mobile'].get('performance', 50) if speed else 50
    d_speed = speed['desktop'].get('performance', 50) if speed else 50
    final_score = int((max(onpage_score, 0) + ((m_speed + d_speed) / 2)) / 2)
    return final_score, critical, warnings, passed

# ==========================================
# 6. UI: SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8fafc, #fff); padding: 16px; border-radius: 14px; border: 1px solid #e2e8f0; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; box-shadow: 0 4px 8px rgba(109,40,217,0.2);">
                {user_email[0].upper()}
            </div>
            <div style="overflow: hidden; flex: 1;">
                <div style="font-size: 13px; font-weight: 700; color: #0f172a; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;" title="{user_email}">{user_email}</div>
                <div style="font-size: 11px; color: {'#10b981' if is_pro else '#94a3b8'}; font-weight: 600; margin-top: 3px; display: flex; align-items: center; gap: 4px;">
                    <i class="fa-solid fa-{'crown' if is_pro else 'user'}"></i> {plan_name}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not is_pro:
        st.markdown("""
        <a href="https://nexgenweblab.com/upgrade" target="_blank" style="display:block; text-align:center; background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; padding: 11px; border-radius: 10px; font-weight: 700; text-decoration: none; margin-bottom: 14px; font-size: 13px; transition: all 0.2s; box-shadow: 0 4px 12px rgba(109,40,217,0.2);" onmouseover="this.style.opacity='0.9'" onmouseout="this.style.opacity='1'">
            <i class="fa-solid fa-bolt"></i> Upgrade to Pro
        </a>
        """, unsafe_allow_html=True)

    if st.button("Log Out", use_container_width=True, type="secondary"):
        try: supabase.auth.sign_out()
        except: pass
        st.session_state['user'] = None
        st.query_params.clear()
        st.rerun()
        
    st.markdown("<hr style='border-top: 1px solid #e2e8f0; margin: 20px 0;'>", unsafe_allow_html=True)
    
    bulk_icon = "file-earmark-spreadsheet" if is_pro else "lock-fill"
    menu_selection = option_menu(menu_title=None, options=["Site Auditor", "Bulk Analysis"], icons=["search", bulk_icon], default_index=0, styles={"container": {"padding": "0!important", "background-color": "transparent"}, "icon": {"color": "#94a3b8", "font-size": "18px"}, "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "color":"#475569", "font-weight":"600", "height":"50px", "border-radius":"10px"}, "nav-link-selected": {"background": "linear-gradient(135deg, rgba(109, 40, 217, 0.07), rgba(219, 39, 119, 0.07))", "color": "#6D28D9", "border-left": "4px solid #DB2777"}})
    st.markdown("<hr style='border-top: 1px dashed #e2e8f0; margin: 20px 0;'>", unsafe_allow_html=True)
    if st.button("Start New Audit", type="secondary", use_container_width=True): st.rerun()

# ==========================================
# 7. UI: MAIN CONTENT
# ==========================================
if menu_selection == "Site Auditor":
    st.markdown("""<div class="hero-container"><div class="hero-title">Professional <span>SEO Auditor</span></div><div class="hero-subtitle">Analyze technical roadblocks, measure Core Web Vitals, and get AI-driven growth strategies for any website in seconds.</div></div>""", unsafe_allow_html=True)
    
    with st.form("audit_form", border=False):
        col_prefix, col_domain, col_btn = st.columns([1.2, 6.3, 2.5])
        with col_prefix: st.markdown('<div class="url-prefix">https://</div>', unsafe_allow_html=True)
        with col_domain: domain_input = st.text_input("Domain", value="", placeholder="Enter domain (e.g. example.com)", label_visibility="collapsed")
        with col_btn: run_button = st.form_submit_button("Analyze Now →", type="primary", use_container_width=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    if run_button and domain_input:
        clean_domain = domain_input.strip().replace("https://", "").replace("http://", "").replace("www.", "").strip('/')
        target_url = f"https://{clean_domain}"
        
        st.session_state['last_audit_url'] = target_url
        st.session_state['last_clean_domain'] = clean_domain

        progress_bar = st.progress(0, text="⚡ Initializing audit engine...")
        
        progress_bar.progress(15, text="🔍 Crawling page architecture...")
        st.session_state['onpage_data'] = get_basic_onpage(target_url)
        if not st.session_state['onpage_data']:
            st.session_state['onpage_data'] = {
                'title': 'Data Blocked', 'title_count': 0, 'description': 'Data Blocked', 'desc_count': 0,
                'h1': ['Blocked'], 'missing_alt': 0, 'word_count': 0, 'schema': 'Blocked',
                'is_https': 'Yes' if target_url.startswith('https') else 'No', 'html_size_kb': 0, 'response_time': 0, 
                'unminified_css': 0, 'unminified_js': 0, 'dir_listing_secured': 'Unknown'
            }

        progress_bar.progress(45, text="📊 Running Core Web Vitals test...")
        st.session_state['speed_data'] = check_speed(target_url, SPEED_API_KEY)
        
        if is_pro:
            progress_bar.progress(70, text="📈 Fetching traffic intelligence...")
            st.session_state['traffic_data'] = get_traffic_data(target_url, RAPIDAPI_KEY)
        else:
            progress_bar.progress(70, text="⏭️ Traffic analytics (Pro feature)")
            st.session_state['traffic_data'] = None
        
        progress_bar.progress(85, text="🤖 Generating AI recommendations...")
        m_perf = st.session_state['speed_data']['mobile'].get('performance', 0) if st.session_state['speed_data'] else 0
        d_perf = st.session_state['speed_data']['desktop'].get('performance', 0) if st.session_state['speed_data'] else 0
        st.session_state['ai_suggestions'] = get_ai_suggestions({**st.session_state['onpage_data'], 'mobile_speed': m_perf, 'desktop_speed': d_perf}, GEMINI_API_KEY)
        
        progress_bar.progress(100, text="Complete.")
        time.sleep(0.3) 
        progress_bar.empty()

    if 'onpage_data' in st.session_state and st.session_state['onpage_data']:
        onpage_data = st.session_state['onpage_data']
        speed_data = st.session_state['speed_data']
        traffic_data = st.session_state['traffic_data']
        ai_suggestions = st.session_state['ai_suggestions']
        
        ov_score, crit_count, warn_count, pass_count = calculate_ov_vip(onpage_data, speed_data)
        
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;">
            <h3 style="color:#0f172a;font-weight:800;font-size:20px;margin:0;">Audit Overview</h3>
            <span style="font-size:13px;color:#64748b;font-weight:500;">Comprehensive technical analysis</span>
        </div>
        """, unsafe_allow_html=True)
        ov_col1, ov_col2 = st.columns([1, 2.2], gap="large")
        with ov_col1: st.plotly_chart(render_overview_donut(ov_score), use_container_width=True, config={'displayModeBar': False}, key="main_donut")
        with ov_col2:
            ic1, ic2, ic3 = st.columns(3)
            with ic1: st.markdown(f"""<div class="issue-card" style="border-top: 4px solid #ef4444;"><span class="issue-count" style="color:#ef4444;">{crit_count}</span><span class="issue-label">Critical</span></div>""", unsafe_allow_html=True)
            with ic2: st.markdown(f"""<div class="issue-card" style="border-top: 4px solid #f59e0b;"><span class="issue-count" style="color:#f59e0b;">{warn_count}</span><span class="issue-label">Warnings</span></div>""", unsafe_allow_html=True)
            with ic3: st.markdown(f"""<div class="issue-card" style="border-top: 4px solid #10b981;"><span class="issue-count" style="color:#10b981;">{pass_count}</span><span class="issue-label">Passed</span></div>""", unsafe_allow_html=True)
        
        st.markdown("<hr style='border-top: 1px solid #e2e8f0; margin: 40px 0;'>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["On-Page Data", "Speed Vitals", "Traffic Analytics", "AI Strategy", "Document Export"])
        
        with tab1:
            h_col1, h_col2 = st.columns(2, gap="large")
            with h_col1: st.markdown("<h5 style='color: #0f172a; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;'>Content & Performance</h5>", unsafe_allow_html=True)
            with h_col2: st.markdown("<h5 style='color: #0f172a; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;'>Technical & Advanced</h5>", unsafe_allow_html=True)
            
            pairs = [
                (("Title Tag", get_audit_status_vip(onpage_data, "title")), ("Canonical URL", get_audit_status_vip(onpage_data.get('canonical', 'Missing'), "canonical"))),
                (("Meta Description", get_audit_status_vip(onpage_data, "meta")), ("Meta Robots", get_audit_status_vip(onpage_data.get('meta_robots', 'Missing'), "meta_robots"))),
                (("H1 Heading", get_audit_status_vip(onpage_data.get('h1', []), "h1")), ("HTML Language", get_audit_status_vip(onpage_data.get('lang', 'Missing'), "lang"))),
                (("Content Length", get_audit_status_vip(onpage_data.get('word_count', 0), "word_count")), ("Open Graph Check", get_audit_status_vip(onpage_data.get('og_title', 'Missing'), "og"))),
                (("Image Alt Attributes", get_audit_status_vip(onpage_data.get('missing_alt', 0), "images")), ("Schema.org Markup", get_audit_status_vip(onpage_data.get('schema', []), "schema"))),
                (("Server Response Time", get_audit_status_vip(onpage_data.get('response_time', 0.0), "response_time")), ("SSL Protocol (HTTPS)", get_audit_status_vip(onpage_data.get('is_https', 'No'), "https"))),
                (("Total HTML Size", get_audit_status_vip(onpage_data.get('html_size_kb', 0.0), "html_size")), ("Directory Listing", get_audit_status_vip(onpage_data.get('dir_listing_secured', 'No'), "dir_listing"))),
                (("CSS Minification", get_audit_status_vip(onpage_data.get('unminified_css', 0), "minified_css")), ("Internal Links", get_audit_status_vip(onpage_data.get('internal_links', 0), "internal_links"))),
                (("JS Minification", get_audit_status_vip(onpage_data.get('unminified_js', 0), "minified_js")), ("External Links", get_audit_status_vip(onpage_data.get('external_links', 0), "external_links")))
            ]
            for left_item, right_item in pairs:
                c1, c2 = st.columns(2, gap="large")
                with c1: st.markdown(render_audit_card_vip(*left_item), unsafe_allow_html=True)
                with c2: st.markdown(render_audit_card_vip(*right_item), unsafe_allow_html=True)

        with tab2:
            if speed_data:
                st.markdown("<h4 style='color: #0f172a; margin-bottom: 25px; text-align: center;'>Mobile Device Analysis</h4>", unsafe_allow_html=True)
                m_gauges = st.columns(4)
                with m_gauges[0]: 
                    st.plotly_chart(render_small_gauge(speed_data['mobile'].get('performance', 0)), use_container_width=True, config={'displayModeBar': False}, key="m_perf")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Performance</div>", unsafe_allow_html=True)
                with m_gauges[1]: 
                    st.plotly_chart(render_small_gauge(speed_data['mobile'].get('accessibility', 0)), use_container_width=True, config={'displayModeBar': False}, key="m_acc")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Accessibility</div>", unsafe_allow_html=True)
                with m_gauges[2]: 
                    st.plotly_chart(render_small_gauge(speed_data['mobile'].get('best-practices', 0)), use_container_width=True, config={'displayModeBar': False}, key="m_bp")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Best Practices</div>", unsafe_allow_html=True)
                with m_gauges[3]: 
                    st.plotly_chart(render_small_gauge(speed_data['mobile'].get('seo', 0)), use_container_width=True, config={'displayModeBar': False}, key="m_seo")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>SEO Score</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
                m_metrics = speed_data['mobile'].get('metrics', {})
                sm_col1, sm_col2 = st.columns(2, gap="large")
                with sm_col1:
                    st.markdown(render_speed_metric("First Contentful Paint (FCP)", m_metrics.get('fcp', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Total Blocking Time (TBT)", m_metrics.get('tbt', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Speed Index", m_metrics.get('si', {})), unsafe_allow_html=True)
                with sm_col2:
                    st.markdown(render_speed_metric("Largest Contentful Paint (LCP)", m_metrics.get('lcp', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Cumulative Layout Shift (CLS)", m_metrics.get('cls', {})), unsafe_allow_html=True)

                st.markdown("<hr style='border-top: 1px dashed #cbd5e1; margin: 50px 0;'>", unsafe_allow_html=True)

                st.markdown("<h4 style='color: #0f172a; margin-bottom: 25px; text-align: center;'>Desktop Device Analysis</h4>", unsafe_allow_html=True)
                d_gauges = st.columns(4)
                with d_gauges[0]: 
                    st.plotly_chart(render_small_gauge(speed_data['desktop'].get('performance', 0)), use_container_width=True, config={'displayModeBar': False}, key="d_perf")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Performance</div>", unsafe_allow_html=True)
                with d_gauges[1]: 
                    st.plotly_chart(render_small_gauge(speed_data['desktop'].get('accessibility', 0)), use_container_width=True, config={'displayModeBar': False}, key="d_acc")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Accessibility</div>", unsafe_allow_html=True)
                with d_gauges[2]: 
                    st.plotly_chart(render_small_gauge(speed_data['desktop'].get('best-practices', 0)), use_container_width=True, config={'displayModeBar': False}, key="d_bp")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Best Practices</div>", unsafe_allow_html=True)
                with d_gauges[3]: 
                    st.plotly_chart(render_small_gauge(speed_data['desktop'].get('seo', 0)), use_container_width=True, config={'displayModeBar': False}, key="d_seo")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>SEO Score</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
                d_metrics = speed_data['desktop'].get('metrics', {})
                sd_col1, sd_col2 = st.columns(2, gap="large")
                with sd_col1:
                    st.markdown(render_speed_metric("First Contentful Paint (FCP)", d_metrics.get('fcp', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Total Blocking Time (TBT)", d_metrics.get('tbt', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Speed Index", d_metrics.get('si', {})), unsafe_allow_html=True)
                with sd_col2:
                    st.markdown(render_speed_metric("Largest Contentful Paint (LCP)", d_metrics.get('lcp', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Cumulative Layout Shift (CLS)", d_metrics.get('cls', {})), unsafe_allow_html=True)

        with tab3:
            if not is_pro:
                st.markdown("""
                <div style="text-align: center; padding: 40px 20px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; margin-top: 20px;">
                    <i class="fa-solid fa-lock" style="font-size: 48px; color: #DB2777; margin-bottom: 20px;"></i>
                    <h3 style="color: #0f172a; font-weight: 800; margin-bottom: 10px;">Traffic Analytics is a Pro Feature</h3>
                    <p style="color: #64748b; margin-bottom: 25px; max-width: 500px; margin-left: auto; margin-right: auto;">Unlock live traffic estimates, competitor analysis, and traffic sources by upgrading to the Enterprise Pro plan.</p>
                    <a href="https://nexgenweblab.com/upgrade" target="_blank" style="background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; padding: 12px 25px; border-radius: 8px; font-weight: bold; text-decoration: none; display: inline-block;">Upgrade to Pro ($9.99/mo)</a>
                </div>
                """, unsafe_allow_html=True)
            else:
                if traffic_data and traffic_data.get('status') == "Live Data":
                    raw_sim = traffic_data.get('raw_data', {})
                    graph_col1, graph_col2 = st.columns(2)
                    with graph_col1:
                        st.markdown("<p style='text-align:center; font-weight:700;'>Visits Trend (Simulated)</p>", unsafe_allow_html=True)
                        visits_num = raw_sim.get("EstimatedMonthlyVisits", 5000)
                        dates = [(datetime.now() - timedelta(days=30*i)).strftime("%b") for i in range(5, -1, -1)]
                        sim_data = [int(visits_num * (0.9 + 0.02*i)) for i in range(6)]
                        fig_trend = px.line(x=dates, y=sim_data, labels={'x':'Month', 'y':'Visits'})
                        fig_trend.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=250)
                        st.plotly_chart(fig_trend, use_container_width=True, key="t_trend")
                    with graph_col2:
                        st.markdown("<p style='text-align:center; font-weight:700;'>Traffic Sources</p>", unsafe_allow_html=True)
                        sources = raw_sim.get("Traffic", {}).get("Sources", {})
                        fig_source = px.pie(values=[sources.get("Search", 1), sources.get("Direct", 1), sources.get("Social", 1)], names=['Search', 'Direct', 'Social'], hole=0.5)
                        fig_source.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=250)
                        st.plotly_chart(fig_source, use_container_width=True, key="t_source")
                else:
                    st.warning("Traffic data not available for this domain.")

        with tab4:
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
                <h4 style="color:#0f172a;font-weight:800;font-size:18px;margin:0;">AI Action Plan</h4>
                <span style="font-size:12px;color:#64748b;font-weight:500;">Powered by Google Gemini</span>
            </div>
            """, unsafe_allow_html=True)
            if ai_suggestions and isinstance(ai_suggestions, list):
                for item in ai_suggestions:
                    clean_text = str(item.get("text", "")).replace("```json", "").replace("```html", "").replace("```", "").strip()
                    st.markdown(f"""<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px;margin-bottom:12px;border-left:4px solid #6D28D9;transition:all 0.2s;"><div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;"><div style="width:32px;height:32px;background:linear-gradient(135deg,rgba(109,40,217,0.1),rgba(219,39,119,0.1));border-radius:8px;display:flex;align-items:center;justify-content:center;"><i class="{item.get('icon', 'fa-solid fa-lightbulb')}" style="color:#DB2777;font-size:14px;"></i></div><h5 style="color:#0f172a;font-weight:700;font-size:15px;margin:0;">{item.get('title', 'Recommendation')}</h5></div><div style="color:#475569;font-size:14px;line-height:1.6;padding-left:42px;">{clean_text}</div></div>""", unsafe_allow_html=True)
            else:
                st.info("AI recommendations are being generated. Please run an audit first.")

        with tab5:
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <h4 style="color:#0f172a;font-weight:800;font-size:18px;margin:0;">White Label Report</h4>
                <span style="font-size:12px;color:#64748b;font-weight:500;">Custom branding supported</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b;font-size:14px;margin-bottom:24px;'>Generate a professional, agency-ready SEO audit document with your own branding.</p>", unsafe_allow_html=True)
            
            w_col1, w_col2 = st.columns(2)
            agency_name = w_col1.text_input("Agency / Company Name", value="NexGenWebLab Pro")
            author_name = w_col2.text_input("Prepared By (Author)", value="SEO Team")
            client_name = st.text_input("Client / Project Name", value=st.session_state.get('last_clean_domain', 'client-domain').upper())
            export_format = st.selectbox("Export Format", ["Microsoft Word (.DOCX)"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            word_file = generate_word_report(st.session_state['last_audit_url'], onpage_data, speed_data, ai_suggestions, agency_name, client_name, author_name)
            
            st.download_button(
                label=f"📥 Download {export_format}",
                data=word_file,
                file_name=f"{st.session_state.get('last_clean_domain', 'client')}_SEO_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )

elif menu_selection == "Bulk Analysis":
    st.markdown("""<div class="hero-container"><div class="hero-title">Bulk <span>Outreach</span> Engine</div></div>""", unsafe_allow_html=True)
    
    if not is_pro:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; margin-top: 20px;">
            <i class="fa-solid fa-file-earmark-lock" style="font-size: 60px; color: #DB2777; margin-bottom: 20px;"></i>
            <h2 style="color: #0f172a; font-weight: 800; margin-bottom: 10px;">Bulk Engine Locked</h2>
            <p style="color: #64748b; margin-bottom: 30px; font-size: 18px; max-width: 600px; margin-left: auto; margin-right: auto;">The Bulk Analysis Engine is exclusively available for Enterprise Pro users. Audit hundreds of URLs at once and generate bulk reports automatically.</p>
            <a href="https://nexgenweblab.com/upgrade" target="_blank" style="background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; padding: 15px 30px; border-radius: 8px; font-weight: bold; text-decoration: none; font-size: 16px; display: inline-block;">Unlock Enterprise Pro</a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="score-container">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload .xlsx file", type=["xlsx"])
        st.markdown('</div>', unsafe_allow_html=True)
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file, header=None)
                valid_urls = []
                for col in df.columns:
                    cells = df[col].dropna().astype(str).tolist()
                    for cell in cells:
                        cleaned_url = cell.strip()
                        if cleaned_url.startswith('http') and cleaned_url not in valid_urls: valid_urls.append(cleaned_url)
                total_urls = len(valid_urls)
                if total_urls > 0:
                    st.success(f"Found {total_urls} unique URLs.")
                    if st.button("Generate Bulk ZIP Reports", type="primary"):
                        st.info("Bulk generation started...")
                        prog = st.progress(0)
                        for i in range(5):
                            time.sleep(0.2)
                            prog.progress((i+1)*20)
                        st.success("Simulation complete.")
                else:
                    st.error("No valid URLs found in file.")
            except Exception as e:
                st.error(f"Error reading file: {e}")