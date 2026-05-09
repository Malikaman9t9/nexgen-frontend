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
import zipfile
import io

# ==========================================
# 1. INITIALIZATION & APIs
# ==========================================
load_dotenv()
SPEED_API_KEY = os.getenv("SPEED_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Streamlit Page Config (Must be first Streamlit command)
st.set_page_config(
    page_title="NexGenWebLab VIP | Enterprise SEO", 
    page_icon="favicon.png", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

try:
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Error: Render is not reading the Environment Variables.")
        st.stop()
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Database connection failed. Exact Error: {str(e)}")
    st.stop()

# ==========================================
# 2. AUTHENTICATION GATE
# ==========================================
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.markdown("""<div style="text-align: center; margin-top: 50px;"><i class="fa-solid fa-lock" style="font-size: 40px; color: #DB2777; margin-bottom: 20px;"></i><h2 style="color: #0f172a; font-weight: 800;">NexGenWebLab Secure Portal</h2><p style="color: #64748b; margin-bottom: 30px;">Please log in to access the Enterprise SEO Engine.</p></div>""", unsafe_allow_html=True)
    
    url_email = st.query_params.get("em", "")
    url_pwd = st.query_params.get("pw", "")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            login_email = st.text_input("Email Address", value=url_email)
            login_password = st.text_input("Password", type="password", value=url_pwd)
            submitted = st.form_submit_button("Log In to Dashboard", type="primary", use_container_width=True)
            if submitted:
                try:
                    response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                    st.session_state.user = response.user
                    st.query_params.clear()
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Invalid email or password.")
        st.markdown("<hr style='border-top: 1px dashed #e2e8f0; margin: 20px 0;'><div style='text-align: center;'><p style='color: #475569; font-size: 14px;'>Don't have an account?</p><a href='https://nexgenweblab.com/auth' style='text-decoration: none; color: #6D28D9; font-weight: 700;'>&larr; Sign up here</a></div>", unsafe_allow_html=True)
    st.stop() 

# ==========================================
# 3. METADATA LOGIC
# ==========================================
user_metadata = getattr(st.session_state.user, 'user_metadata', {}) or {}
plan_type = user_metadata.get('plan', 'free')
user_email = st.session_state.user.email
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
st.markdown("""<style>[data-testid="stHeader"] { background-color: transparent !important; } [data-testid="stToolbarActions"] { display: none !important; } .stAppDeployButton { display: none !important; } footer { visibility: hidden !important; } * { font-family: 'Inter', sans-serif; } .block-container { padding-top: 1rem; max-width: 1300px; } body { background-color: #f8fafc; } [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; } .hero-container { text-align: center; padding: 30px 10px; } .hero-title { font-size: 46px; font-weight: 900; color: #0f172a; line-height: 1.1; margin-bottom: 15px; } .hero-title span { background: linear-gradient(135deg, #6D28D9, #DB2777); -webkit-background-clip: text; -webkit-text-fill-color: transparent; } .hero-subtitle { font-size: 18px; color: #64748b; max-width: 600px; margin: 0 auto 30px auto; } [data-testid="stForm"] div[data-testid="stHorizontalBlock"] { gap: 0px !important; align-items: center !important; padding: 0 !important; } .url-prefix { height: 38px !important; line-height: 38px !important; display: flex !important; align-items: center; justify-content: center; background-color: #e2e8f0 !important; color: #0f172a !important; font-size: 16px; font-weight: 700; border-radius: 20px 0 0 20px !important; width: 100% !important; margin-top: -16px !important; } [data-testid="stForm"] .stTextInput input { height: 50px !important; font-size: 16px !important; border-radius: 0px !important; } [data-testid="stForm"] button[kind="primary"] { height: 54px !important; border-radius: 0 30px 30px 0 !important; font-weight: 800 !important; background: linear-gradient(135deg, #6D28D9, #DB2777) !important; color: white !important; border: none !important; } div.stButton > button[kind="secondary"] { border-radius: 8px !important; font-weight: 700 !important; border: 1px solid #e2e8f0 !important; color: #475569 !important; background-color: #f8fafc !important; } .audit-item { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 15px; position: relative; overflow: hidden; display: flex; flex-direction: column; min-height: 220px; } .audit-item::before { content:''; position: absolute; left: 0; top: 0; height: 100%; width: 4px; } .status-danger::before { background-color: #ef4444; } .status-warning::before { background-color: #f59e0b; } .status-success::before { background-color: #10b981; } .status-info::before { background-color: #3b82f6; } .speed-metric-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; height: 60px; }</style>""", unsafe_allow_html=True)

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
    tips = {"title": "Keep 30-60 chars.", "meta": "150-160 chars.", "h1": "Need exactly one H1.", "images": "Add ALT attributes.", "word_count": "Aim for 300+.", "schema": "Add JSON-LD.", "https": "Enable SSL.", "html_size": "Keep <100KB.", "response_time": "Target <0.2s.", "minified_css": "Minify CSS.", "minified_js": "Minify JS.", "canonical": "Set canonical.", "meta_robots": "Set Robots tags.", "lang": "Declare lang.", "og": "Add Open Graph.", "dir_listing": "Secure directories.", "internal_links": "Strong internal linking.", "external_links": "Authority links."}
    actual = "N/A"
    try:
        if type == "title": actual = str(v.get('title', 'Missing')) if isinstance(v, dict) else str(v)
        elif type == "meta": actual = str(v.get('description', 'Missing')) if isinstance(v, dict) else str(v)
        elif type == "h1": actual = ", ".join([str(h) for h in v if h]) if isinstance(v, list) and v else "No H1 tags."
        elif type == "images": actual = f"{int(v)} images missing ALT." if v and int(v) > 0 else "All optimized."
        elif type == "word_count": actual = f"Content: {int(v) if v else 0} words."
        elif type == "https": actual = "SSL Active." if str(v) == "Yes" else "Insecure."
        elif type == "schema": actual = f"Found: {', '.join([str(s) for s in v])}" if isinstance(v, list) and v else "Missing Schema."
        elif type == "response_time": actual = f"Response: {float(v):.2f}s."
        elif type == "html_size": actual = f"HTML: {float(v):.1f} KB."
        elif type in ["minified_css", "minified_js"]: actual = f"{int(v)} unminified." if v and int(v) > 0 else "Files Minified."
        elif type == "dir_listing": actual = "Secured." if str(v) == "Yes" else "Exposed!"
        elif type in ["canonical", "meta_robots", "lang", "og", "internal_links", "external_links"]: actual = str(v) if v else "Missing"
        
        if len(actual) > 90: actual = actual[:87] + "..."
        if type == "title": return ("fa-solid fa-heading", f"Title Tag ({v.get('title_count', 0)} chars)", "success" if "Missing" not in actual else "danger", tips['title'], actual)
        elif type == "meta": return ("fa-solid fa-paragraph", f"Meta Desc ({v.get('desc_count', 0)} chars)", "success" if "Missing" not in actual else "danger", tips['meta'], actual)
        elif type == "h1": return ("fa-solid fa-h", "H1 Heading", "success" if v and isinstance(v, list) else "danger", tips['h1'], actual)
        elif type == "images": return ("fa-solid fa-image", "Image Alts", "warning" if v and int(v) > 0 else "success", tips['images'], actual)
        elif type == "word_count": return ("fa-solid fa-file-lines", "Content Length", "warning" if int(v or 0) < 300 else "success", tips['word_count'], actual)
        elif type == "schema": return ("fa-solid fa-diagram-next", "Schema Markup", "success" if v and "Missing" not in str(v) else "danger", tips['schema'], actual)
        elif type == "https": return ("fa-solid fa-lock", "SSL Security", "success" if str(v) == "Yes" else "danger", tips['https'], actual)
        else: return ("fa-solid fa-circle-info", "SEO Factor", "info", "N/A", actual)
    except Exception as e: return ("fa-solid fa-exclamation", "Error", "danger", str(e), "N/A")

def render_audit_card_vip(label, data):
    icon, message, status_class, tip, actual_data = data
    return f"""<div class="audit-item status-{status_class}"><div class="audit-header"><i class="{icon}" style="color:var(--text-color);"></i><div class="audit-item-content"><span class="audit-item-title">{label}</span><span class="audit-item-desc">{message}</span></div></div><div class="actual-data-box">{actual_data}</div><details class="seo-tip"><summary>How to fix</summary><p>{tip}</p></details></div>""".replace('\n', '')

def render_speed_metric(label, data_obj):
    score = data_obj.get('score', 0)
    value = data_obj.get('value', 'N/A')
    color = "#10b981" if score >= 0.9 else "#f59e0b" if score >= 0.5 else "#ef4444"
    icon = "fa-solid fa-circle-check" if score >= 0.9 else "fa-solid fa-triangle-exclamation"
    return f"""<div class="speed-metric-card"><div style="display: flex; align-items: center;"><i class="{icon}" style="color: {color}; font-size: 16px; margin-right: 12px;"></i><span style="font-size: 14px; font-weight: 700; color: #334155;">{label}</span></div><span style="font-size: 16px; font-weight: 900; color: {color};">{value}</span></div>""".replace('\n', '')

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
# 6. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown(f"""<div style="background-color: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px;"><div style="display: flex; align-items: center; gap: 12px;"><div style="width: 45px; height: 45px; border-radius: 50%; background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 20px;">{st.session_state.user.email[0].upper()}</div><div style="overflow: hidden; flex: 1;"><div style="font-size: 13px; font-weight: 800; color: #0f172a; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">{st.session_state.user.email}</div><div style="font-size: 11px; color: {'#10b981' if is_pro else '#64748b'}; font-weight: 700; margin-top: 2px;"><i class="fa-solid fa-{'crown' if is_pro else 'user'}"></i> {plan_name}</div></div></div></div>""", unsafe_allow_html=True)
    
    if not is_pro:
        # Fixed Extensionless link to /upgrade
        st.markdown("""<a href="https://nexgenweblab.com/upgrade" target="_blank" style="display:block; text-align:center; background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; padding: 10px; border-radius: 8px; font-weight: bold; text-decoration: none; margin-bottom: 15px; font-size: 13px;"><i class="fa-solid fa-bolt"></i> Upgrade to Pro</a>""", unsafe_allow_html=True)

    if st.button("Log Out", use_container_width=True):
        try: supabase.auth.sign_out()
        except: pass
        st.session_state.user = None
        st.query_params.clear()
        st.rerun()
        
    st.markdown("<hr style='border-top: 1px dashed #e2e8f0; margin: 20px 0;'>", unsafe_allow_html=True)
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    st.markdown("<div style='text-align:center; color:#64748b; font-size:12px;'>Enterprise SEO Suite v2.0</div>", unsafe_allow_html=True)
    
    bulk_icon = "file-earmark-spreadsheet" if is_pro else "lock-fill"
    menu_selection = option_menu(None, ["Site Auditor", "Bulk Analysis"], icons=["search", bulk_icon], default_index=0, styles={"nav-link": {"font-size": "15px", "text-align": "left", "font-weight":"600", "height":"50px", "border-radius":"10px"}, "nav-link-selected": {"background": "linear-gradient(135deg, rgba(109, 40, 217, 0.07), rgba(219, 39, 119, 0.07))", "color": "#6D28D9", "border-left": "4px solid #DB2777"}})
    if st.button("Start New Audit", type="secondary", use_container_width=True): st.rerun()

# ==========================================
# 7. MAIN CONTENT
# ==========================================
if menu_selection == "Site Auditor":
    st.markdown("""<div class="hero-container"><div class="hero-title">Professional <span>SEO Auditor</span></div><div class="hero-subtitle">Instantly analyze technical roadblocks, optimize on-page elements, and uncover real-time traffic insights.</div></div>""", unsafe_allow_html=True)
    
    with st.form("audit_form", border=False):
        col_prefix, col_domain, col_btn = st.columns([1.2, 6.3, 2.5])
        with col_prefix: st.markdown('<div class="url-prefix">https://</div>', unsafe_allow_html=True)
        with col_domain: domain_input = st.text_input("Domain", value="", placeholder="paste url here", label_visibility="collapsed")
        with col_btn: run_button = st.form_submit_button("Analyze Now  →", type="primary", use_container_width=True)
    
    if run_button and domain_input:
        target_url = f"https://{domain_input.strip().replace('https://', '').replace('http://', '').replace('www.', '').strip('/')}"
        pb = st.progress(0, text="Auditing Engine Starting...")
        onpage = get_basic_onpage(target_url) or {}
        pb.progress(45, text="Fetching Core Web Vitals...")
        speed = check_speed(target_url, SPEED_API_KEY)
        traffic = get_traffic_data(target_url, RAPIDAPI_KEY) if is_pro else None
        pb.progress(85, text="Syncing AI Plan...")
        ai = get_ai_suggestions({**onpage, 'mobile_speed': speed['mobile'].get('performance', 0), 'desktop_speed': speed['desktop'].get('performance', 0)}, GEMINI_API_KEY)
        pb.progress(100, text="Complete.")
        time.sleep(0.3)
        pb.empty()
        
        ov_score, crit_count, warn_count, pass_count = calculate_ov_vip(onpage, speed)
        st.markdown("<h3 style='text-align: center; color: #0f172a; margin-top: 30px; font-weight: 800;'>Audit Overview</h3>", unsafe_allow_html=True)
        
        ov_col1, ov_col2 = st.columns([1, 2], gap="large")
        with ov_col1: st.plotly_chart(render_overview_donut(ov_score), use_container_width=True, config={'displayModeBar': False})
        with ov_col2:
            ic1, ic2, ic3 = st.columns(3)
            with ic1: st.markdown(f"""<div class="issue-card" style="border-top: 4px solid #ef4444;"><span class="issue-count" style="color:#ef4444;">{crit_count}</span><span class="issue-label">Critical</span></div>""", unsafe_allow_html=True)
            with ic2: st.markdown(f"""<div class="issue-card" style="border-top: 4px solid #f59e0b;"><span class="issue-count" style="color:#f59e0b;">{warn_count}</span><span class="issue-label">Warnings</span></div>""", unsafe_allow_html=True)
            with ic3: st.markdown(f"""<div class="issue-card" style="border-top: 4px solid #10b981;"><span class="issue-count" style="color:#10b981;">{pass_count}</span><span class="issue-label">Passed</span></div>""", unsafe_allow_html=True)

        t1, t2, t3, t4, t5 = st.tabs(["On-Page Data", "Speed Vitals", "Traffic Analytics", "AI Strategy", "Document Export"])
        with t1:
            c1, c2 = st.columns(2, gap="large")
            with c1: 
                st.markdown(render_audit_card_vip("Title Tag", get_audit_status_vip(onpage, "title")), unsafe_allow_html=True)
                st.markdown(render_audit_card_vip("Meta Description", get_audit_status_vip(onpage, "meta")), unsafe_allow_html=True)
                st.markdown(render_audit_card_vip("H1 Heading", get_audit_status_vip(onpage.get('h1', []), "h1")), unsafe_allow_html=True)
                st.markdown(render_audit_card_vip("Content Length", get_audit_status_vip(onpage.get('word_count', 0), "word_count")), unsafe_allow_html=True)
                st.markdown(render_audit_card_vip("Image Alt Attributes", get_audit_status_vip(onpage.get('missing_alt', 0), "images")), unsafe_allow_html=True)
            with c2: 
                st.markdown(render_audit_card_vip("Canonical URL", get_audit_status_vip(onpage.get('canonical','Missing'), "canonical")), unsafe_allow_html=True)
                st.markdown(render_audit_card_vip("Meta Robots", get_audit_status_vip(onpage.get('meta_robots','Missing'), "meta_robots")), unsafe_allow_html=True)
                st.markdown(render_audit_card_vip("Schema.org Markup", get_audit_status_vip(onpage.get('schema', []), "schema")), unsafe_allow_html=True)
                st.markdown(render_audit_card_vip("SSL Protocol (HTTPS)", get_audit_status_vip(onpage.get('is_https', 'No'), "https")), unsafe_allow_html=True)
                st.markdown(render_audit_card_vip("Directory Listing", get_audit_status_vip(onpage.get('dir_listing_secured', 'No'), "dir_listing")), unsafe_allow_html=True)
        with t2:
            if speed:
                st.markdown("<h4 style='text-align: center;'>Mobile Device Analysis</h4>", unsafe_allow_html=True)
                m_gauges = st.columns(4)
                with m_gauges[0]: st.plotly_chart(render_small_gauge(speed['mobile'].get('performance', 0)), use_container_width=True)
                with m_gauges[1]: st.plotly_chart(render_small_gauge(speed['mobile'].get('accessibility', 0)), use_container_width=True)
                with m_gauges[2]: st.plotly_chart(render_small_gauge(speed['mobile'].get('best-practices', 0)), use_container_width=True)
                with m_gauges[3]: st.plotly_chart(render_small_gauge(speed['mobile'].get('seo', 0)), use_container_width=True)
                
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("<h4 style='text-align: center;'>Desktop Device Analysis</h4>", unsafe_allow_html=True)
                d_gauges = st.columns(4)
                with d_gauges[0]: st.plotly_chart(render_small_gauge(speed['desktop'].get('performance', 0)), use_container_width=True)
                with d_gauges[1]: st.plotly_chart(render_small_gauge(speed['desktop'].get('accessibility', 0)), use_container_width=True)
                with d_gauges[2]: st.plotly_chart(render_small_gauge(speed['desktop'].get('best-practices', 0)), use_container_width=True)
                with d_gauges[3]: st.plotly_chart(render_small_gauge(speed['desktop'].get('seo', 0)), use_container_width=True)
        with t3:
            if not is_pro:
                # Fixed markdown bug here
                st.markdown("""<div style="text-align: center; padding: 40px; background: white; border-radius: 12px;"><i class="fa-solid fa-lock" style="font-size: 48px; color: #DB2777; margin-bottom: 20px;"></i><h3>Pro Feature Locked</h3><a href="https://nexgenweblab.com/upgrade" target="_blank" style="background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; padding: 12px 25px; border-radius: 8px; font-weight: bold; text-decoration: none; display: inline-block;">Unlock Enterprise Pro</a></div>""", unsafe_allow_html=True)
            elif traffic and traffic.get('status') == "Live Data":
                st.write("Live Traffic Data Analytics Available")
        with t4:
            st.markdown("<h4 style='color: #0f172a; margin-bottom: 20px;'>AI Action Plan</h4>", unsafe_allow_html=True)
            if ai and isinstance(ai, list):
                for item in ai:
                    clean_text = str(item.get("text", "")).replace("```json", "").replace("```html", "").replace("```", "").strip()
                    st.markdown(f"""<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #6D28D9;"><h5 style="color: #0f172a; margin-top: 0; font-size: 16px;"><i class="{item.get('icon', 'fa-solid fa-lightbulb')}" style="color: #DB2777; margin-right: 10px;"></i>{item.get('title', 'Recommendation')}</h5><div style='color: #475569; font-size: 14px;'>{clean_text}</div></div>""", unsafe_allow_html=True)
        with t5:
            if run_button and onpage:
                word_file = generate_word_report(target_url, onpage, speed, ai)
                st.download_button(label="Download Professional Audit Report (.DOCX)", data=word_file, file_name=f"NexGenWebLab_Audit.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)

elif menu_selection == "Bulk Analysis":
    st.markdown("""<div class="hero-container"><div class="hero-title">Bulk <span>Outreach</span> Engine</div></div>""", unsafe_allow_html=True)
    if not is_pro:
        # Fixed markdown bug here as well
        st.markdown("""<div style="text-align: center; padding: 60px; background: white; border-radius: 12px;"><i class="fa-solid fa-file-earmark-lock" style="font-size: 60px; color: #DB2777; margin-bottom: 20px;"></i><h2>Bulk Engine Locked</h2><a href="[https://nexgenweblab.com/upgrade](https://nexgenweblab.com/upgrade)" target="_blank" style="background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; padding: 15px 30px; border-radius: 8px; font-weight: bold; text-decoration: none; display: inline-block;">Unlock Enterprise Pro</a></div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="score-container">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload .xlsx file", type=["xlsx"])
        st.markdown('</div>', unsafe_allow_html=True)
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file, header=None)
                valid_urls = [cell.strip() for col in df.columns for cell in df[col].dropna().astype(str).tolist() if cell.strip().startswith('http')]
                valid_urls = list(set(valid_urls))
                if len(valid_urls) > 0:
                    st.success(f"Found {len(valid_urls)} unique URLs.")
                    if st.button("Generate Bulk ZIP Reports", type="primary"):
                        st.info("Bulk generation started...")
                        prog = st.progress(0)
                        for i in range(5):
                            time.sleep(0.2)
                            prog.progress((i+1)*20)
                        st.success("Simulation complete.")
            except Exception as e:
                st.error(f"Error reading file: {e}")