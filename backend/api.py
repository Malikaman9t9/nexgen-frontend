import os
import io
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from modules.onpage_scraper import get_basic_onpage
from modules.speed_checker import check_speed
from modules.traffic_checker import get_traffic_data
from modules.ai_analyzer import get_ai_suggestions, get_ai_paragraphs
from modules.report_export import generate_word_report
from modules.html_report import generate_html_report_single, generate_html_report_bulk, generate_advanced_html_report

load_dotenv()

SPEED_API_KEY = os.getenv("SPEED_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

app = FastAPI(title="NexGenWebLab API")

CORS_RAW = os.getenv("ALLOWED_ORIGINS")
if CORS_RAW:
    CORS_ORIGINS = [o.strip() for o in CORS_RAW.split(",") if o.strip()]
else:
    CORS_ORIGINS = [
        "https://nexgenweblab.com",
        "https://www.nexgenweblab.com",
        "https://tools.nexgenweblab.com",
        "http://localhost:5173",
        "http://localhost:3000",
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
    ai_paragraphs: dict | None = None
    agency_name: str = "NexGenWebLab"
    client_name: str = "Client"
    author_name: str = "SEO Team"
    logo_url: str = ""
    custom_css: str = ""
    primary_color: str = "#6D28D9"
    secondary_color: str = "#DB2777"
    language: str = "en"
    white_label: bool = False


class AIParagraphsRequest(BaseModel):
    onpage_data: dict
    mobile_speed: int = 0
    desktop_speed: int = 0


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
    if not req.url or not req.url.strip():
        return JSONResponse({"error": "url is required"}, status_code=422)
    try:
        result = get_basic_onpage(req.url.strip())
        if result is None:
            return JSONResponse({"error": "Failed to scrape URL — page unreachable or returned non-200"}, status_code=502)
        return result
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": f"On-page analysis failed: {str(e)}"}, status_code=500)


@app.post("/api/speed")
def speed(req: URLRequest):
    if not req.url or not req.url.strip():
        return JSONResponse({"error": "url is required"}, status_code=422)
    try:
        result = check_speed(req.url.strip(), SPEED_API_KEY)
        if result is None:
            return JSONResponse({"error": "Speed analysis returned no data"}, status_code=502)
        return result
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": f"Speed analysis failed: {str(e)}"}, status_code=500)


@app.post("/api/traffic")
def traffic(req: URLRequest):
    if not req.url or not req.url.strip():
        return JSONResponse({"error": "url is required"}, status_code=422)
    try:
        return get_traffic_data(req.url.strip(), RAPIDAPI_KEY)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": f"Traffic analysis failed: {str(e)}"}, status_code=500)


@app.post("/api/ai")
def ai(req: AIRequest):
    if not req.onpage_data:
        return JSONResponse({"error": "onpage_data is required"}, status_code=422)
    try:
        seo_data = {**req.onpage_data, "mobile_speed": req.mobile_speed, "desktop_speed": req.desktop_speed}
        return get_ai_suggestions(seo_data, GEMINI_API_KEY)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": f"AI analysis failed: {str(e)}"}, status_code=500)


@app.post("/api/ai/paragraphs")
def ai_paragraphs(req: AIParagraphsRequest):
    if not req.onpage_data:
        return JSONResponse({"error": "onpage_data is required"}, status_code=422)
    try:
        seo_data = {**req.onpage_data, "mobile_speed": req.mobile_speed, "desktop_speed": req.desktop_speed}
        return get_ai_paragraphs(seo_data, GEMINI_API_KEY)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": f"AI paragraphs failed: {str(e)}"}, status_code=500)


@app.post("/api/export")
def export_report(req: ExportRequest):
    if not req.url or not req.url.strip():
        return JSONResponse({"error": "url is required"}, status_code=422)
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
        filename = req.client_name.replace(" ", "_") if req.client_name else "SEO_Report"
        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}_SEO_Report.docx"},
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e), "detail": traceback.format_exc()}, status_code=500)


@app.post("/api/export/html")
def export_html_report(req: HTMLReportRequest):
    if not req.url or not req.url.strip():
        return JSONResponse({"error": "url is required"}, status_code=422)
    try:
        html_bytes = generate_html_report_single(
            url=req.url,
            onpage_data=req.onpage_data or {},
            speed_data=req.speed_data or {},
            traffic_data=req.traffic_data or {},
            ai_suggestions=req.ai_suggestions or [],
            agency_name=req.agency_name or "NexGenWebLab",
            client_name=req.client_name or "Client",
            author_name=req.author_name or "SEO Team",
            logo_url=req.logo_url or "",
            custom_css=req.custom_css or "",
        )
        filename = req.client_name.replace(" ", "_") if req.client_name else "SEO_Report"
        return StreamingResponse(
            io.BytesIO(html_bytes),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={filename}_SEO_Report.html"},
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": f"HTML export failed: {str(e)}"}, status_code=500)


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
            url=req.url or "",
            onpage_data=req.onpage_data or {},
            speed_data=req.speed_data or {},
            traffic_data=req.traffic_data or {},
            ai_suggestions=req.ai_suggestions or [],
            ai_paragraphs=req.ai_paragraphs or None,
            agency_name=req.agency_name or "NexGenWebLab",
            client_name=req.client_name or "Client",
            author_name=req.author_name or "SEO Team",
            logo_base64=logo_base64,
            custom_css=req.custom_css or "",
            primary_color=req.primary_color,
            secondary_color=req.secondary_color,
            language=req.language,
            white_label=req.white_label,
        )
        html_content = html_bytes.decode("utf-8") if isinstance(html_bytes, bytes) else html_bytes
        return HTMLResponse(content=html_content)
    except Exception as e:
        error_msg = str(e) + "\n" + traceback.format_exc()
        content = error_msg[:2000]
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        return HTMLResponse(
            content=f"<html><body><h1>Error generating report</h1><p style='font-family:monospace;white-space:pre-wrap;'>{content}</p></body></html>",
            status_code=500,
        )


@app.post("/api/export/bulk/html")
def export_bulk_html_report(req: BulkReportRequest):
    if not req.reports or not isinstance(req.reports, list):
        return JSONResponse({"error": "reports must be a non-empty list"}, status_code=422)
    try:
        combined_html = generate_html_report_bulk(
            reports_data=req.reports,
            agency_name=req.agency_name or "NexGenWebLab",
        )
        return StreamingResponse(
            io.BytesIO(combined_html),
            media_type="text/html",
            headers={"Content-Disposition": "attachment; filename=bulk_seo_report.html"},
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": f"Bulk export failed: {str(e)}"}, status_code=500)


@app.get("/api/report-template")
def get_report_template():
    try:
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
            },
        }
        return template
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": f"Failed to load template: {str(e)}"}, status_code=500)
