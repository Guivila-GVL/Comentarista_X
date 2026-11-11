"""
Validación de Conexión y Renderizado con Grafana Renderer (8081)
Tarea 26: Validar Conexión con Grafana Renderer (8081)
"""

import sys
import os
import io
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.grafana_client import (
    check_grafana_health,
    check_renderer_health,
    list_dashboards,
    get_dashboard_panels,
    render_panel,
    render_hourly_price_panel
)

def run_renderer_tests():
    print("==================================================================")
    print("  TEST 1: Conexión Directa con Grafana Image Renderer (Puerto 8081)")
    print("==================================================================")
    renderer_health = check_renderer_health()
    print("Renderer Health Response:", renderer_health)
    assert renderer_health["status"] == "ok", f"Renderer offline: {renderer_health}"
    print("[PASS] Grafana Image Renderer responde en http://localhost:8081/healthz")
    print(f"       Versión detectada: {renderer_health.get('version')}")

    print("\n==================================================================")
    print("  TEST 2: Estado del Servidor Grafana (Puerto 3000)")
    print("==================================================================")
    grafana_health = check_grafana_health()
    print("Grafana Health Response:", grafana_health)
    assert grafana_health["status"] == "ok", f"Grafana offline: {grafana_health}"
    print(f"[PASS] Grafana operativo (v{grafana_health.get('version')})")

    print("\n==================================================================")
    print("  TEST 3: Localización de Paneles de Precio Horario de Energía")
    print("==================================================================")
    dashboards = list_dashboards()
    print(f"Dashboards encontrados en Grafana: {len(dashboards)}")
    assert len(dashboards) > 0, "No se encontraron cuadros de mando en Grafana"
    
    hourly_panels = []
    for d in dashboards:
        panels = get_dashboard_panels(d["uid"])
        for p in panels:
            title_lower = p["title"].lower()
            if any(term in title_lower for term in ["precio", "pvpc", "horari"]):
                hourly_panels.append({
                    "dashboard_uid": d["uid"],
                    "dashboard_title": d["title"],
                    "panel_id": p["id"],
                    "panel_title": p["title"]
                })

    print(f"Paneles de precios/horarios identificados: {len(hourly_panels)}")
    for hp in hourly_panels[:5]:
        print(f" - [{hp['dashboard_uid']}] Panel {hp['panel_id']}: '{hp['panel_title']}' ({hp['dashboard_title']})")
    assert len(hourly_panels) > 0, "No se encontró ningún panel de precio horario"

    print("\n==================================================================")
    print("  TEST 4: Renderizado y Descarga de Captura PNG del Panel de Precio Horario")
    print("==================================================================")
    # Seleccionamos panel maestro de precio horario de hoy (uid: pvpc-dashboard-maestro, panel: 105)
    # o primer panel horario encontrado
    target_dashboard = "pvpc-dashboard-maestro"
    target_panel = 105
    target_title = "Curva Horaria 24h - Precio PVPC de Hoy"
    
    print(f"Solicitando renderizado de: {target_title} (DB: {target_dashboard}, Panel: {target_panel})...")
    img_relative_path = render_hourly_price_panel(
        dashboard_uid=target_dashboard,
        panel_id=target_panel,
        from_time="now/d",
        to_time="now"
    )
    
    print("Ruta devuelta por el renderizador:", img_relative_path)
    assert img_relative_path is not None, "El renderizado devolvió None"
    
    img_full_path = Path(__file__).resolve().parent / "app" / img_relative_path.lstrip("/").replace("static/", "static/")
    print("Ruta física del archivo:", img_full_path)
    assert img_full_path.exists(), f"El archivo PNG no existe en disco: {img_full_path}"
    
    file_size = img_full_path.stat().st_size
    print(f"Tamaño del archivo PNG: {file_size} bytes")
    assert file_size > 1000, f"El archivo descargado es demasiado pequeño ({file_size} bytes)"

    # Validación de cabecera y dimensiones con Pillow
    with open(img_full_path, "rb") as f:
        header = f.read(8)
        assert header == b'\x89PNG\r\n\x1a\n', "Cabecera mágica de archivo PNG no válida"
    
    with Image.open(img_full_path) as img:
        print(f"Formato: {img.format}, Dimensiones: {img.size[0]}x{img.size[1]} px, Modo: {img.mode}")
        assert img.format == "PNG", f"Formato incorrecto: {img.format}"
        assert img.size[0] == 1200 and img.size[1] == 675, f"Dimensiones no estándar (se esperaba 1200x675): {img.size}"

    print("[PASS] Captura PNG del panel de precio horario de Grafana verificada exitosamente!")
    print(f"       Archivo generado: {img_full_path.name} ({file_size} bytes)")
    
    print("\n==================================================================")
    print("  TEST 5: Endpoint FastAPI /api/grafana/renderer/health")
    print("==================================================================")
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    res_health = client.get("/api/grafana/renderer/health")
    assert res_health.status_code == 200, f"Renderer health endpoint failed: {res_health.status_code}"
    print("[PASS] Endpoint /api/grafana/renderer/health:", res_health.json())

    res_status = client.get("/api/status")
    assert res_status.status_code == 200
    assert "renderer" in res_status.json().get("grafana", {})
    print("[PASS] Endpoint /api/status integra renderer:", res_status.json()["grafana"]["renderer"])

    print("\n==================================================================")
    print("  TODAS LAS PRUEBAS DE GRAFANA RENDERER (8081) SUPERADAS CON ÉXITO")
    print("==================================================================")

if __name__ == "__main__":
    run_renderer_tests()
