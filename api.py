import os
import io
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from modules.onpage_scraper import get_basic_onpage
from modules.speed_checker import check_speed
from modules.traffic_checker import get_traffic_data
from modules.ai_analyzer import get_ai_suggestions
from modules.report_export import generate_word_report
from modules.html_report import generate_html_report_single, generate_html_report_bulk, generate_advanced_html_report

load_dotenv()

SPEED_API_KEY = os.getenv("SPEED_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

app = FastAPI(title="NexGenWebLab API")

CORS_ORIGINS = [
    "https://tools.nexgenweblab.com",
    "https://nexgenweblab.com",
    "http://localhost:5173",
    "http://localhost:4173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

class AIRequest(BaseModel):
    onpage_data: dict
    mobile_speed: int = 0
    desktop_speed: int = 0

class ExportRequest(BaseModel):
    url: str
    onpage_data: dict
    speed_data: dict = {}
    traffic_data: dict = {}
    ai_suggestions: list = []
    agency_name: str = "NexGenWebLab Pro"
    client_name: str = "Client"
    author_name: str = "SEO Team"

class HTMLReportRequest(BaseModel):
    url: str
    onpage_data: dict = {}
    speed_data: dict = {}
    traffic_data: dict = {}
    ai_suggestions: list = []
    agency_name: str = "NexGenWebLab"
    client_name: str = "Client"
    author_name: str = "SEO Team"
    logo_url: str = ""
    custom_css: str = ""
    primary_color: str = "#6D28D9"
    secondary_color: str = "#DB2777"
    language: str = "en"
    white_label: bool = False

class BulkReportRequest(BaseModel):
    reports: list
    agency_name: str = "NexGenWebLab"

@app.get("/")
def root():
    return {"message": "NexGenWebLab API", "version": "1.0", "docs": "/docs"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/onpage")
def onpage(req: URLRequest):
    return get_basic_onpage(req.url)

@app.post("/api/speed")
def speed(req: URLRequest):
    return check_speed(req.url, SPEED_API_KEY)

@app.post("/api/traffic")
def traffic(req: URLRequest):
    return get_traffic_data(req.url, RAPIDAPI_KEY)

@app.post("/api/ai")
def ai(req: AIRequest):
    seo_data = {**req.onpage_data, "mobile_speed": req.mobile_speed, "desktop_speed": req.desktop_speed}
    return get_ai_suggestions(seo_data, GEMINI_API_KEY)

@app.post("/api/export")
def export_report(req: ExportRequest):
    try:
        docx_bytes = generate_word_report(
            url=req.url,
            onpage_data=req.onpage_data or {},
            speed_data=req.speed_data or {},
            traffic_data=req.traffic_data or {},
            ai_suggestions=req.ai_suggestions or [],
            agency_name=req.agency_name or "NexGenWebLab",
            client_name=req.client_name or "Client",
            author_name=req.author_name or "SEO Team",
        )
        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={req.client_name.replace(' ', '_') if req.client_name else 'SEO_Report'}_SEO_Report.docx"},
        )
    except Exception as e:
        print(f"[ERROR] Export failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e), "detail": traceback.format_exc()}, status_code=500)

@app.post("/api/export/html")
def export_html_report(req: HTMLReportRequest):
    html_bytes = generate_html_report_single(
        url=req.url,
        onpage_data=req.onpage_data,
        speed_data=req.speed_data,
        traffic_data=req.traffic_data,
        ai_suggestions=req.ai_suggestions,
        agency_name=req.agency_name,
        client_name=req.client_name,
        author_name=req.author_name,
        logo_url=req.logo_url,
        custom_css=req.custom_css,
    )
    return StreamingResponse(
        io.BytesIO(html_bytes),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename={req.client_name.replace(' ', '_')}_SEO_Report.html"},
    )

@app.post("/api/export/html/preview")
def preview_html_report(req: HTMLReportRequest):
    try:
        logo_base64 = None
        if req.logo_url:
            try:
                import base64 as b64
                import requests as req_lib
                resp = req_lib.get(req.logo_url, timeout=10)
                if resp.ok:
                    logo_base64 = b64.b64encode(resp.content).decode()
            except Exception as e:
                print(f"Logo fetch error: {e}")
        
        html_bytes = generate_advanced_html_report(
            url=req.url,
            onpage_data=req.onpage_data,
            speed_data=req.speed_data or {},
            traffic_data=req.traffic_data or {},
            ai_suggestions=req.ai_suggestions or [],
            agency_name=req.agency_name,
            client_name=req.client_name,
            author_name=req.author_name,
            logo_base64=logo_base64,
            custom_css=req.custom_css or "",
            primary_color=req.primary_color,
            secondary_color=req.secondary_color,
            language=req.language,
            white_label=req.white_label,
        )
        html_content = html_bytes.decode('utf-8') if isinstance(html_bytes, bytes) else html_bytes
        return HTMLResponse(content=html_content)
    except Exception as e:
        error_msg = str(e)
        try:
            import traceback
            error_msg += "\n" + traceback.format_exc()
        except:
            pass
        content = error_msg[:2000]
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='replace')
        return HTMLResponse(content=f"<html><body><h1>Error generating report</h1><p style='font-family:monospace;white-space:pre-wrap;'>{content}</p></body></html>", status_code=500)

@app.post("/api/export/bulk/html")
def export_bulk_html_report(req: BulkReportRequest):
    combined_html = generate_html_report_bulk(
        reports_data=req.reports,
        agency_name=req.agency_name,
    )
    return StreamingResponse(
        io.BytesIO(combined_html),
        media_type="text/html",
        headers={"Content-Disposition": "attachment; filename=bulk_seo_report.html"},
    )

@app.get("/api/report-template")
def get_report_template():
    template = {
        "sections": [
            {"id": "header", "name": "Report Header", "enabled": True},
            {"id": "scores", "name": "Performance Scores", "enabled": True},
            {"id": "metrics", "name": "Key Metrics", "enabled": True},
            {"id": "onpage", "name": "On-Page SEO", "enabled": True},
            {"id": "speed", "name": "Core Web Vitals", "enabled": True},
            {"id": "traffic", "name": "Traffic Analysis", "enabled": True},
            {"id": "ai", "name": "AI Recommendations", "enabled": True},
            {"id": "keywords", "name": "Top Keywords", "enabled": True},
        ],
        "customizations": {
            "logo_url": "",
            "primary_color": "#6D28D9",
            "secondary_color": "#DB2777",
            "agency_name": "NexGenWebLab",
            "show_gauges": True,
            "show_charts": True,
            "white_label": False,
        }
    }
    return template