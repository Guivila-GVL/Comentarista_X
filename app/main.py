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
    check_renderer_health,
    list_dashboards,
    get_dashboard_panels,
    render_panel,
    render_hourly_price_panel
)
from app.core.ai_engine import refine_tweet, modify_tweet_with_feedback
from app.core.fact_checker import (
    process_idea_and_prepare_tweet,
    update_infographic_custom
)

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

class RefineRequest(BaseModel):
    current_text: str
    feedback: str
    fact_context: Optional[str] = ""
    tone: Optional[str] = "Divulgativo"

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

@app.get("/api/grafana/renderer/health")
async def get_renderer_health():
    """Comprueba el estado directo del servicio Grafana Image Renderer (8081)."""
    return check_renderer_health()

@app.post("/api/grafana/render-hourly-price")
async def render_hourly_price(
    dashboard_uid: Optional[str] = "pvpc-dashboard-maestro",
    panel_id: Optional[int] = 105,
    from_time: Optional[str] = "now/d",
    to_time: Optional[str] = "now"
):
    """Renderiza de forma directa la captura del panel de precio horario de Grafana."""
    img_url = render_hourly_price_panel(
        dashboard_uid=dashboard_uid or "pvpc-dashboard-maestro",
        panel_id=panel_id or 105,
        from_time=from_time or "now/d",
        to_time=to_time or "now",
        output_dir=str(MEDIA_DIR)
    )
    if not img_url:
        raise HTTPException(status_code=500, detail="Error al renderizar el panel de precio horario")
    return {"status": "ok", "image_url": img_url}

@app.post("/api/generate")
async def generate_variants(req: GenerateRequest):
    if not req.idea or not req.idea.strip():
        raise HTTPException(status_code=400, detail="La idea no puede estar vacía")
    result = refine_tweet(req.idea, tone=req.tone or "Divulgativo", context_info=req.context_info or "")
    return result

class InfographicUpdateRequest(BaseModel):
    title: Optional[str] = "Infografía"
    subtitle: Optional[str] = ""
    cards: Optional[list] = []
    instruction: Optional[str] = ""

class ConfigRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    user_name: Optional[str] = None
    user_handle: Optional[str] = None

@app.post("/api/search-and-draft")
async def search_and_draft(req: GenerateRequest):
    """
    PASO 1 y 2: Busca noticias y datos reales relacionados con la idea.
    PASO 3: Redacta y prepara el tweet directamente para el simulador de X.
    PASO 4: Estructura los 3 puntos de la infografía.
    """
    if not req.idea or not req.idea.strip():
        raise HTTPException(status_code=400, detail="La idea no puede estar vacía")
    result = process_idea_and_prepare_tweet(req.idea, tone=req.tone or "Divulgativo")
    return result

@app.post("/api/factcheck-and-generate")
async def factcheck_and_generate(req: GenerateRequest):
    """Compatibilidad: Mapea al pipeline dinámico"""
    if not req.idea or not req.idea.strip():
        raise HTTPException(status_code=400, detail="La idea no puede estar vacía")
    return process_idea_and_prepare_tweet(req.idea, tone=req.tone or "Divulgativo")

@app.post("/api/refine")
async def refine_tweet_post(req: RefineRequest):
    """
    Refinamiento iterativo guiado por los comentarios del usuario:
    Aplica las modificaciones directamente sobre el tweet en vivo.
    """
    if not req.current_text or not req.current_text.strip():
        raise HTTPException(status_code=400, detail="El tweet actual está vacío")
    if not req.feedback or not req.feedback.strip():
        raise HTTPException(status_code=400, detail="La instrucción o comentario no puede estar vacía")
    
    result = modify_tweet_with_feedback(
        current_text=req.current_text,
        feedback=req.feedback,
        fact_context=req.fact_context or "",
        tone=req.tone or "Divulgativo"
    )
    return result

@app.post("/api/update-infographic")
async def update_infographic_endpoint(req: InfographicUpdateRequest):
    """
    Permite modificar y regenerar la infografía al vuelo con las órdenes del usuario
    o con las tarjetas editadas directamente.
    """
    cards = req.cards or []
    # Si el usuario dio una orden textual de modificación sobre las tarjetas
    if req.instruction:
        instr_lower = req.instruction.lower()
        # Modificar título si lo pide
        if "título" in instr_lower or "titulo" in instr_lower:
            parts = req.instruction.split(":", 1)
            if len(parts) > 1:
                req.title = parts[1].strip()
        # Si pide modificar alguna tarjeta
        for i, card in enumerate(cards):
            target_str = f"tarjeta {i+1}"
            if target_str in instr_lower or (i == 1 and "tarjeta 2" in instr_lower):
                card["desc"] = req.instruction[:75]
                card["val"] = "Dato Actualizado"

    img_url = update_infographic_custom(
        title=req.title or "Claves del Análisis",
        subtitle=req.subtitle or "Datos e información contrastada",
        cards=cards
    )
    return {
        "status": "ok",
        "infographic_url": img_url,
        "infographic_data": {
            "title": req.title,
            "subtitle": req.subtitle,
            "cards": cards
        }
    }

@app.post("/api/config")
async def update_config(req: ConfigRequest):
    """Permite guardar claves y configuración directamente desde la UI."""
    env_path = BASE_DIR.parent / ".env"
    lines = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    
    config_dict = {
        "GEMINI_API_KEY": req.gemini_api_key,
        "DEFAULT_USER_NAME": req.user_name,
        "DEFAULT_USER_HANDLE": req.user_handle
    }

    new_lines = []
    seen = set()
    for line in lines:
        matched = False
        for k, v in config_dict.items():
            if v is not None and line.startswith(f"{k}="):
                new_lines.append(f"{k}={v}\n")
                seen.add(k)
                matched = True
                break
        if not matched:
            new_lines.append(line)

    for k, v in config_dict.items():
        if v is not None and k not in seen:
            new_lines.append(f"{k}={v}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    load_dotenv(override=True)
    return {"status": "ok", "message": "Configuración guardada correctamente"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = f"upload_{file.filename}"
    file_path = MEDIA_DIR / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "ok", "image_url": f"/static/media/{filename}"}
