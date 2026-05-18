import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np
from datetime import datetime

def create_score_gauge(score, size=(2, 2)):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 80 else "#10b981"
    label_color = "#0f172a"
    
    fig, ax = plt.subplots(figsize=size)
    ax.set_aspect('equal')
    ax.axis('off')
    
    theta = np.linspace(0.75 * np.pi, 0.25 * np.pi, 100)
    theta_filled = np.linspace(0.75 * np.pi, 0.75 * np.pi + (score / 100) * 1.5 * np.pi, 50)
    
    ax.plot(np.cos(theta), np.sin(theta), color='#e2e8f0', linewidth=12, solid_capstyle='round')
    ax.plot(np.cos(theta_filled), np.sin(theta_filled), color=color, linewidth=12, solid_capstyle='round')
    
    ax.text(0, -0.15, f'{score}', ha='center', va='center', fontsize=36, fontweight='bold', color=label_color, family='sans-serif')
    ax.text(0, -0.38, 'Score', ha='center', va='center', fontsize=12, color='#64748b', family='sans-serif')
    
    plt.tight_layout(pad=0.5)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=True, bbox_inches='tight', dpi=150)
    plt.close(fig)
    img_stream.seek(0)
    return base64.b64encode(img_stream.read()).decode()

def create_bar_chart(data, title, color="#6D28D9", size=(6, 3)):
    if not data:
        return None
    
    months = [d.get('month', '') for d in data]
    values = [d.get('visits', 0) for d in data]
    
    fig, ax = plt.subplots(figsize=size)
    bars = ax.bar(months, values, color=color, edgecolor='white', linewidth=1.5, width=0.7)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.02,
                   f'{val:,}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#475569')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e2e8f0')
    ax.spines['bottom'].set_color('#e2e8f0')
    ax.tick_params(colors='#64748b', labelsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold', color='#0f172a', pad=10)
    ax.set_facecolor('#fafafa')
    fig.patch.set_facecolor('#fafafa')
    
    plt.tight_layout(pad=1)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=False, bbox_inches='tight', dpi=100)
    plt.close(fig)
    img_stream.seek(0)
    return base64.b64encode(img_stream.read()).decode()

def create_pie_chart(data, title, colors=["#6D28D9", "#DB2777", "#F59E0B", "#10B981"]):
    if not data:
        return None
    
    labels = [d.get('name', d.get('label', 'Unknown')) for d in data]
    values = [d.get('value', 0) for d in data]
    
    fig, ax = plt.subplots(figsize=(4, 4))
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                       colors=colors[:len(data)], startangle=90,
                                       wedgeprops=dict(width=0.5, edgecolor='white'))
    for text in texts:
        text.set_fontsize(10)
        text.set_color('#475569')
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')
        autotext.set_color('white')
    
    ax.set_title(title, fontsize=11, fontweight='bold', color='#0f172a', pad=10)
    fig.patch.set_facecolor('white')
    
    plt.tight_layout(pad=1)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=False, bbox_inches='tight', dpi=100)
    plt.close(fig)
    img_stream.seek(0)
    return base64.b64encode(img_stream.read()).decode()

def generate_html_report(url, onpage_data, speed_data, traffic_data, ai_suggestions, 
                        agency_name="NexGenWebLab", client_name="Client", 
                        author_name="SEO Team", logo_url="", custom_css=""):
    
    mobile_score = speed_data.get('mobile', {}).get('performance', 0) if speed_data else 0
    desktop_score = speed_data.get('desktop', {}).get('performance', 0) if speed_data else 0
    avg_score = (mobile_score + desktop_score) // 2
    
    mobile_gauge = create_score_gauge(mobile_score)
    desktop_gauge = create_score_gauge(desktop_score)
    overall_gauge = create_score_gauge(avg_score)
    
    monthly_chart = None
    if traffic_data and traffic_data.get('monthly_visits_list'):
        monthly_chart = create_bar_chart(traffic_data['monthly_visits_list'], 'Monthly Traffic Trend', '#6D28D9')
    
    sources = []
    if traffic_data:
        if traffic_data.get('search_traffic') != 'N/A':
            sources.append({'name': 'Organic Search', 'value': float(traffic_data.get('search_traffic', '0').replace('%', ''))})
        if traffic_data.get('direct_traffic') != 'N/A':
            sources.append({'name': 'Direct', 'value': float(traffic_data.get('direct_traffic', '0').replace('%', ''))})
        if traffic_data.get('social_traffic') != 'N/A':
            sources.append({'name': 'Social Media', 'value': float(traffic_data.get('social_traffic', '0').replace('%', ''))})
        if traffic_data.get('referral_traffic') != 'N/A':
            sources.append({'name': 'Referral', 'value': float(traffic_data.get('referral_traffic', '0').replace('%', ''))})
    
    sources_chart = create_pie_chart(sources, 'Traffic Sources') if sources else None
    
    onpage_items = [
        ('Title Tag', onpage_data.get('title', 'Missing'), onpage_data.get('title', '') != 'Missing'),
        ('Meta Description', onpage_data.get('description', 'Missing'), onpage_data.get('description', '') != 'Missing'),
        ('H1 Headings', ', '.join(onpage_data.get('h1', ['Missing']))[:100], len(onpage_data.get('h1', [])) > 0),
        ('Word Count', str(onpage_data.get('word_count', 0)) + ' words', onpage_data.get('word_count', 0) > 300),
        ('HTTPS/SSL', onpage_data.get('is_https', 'No'), onpage_data.get('is_https', '') == 'Yes'),
        ('Schema Markup', onpage_data.get('schema', 'Missing'), onpage_data.get('schema', '') != 'Missing'),
        ('Canonical URL', onpage_data.get('canonical', 'Missing'), onpage_data.get('canonical', '') != 'Missing'),
        ('Missing ALT Images', str(onpage_data.get('missing_alt', 0)) + ' images', onpage_data.get('missing_alt', 0) == 0),
        ('HTML Size', str(onpage_data.get('html_size_kb', 0)) + ' KB', onpage_data.get('html_size_kb', 0) < 150),
        ('Response Time', str(onpage_data.get('response_time', 0)) + 's', onpage_data.get('response_time', 0) < 1),
    ]
    
    ai_items = []
    if ai_suggestions and isinstance(ai_suggestions, list):
        for item in ai_suggestions[:5]:
            ai_items.append({
                'title': item.get('title', 'Recommendation'),
                'text': item.get('text', '')
            })
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Audit Report - {client_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 20px; }}
        
        .report-header {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; padding: 40px; border-radius: 16px; margin-bottom: 30px; position: relative; overflow: hidden; }}
        .report-header::before {{ content: ''; position: absolute; top: -50%; right: -20%; width: 400px; height: 400px; background: rgba(109, 40, 217, 0.15); border-radius: 50%; }}
        .report-header::after {{ content: ''; position: absolute; bottom: -30%; left: -10%; width: 300px; height: 300px; background: rgba(219, 39, 119, 0.1); border-radius: 50%; }}
        .header-content {{ position: relative; z-index: 1; }}
        .agency-name {{ font-size: 14px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.8; margin-bottom: 8px; }}
        .report-title {{ font-size: 28px; font-weight: 700; margin-bottom: 20px; }}
        .report-meta {{ display: flex; gap: 30px; font-size: 13px; opacity: 0.9; }}
        .report-meta span {{ display: flex; align-items: center; gap: 6px; }}
        
        .scores-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }}
        .score-card {{ background: white; border-radius: 12px; padding: 24px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
        .score-card h4 {{ font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }}
        .score-card img {{ max-width: 120px; margin: 0 auto; }}
        
        .section {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
        .section-title {{ font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #e2e8f0; display: flex; align-items: center; gap: 10px; }}
        .section-title::before {{ content: ''; width: 4px; height: 20px; background: linear-gradient(180deg, #6D28D9, #DB2777); border-radius: 2px; }}
        
        .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
        .metric-box {{ background: #f8fafc; border-radius: 10px; padding: 18px; text-align: center; }}
        .metric-value {{ font-size: 22px; font-weight: 700; color: #1e293b; }}
        .metric-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
        
        .checklist {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
        .check-item {{ display: flex; align-items: flex-start; gap: 12px; padding: 14px; background: #f8fafc; border-radius: 8px; }}
        .check-icon {{ width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }}
        .check-icon.pass {{ background: #dcfce7; color: #16a34a; }}
        .check-icon.fail {{ background: #fee2e2; color: #dc2626; }}
        .check-icon.warn {{ background: #fef3c7; color: #d97706; }}
        .check-text {{ font-size: 14px; color: #475569; }}
        .check-label {{ font-weight: 600; color: #1e293b; }}
        .check-value {{ font-size: 12px; color: #64748b; margin-top: 2px; }}
        
        .charts-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }}
        .chart-box {{ background: #f8fafc; border-radius: 10px; padding: 20px; }}
        .chart-title {{ font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 15px; text-align: center; }}
        .chart-box img {{ width: 100%; border-radius: 8px; }}
        
        .ai-cards {{ display: grid; gap: 15px; }}
        .ai-card {{ background: linear-gradient(135deg, #f5f3ff, #fdf2f8); border-radius: 10px; padding: 20px; border-left: 4px solid #6D28D9; }}
        .ai-card h5 {{ font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 8px; }}
        .ai-card p {{ font-size: 13px; color: #64748b; line-height: 1.6; }}
        
        .keywords-table {{ width: 100%; border-collapse: collapse; }}
        .keywords-table th {{ background: #f1f5f9; padding: 12px 16px; text-align: left; font-size: 12px; text-transform: uppercase; color: #64748b; letter-spacing: 1px; }}
        .keywords-table td {{ padding: 12px 16px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
        .keywords-table tr:hover {{ background: #f8fafc; }}
        
        .footer {{ text-align: center; padding: 30px; color: #64748b; font-size: 12px; }}
        .footer-brand {{ font-weight: 600; color: #6D28D9; }}
        
        @media print {{ 
            body {{ background: white; }}
            .section {{ box-shadow: none; border: 1px solid #e2e8f0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <div class="header-content">
                <div class="agency-name">{agency_name}</div>
                <h1 class="report-title">Technical SEO Audit Report</h1>
                <div class="report-meta">
                    <span><strong>URL:</strong> {url}</span>
                    <span><strong>Client:</strong> {client_name}</span>
                    <span><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</span>
                </div>
            </div>
        </div>
        
        <div class="scores-grid">
            <div class="score-card">
                <h4>Overall Score</h4>
                <img src="data:image/png;base64,{overall_gauge}" alt="Overall Score">
            </div>
            <div class="score-card">
                <h4>Mobile Performance</h4>
                <img src="data:image/png;base64,{mobile_gauge}" alt="Mobile Score">
            </div>
            <div class="score-card">
                <h4>Desktop Performance</h4>
                <img src="data:image/png;base64,{desktop_gauge}" alt="Desktop Score">
            </div>
        </div>
        
        <div class="section">
            <h3 class="section-title">Key Metrics</h3>
            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-value">{onpage_data.get('title', 'Missing')[:30] if onpage_data.get('title', '') != 'Missing' else 'Missing'}</div>
                    <div class="metric-label">Title</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{onpage_data.get('word_count', 0)}</div>
                    <div class="metric-label">Word Count</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{onpage_data.get('missing_alt', 0)}</div>
                    <div class="metric-label">Missing ALTs</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{traffic_data.get('global_rank', 'N/A') if traffic_data else 'N/A'}</div>
                    <div class="metric-label">Global Rank</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{traffic_data.get('monthly_visits', 'N/A') if traffic_data else 'N/A'}</div>
                    <div class="metric-label">Monthly Visits</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{traffic_data.get('bounce_rate', 'N/A') if traffic_data else 'N/A'}</div>
                    <div class="metric-label">Bounce Rate</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{onpage_data.get('is_https', 'No')}</div>
                    <div class="metric-label">HTTPS</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{onpage_data.get('response_time', 0):.2f}s</div>
                    <div class="metric-label">Load Time</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3 class="section-title">On-Page SEO Checklist</h3>
            <div class="checklist">'''

    for label, value, is_pass in onpage_items:
        icon_class = 'pass' if is_pass else 'fail'
        icon_char = '✓' if is_pass else '✗'
        html += f'''
                <div class="check-item">
                    <div class="check-icon {icon_class}">{icon_char}</div>
                    <div class="check-text">
                        <div class="check-label">{label}</div>
                        <div class="check-value">{value}</div>
                    </div>
                </div>'''

    html += '''
            </div>
        </div>'''

    if monthly_chart or sources_chart:
        html += '''
        <div class="section">
            <h3 class="section-title">Traffic Analysis</h3>
            <div class="charts-row">'''
        if monthly_chart:
            html += f'<div class="chart-box"><div class="chart-title">Monthly Traffic Trend</div><img src="data:image/png;base64,{monthly_chart}" alt="Monthly Traffic"></div>'
        if sources_chart:
            html += f'<div class="chart-box"><div class="chart-title">Traffic Sources</div><img src="data:image/png;base64,{sources_chart}" alt="Traffic Sources"></div>'
        html += '''
            </div>
        </div>'''

    if ai_items:
        html += '''
        <div class="section">
            <h3 class="section-title">AI Strategic Recommendations</h3>
            <div class="ai-cards">'''
        for item in ai_items:
            html += f'''
                <div class="ai-card">
                    <h5>{item['title']}</h5>
                    <p>{item['text']}</p>
                </div>'''
        html += '''
            </div>
        </div>'''

    if traffic_data and traffic_data.get('top_keywords'):
        html += '''
        <div class="section">
            <h3 class="section-title">Top Organic Keywords</h3>
            <table class="keywords-table">
                <thead>
                    <tr>
                        <th>Keyword</th>
                        <th>Monthly Visits</th>
                        <th>Position</th>
                    </tr>
                </thead>
                <tbody>'''
        for kw in traffic_data['top_keywords'][:10]:
            html += f'''
                    <tr>
                        <td>{kw.get('keyword', 'N/A')}</td>
                        <td>{kw.get('visits', 0):,}</td>
                        <td>#{kw.get('position', 0)}</td>
                    </tr>'''
        html += '''
                </tbody>
            </table>
        </div>'''

    html += f'''
        <div class="footer">
            <p>Generated by <span class="footer-brand">{agency_name}</span> | NexGenWebLab SEO Platform</p>
            <p style="margin-top: 8px;">Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>'''

    return html.encode()

def generate_html_report_single(url, onpage_data, speed_data, traffic_data, ai_suggestions,
                                  agency_name, client_name, author_name, logo_url="", custom_css=""):
    return generate_html_report(url, onpage_data, speed_data, traffic_data, ai_suggestions,
                                agency_name, client_name, author_name, logo_url, custom_css)

def generate_html_report_bulk(reports_data, agency_name="NexGenWebLab"):
    individual_reports = []
    for rd in reports_data:
        html = generate_html_report(
            url=rd.get('url', ''),
            onpage_data=rd.get('onpage_data', {}),
            speed_data=rd.get('speed_data', {}),
            traffic_data=rd.get('traffic_data', {}),
            ai_suggestions=rd.get('ai_suggestions', []),
            agency_name=agency_name,
            client_name=rd.get('client_name', 'Client'),
            author_name=rd.get('author_name', 'SEO Team')
        )
        individual_reports.append(html.decode('utf-8'))
    
    combined_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Bulk SEO Report - {agency_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f8fafc; }}
        .bulk-header {{ background: linear-gradient(135deg, #1e293b, #334155); color: white; padding: 40px; text-align: center; margin-bottom: 40px; }}
        .bulk-header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .bulk-header p {{ opacity: 0.8; }}
        .report-summary {{ max-width: 1100px; margin: 0 auto 40px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
        .summary-card {{ background: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
        .summary-card h3 {{ font-size: 36px; font-weight: 700; color: #6D28D9; }}
        .summary-card p {{ color: #64748b; font-size: 14px; }}
        .individual-report {{ max-width: 1100px; margin: 0 auto 40px; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
        .report-banner {{ background: linear-gradient(135deg, #6D28D9, #DB2777); color: white; padding: 20px 30px; font-weight: 600; font-size: 18px; }}
    </style>
</head>
<body>
    <div class="bulk-header">
        <h1>Bulk SEO Audit Report</h1>
        <p>{agency_name} | {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
    <div class="report-summary">
        <div class="summary-card">
            <h3>{len(reports_data)}</h3>
            <p>Total Audits</p>
        </div>
        <div class="summary-card">
            <h3>{sum(1 for r in reports_data if r.get('speed_data', {}).get('mobile', {}).get('performance', 0) >= 80)}</h3>
            <p>Passing Core Web Vitals</p>
        </div>
        <div class="summary-card">
            <h3>{sum(r.get('onpage_data', {}).get('missing_alt', 0) for r in reports_data)}</h3>
            <p>Total Missing ALTs</p>
        </div>
        <div class="summary-card">
            <h3>{sum(1 for r in reports_data if r.get('onpage_data', {}).get('is_https') == 'Yes')}</h3>
            <p>HTTPS Secure</p>
        </div>
    </div>'''

    for i, report_html in enumerate(individual_reports, 1):
        html_stripped = report_html.replace('<body>', '<body>').replace('</body>', '').replace('<html>', '').replace('</html>', '')
        html_stripped = html_stripped.replace('<head>', '<div class="report-page">').replace('</head>', '</div>')
        html_stripped = f'''
        <div class="individual-report">
            <div class="report-banner">Report {i}: {reports_data[i-1].get('url', 'N/A')}</div>
            <div class="report-content">
                {html_stripped}
            </div>
        </div>'''
        combined_html += html_stripped

    combined_html += '''
</body>
</html>'''

    return combined_html.encode()