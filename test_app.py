import sys
import io
from fastapi.testclient import TestClient
from app.main import app

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = TestClient(app)

def run_tests():
    print("--- 1. Testing Index HTML ---")
    r = client.get("/")
    assert r.status_code == 200, f"Index failed: {r.status_code}"
    print("[PASS] Index HTML 200 OK")

    print("\n--- 2. Testing API Status ---")
    r = client.get("/api/status")
    assert r.status_code == 200, f"Status failed: {r.status_code}"
    status_data = r.json()
    print("[PASS] Status:", status_data)

    print("\n--- 3. Testing Grafana Dashboards ---")
    r = client.get("/api/grafana/dashboards")
    assert r.status_code == 200, f"Dashboards failed: {r.status_code}"
    dbs = r.json().get("dashboards", [])
    print(f"[PASS] Grafana Dashboards count: {len(dbs)}")

    print("\n--- 4. Testing Grafana Panels for 'pvpc-generacion-ingresos' ---")
    r = client.get("/api/grafana/panels?uid=pvpc-generacion-ingresos")
    assert r.status_code == 200
    panels = r.json().get("panels", [])
    print(f"[PASS] Panels count: {len(panels)}")
    for p in panels[:5]:
        print(f"  - [Panel {p['id']}] {p['title']}")

    print("\n--- 5. Testing Tweet Generation & Optimization ---")
    r = client.post("/api/generate", json={
        "idea": "Hoy el precio del pool eléctrico ha marcado 0,00 €/MWh durante 6 horas por la gran producción eólica. Las baterías han cargado a coste cero.",
        "tone": "Divulgativo"
    })
    assert r.status_code == 200, f"Generate failed: {r.status_code}"
    variants = r.json().get("variants", [])
    print(f"[PASS] Generated {len(variants)} variants")

    print("\n--- 6. Testing Fact-Checking & Infographic Pipeline (User Case: RESA) ---")
    user_idea = "El sistema de protección RESA se ha activado otra vez. El deterioro de nuestra infraestructura eléctrica no para."
    r = client.post("/api/factcheck-and-generate", json={
        "idea": user_idea,
        "tone": "Divulgativo"
    })
    assert r.status_code == 200, f"Factcheck failed: {r.status_code}"
    fc_data = r.json()
    print("[PASS] Fact-check verdict:", fc_data["fact_check"]["verdict"])
    print("[PASS] News reference:", fc_data["news"][0]["title"])
    print("[PASS] Infographic created:", fc_data["infographic_url"])
    print("[PASS] Verified variants count:", len(fc_data["variants"]))
    for v in fc_data["variants"]:
        print(f"  - [{v['tone']}] ({v['char_count']} chars): {v['text'][:70]}...")

    print("\n===============================")
    print("ALL APP INTEGRATION TESTS PASSED!")
    print("===============================")

if __name__ == "__main__":
    run_tests()
