import matplotlib
matplotlib.use('Agg') # Ensures backend rendering without GUI popups
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import datetime
import io

def create_gauge_image(score):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 90 else "#10b981"
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.pie([score, max(100-score, 0)], colors=[color, '#f1f5f9'], startangle=90, counterclock=False, wedgeprops=dict(width=0.25))
    ax.text(0, 0, str(score), ha='center', va='center', fontsize=24, fontweight='bold', color='#0f172a', family='sans-serif')
    plt.axis('off')
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=True, bbox_inches='tight', dpi=150)
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

def create_bar_chart(values, labels, title="Score"):
    fig, ax = plt.subplots(figsize=(4, 2))
    colors = ['#10b981' if v >= 90 else '#f59e0b' if v >= 50 else '#ef4444' for v in values]
    bars = ax.barh(labels, values, color=colors)
    ax.set_xlim(0, 100)
    for bar, val in zip(bars, values):
        ax.text(val + 2, bar.get_y() + bar.get_height()/2, f'{val}', va='center', fontsize=10)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=True, bbox_inches='tight', dpi=150)
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

def generate_word_report(url, onpage_data, speed_data, ai_suggestions, agency_name="SEO Agency", client_name="Client", author_name="SEO Expert"):
    doc = Document()
    doc.sections[0].page_width = Inches(8.5)
    doc.sections[0].page_height = Inches(11)
    
    # --- TITLE PAGE (DARK COVER) ---
    title_section = doc.add_heading('', 0)
    run = title_section.add_run(f'{agency_name}')
    run.font.size = Pt(36)
    run.font.color.rgb = RGBColor(109, 40, 217)
    run.font.bold = True
    title_section.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_heading('', 0)
    run = subtitle.add_run('Technical SEO Audit Report')
    run.font.size = Pt(28)
    run.font.color.rgb = RGBColor(30, 41, 59)
    run.font.bold = True
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph("\n")
    sub = doc.add_heading('', 1)
    run = sub.add_run(f'Prepared for: {client_name}')
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(100, 116, 139)
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph("\n\n")
    
    # Meta info
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Target URL:", url),
        ("Prepared by:", author_name),
        ("Date:", datetime.datetime.now().strftime('%B %d, %Y')),
        ("Report Type:", "Comprehensive SEO Audit"),
    ]
    for i, (label, value) in enumerate(meta_data):
        meta_table.rows[i].cells[0].text = label
        meta_table.rows[i].cells[0].paragraphs[0].runs[0].bold = True
        meta_table.rows[i].cells[1].text = value
    
    doc.add_page_break()

    # --- PERFORMANCE SCORES ---
    doc.add_heading('1. Performance Scores', level=1)
    
    mobile_score = speed_data.get('mobile', {}).get('performance', 0) if speed_data else 0
    desktop_score = speed_data.get('desktop', {}).get('performance', 0) if speed_data else 0
    avg_score = (mobile_score + desktop_score) // 2
    
    scores_table = doc.add_table(rows=1, cols=3)
    scores_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    scores_data = [
        ("Overall Score", str(avg_score)),
        ("Mobile", str(mobile_score)),
        ("Desktop", str(desktop_score)),
    ]
    for i, (label, score) in enumerate(scores_data):
        cell = scores_table.rows[0].cells[i]
        cell.text = f"{label}\n{score}"
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if int(score) >= 90:
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(16, 185, 129)
        elif int(score) >= 50:
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(245, 158, 11)
        else:
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(239, 68, 68)
        cell.paragraphs[0].runs[0].font.size = Pt(24)
        cell.paragraphs[0].runs[0].bold = True
    
    doc.add_paragraph("\n")

    # --- KEY METRICS ---
    doc.add_heading('2. Key Performance Metrics', level=1)
    
    metrics_table = doc.add_table(rows=2, cols=4)
    metrics_data = [
        ["Global Rank", onpage_data.get('is_https', 'N/A')],
        ["Word Count", str(onpage_data.get('word_count', 0))],
        ["Missing ALTs", str(onpage_data.get('missing_alt', 0))],
        ["H1 Headings", str(len(onpage_data.get('h1', [])))],
    ]
    for i, (label, value) in enumerate(metrics_data):
        row = i // 4
        col = i % 4
        metrics_table.rows[row].cells[col].text = f"{label}: {value}"
        metrics_table.rows[row].cells[col].paragraphs[0].runs[0].font.size = Pt(10)
    
    doc.add_paragraph("\n")

    # --- ON-PAGE SEO ---
    doc.add_heading('3. Technical On-Page SEO', level=1)
    
    def add_metric(label, value, passed=True):
        p = doc.add_paragraph()
        p.add_run(f"{'✓' if passed else '✗'} {label}: ").bold = True
        val_str = str(value) if value else "N/A"
        if len(val_str) > 100: val_str = val_str[:97] + "..."
        run = p.add_run(val_str)
        run.font.color.rgb = RGBColor(16, 185, 129) if passed else RGBColor(239, 68, 68)
    
    add_metric('Title Tag', onpage_data.get('title', 'Missing'), bool(onpage_data.get('title')))
    add_metric('Meta Description', onpage_data.get('description', 'Missing'), bool(onpage_data.get('description')))
    add_metric('H1 Headings', ", ".join(onpage_data.get('h1', [])) or 'None', len(onpage_data.get('h1', [])) > 0)
    add_metric('Word Count', f"{onpage_data.get('word_count', 0)} words", onpage_data.get('word_count', 0) >= 300)
    add_metric('Missing Image ALTs', f"{onpage_data.get('missing_alt', 0)} images", onpage_data.get('missing_alt', 0) == 0)
    add_metric('SSL Secure (HTTPS)', onpage_data.get('is_https', 'No'), onpage_data.get('is_https', '') == 'Yes')
    add_metric('Schema Markup', 'Present' if onpage_data.get('schema') else 'Missing', bool(onpage_data.get('schema')))
    add_metric('Canonical URL', onpage_data.get('canonical', 'Not set')[:60], bool(onpage_data.get('canonical')))
    add_metric('Robots Meta', onpage_data.get('meta_robots', 'Not set'), onpage_data.get('meta_robots') != 'noindex')
    
    doc.add_page_break()

    # --- CORE WEB VITALS ---
    doc.add_heading('4. Core Web Vitals & Speed Analysis', level=1)
    
    def render_speed_section(device_name, device_data):
        doc.add_heading(f'{device_name} Performance', level=2)
        score = device_data.get('performance', 0)
        p = doc.add_paragraph()
        run = p.add_run(f"Overall Score: {score}/100")
        run.bold = True
        run.font.size = Pt(16)
        if score >= 90:
            run.font.color.rgb = RGBColor(16, 185, 129)
        elif score >= 50:
            run.font.color.rgb = RGBColor(245, 158, 11)
        else:
            run.font.color.rgb = RGBColor(239, 68, 68)
        
        try:
            gauge_img = create_gauge_image(score)
            doc.add_picture(gauge_img, width=Inches(1.5))
        except Exception as e:
            print(f"[-] Gauge image creation failed: {e}")
        
        raw_metrics = device_data.get('metrics', {})
        metrics_items = [
            ("First Contentful Paint (FCP)", raw_metrics.get('fcp', {}).get('value', 'N/A')),
            ("Largest Contentful Paint (LCP)", raw_metrics.get('lcp', {}).get('value', 'N/A')),
            ("Total Blocking Time (TBT)", raw_metrics.get('tbt', {}).get('value', 'N/A')),
            ("Cumulative Layout Shift (CLS)", raw_metrics.get('cls', {}).get('value', 'N/A')),
            ("Speed Index (SI)", raw_metrics.get('si', {}).get('value', 'N/A')),
        ]
        for label, value in metrics_items:
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(f"{label}: ").bold = True
            p.add_run(str(value))
        doc.add_paragraph()

    if speed_data:
        render_speed_section('Mobile', speed_data.get('mobile', {}))
        render_speed_section('Desktop', speed_data.get('desktop', {}))
    else:
        doc.add_paragraph("Speed data not available. Run a speed audit to generate this section.")

    doc.add_page_break()

    # --- AI RECOMMENDATIONS ---
    doc.add_heading('5. AI Strategic Recommendations', level=1)
    doc.add_paragraph("Based on the technical audit above, here are prioritized recommendations to improve your SEO performance:")
    
    if ai_suggestions and isinstance(ai_suggestions, list):
        for i, item in enumerate(ai_suggestions[:8], 1):
            p = doc.add_paragraph(style='List Number')
            run = p.add_run(f"{item.get('title', 'Recommendation')}: ")
            run.bold = True
            run.font.color.rgb = RGBColor(109, 40, 217)
            p.add_run(str(item.get('text', '')).replace("```", "").strip()[:300])
    else:
        doc.add_paragraph("No AI recommendations available. Ensure your AI module is properly configured.")

    doc.add_page_break()

    # --- FOOTER ---
    footer_para = doc.add_paragraph()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer_para.add_run(f"Generated by {agency_name} | Powered by NexGenWebLab")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(100, 116, 139)
    footer_para.add_run(f"\n{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream.getvalue()