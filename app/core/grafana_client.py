import os
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000").rstrip("/")
GRAFANA_AUTH = os.getenv("GRAFANA_AUTH", "Basic YWRtaW46NjM3M0d1aWxsZQ==")

def get_headers() -> Dict[str, str]:
    headers = {}
    if GRAFANA_AUTH:
        headers["Authorization"] = GRAFANA_AUTH
    return headers

def check_grafana_health() -> Dict[str, Any]:
    """Comprueba el estado del servidor local de Grafana."""
    try:
        r = requests.get(f"{GRAFANA_URL}/api/health", headers=get_headers(), timeout=3)
        if r.status_code == 200:
            return {"status": "ok", "version": r.json().get("version", "unknown")}
        return {"status": "error", "message": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"status": "offline", "message": str(e)}

def list_dashboards() -> List[Dict[str, Any]]:
    """Obtiene la lista de cuadros de mando disponibles en Grafana."""
    try:
        r = requests.get(f"{GRAFANA_URL}/api/search?type=dash-db", headers=get_headers(), timeout=5)
        if r.status_code == 200:
            dashboards = []
            for item in r.json():
                dashboards.append({
                    "id": item.get("id"),
                    "uid": item.get("uid"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "folderTitle": item.get("folderTitle", "General")
                })
            return dashboards
        return []
    except Exception as e:
        print(f"[GrafanaClient] Error al listar dashboards: {e}")
        return []

def get_dashboard_panels(dashboard_uid: str) -> List[Dict[str, Any]]:
    """Obtiene todos los paneles configurados dentro de un dashboard específico."""
    try:
        r = requests.get(f"{GRAFANA_URL}/api/dashboards/uid/{dashboard_uid}", headers=get_headers(), timeout=5)
        if r.status_code != 200:
            return []
        
        data = r.json()
        dashboard_meta = data.get("dashboard", {})
        slug = data.get("meta", {}).get("slug", dashboard_uid)
        panels_raw = dashboard_meta.get("panels", [])
        
        clean_panels = []
        for p in panels_raw:
            # Los paneles tipo 'row' o sin título a veces son separadores
            p_id = p.get("id")
            p_title = p.get("title") or f"Panel {p_id}"
            p_type = p.get("type", "desconocido")
            
            # Si es una fila con sub-paneles
            if p_type == "row" and "panels" in p:
                for sub_p in p["panels"]:
                    clean_panels.append({
                        "id": sub_p.get("id"),
                        "title": sub_p.get("title") or f"Panel {sub_p.get('id')}",
                        "type": sub_p.get("type"),
                        "slug": slug,
                        "uid": dashboard_uid
                    })
            else:
                clean_panels.append({
                    "id": p_id,
                    "title": p_title,
                    "type": p_type,
                    "slug": slug,
                    "uid": dashboard_uid
                })
        return clean_panels
    except Exception as e:
        print(f"[GrafanaClient] Error al obtener paneles para {dashboard_uid}: {e}")
        return []

def render_panel(
    dashboard_uid: str,
    panel_id: int,
    from_time: str = "now-24h",
    to_time: str = "now",
    width: int = 1200,
    height: int = 675,
    output_dir: Optional[str] = None
) -> Optional[str]:
    """
    Renderiza un panel de Grafana a formato imagen PNG mediante su endpoint /render/d-solo.
    Optimizado en 1200x675 (proporción 16:9 ideal para X).
    """
    try:
        # Obtenemos el slug para una URL limpia de Grafana
        r_meta = requests.get(f"{GRAFANA_URL}/api/dashboards/uid/{dashboard_uid}", headers=get_headers(), timeout=5)
        slug = dashboard_uid
        if r_meta.status_code == 200:
            slug = r_meta.json().get("meta", {}).get("slug", dashboard_uid)
            
        render_url = (
            f"{GRAFANA_URL}/render/d-solo/{slug}/{dashboard_uid}"
            f"?orgId=1&panelId={panel_id}&width={width}&height={height}&from={from_time}&to={to_time}"
        )
        
        r = requests.get(render_url, headers=get_headers(), timeout=25)
        if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
            if not output_dir:
                output_dir = os.path.join(os.path.dirname(__file__), "..", "static", "media")
            
            os.makedirs(output_dir, exist_ok=True)
            filename = f"grafana_{dashboard_uid}_p{panel_id}_{int(os.times()[4])}.png"
            file_path = os.path.join(output_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(r.content)
            
            # Devolvemos la ruta relativa para el frontend
            return f"/static/media/{filename}"
        else:
            print(f"[GrafanaClient] Error en respuesta de renderizado: {r.status_code} - {r.text[:200]}")
            return None
    except Exception as e:
        print(f"[GrafanaClient] Excepción durante el renderizado: {e}")
        return None
