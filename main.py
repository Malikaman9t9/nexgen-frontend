import os
import io
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from modules.onpage_scraper import get_basic_onpage
from modules.speed_checker import check_speed
from modules.traffic_checker import get_traffic_data
from modules.ai_analyzer import get_ai_suggestions
from modules.report_export import generate_word_report

load_dotenv()

SPEED_API_KEY = os.getenv("SPEED_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

app = FastAPI(title="NexGenWebLab API")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS.split(","),
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
    speed_data: dict
    ai_suggestions: list = []
    agency_name: str = "NexGenWebLab Pro"
    client_name: str = "Client"
    author_name: str = "SEO Team"

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
    docx_bytes = generate_word_report(
        url=req.url,
        onpage_data=req.onpage_data,
        speed_data=req.speed_data,
        ai_suggestions=req.ai_suggestions,
        agency_name=req.agency_name,
        client_name=req.client_name,
        author_name=req.author_name,
    )
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={req.client_name.replace(' ', '_')}_SEO_Report.docx"},
    )

@app.get("/api/health")
def health():
    return {"status": "ok"}
