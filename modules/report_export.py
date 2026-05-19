import matplotlib
matplotlib.use('Agg') # Ensures backend rendering without GUI popups
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime
import io

PRIMARY_COLOR = RGBColor(109, 40, 217)    # #6D28D9
SECONDARY_COLOR = RGBColor(219, 39, 119)  # #DB2777
SUCCESS_COLOR = RGBColor(16, 185, 129)     # #10b981
WARNING_COLOR = RGBColor(245, 158, 11)     # #f59e0b
DANGER_COLOR = RGBColor(239, 68, 68)       # #ef4444
DARK_COLOR = RGBColor(15, 23, 42)          # #0f172a
SLATE_COLOR = RGBColor(100, 116, 139)      # #64748b

def set_cell_shading(cell, fill_color):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), fill_color)
    cell._tc.get_or_add_tcPr().append(shading)

def create_gauge_image(score):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 90 else "#10b981"
    fig, ax = plt.subplots(figsize=(1.5, 1.5))
    ax.pie([score, max(100-score, 0)], colors=[color, '#f1f5f9'], startangle=90, counterclock=False, wedgeprops=dict(width=0.25))
    ax.text(0, 0, str(score), ha='center', va='center', fontsize=18, fontweight='bold', color='#0f172a', family='sans-serif')
    plt.axis('off')
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=True, bbox_inches='tight', dpi=150)
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

def create_pie_chart(data_dict, title="Traffic Sources"):
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    colors = ['#6D28D9', '#DB2777', '#F59E0B', '#10B981', '#3B82F6'][:len(labels)]
    
    fig, ax = plt.subplots(figsize=(3, 3))
    wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    for autotext in autotexts:
        autotext.set_fontsize(8)
    ax.set_title(title, fontsize=10, fontweight='bold')
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=True, bbox_inches='tight', dpi=150)
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

def create_bar_chart(data_dict, title="Performance"):
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    colors = ['#10b981' if v >= 90 else '#f59e0b' if v >= 50 else '#ef4444' for v in values]
    
    fig, ax = plt.subplots(figsize=(5, 2))
    bars = ax.barh(labels, values, color=colors)
    ax.set_xlim(0, 100)
    for bar, val in zip(bars, values):
        ax.text(min(val + 3, 95), bar.get_y() + bar.get_height()/2, f'{val}', va='center', fontsize=9)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=True, bbox_inches='tight', dpi=150)
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

def generate_word_report(url, onpage_data, speed_data, traffic_data, ai_suggestions, agency_name="SEO Agency", client_name="Client", author_name="SEO Expert"):
    doc = Document()
    doc.sections[0].page_width = Inches(8.5)
    doc.sections[0].page_height = Inches(11)
    
    # --- COVER PAGE (Dark gradient style) ---
    cover_table = doc.add_table(rows=1, cols=1)
    cover_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cover_cell = cover_table.rows[0].cells[0]
    set_cell_shading(cover_cell, '0F172A')  # Dark background
    
    cover_para = cover_cell.paragraphs[0]
    cover_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    run = cover_para.add_run('\n\nTECHNICAL SEO AUDIT REPORT\n\n')
    run.font.size = Pt(32)
    run.font.color.rgb = RGBColor(255, 255, 255)
    run.font.bold = True
    
    run2 = cover_para.add_run(f'{agency_name}\n\n')
    run2.font.size = Pt(18)
    run2.font.color.rgb = PRIMARY_COLOR
    run2.font.bold = True
    
    doc.add_paragraph()
    
    sub_table = doc.add_table(rows=1, cols=1)
    sub_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sub_cell = sub_table.rows[0].cells[0]
    set_cell_shading(sub_cell, '1E293B')
    
    sub_para = sub_cell.paragraphs[0]
    sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run3 = sub_para.add_run(f'Prepared for: {client_name}\n')
    run3.font.size = Pt(16)
    run3.font.color.rgb = RGBColor(255, 255, 255)
    run3.font.bold = True
    
    doc.add_paragraph()
    
    # Meta info box
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.style = 'Table Grid'
    meta_data = [
        ("Target URL:", url),
        ("Prepared by:", author_name),
        ("Date:", datetime.datetime.now().strftime('%B %d, %Y')),
        ("Report Type:", "Comprehensive SEO Audit"),
    ]
    for i, (label, value) in enumerate(meta_data):
        cell = meta_table.rows[i].cells[0]
        cell.text = label
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = PRIMARY_COLOR
        meta_table.rows[i].cells[1].text = value
    
    doc.add_page_break()

    # --- SECTION 1: PERFORMANCE SCORES ---
    heading1 = doc.add_heading('1. Performance Scores', level=1)
    heading1.runs[0].font.color.rgb = DARK_COLOR
    
    p = doc.add_paragraph()
    p.add_run('Performance metrics based on Google Lighthouse analysis').italic = True
    p.runs[0].font.color.rgb = SLATE_COLOR
    
    mobile_score = speed_data.get('mobile', {}).get('performance', 0) if speed_data else 0
    desktop_score = speed_data.get('desktop', {}).get('performance', 0) if speed_data else 0
    avg_score = (mobile_score + desktop_score) // 2
    
    scores_table = doc.add_table(rows=2, cols=3)
    scores_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = ['Overall Score', 'Mobile', 'Desktop']
    for i, h in enumerate(headers):
        cell = scores_table.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = SLATE_COLOR
        set_cell_shading(cell, 'F8FAFC')
    
    scores = [('Overall', avg_score), ('Mobile', mobile_score), ('Desktop', desktop_score)]
    for i, (label, score) in enumerate(scores):
        cell = scores_table.rows[1].cells[i]
        cell.text = str(score)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].runs[0].font.size = Pt(36)
        cell.paragraphs[0].runs[0].bold = True
        if score >= 90:
            cell.paragraphs[0].runs[0].font.color.rgb = SUCCESS_COLOR
        elif score >= 50:
            cell.paragraphs[0].runs[0].font.color.rgb = WARNING_COLOR
        else:
            cell.paragraphs[0].runs[0].font.color.rgb = DANGER_COLOR
    
    # Summary bar
    doc.add_paragraph()
    summary_p = doc.add_paragraph()
    summary_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    onpage_checks = [
        ('Title Tag', bool(onpage_data.get('title'))),
        ('Meta Description', bool(onpage_data.get('description'))),
        ('H1 Headings', len(onpage_data.get('h1', [])) > 0),
        ('Word Count', onpage_data.get('word_count', 0) >= 300),
        ('HTTPS/SSL', onpage_data.get('is_https', '') == 'Yes'),
        ('Schema Markup', bool(onpage_data.get('schema'))),
        ('Canonical URL', bool(onpage_data.get('canonical'))),
        ('Missing ALT Images', onpage_data.get('missing_alt', 0) == 0),
    ]
    passed = sum(1 for _, p in onpage_checks if p)
    failed = sum(1 for _, p in onpage_checks if not p)
    
    summary_run = summary_p.add_run(f'✓ {passed} Passed    ✗ {failed} Issues Found')
    summary_run.font.size = Pt(14)
    summary_run.bold = True
    
    doc.add_page_break()

    # --- SECTION 2: KEY METRICS ---
    heading2 = doc.add_heading('2. Key Performance Metrics', level=1)
    heading2.runs[0].font.color.rgb = DARK_COLOR
    
    metrics_table = doc.add_table(rows=2, cols=4)
    metrics_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    if traffic_data:
        metrics_data = [
            ('Global Rank', traffic_data.get('global_rank', 'N/A')),
            ('Monthly Visits', traffic_data.get('monthly_visits', 'N/A')),
            ('Bounce Rate', traffic_data.get('bounce_rate', 'N/A')),
            ('Pages/Visit', traffic_data.get('pages_per_visit', 'N/A')),
        ]
    else:
        metrics_data = [
            ('Global Rank', 'N/A'),
            ('Monthly Visits', 'N/A'),
            ('Bounce Rate', 'N/A'),
            ('Pages/Visit', 'N/A'),
        ]
    
    for i, (label, value) in enumerate(metrics_data):
        row = i // 4
        col = i % 4
        cell = metrics_table.rows[row].cells[col]
        cell.text = label
        cell.paragraphs[0].runs[0].font.size = Pt(10)
        cell.paragraphs[0].runs[0].font.color.rgb = SLATE_COLOR
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(cell, 'F8FAFC')
    
    doc.add_paragraph()

    # --- SECTION 3: TRAFFIC SOURCES ---
    if traffic_data:
        doc.add_heading('3. Traffic Sources & Off-Page SEO', level=1)
        
        sources_table = doc.add_table(rows=2, cols=4)
        sources_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        source_labels = ['Organic Search', 'Direct', 'Social', 'Referral']
        source_values = [
            traffic_data.get('search_traffic', 'N/A'),
            traffic_data.get('direct_traffic', 'N/A'),
            traffic_data.get('social_traffic', 'N/A'),
            traffic_data.get('referral_traffic', 'N/A'),
        ]
        
        for i, label in enumerate(source_labels):
            cell = sources_table.rows[0].cells[i]
            cell.text = label
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cell.paragraphs[0].runs[0].bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = SLATE_COLOR
            set_cell_shading(cell, 'F5F3FF')
        
        for i, value in enumerate(source_values):
            cell = sources_table.rows[1].cells[i]
            cell.text = value
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cell.paragraphs[0].runs[0].font.size = Pt(18)
            cell.paragraphs[0].runs[0].bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = PRIMARY_COLOR
        
        doc.add_paragraph()

    # --- SECTION 4: ON-PAGE SEO ---
    doc.add_heading('4. Technical On-Page SEO', level=1)
    
    onpage_table = doc.add_table(rows=len(onpage_checks), cols=3)
    onpage_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    header_row = onpage_table.rows[0]
    headers = ['Check Item', 'Status', 'Value']
    for i, h in enumerate(headers):
        cell = header_row.cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = SLATE_COLOR
        set_cell_shading(cell, 'F8FAFC')
    
    check_details = [
        ('Title Tag', onpage_data.get('title', 'Missing')[:50]),
        ('Meta Description', onpage_data.get('description', 'Missing')[:80]),
        ('H1 Headings', f"{len(onpage_data.get('h1', []))} found"),
        ('Word Count', f"{onpage_data.get('word_count', 0)} words"),
        ('Missing Image ALTs', f"{onpage_data.get('missing_alt', 0)} missing"),
        ('SSL Secure (HTTPS)', onpage_data.get('is_https', 'No')),
        ('Schema Markup', 'Present' if onpage_data.get('schema') else 'Missing'),
        ('Canonical URL', onpage_data.get('canonical', 'Not set')[:50]),
    ]
    
    for i, (label, passed_check) in enumerate(onpage_checks):
        row = onpage_table.rows[i + 1]
        
        label_cell = row.cells[0]
        label_cell.text = label
        label_cell.paragraphs[0].runs[0].font.size = Pt(11)
        
        status_cell = row.cells[1]
        status_cell.text = '✓' if passed_check else '✗'
        status_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        status_cell.paragraphs[0].runs[0].font.size = Pt(14)
        status_cell.paragraphs[0].runs[0].bold = True
        status_cell.paragraphs[0].runs[0].font.color.rgb = SUCCESS_COLOR if passed_check else DANGER_COLOR
        
        value_cell = row.cells[2]
        value_cell.text = check_details[i][1]
        value_cell.paragraphs[0].runs[0].font.size = Pt(10)
        value_cell.paragraphs[0].runs[0].font.color.rgb = SLATE_COLOR
    
    doc.add_page_break()

    # --- SECTION 5: CORE WEB VITALS ---
    doc.add_heading('5. Core Web Vitals & Speed Analysis', level=1)
    
    def render_speed_section(device_name, device_data):
        if not device_data:
            return
        doc.add_heading(f'{device_name} Performance', level=2)
        
        score = device_data.get('performance', 0)
        
        # Score display
        score_para = doc.add_paragraph()
        score_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        score_run = score_para.add_run(f'{score}/100')
        score_run.font.size = Pt(48)
        score_run.bold = True
        if score >= 90:
            score_run.font.color.rgb = SUCCESS_COLOR
        elif score >= 50:
            score_run.font.color.rgb = WARNING_COLOR
        else:
            score_run.font.color.rgb = DANGER_COLOR
        
        label_para = doc.add_paragraph()
        label_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if score >= 90:
            label_run = label_para.add_run('Excellent')
        elif score >= 70:
            label_run = label_para.add_run('Good')
        elif score >= 50:
            label_run = label_para.add_run('Needs Work')
        else:
            label_run = label_para.add_run('Poor')
        label_run.font.color.rgb = SLATE_COLOR
        
        try:
            gauge_img = create_gauge_image(score)
            doc.add_picture(gauge_img, width=Inches(1.5))
        except Exception as e:
            print(f"[-] Gauge image creation failed: {e}")
        
        # Metrics table
        raw_metrics = device_data.get('metrics', {})
        metrics_items = [
            ('First Contentful Paint (FCP)', raw_metrics.get('fcp', {}).get('value', 'N/A')),
            ('Largest Contentful Paint (LCP)', raw_metrics.get('lcp', {}).get('value', 'N/A')),
            ('Total Blocking Time (TBT)', raw_metrics.get('tbt', {}).get('value', 'N/A')),
            ('Cumulative Layout Shift (CLS)', raw_metrics.get('cls', {}).get('value', 'N/A')),
            ('Speed Index (SI)', raw_metrics.get('si', {}).get('value', 'N/A')),
        ]
        
        metrics_table = doc.add_table(rows=len(metrics_items), cols=2)
        for i, (label, value) in enumerate(metrics_items):
            metrics_table.rows[i].cells[0].text = label
            metrics_table.rows[i].cells[0].paragraphs[0].runs[0].font.size = Pt(10)
            metrics_table.rows[i].cells[1].text = str(value)
            metrics_table.rows[i].cells[1].paragraphs[0].runs[0].font.size = Pt(10)
            metrics_table.rows[i].cells[1].paragraphs[0].runs[0].bold = True
        
        doc.add_paragraph()

    if speed_data:
        render_speed_section('Mobile', speed_data.get('mobile', {}))
        render_speed_section('Desktop', speed_data.get('desktop', {}))
    else:
        doc.add_paragraph("Speed data not available. Run a speed audit to generate this section.")

    doc.add_page_break()

    # --- SECTION 6: TOP KEYWORDS ---
    if traffic_data and traffic_data.get('top_keywords'):
        doc.add_heading('6. Top Organic Keywords', level=1)
        
        keywords_table = doc.add_table(rows=1 + len(traffic_data['top_keywords']), cols=3)
        keywords_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Header
        headers = ['Keyword', 'Monthly Visits', 'Position']
        for i, h in enumerate(headers):
            cell = keywords_table.rows[0].cells[i]
            cell.text = h
            cell.paragraphs[0].runs[0].bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = SLATE_COLOR
            set_cell_shading(cell, 'F8FAFC')
        
        # Data rows
        for i, kw in enumerate(traffic_data['top_keywords'][:10]):
            row = keywords_table.rows[i + 1]
            row.cells[0].text = kw.get('keyword', 'N/A')
            row.cells[1].text = str(kw.get('visits', 0))
            row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row.cells[2].text = f"#{kw.get('position', 0)}"
            row.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row.cells[2].paragraphs[0].runs[0].font.color.rgb = PRIMARY_COLOR
            row.cells[2].paragraphs[0].runs[0].bold = True
        
        doc.add_paragraph()

    # --- SECTION 7: AI RECOMMENDATIONS ---
    doc.add_heading('7. AI Strategic Recommendations', level=1)
    doc.add_paragraph("Based on the technical audit above, here are prioritized recommendations to improve your SEO performance:")
    
    if ai_suggestions and isinstance(ai_suggestions, list):
        for i, item in enumerate(ai_suggestions[:10], 1):
            p = doc.add_paragraph(style='List Number')
            run = p.add_run(f"{item.get('title', 'Recommendation')}: ")
            run.bold = True
            run.font.color.rgb = PRIMARY_COLOR
            p.add_run(str(item.get('text', '')).replace("```", "").strip()[:400])
    else:
        doc.add_paragraph("No AI recommendations available. Ensure your AI module is properly configured.")

    doc.add_page_break()

    # --- FOOTER ---
    footer_para = doc.add_paragraph()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    line = footer_para.add_run('─' * 60 + '\n')
    line.font.color.rgb = SLATE_COLOR
    
    brand_run = footer_para.add_run(f'Generated by {agency_name} | Powered by NexGenWebLab\n')
    brand_run.font.size = Pt(12)
    brand_run.bold = True
    brand_run.font.color.rgb = PRIMARY_COLOR
    
    date_run = footer_para.add_run(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    date_run.font.size = Pt(10)
    date_run.font.color.rgb = SLATE_COLOR

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream.getvalue()