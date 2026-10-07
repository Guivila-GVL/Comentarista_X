import os
import shutil
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from app.core.grafana_client import (
    check_grafana_health,
    list_dashboards,
    get_dashboard_panels,
    render_panel
)
from app.core.ai_engine import refine_tweet
from app.core.fact_checker import analyze_and_factcheck

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MEDIA_DIR = STATIC_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(
    title="Proyecto Comentarista API",
    description="Asistente editorial para X con integración en tiempo real de Grafana y motor de IA.",
    version="1.0.0"
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class GenerateRequest(BaseModel):
    idea: str
    tone: Optional[str] = "Divulgativo"
    context_info: Optional[str] = ""

class RenderGrafanaRequest(BaseModel):
    dashboard_uid: str
    panel_id: int
    from_time: Optional[str] = "now-24h"
    to_time: Optional[str] = "now"
    width: Optional[int] = 1200
    height: Optional[int] = 675

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html no encontrado")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/status")
async def get_status():
    grafana_status = check_grafana_health()
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "online",
        "grafana": grafana_status,
        "ai_engine": {
            "provider": "Gemini 2.5 Flash" if has_gemini else "Modo Local Sintético",
            "active": True
        },
        "user_profile": {
            "name": os.getenv("DEFAULT_USER_NAME", "Guillermo Vila"),
            "handle": os.getenv("DEFAULT_USER_HANDLE", "guivila")
        }
    }

@app.get("/api/grafana/dashboards")
async def get_dashboards():
    dashboards = list_dashboards()
    return {"dashboards": dashboards}

@app.get("/api/grafana/panels")
async def get_panels(uid: str = Query(..., description="UID del cuadro de mando")):
    panels = get_dashboard_panels(uid)
    return {"panels": panels}

@app.post("/api/grafana/render")
async def render_grafana_panel(req: RenderGrafanaRequest):
    img_url = render_panel(
        dashboard_uid=req.dashboard_uid,
        panel_id=req.panel_id,
        from_time=req.from_time or "now-24h",
        to_time=req.to_time or "now",
        width=req.width or 1200,
        height=req.height or 675,
        output_dir=str(MEDIA_DIR)
    )
    if not img_url:
        raise HTTPException(status_code=500, detail="Error al renderizar la imagen desde Grafana")
    return {"status": "ok", "image_url": img_url}

@app.post("/api/generate")
async def generate_variants(req: GenerateRequest):
    if not req.idea or not req.idea.strip():
        raise HTTPException(status_code=400, detail="La idea no puede estar vacía")
    result = refine_tweet(req.idea, tone=req.tone or "Divulgativo", context_info=req.context_info or "")
    return result

@app.post("/api/factcheck-and-generate")
async def factcheck_and_generate(req: GenerateRequest):
    """
    Pipeline integral solicitado:
    1. Verifica la afirmación y terminología (fact-checking).
    2. Busca noticias reales y respaldo documental.
    3. Genera una infografía 16:9 explicativa.
    4. Genera variantes de tweets con datos contrastados y enlaces a fuentes.
    """
    if not req.idea or not req.idea.strip():
        raise HTTPException(status_code=400, detail="La idea no puede estar vacía")
    result = analyze_and_factcheck(req.idea)
    return result

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = f"upload_{file.filename}"
    file_path = MEDIA_DIR / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "ok", "image_url": f"/static/media/{filename}"}
