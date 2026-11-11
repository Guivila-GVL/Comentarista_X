"""
Script de verificación de salud y diagnóstico del servidor de Comentarista en puerto 8000.
"""
import sys
import json
import urllib.request

def check_server(host="127.0.0.1", port=8000):
    base_url = f"http://{host}:{port}"
    print(f"Verificando servidor en {base_url}...")
    
    endpoints = [
        ("/", "Página Principal (HTML)"),
        ("/api/status", "Estado de la API y Grafana"),
        ("/docs", "Documentación Swagger de FastAPI"),
    ]
    
    all_ok = True
    for path, description in endpoints:
        url = f"{base_url}{path}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HealthCheck/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                status_code = resp.status
                body = resp.read()
                if status_code == 200:
                    print(f"  [PASS] {description} ({path}) -> HTTP {status_code} OK ({len(body)} bytes)")
                    if path == "/api/status":
                        try:
                            data = json.loads(body.decode("utf-8"))
                            grafana_status = data.get("grafana", {}).get("status", "unknown")
                            ai_provider = data.get("ai_engine", {}).get("provider", "unknown")
                            print(f"         + Grafana: {grafana_status}")
                            print(f"         + Motor IA: {ai_provider}")
                        except Exception:
                            pass
                else:
                    print(f"  [FAIL] {description} ({path}) -> HTTP {status_code}")
                    all_ok = False
        except Exception as e:
            print(f"  [ERROR] {description} ({path}) -> Error de conexión: {e}")
            all_ok = False

    return all_ok

if __name__ == "__main__":
    success = check_server()
    if success:
        print("\n=> DIAGNÓSTICO: Servidor Comentarista respondiendo 200 OK en el puerto 8000. Estado operativo.")
        sys.exit(0)
    else:
        print("\n=> DIAGNÓSTICO: Fallo al conectar o respuestas inesperadas en el puerto 8000.")
        sys.exit(1)
