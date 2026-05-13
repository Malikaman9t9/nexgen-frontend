import matplotlib
matplotlib.use('Agg') # Ensures backend rendering without GUI popups
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import datetime
import io

def create_gauge_image(score):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 90 else "#10b981"
    fig, ax = plt.subplots(figsize=(1.5, 1.5))
    ax.pie([score, max(100-score, 0)], colors=[color, '#f1f5f9'], startangle=90, counterclock=False, wedgeprops=dict(width=0.25))
    ax.text(0, 0, str(score), ha='center', va='center', fontsize=20, fontweight='bold', color='#0f172a', family='sans-serif')
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=True, bbox_inches='tight', dpi=150)
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

def generate_word_report(url, onpage_data, speed_data, ai_suggestions, agency_name="SEO Agency", client_name="Client", author_name="SEO Expert"):
    doc = Document()
    
    # --- TITLE PAGE (WHITE LABEL) ---
    title = doc.add_heading(f'{agency_name} - SEO Audit Report', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph("\n")
    sub = doc.add_heading(f'Prepared for: {client_name}', level=1)
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph("\n\n")
    p_details = doc.add_paragraph()
    p_details.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_details.add_run(f"Target URL: {url}\n").bold = True
    p_details.add_run(f"Prepared by: {author_name}\n")
    p_details.add_run(f"Date: {datetime.datetime.now().strftime('%B %d, %Y')}")
    
    doc.add_page_break()

    # --- PAGE 2: ON-PAGE SEO ---
    doc.add_heading('1. Technical On-Page SEO', level=1)
    
    def add_metric(label, value):
        p = doc.add_paragraph()
        p.add_run(f"{label}: ").bold = True
        val_str = str(value) if value else "N/A"
        if len(val_str) > 150: val_str = val_str[:147] + "..."
        p.add_run(val_str)

    add_metric('Title Tag', onpage_data.get('title'))
    add_metric('Meta Description', onpage_data.get('description'))
    add_metric('H1 Headings', ", ".join(onpage_data.get('h1', [])))
    add_metric('Word Count', onpage_data.get('word_count'))
    add_metric('Missing Image ALTs', onpage_data.get('missing_alt'))
    add_metric('SSL Secure (HTTPS)', onpage_data.get('is_https'))
    add_metric('Schema Markup', onpage_data.get('schema'))
    add_metric('Canonical URL', onpage_data.get('canonical'))
    add_metric('Robots Meta', onpage_data.get('meta_robots'))
    
    doc.add_page_break()

    # --- PAGE 3: CORE WEB VITALS ---
    doc.add_heading('2. Core Web Vitals & Speed', level=1)
    
    def render_speed_section(device_name, device_data):
        doc.add_heading(f'{device_name} Analysis', level=2)
        score = device_data.get('performance', 0)
        p = doc.add_paragraph()
        p.add_run(f"Overall Performance Score: {score}/100").bold = True
        
        try:
            gauge_img = create_gauge_image(score)
            doc.add_picture(gauge_img, width=Inches(1.5))
        except Exception as e:
            print(f"[-] Gauge image creation failed: {e}")
            # Continue without gauge image instead of silent failure
        
        raw_metrics = device_data.get('metrics', {})
        doc.add_paragraph(f"First Contentful Paint (FCP): {raw_metrics.get('fcp', {}).get('value', 'N/A')}", style='List Bullet')
        doc.add_paragraph(f"Largest Contentful Paint (LCP): {raw_metrics.get('lcp', {}).get('value', 'N/A')}", style='List Bullet')
        doc.add_paragraph(f"Total Blocking Time (TBT): {raw_metrics.get('tbt', {}).get('value', 'N/A')}", style='List Bullet')
        doc.add_paragraph(f"Cumulative Layout Shift (CLS): {raw_metrics.get('cls', {}).get('value', 'N/A')}", style='List Bullet')
        doc.add_paragraph("\n")

    if speed_data:
        render_speed_section('Mobile', speed_data.get('mobile', {}))
        render_speed_section('Desktop', speed_data.get('desktop', {}))

    doc.add_page_break()

    # --- PAGE 4: AI OVERVIEW ---
    doc.add_heading('3. AI Action Plan & Strategy', level=1)
    doc.add_paragraph("Based on the technical snapshot above, here is the strategic roadmap to resolve these issues:")
    
    if ai_suggestions and isinstance(ai_suggestions, list):
        for item in ai_suggestions:
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(f"{item.get('title', 'Recommendation')}: ").bold = True
            p.add_run(str(item.get('text', '')).replace("```", ""))
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream.getvalue()